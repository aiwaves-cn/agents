import copy
import json
import logging
import os.path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.optimization.optimizer import Optimizer
from agents.utils.prompts import DEFAULT_NODE_PROMPT_TEMPLATES
from agents.evaluation import Case
from agents.agents.llm import LLMConfig, OpenAILLM
from agents.task.solution import SolutionConfig, Solution
from agents.optimization.optimizer import OptimizerConfig
from agents.optimization.utils import OptimUtils
from agents.optimization import prompt_formatter


class PromptOptimizerConfig(OptimizerConfig):
    """
    Configuration for the Prompt Optimizer.

    This class parses and stores the configuration settings specific to the prompt optimizer,
    extending the generic OptimizerConfig.

    Args:
        config_path (str): Path to the configuration file.

    Attributes:
        allow_delete_template_variable (bool): Whether to allow deleting template variables. Defaults to False.
        llm_config (dict): Configuration dictionary for the large language model.
        meta_prompt (dict): Configuration dictionary for the meta prompt.
        needed_optim_component (list): List of components that need optimization.
        needed_optim_padding (bool): Whether padding is needed for optimization. Defaults to False.
    """

    def __init__(self, config_path):
        super().__init__(config_path)

        # The parent class parses the part of the fields that are public, and only the fields that prompt_optimizer are parsed here
        self.allow_delete_template_variable: bool = self.prompt_optimizer_setting_dict.get(
            "allow_delete_template_variable", False
        )
        self.llm_config: dict = self.prompt_optimizer_setting_dict.get("llm_config")
        self.meta_prompt: dict = self.prompt_optimizer_setting_dict.get("meta_prompt")
        self.needed_optim_component: list = self.prompt_optimizer_setting_dict.get("needed_optim_component")
        self.needed_optim_padding: bool = self.prompt_optimizer_setting_dict.get("needed_optim_padding", False)


class PromptOptimizer(Optimizer):
    """
    The Prompt Optimizer class for optimizing prompts.

    This class extends the generic Optimizer and uses the PromptOptimizerConfig to set up
    prompt optimization, including handling large language model (LLM) configurations and
    managing optimization components.

    Args:
        config (PromptOptimizerConfig): Configuration instance for the prompt optimizer.
        logger_name (str, optional): Name of the logger. Defaults to None.
    """

    def __init__(self, config: PromptOptimizerConfig, logger_name=None):
        super().__init__(config)
        self.config = config

        # Specifies whether to delete variables in the prompt template
        self.allow_delete_template_variable = config.allow_delete_template_variable
        assert (not self.has_ground_truth) or (
                self.has_ground_truth and self.has_result
        )

        # prompt
        self.meta_backward = config.meta_prompt["backward"]
        self.meta_optim = config.meta_prompt["optimization"]

        # optim_component
        self.needed_optim_component = config.needed_optim_component
        self.needed_optim_padding = config.needed_optim_padding

        # llm
        llm_config = LLMConfig(config.llm_config)
        self.llm_eval = OpenAILLM(llm_config) if llm_config else None

        # log
        self.logger = logging.getLogger(logger_name) if logger_name else logging.getLogger(__name__)

    def optimize(self, case_list: list[Case], solution: Solution, save_step_path, parallel_max_num=8):
        """
        Optimizes the prompts for a list of cases and updates the solution accordingly.

        Args:
            case_list (list[Case]): The list of cases to be optimized.
            solution (Solution): The solution to be optimized.
            save_step_path (str): The path to save the results of each step.
            parallel_max_num (int): The maximum number of parallel processes. Defaults to 8.

        Returns:
            tuple: The updated solution and optimization status.
        """
        step_info = {"score_before_optim": [case.loss.score for case in case_list]}
        step_info["average_score_before_optim"] = sum(step_info["score_before_optim"]) / len(case_list)

        # step2: get loss(the difference between result and ground_truth) and calculate the gradient of the loss
        self.logger.debug("In prompt optimizer, start backward")
        self.parallel_backward(case_list, parallel_max_num, save_step_path / "case_after_backward")
        self.logger.debug("In prompt optimizer, backward finished")

        # step3: update sop's prompt_template
        self.logger.debug("In prompt optimizer, start optimize prompt")
        optim_info_list = self.optimize_prompt(case_list)

        # attempt to optimize the solution based on optim_info_list
        optim_status = self.try_optim_prompt(case_list, solution, optim_info_list)

        # Determine the version of solution and case accepted by the current step
        for case in case_list:
            case.dump(os.path.join(str(save_step_path / "case_final"), f"{case.case_id}.json"))
        solution.dump(save_step_path)
        solution = Solution(config=SolutionConfig(f"{save_step_path}/solution.json"))

        # save the step info
        self.save_step(
            save_step_path,
            optim_info_list,
            step_info,
            optim_status,
        )
        return solution, optim_status

    def backward(self, case: Case, save_dir: str = None):
        """
        Performs backward optimization for the given case to get the gradient of the loss.

        Args:
            case (Case): The case to be optimized.
            save_dir (str, optional): The directory to save the results. Defaults to None.
        """
        # Transfer the result from loss, specifically the requirements/suggestions for the previous state, to the last state
        last_requirement_for_previous = case.loss.requirement_for_previous

        # Process each state to get modification suggestions, from back to front
        for s_idx, state in enumerate(case.trajectory.states[::-1]):
            # Get the state data and fill it into backward_prompt_temp
            state_index = len(case.trajectory.states) - s_idx - 1
            state_data = state.get_dict_for_trainer(
                ["prompt_template", "response", "prompt_components", "last_prompt_str", "prompts_order"])

            # Needed optimization components, if padding is needed, add all keys from prompt_template
            state_data["needed_optim_component"] = self.needed_optim_component[:]
            state_data["needed_optim_component"].extend(
                state_data["prompt_template"].keys()) if self.needed_optim_padding else None
            state_data["requirement_for_previous"] = last_requirement_for_previous
            state_data["previous_output"] = (
                case.trajectory.states[state_index - 1].action.content
                if state_index > 0
                else "This is the first node, no previous output."
            )
            state_data["content"] = state.action.content

            # Construct the prompt and call the model
            backward_prompt = prompt_formatter.formulate_prompt(self.meta_backward, state_data)

            # Call the large model to evaluate and extract results
            _, content = self.llm_eval.get_response(
                chat_messages=None,
                system_prompt="",
                last_prompt=backward_prompt,
                stream=False,
            )

            backward_info_dict = OptimUtils.extract_data_from_response(
                content,
                self.meta_backward["extract_key"],
                self.logger,
                "There are neither suggestions nor requirements.",
            )
            backward_info_dict["response"] = content
            backward_info_dict["prompt"] = backward_prompt
            assert "suggestion" in backward_info_dict.keys(), "suggestion must be in the extracted data"
            assert "requirement_for_previous" in backward_info_dict.keys(), "requirement_for_previous must be in the extracted data"

            # Update last_state_requirement, i.e., current state's requirements/suggestions for the previous state
            state.backward.update(**backward_info_dict)
            last_requirement_for_previous = state.backward.requirement_for_previous

        # save the case
        if save_dir:
            case.dump(os.path.join(save_dir, f"{case.case_id}.json"))

    def parallel_backward(
            self, case_list: list[Case], parallel_max_num, save_case_dir=None
    ):
        """
        Performs parallel backward optimization for a list of cases.

        Args:
            case_list (list[Case]): The list of cases to be optimized.
            parallel_max_num (int): The maximum number of parallel processes.
            save_case_dir (str, optional): The directory to save the cases after backward. Defaults to None.
        """
        with ThreadPoolExecutor(max_workers=parallel_max_num) as executor:
            futures = [
                executor.submit(self.backward, case, str(save_case_dir))
                for case in case_list
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error processing case: {e}")

    def optimize_prompt(self, case_list: list[Case]):
        """
        Optimizes the agent's prompt to minimize loss.

        Args:
            case_list (list[Case]): A batch of cases.

        Returns:
            list: A list of optimization information.
        """
        optim_info_list = []

        # Start optimizing from the last state, therefore it's a double loop: outer is state, inner is case
        case0_state_num = len(case_list[0].trajectory.states)
        for state_idx in range(case0_state_num - 1, -1, -1):
            # Call the large model for optimization and store the results in sop
            optim_prompt = prompt_formatter.formulate_prompt_for_prompt_optim(
                self.meta_optim, case_list, state_idx, self.needed_optim_component)
            _, content = self.llm_eval.get_response(
                chat_messages=None, system_prompt="", last_prompt=optim_prompt, stream=False)

            # print("\033[93m" + f"optim的prompt为：\n{optim_prompt}" + "\033[0m")
            # print("\033[93m" + f"optim的输出结果为：\n{content}" + "\033[0m")

            # Extract the output results: ["new_prompt", "analyse"]
            extract_dict = OptimUtils.extract_data_from_response(content, self.meta_optim["extract_key"])

            cur_optim_info = {
                "new_prompt": extract_dict["new_prompt"],
                "analyse": extract_dict.get("analyse", "未输出analyse"),
                "suggestion": [
                    case.trajectory.states[state_idx].backward.suggestion
                    for case in case_list
                ],
            }
            optim_info_list.insert(0, cur_optim_info)

        return optim_info_list

    def try_optim_prompt(self, case_list: list[Case], solution, optim_info_list):
        """
        Checks each prompt for validity and updates the solution if valid.

        Args:
            case_list (list[Case]): The list of cases.
            solution (Solution): The solution to be updated.
            optim_info_list (list): The list of optimization information.

        Returns:
            bool: The optimization status.
        """
        optim_status = False
        for state_index, cur_optim_info in enumerate(optim_info_list):
            # Save new template if valid
            new_template = cur_optim_info["new_prompt"]
            node_name = case_list[0].trajectory.states[state_index].node.node_name
            role_name = case_list[0].trajectory.states[state_index].action.agent_role

            # Get old configuration for comparison and validity check
            used_padding_template = case_list[0].trajectory.states[state_index].action.used_prompt_templates
            used_primary_template = solution.sop.nodes[node_name].node_primary_prompts[role_name]
            last_used_template = {**used_padding_template, **used_primary_template}

            check_result, new_template_dict, old_prompt_dict = (
                self.check_if_new_prompt_legal(
                    new_template,
                    last_used_template,
                    self.allow_delete_template_variable,
                    self.logger,
                )
            )

            if check_result:
                optim_status = True  # There is at least one valid optimization result
                self.update_prompt(solution, node_name, role_name, new_template_dict)

                self.logger.info(f"The new prompt for state_idx {state_index} is valid and updated in the solution.")
                self.logger.debug(f"The new prompt: {str(new_template_dict)}")
                self.logger.debug(f"The old prompt: {str(old_prompt_dict)}")
            else:
                self.logger.info(f"The new prompt for state_idx {state_index} is invalid.")
                self.logger.debug(f"The invalid new prompt: {str(new_template_dict)}")
        return optim_status

    def update_prompt(self, solution, node_name, role_name, new_template_dict):
        """
        Updates the prompt in the solution.

        Args:
            solution (Solution): The solution to be updated.
            node_name (str): The name of the node.
            role_name (str): The name of the role.
            new_template_dict (dict): The new template dictionary.
        """
        for key in new_template_dict:
            node = solution.sop.nodes[node_name]
            if key in ["TASK", "RULE", "STYLE", "EXAMPLE", "COT"]:
                node.node_primary_prompts[role_name][key] = new_template_dict[key]
            else:
                node.node_prompt_templates[key] = new_template_dict[key]

    @staticmethod
    def save_step(step_save_path, optim_info_list, step_info, optim_status):
        """
        Saves the final optimization results.

        Args:
            step_save_path (str): The path to save the step information.
            optim_info_list (list): The list of optimization information.
            step_info (dict): The step information.
            optim_status (bool): The optimization status.
        """
        step_info.update({"optim_status": optim_status, "optim_info": optim_info_list})

        with open(step_save_path / "step_info.json", "a", encoding="utf-8") as f:
            json.dump(step_info, f, ensure_ascii=False, indent=4)

    @staticmethod
    def check_if_new_prompt_legal(
            new_prompt_dict_str: str,
            old_prompt_dict: dict,
            allow_delete_template_variable: bool = False,
            logger=None,
    ):
        """
        Check if the new prompt is legal.

        This function checks whether the new prompt (given as a JSON string) is a valid update
        to the old prompt. It ensures that the new prompt's keys are a subset of the old prompt's keys
        and that variable counts are appropriate based on the `allow_delete_template_variable` flag.

        Args:
            new_prompt_dict_str (str): The new prompt as a JSON string, corresponding to the
                `node_prompt_templates` field in the SOP.
            old_prompt_dict (dict): The old prompt as a dictionary, corresponding to the
                `node_prompt_templates` field in the SOP.
            allow_delete_template_variable (bool, optional): Whether deleting variables in the template is allowed.
                Defaults to False.
            logger (Logger, optional): Logger instance for logging information and errors. Defaults to None.

        Returns:
            tuple: A tuple containing:
                - bool: Indicates whether the new prompt is legal.
                - dict or None: The new prompt as a dictionary if it is legal, otherwise None.
                - dict: The old prompt dictionary.
        """
        old_prompt_dict = copy.deepcopy(old_prompt_dict)
        if not new_prompt_dict_str or new_prompt_dict_str == "{}":
            logger.info("The new prompt is empty or just an empty bracket '{}', not optimizing.")
            return False, {}, old_prompt_dict

        # Handle special character issues and convert the string to a JSON dictionary
        try:
            fixed_new_prompt_dict_str = OptimUtils.escape_special_chars_in_json_string(new_prompt_dict_str)
            if fixed_new_prompt_dict_str != new_prompt_dict_str:
                logger.info(
                    "Special characters found in the new prompt and have been escaped. The escaped prompt is: " + fixed_new_prompt_dict_str)
            new_prompt_dict = json.loads(fixed_new_prompt_dict_str)
        except json.JSONDecodeError:
            logger.error("The new prompt is not a valid JSON format: " + new_prompt_dict_str)
            return False, None, old_prompt_dict

        # Ensure the keys in the new prompt are a subset of the keys in the old prompt
        if not set(new_prompt_dict.keys()).issubset(set(old_prompt_dict.keys())):
            logger.error(
                "New prompt dictionary contains new keys. New prompt keys: " + str(
                    new_prompt_dict.keys()) + ", Old prompt keys: " + str(old_prompt_dict.keys()))
            return False, None, old_prompt_dict

        # Iterate and check if each prompt is valid
        for key in new_prompt_dict.keys():
            new_prompt = new_prompt_dict[key]
            old_prompt = old_prompt_dict[key]

            old_variables = prompt_formatter.get_config_needed_variables(
                {"old_prompt": old_prompt}, specific_key_list=["old_prompt"]
            )
            new_variables = prompt_formatter.get_config_needed_variables(
                {"new_prompt": new_prompt}, specific_key_list=["new_prompt"]
            )

            # 1. Check if there are additional variables
            if len(new_variables) > len(old_variables):
                logger.error(
                    "The number of variables in the new prompt exceeds that in the old prompt. New prompt variables: " +
                    str(new_variables) + ", Old prompt variables: " + str(old_variables))
                return False, None, old_prompt_dict

            # 2. Check if there are deleted variables
            if len(new_variables) < len(old_variables):
                if not allow_delete_template_variable:
                    if logger:
                        logger.error(
                            "The number of variables in the new prompt is less than that in the old prompt, and allow_delete_template_variable is False. New prompt variables: " + str(
                                new_variables) + ", Old prompt variables: " + str(old_variables))
                    return False, None, old_prompt_dict
                else:
                    if logger:
                        logger.info(
                            "The number of variables in the new prompt is less than that in the old prompt, but deleting template variables is allowed. New prompt variables: " + str(
                                new_variables) + ", Old prompt variables: " + str(old_variables))

            # 3. Check if there are modified variables
            for var in new_variables:
                if var not in old_variables:
                    if logger:
                        logger.error(
                            f"Variable {var} in the new prompt is not in the old prompt. New prompt: {new_prompt}, Old prompt: {old_prompt}")
                    return False, None, old_prompt_dict

        return True, new_prompt_dict, old_prompt_dict


if __name__ == "__main__":
    backward_component_cn = """
    你现在是一个大语言模型的prompt精调师，现在需要你给出一些对prompt模板的优化建议，给出的建议请使用<suggestion></suggestion>包裹，比如<suggestion>可以简短一些</suggestion>。
    整个任务分为多个步骤完成，我会给你前一步的输出，后一步对当前步的要求，当前步的输出和prompt_components，你需要对当前步的prompt_components提出改进的建议，实际使用时的prompt是由prompt_components拼接而成的。

    - 当前的prompt_components是：<prompt_components>{prompt_components}</prompt_components>
    - 按顺序拼接prompt_components可以组成prompt，拼接的顺序为：<order>{prompts_order}</order>

    - 前一步的输出结果是：<previous_output>{previous_output}</previous_output>

    - 当前的输出是：<output>{response}</output>

    - 后一步的对当前步输出的要求是: <requirement>{requirement_for_previous}</requirement>

    - 需要你优化的prompt模板的字段是：{needed_optim_component}

    你需要对prompt_components中的指定字段进行优化，建议请使用自然语言给出，并使用<suggestion></suggestion>包裹，
    对当前prompt提出修改建议。你还需要提出前一步输出的要求，请使用<requirement_for_previous></requirement_for_previous>包裹，比如：<requirement_for_previous>分析中应该包括原始数据的比较</requirement_for_previous>。

    注意：
    1.请务必保证输出的结果分别用<requirement_for_previous></requirement_for_previous>、<suggestion></suggestion>包裹，且只出现一次。
    2.如果你是第一个节点，用<requirement_for_previous></requirement_for_previous>中可以是“当前是第一个节点”
    3.请注意，在分析的时候请记住这个prompt模板会被应用到多个不同的数据上，所以你的建议应该是通用的，不应只专注于此处提供的例子。
    4.请一步步分析。
    """

    backward_component_en = """
    You are now a prompt optimization specialist for a large language model. You need to provide some optimization suggestions for the prompt templates. Please use `<suggestion></suggestion>` to wrap your suggestions, for example, `<suggestion>can be shorter</suggestion>`.

    The entire task is completed in multiple steps. I will provide you with the output of the previous step, the requirements for the current step, the output of the current step, and the prompt_components. You need to propose improvements for the prompt_components of the current step. The actual prompt used is assembled from prompt_components.

    - The current prompt_components are: <prompt_components>{prompt_components}</prompt_components>

    - The prompt can be composed by concatenating the prompt_components in the following order: <order>{prompts_order}</order>

    - The output of the previous step is: <previous_output>{previous_output}</previous_output>

    - The output of the current step is: <output>{response}</output>

    - The requirement for the current step's output is: <requirement>{requirement_for_previous}</requirement>

    - The field of the prompt template that needs to be optimized is: {needed_optim_component}

    You need to optimize the specified field in the prompt_components. Please provide suggestions in natural language and wrap them with `<suggestion></suggestion>`. 
    Propose modifications to the current prompt. You also need to propose requirements for the output of the previous step. Please use `<requirement_for_previous></requirement_for_previous>` to wrap them, for example: `<requirement_for_previous>The analysis should include a comparison of the original data</requirement_for_previous>`.

    Note:
    1. Please ensure that the output is wrapped with `<requirement_for_previous></requirement_for_previous>` and `<suggestion></suggestion>`, and appears only once.
    2. If you are the first node, use `<requirement_for_previous>Current is the first node</requirement_for_previous>`.
    3. Please remember that this prompt template will be applied to multiple different data sets, so your suggestions should be general and not just focused on the provided example.
    4. Please analyze step by step.
    """

    optim_component = """
你现在是一个大语言模型的prompt精调师，我会给你一个prompt模板及其对应的输入和输出信息，请根据给出的数据对prompt进行修改：
- 当前的prompt_components是：<prompt_components>{prompt_components}</prompt_components>
- 按顺序拼接prompt_components可以组成prompt，拼接的顺序为：<order>{prompts_order}</order>

如下是对prompt_components的一些解释信息，这些prompt_components是用于构建prompt_template的基本组成部分：
{
    "TASK": "与这个任务有关的描述信息",
    "RULE": "限定输出的一些规则",
    "STYLE": "限定回答的风格",
    "EXAMPLE": "便于理解的例子",
    "COT": "用于让大模型一步步推理分析，比如please think step by step"
}

如下是采用这个template时模型的一些信息：

# Instance {index}
- 对prompt的修改建议: <suggestion>{suggestion}</suggestion>

你需要依据以上内容进行分析，并输出优化后的prompt结果。你只需要优化如下的字段：{needed_optim_component}。
分析的过程请使用<analyse></analyse>包裹，新的prompt请用<new_prompt></new_prompt>包裹，具体内容应使用json格式的字典给出，其应可以直接被json.loads()方法转换为字典。

比如，当需要优化字段"COT"和"STYLE"时，你的输出应为：<new_prompt>{"COT": "Please think step by step","STYLE": "Please answer in an essay style"}</new_prompt>。
如果你认为原先的COT字段已经足够优秀，在优化prompt的字典中应该不包含"COT"字段，如果你认为所有的字段都已足够优秀，请输出空字典，即<new_prompt>{}</new_prompt>。

注意：
1. 实际使用prompt模板时，采用的是python的format()方法将变量填充到prompt中，所以请保证新prompt和旧prompt中用{}包裹的内容是一样的，不能增加变量，尽量不要减少变量。
2. 请保证你输出的新prompt模板可以直接使用 json.loads() 方法转换为字典，因此你需要注意应使用双引号和转义字符的使用。
3. 请保证<analyse></analyse>、<new_prompt></new_prompt>出现且都只出现一次。
4. 如果你认为当前的prompt模板表现的足够优秀，请输出<new_prompt>{}</new_prompt>。
    """

    optim_component_en = """
You are now a fine-tuner for a large language model prompt. I will provide you with a prompt template and its corresponding input and output information. Please modify the prompt based on the given data:

- The current `prompt_components` are: <prompt_components>{prompt_components}</prompt_components>
- The prompt can be composed by concatenating the prompt_components in the following order: <order>{prompts_order}</order>

Here is some explanatory information about the `prompt_components`, which are the basic building blocks for constructing the `prompt_template`:
```json
{
    "TASK": "Description related to this task",
    "RULE": "Some rules to constrain the output",
    "STYLE": "The style to constrain the response",
    "EXAMPLE": "Examples for better understanding",
    "COT": "Used to prompt the model to think step by step, e.g., please think step by step"
}
```

Below is some information about the model's performance with this template:


# Instance {index}
- Suggestions for prompt modification: <suggestion>{suggestion}</suggestion>


You need to analyze the above content and output an optimized prompt result. You only need to optimize the following fields: {needed_optim_component}.
Wrap the analysis process with <analyse></analyse>, and the new prompt with <new_prompt></new_prompt>. The specific content should be given as a JSON formatted dictionary, which can be directly converted to a dictionary using the json.loads() method.

For example, when fields "COT" and "STYLE" need to be optimized, your output would be a dictionary containing these two keys, as shown in the following example: <new_prompt>{"COT": "Please think step by step","STYLE": "Please answer in an essay style"}</new_prompt>.
If you believe the original "COT" field is already excellent, the optimized prompt dictionary should not include the "COT" field. If you believe all fields are already excellent, please output an empty dictionary, i.e., <new_prompt>{}</new_prompt>.

Notes:
1. When using the prompt template in practice, the python format() method is used to fill the variables into the prompt, so please ensure that the content wrapped in {} remains the same in both the new and old prompts. Avoid adding or removing variables as much as possible.
2. Ensure that your outputted new prompt template can be directly converted to a dictionary using the json.loads() method, so you need to pay attention to the use of double quotes and escape characters.
3. Ensure that <analyse></analyse> and <new_prompt></new_prompt> appear only once each.
4. If you believe the current prompt template performs excellently, please output <new_prompt>{}</new_prompt>.
"""

    # The last four prompts have been abandoned and are now optimized in the form of components
    backward_old_cn = """
你现在是一个大语言模型的prompt精调师，现在需要你给出一些对prompt模板的优化建议，给出的建议请使用<suggestion></suggestion>包裹，比如<suggestion>可以简短一些</suggestion>。
整个任务分为多个步骤完成，我会给你前一步的输出，后一步对当前步的要求，当前步的输出和prompt模板，你需要对当前步的prompt模板提出改进的建议。

- 需要被优化的prompt模板是：<prompt_template>{prompt_template}</prompt_template>

- 前一步的输出结果是：<previous_output>{previous_output}</previous_output>

- 当前的输出是：<output>{response}</output>

- 后一步的对当前步输出的要求是: <requirement>{requirement_for_previous}</requirement>

除了对对当前prompt提出修改建议。你还需要提出前一步输出的要求，请使用<requirement_for_previous></requirement_for_previous>包裹，比如：<requirement_for_previous>分析中应该包括原始数据的比较</requirement_for_previous>。

注意：
1.请务必保证输出的结果分别用<requirement_for_previous></requirement_for_previous>、<suggestion></suggestion>包裹，且只出现一次。
2.如果你是第一个节点，用<requirement_for_previous></requirement_for_previous>中可以是“当前是第一个节点”
3.请注意，在分析的时候请记住这个prompt模板会被应用到多个不同的数据上，所以你的建议应该是通用的，不应只专注于此处提供的例子。
4.请一步步分析。
"""

    backward_old_en = """
You are now a prompt fine-tuner for a large language model. You are tasked with providing suggestions for optimizing the prompt template. 
Please enclose your suggestions using <suggestion></suggestion>, for example, <suggestion>it could be made shorter</suggestion>. 
The task is divided into multiple steps; I will provide you with the output from the previous step, the requirement proposed by the next step for the current output, the current output itself, and the prompt template. You need to suggest improvements for the current step's prompt template.

- The prompt template that needs optimization is: <prompt_template>{prompt_template}</prompt_template>

- The output from the previous step is: <previous_output>{previous_output}</previous_output>

- The current output is: <output>{response}</output>

- The requirement proposed by the next step for the current output is: <requirement>{requirement_for_previous}</requirement>

In addition to suggesting modifications for the current prompt template, you also need to propose requirements for the output of the previous step. Please wrap these using <requirement_for_previous></requirement_for_previous>, for example: <requirement_for_previous>the analysis should include a comparison of original data</requirement_for_previous>.

Note:
1. Ensure that the results are wrapped with <requirement_for_previous></requirement_for_previous> and <suggestion></suggestion>, and each tag appears only once.
2. If you are the first node, you can state within <requirement_for_previous></requirement_for_previous> “This is the first node.”
3. Please note that during your analysis, remember that this prompt template will be applied to multiple different datasets, so your suggestions should be general and not solely focused on the examples provided here.
4. Please analyze step by step.
"""

    optim_cn = """
    你现在是一个大语言模型的prompt精调师，我会给你一个prompt模板及其对应的输入和输出信息，请根据给出的数据对prompt进行修改：
    - 当前的prompt_templates是：{prompt_template}。

    如下是采用这个template时模型的一些信息：

    # Example {index}
    - 输出结果: <output>{response}</output>
    - 对prompt的修改建议: <suggestion>{suggestion}</suggestion>

    你需要依据以上内容分析，并输出优化后的prompt结果。分析的过程请使用<analyse></analyse>包裹，新的prompt请用<new_prompt></new_prompt>包裹。

    注意：
    1. 实际使用prompt模板时，采用的是python的format()方法将变量填充到prompt中，所以请保证新prompt和旧prompt中用{}包裹的内容是一样的，不能增加变量，尽量不要减少变量。
    2. 请保证你输出的新prompt模板可以直接使用 json.loads() 方法转换为字典，因此你需要注意应使用双引号和转义字符的使用。
    3. 请保证<analyse></analyse>、<new_prompt></new_prompt>出现且都只出现一次。
    4. 如果你认为当前的prompt模板表现的足够优秀，请将<new_prompt></new_prompt>留空。
    5. 你需要严格注意输出与最终结果是否匹配，尤其是在简洁程度上。
    """

    optim_en = """
    You are now a prompt fine-tuner for a large language model. I will provide you with a prompt template along with its corresponding input and output information. 

    Please modify the prompt based on the provided data:
    - The current prompt template is: {prompt_template}.

    Here is some information about the model when using this template:

    # Example {index}
    - Output result: <output>{response}</output>
    - Suggestion: <suggestion>{suggestion}</suggestion>

    You need to analyze the content above and output the optimized prompt result. Please wrap your analysis in <analyse></analyse> and the new prompt in <new_prompt></new_prompt>.

    Please note:
    1. When actually using the prompt template, the Python format() method is employed to fill variables into the prompt. Therefore, please ensure that the content enclosed in {} in both the new and old prompts remains the same, with no variables added or removed.
    2. Ensure that your new prompt template can be directly converted to a dictionary using the json.loads() method. Therefore, you need to be careful to use double quotes and escape characters properly.
    3. Ensure that <analyse></analyse> and <new_prompt></new_prompt> each appear only once.
    4. If you believe that the current prompt template performs sufficiently well, leave <new_prompt></new_prompt> empty.
    """
