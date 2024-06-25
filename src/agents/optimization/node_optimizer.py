import copy
import logging
import json
import os.path
from functools import partial
from pathlib import Path

from agents import SOP, Solution, AgentTeamConfig, AgentTeam, SolutionConfig
from agents.agents.llm import LLMConfig, OpenAILLM
from agents.optimization.optimizer import Optimizer, OptimizerConfig
from agents.optimization.utils import OptimUtils
from agents.task.node import Node
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.evaluation import Case
from agents.optimization import prompt_formatter


class NodeOptimizerConfig(OptimizerConfig):
    """
    The NodeOptimizerConfig class is used to configure the node optimizer settings.
    It extends the OptimizerConfig class.
    """

    def __init__(self, config_path):
        """
        Initializes the NodeOptimizerConfig object.

        Args:
            config_path (str): The path to the configuration file.
        """
        super().__init__(config_path)

        # The parent class parses the common fields, here we only parse the fields for node_optimizer
        self.llm_config: dict = self.node_optimizer_setting_dict.get("llm_config")
        self.meta_prompt: dict = self.node_optimizer_setting_dict.get("meta_prompt")


class NodeOptimizer(Optimizer):
    """
    The NodeOptimizer class is used to optimize nodes based on the configuration.
    """

    def __init__(self, config: NodeOptimizerConfig, logger_name: str):
        """
        Initializes the NodeOptimizer object.

        Args:
            config (NodeOptimizerConfig): The node optimizer configuration.
            logger_name (str): The name of the logger.
        """
        super().__init__(config)
        self.config = config

        # llm
        self.llm_eval = (OpenAILLM(LLMConfig(config.llm_config)) if config.llm_config else None)

        # prompt
        self.both_prompt = config.meta_prompt.get("both")
        self.meta_backward = config.meta_prompt.get("backward")
        self.meta_optim = config.meta_prompt.get("optim")

        # logger
        self.logger = logging.getLogger(logger_name) if logger_name else logging.getLogger(__name__)

    def optimize(
            self,
            case_list: list[Case],
            solution: Solution,
            save_dir: Path,
            parallel_max_num,
    ):
        """
        Optimizes nodes in the given list of cases.

        Args:
            case_list (list[Case]): The list of cases to be optimized.
            solution (Solution): The solution to be optimized.
            save_dir (Path): The directory to save the results.
            parallel_max_num (int): The maximum number of parallel processes.

        Returns:
            tuple: The updated solution and optimization status.
        """
        self.logger.info("Start Node Optimization")
        saved_ori_solution = copy.deepcopy(solution)

        # backward
        backward_save_dir = save_dir / "case_after_backward"
        partial_funcs = [partial(self.backward, case, solution, backward_save_dir) for case in case_list]
        OptimUtils.parallel_execution(partial_funcs, max_workers=parallel_max_num)

        # optimization (based on the suggestions)
        op_info = self.optimize_node(case_list, solution)

        # Determine the optimization status based on the success of any node optimization
        op_status = any(info["optim_status"] for info in op_info.values())

        # if optimized successfully, update the AgentTeam
        if op_status:
            all_node_roles_description = {}
            for node_name, node in solution.sop.nodes.items():
                all_node_roles_description[node_name] = node.node_roles_description
            agent_team_config = AgentTeamConfig.generate_config(
                solution.task.task_description, all_node_roles_description)
            solution.agent_team = AgentTeam(agent_team_config)

        # save new solution and op_info
        try:
            with open(save_dir / "node_optim_info.json", "w", encoding="utf-8") as f:
                json.dump(op_info, f, ensure_ascii=False, indent=4)
            solution.dump(save_dir)
            solution = Solution(config=SolutionConfig(str(save_dir / "solution.json")))
        except Exception as e:
            self.logger.error(f"Error in saving solution: {e}")
            solution = saved_ori_solution
            solution.dump(save_dir / "accepted_solution")

        return solution, op_status

    def backward(self, case: Case, solution: Solution, save_dir: str):
        """
        Performs backward calculation for each node in the given case.

        Args:
            case (Case): The case for which the backward calculation is performed.
            solution (Solution): The solution associated with the case.
            save_dir (str): The directory to save the results.

        Returns:
            None
        """
        self.logger.info(f"Start backward for case: {case.case_id}")
        last_requirement_for_previous = case.loss.requirement_for_previous

        node_name_list = []
        for state in case.trajectory.states:
            if state.node.node_name not in node_name_list:
                node_name_list.append(state.node.node_name)

        state_idx = 0
        for op_node_name in node_name_list[::-1]:
            # get state idx of the op_node_name, it is the last state idx of the node
            for idx in range(len(case.trajectory.states) - 1, -1, -1):
                if case.trajectory.states[idx].node.node_name == op_node_name:
                    state_idx = idx
                    break

            # Call LLM to calculate backward for each node
            prompt = prompt_formatter.formulate_prompt_for_node_backward(
                self.meta_backward, case, solution.sop.nodes[op_node_name], last_requirement_for_previous)
            _, content = self.llm_eval.get_response(
                chat_messages=None, system_prompt="", last_prompt=prompt, stream=False)

            # Extract data from LLM response
            need_extract_key = self.meta_backward.get("extract_key", copy.deepcopy(
                ["analyse", "suggestion", "requirement_for_previous"]))
            backward_info_dict = OptimUtils.extract_data_from_response(
                content, need_extract_key, self.logger,
                "There are neither suggestions nor requirements.",
            )
            backward_info_dict["response"] = content
            backward_info_dict["prompt"] = prompt
            assert "suggestion" in backward_info_dict.keys(), "suggestion must be in the extracted data"
            assert "requirement_for_previous" in backward_info_dict.keys(), "requirement_for_previous must be in the extracted data"

            # update the state backward info, save the backward info to the case
            case.trajectory.states[state_idx].node_backward.update(**backward_info_dict)
            last_requirement_for_previous = backward_info_dict["requirement_for_previous"]

        # save the backward info to the file
        if save_dir:
            case.dump(os.path.join(save_dir, f"{case.case_id}.json"))

    def optimize_node(self, case_list: list[Case], solution: Solution):
        """
        Optimizes the configuration of each node in the solution based on the cases.

        Args:
            case_list (list[Case]): The list of cases.
            solution (Solution): The solution to be optimized.

        Returns:
            dict: A dictionary with the optimization status and method for each node.
        """
        node_name_list = []
        for state in case_list[0].trajectory.states:
            # Get unique node names based on case0's information and node_name is not duplicated
            if state.node.node_name not in node_name_list:
                node_name_list.append(state.node.node_name)

        # Do optimization for each node and get the optimization method
        op_info = {}
        for node_name in node_name_list:
            new_node, op_status, op_method = self.optimize_single_node(case_list, solution.sop.nodes[node_name])
            solution.sop.nodes[node_name] = new_node
            op_info[node_name] = {"optim_status": op_status, "optim_method": op_method}

        return op_info

    def optimize_single_node(self, case_list: list[Case], node: Node):
        """
        Optimizes the configuration information of a single node.

        Args:
            case_list (list[Case]): The list of cases.
            node (Node): The node to be optimized.

        Returns:
            tuple: The new Node object, a boolean indicating if the update was successful,
                   and the optimization method (JSON if successful, otherwise a string).
        """
        saved_node = copy.deepcopy(node)

        prompt = prompt_formatter.formulate_prompt_for_node_optim(self.meta_optim, node, case_list)
        _, content = self.llm_eval.get_response(chat_messages=None, system_prompt="", last_prompt=prompt, stream=False)

        # Modify the SOP configuration based on LLM suggestions
        extracted_dict = OptimUtils.extract_data_from_response(content, self.meta_optim["extract_key"])
        optim_method_str = extracted_dict.get("result")

        if optim_method_str == "" or optim_method_str == "[]":
            # current node performs well, no need to optimize
            self.logger.debug(f"No need to optimize node: {node.node_name}")
            return node, True, optim_method_str
        elif optim_method_str is None:
            self.logger.error(f"Error in optimizing node: {node.node_name}, the result is None.")
            return node, False, None
        else:
            self.logger.debug(f"try to optimize node: {node.node_name}")
            try:
                return self.do_node_optim(node, optim_method_str, self.logger)
            except Exception as e:
                self.logger.error(f"Error in do_node_optim: {e}")
                self.logger.error(f"optim_method_str: {optim_method_str}")
                # return the original node
                return saved_node, False, optim_method_str

    @staticmethod
    def do_node_optim(node: Node, optim_method_str: str, logger):
        """
        Executes the node optimization based on the given method.

        Note: If an error occurs during optimization, an exception is raised instead of returning,
        because the upper layer will handle the error and return the original unoptimized node.

        Args:
            node (Node): The node to be optimized.
            optim_method_str (str): The optimization method in JSON string format.
            logger: The logger for logging information and errors.

        Returns:
            tuple: The optimized Node object, a boolean indicating if the update was successful,
                   and the optimization method (JSON if successful, otherwise a string).
        """
        optim_method = json.loads(optim_method_str)

        # Validity check, attempt update only if successful
        check_status, reasons = NodeOptimizer.validate_dict(optim_method)

        if not check_status:
            logger.error(f"Error in validating optim_method: {reasons}, optim_method: {optim_method}")
            raise ValueError(f"Error in validating optim_method: {reasons}")
        else:
            logger.debug(f"succeed in validating optim_method, load the json successfully.")
            # try to optim the node
            for rule in optim_method:
                action = rule.get("action")
                if action == "add_role":
                    role_name = rule["role_name"]
                    role_description = rule["role_description"]
                    role_prompt = rule["role_prompt"]
                    role_prompt_key = "step_" + role_name
                    assert role_name not in node.node_prompt_paddings.keys(), f"Role name '{role_name}' already exists."
                    node.node_prompt_templates[role_prompt_key] = role_prompt
                    node.node_roles_description[role_name] = role_description
                    node.node_prompt_paddings[role_name] = {
                        role_prompt_key: {"value_source": "case", "value": "input_data"}}

                elif action == "delete_role":
                    role_name = rule["role_name"]
                    node.node_roles.pop(role_name)
                    node.node_roles_description.pop(role_name)
                    node.node_primary_prompts.pop(role_name)
                    node.node_prompt_templates.pop(role_name)
                    node.node_prompt_paddings.pop(role_name)
                    if len(node.node_prompt_paddings) == 0:
                        raise ValueError("The node should have at least one role.")
                    # begin role may need to be updated
                    if node.begin_role == role_name:
                        node.begin_role = next(iter(node.node_prompt_templates))

                elif action == "update_role_description":
                    role_name = rule["role_name"]
                    role_description = rule["role_description"]
                    node.node_roles_description[role_name] = role_description

                elif action == "update_controller":
                    node.controller.route_type = rule["route_type"]
                    node.controller.route_system_prompt = rule.get("route_system_prompt")
                    node.controller.route_last_prompt = rule.get("route_last_prompt")
                    assert ((node.controller.route_type in ["order", "random"]) or
                            (node.controller.route_type == "llm" and
                             node.controller.route_system_prompt and
                             node.controller.route_last_prompt)), \
                        "when route_type is llm, route_system_prompt and route_last_prompt should not be empty."

                elif action == "update_node_description":
                    node.node_description = rule["node_description"]

                else:
                    logger.error(f"Unknown action '{action}'")
                    raise ValueError(f"Unknown action, the optim rule is '{rule}'")

            # update the node successfully, all the rules are valid
            return node, True, optim_method

    @staticmethod
    def validate_dict(optim_method_list):
        """
        Validates the optimization method list.

        Args:
            optim_method_list (list): The list of optimization methods.

        Returns:
            tuple: A boolean indicating if the validation passed, and a string with the validation message.
        """
        for rule in optim_method_list:
            action = rule.get("action")
            if action == "add_role":
                required_keys = ["role_name", "role_description", "role_prompt"]
                for key in required_keys:
                    if key not in rule:
                        return False, f"Missing key '{key}' for action '{action}'"
                    if not isinstance(rule[key], str) or not rule[key]:
                        return False, f"Invalid value for key '{key}' for action '{action}'"
            elif action == "delete_role":
                required_keys = ["role_name"]
                for key in required_keys:
                    if key not in rule:
                        return False, f"Missing key '{key}' for action '{action}'"
                    if not isinstance(rule[key], str) or not rule[key]:
                        return False, f"Invalid value for key '{key}' for action '{action}'",

            elif action == "update_role_description":
                required_keys = ["role_name", "role_description"]
                for key in required_keys:
                    if key not in rule:
                        return False, f"Missing key '{key}' for action '{action}'"
                    if not isinstance(rule[key], str) or not rule[key]:
                        return False, f"Invalid value for key '{key}' for action '{action}'",

            elif action == "update_controller":
                required_keys = ["route_type", "route_system_prompt", "route_last_prompt"]
                for key in required_keys:
                    if key not in rule:
                        return False, f"Missing key '{key}' for action '{action}'"
                    if not isinstance(rule[key], str):
                        return False, f"Invalid value for key '{key}', the key value is {str(rule[key])}, action is '{action}'"
                    if key == "route_type" and rule[key] not in ["random", "order", "llm"]:
                        return False, f"Invalid value for key '{key}', the key value is {str(rule[key])}, action is '{action}'",
                    if key == "route_type" and rule[key] in ["random", "order"]:
                        # if route_type is random or order, "route_system_prompt", "route_last_prompt" are not needed
                        break

            elif action == "update_node_description":
                required_keys = ["node_description"]
                for key in required_keys:
                    if key not in rule:
                        return False, f"Missing key '{key}' for action '{action}'"
                    if not isinstance(rule[key], str) or not rule[key]:
                        return False, f"Invalid value for key '{key}' for action '{action}'",

            else:
                return False, f"Unknown action '{action}'"
        return True, "Validation passed"


if __name__ == "__main__":
    backward_cn = """
你是一个大模型精调师。现在需要你尝试优化一个node的信息。
对于一个复杂的任务，现已经将其分成多个节点处理，其中每个节点中包含多个role，多个role互相配合完成此node的任务。每个role背后是一个LLM Agent，你需要优化其中的一个Node的配置信息。

如下是一个json格式的Node的配置实例：
```json
{
    "node_name": "summary_node",
    "controller": {
        "route_type": "order",
        "route_system_prompt": "",
        "route_last_prompt": "",
    },
    "begin_role": "role_summary",
    "node_description": "Summarize the findings from the previous step",
    "node_roles_description": {
        "role_summary": "The role needs to summarize the key findings from the previous step concisely and present the final result within <result></result> tags."
    }
}
```

如下是Node配置的相关说明：
- "controller"中的几个字段表明了模型的调度方式，若只有一个role，此项不需要优化：
    - "route_type"表示调度方式，其有三种取值："random"表示随机调度，"order"表示按照顺序调度，"llm"表示由LLM模型决定调度。
    - "route_system_prompt"和"route_last_prompt"在"route_type"为"llm"时会被用到，分别为会给到负责控制调度的LLM模型的system prompt 和 last prompt。
- "begin_role"是一个字符串，表示这个node的开始role的名字。
- "roles"是一个字典，key是role名字，value是这个role会使用的prompt。


你需要决定如何优化这个节点中的配置，具体来说，你需要在如下几方面尝试提出意见：
1. 更新node description字段，这个字段的作用是描述这个node的作用，也是衡量一个node表现效果的重要指标。
2. 更新role的调度方式，注意如果是一个role，不需要优化。
3. 新加role，你需要描述清楚这个role的作用。
4. 删除role，你需要描述清楚删除这个role的原因。
5. 更新role，你需要指出如何更新这个role的description。


接下来我会给到你一个Node的配置信息，你需要根据当前的Node的配置信息，提出优化建议，请使用<suggestion>[put your suggestion here]</suggestion>包裹。同时你还需要根据当前节点的信息，对上一个节点的表现提出一些要求，请使用<requirement_for_previous>[put your requirement here]</requirement_for_previous>包裹。

## Current Node Config
{node_config}


## 运行实例
之前节点的信息：<previous_node>{previous_node_summary}</previous_node>
当前节点的运行输出：<current_node>{role_chat}</current_node>
下一个节点对当前节点的要求：<next node's requirement>{requirement_for_previous}</next node's requirement>


你需要首先给出你的分析过程，然后给出你优化后的结果，分析过程请用<analyse></analyse>包裹。对当前node的优化建议请用<suggestion></suggestion>包裹，对前一个节点的要求请用<requirement_for_previous></requirement_for_previous>包裹。
当你认为当前节点无需优化时，需要输出<suggestion>表现足够优秀了，无修改建议</suggestion>。

注意：给出的建议需要是在给出的五个方面中的一个或多个。
"""

    backward_en = """
You are a large model fine-tuner. Now you need to try to optimize the information of a node. For a complex task, it has been divided into multiple nodes, each of which contains multiple roles that work together to complete the task of this node. Each role is backed by an LLM Agent, and you need to optimize the configuration information of one of the nodes.

Here is an example of a Node configuration in JSON format:
```json
{
    "node_name": "summary_node",
    "controller": {
        "route_type": "order",
        "route_system_prompt": "",
        "route_last_prompt": ""
    },
    "begin_role": "role_summary",
    "node_description": "Summarize the findings from the previous step",
    "node_roles_description": {
        "role_summary": "The role needs to summarize the key findings from the previous step concisely and present the final result within <result></result> tags."
    }
}
```

Here are the relevant explanations for the Node configuration:
- The fields in the "controller" indicate the scheduling method of the model. If there is only one role, this item does not need to be optimized:
  - "route_type" indicates the scheduling method, which has three values: "random" means random scheduling, "order" means sequential scheduling, and "llm" means scheduling determined by the LLM model.
  - "route_system_prompt" and "route_last_prompt" are used when "route_type" is "llm" and are respectively the system prompt and last prompt given to the LLM model responsible for scheduling.
- "begin_role" is a string indicating the name of the starting role of this node.
- "roles" is a dictionary where the key is the role name, and the value is the prompt used by this role.

You need to decide how to optimize the configuration of this node. Specifically, you need to try to provide suggestions in the following aspects:
1. Update the node description field. This field describes the function of the node and is also an important indicator to measure the performance of a node.
2. Update the scheduling method of the role. Note that if there is only one role, no optimization is needed.
3. Add a new role, and you need to clearly describe the function of this role.
4. Delete a role, and you need to clearly describe the reason for deleting this role.
5. Update a role, and you need to indicate how to update the description of this role.


Next, I will give you a Node configuration, and you need to provide optimization suggestions based on the current Node configuration. Please use <suggestion>[put your suggestion here]</suggestion> to enclose your suggestions. 
At the same time, you also need to make some requirements for the performance of the previous node based on the information of the current node, please use <requirement_for_previous>the [put your requirement here] <requirement_for_previous>package.

## Current Node Config
{node_config}


## Run Instance
Previous node information: <previous_node>{previous_node_summary}</previous_node>
Current node output: <current_node>{role_chat}</current_node>
Next node's requirement for the current node: <next node's requirement>{requirement_for_previous}</next node's requirement>


You need to first provide your analysis process, then give your optimized result. Please use <analyse></analyse> to enclose the analysis process. Please use <suggestion></suggestion> to enclose the optimization suggestions for the current node. Please use <requirement_for_previous></requirement_for_previous> to enclose the requirements for the previous node. If you think the current node does not need optimization, you need to output <suggestion>The performance is good enough, no modification suggestions</suggestion>.

Note: The suggestions provided need to be in one or more of the five aspects mentioned above.
"""

    optim_cn = """
你是一个大模型精调师。现在需要你尝试优化一个node的信息。
对于一个复杂的任务，现已经将其分成多个节点处理，其中每个节点中包含多个role，多个role互相配合完成此node的任务。每个role背后是一个LLM Agent，你需要优化其中的一个Node的配置信息。

如下是一个json格式的Node的配置实例：
```json
{
    "node_name": "summary_node",
    "controller": {
        "route_type": "order",
        "route_system_prompt": "",
        "route_last_prompt": "",
    },
    "begin_role": "role_summary",
    "node_description": "Summarize the findings from the previous step",
    "node_roles_description": {
        "role_summary": "The role needs to summarize the key findings from the previous step."
    }
}

如下是Node配置的相关说明：
- "controller"中的几个字段表明了模型的调度方式，若只有一个role，此项不需要优化：
    - "route_type"表示调度方式，其有三种取值："random"表示随机调度，"order"表示按照顺序调度，"llm"表示由LLM模型决定调度。
    - "route_system_prompt"和"route_last_prompt"在"route_type"为"llm"时会被用到，分别为会给到负责控制调度的LLM模型的system prompt 和 last prompt。
- "begin_role"是一个字符串，表示这个node的开始role的名字。
- "roles"是一个字典，key是role名字，value是这个role会使用的prompt。


接下来我会给你一个node的配置信息，以及几条修改建议，你需要根据修改建议对Node的配置信息进行修改：

## Current Node Config
{node_config}

## Suggestions
{suggestions}



在给出修改方案时，你需要按照如下格式给出优化结果，其是一个列表，每个元素是一个dict，dict中包含一个action字段，表示对Node的操作，以及其他的字段，具体如下：
```json
[
    {
        # 增加一个名为 role_check 的role，需要给定role_name, role_description, role_prompt
        "action": "add_role",
        "role_name": "role_check",
        "role_description": "Check the result of the previous step",
        "role_prompt": "Output your thinking steps firstly, and if the answer is correct, output <result>1</result>, if the answer is incorrect, output <result>0</result>, <answer></answer>"
    },
    {
        # 删除一个role，需要给定role_name,
        "action": "delete_role",
        "role_name": "role_analyse",
    },
    {
        # 更改 role_summary 的Node description
        "action": "update_role_description",
        "role_name": "role_summary",
        "role_description": "The role needs to summarize the key findings from the previous step concisely and present the final result within <result></result> tags.",
    },
    {
        # 更新role之间的转移方式，需要给定route_type, route_system_prompt, route_last_prompt
        "action": "update_controller",
        "route_type": "order",
        "route_system_prompt": "",
        "route_last_prompt": "",
    },
    {
        # 更改 node description
        "action": "update_node_description",
        "node_description": "Summarize the findings from the previous step and output the final result. The results are usually between 1 and 5 words."
    }
]
```

你给出的优化结果应该使用<result></result> 包裹，即<result></result>内部应该是一个json格式的列表，其应该可以直接被保存为json.loads()加载。

注意：
1. 如果你认为当前的配置信息已经足够优秀，无需修改，你可以直接输出一个空的列表。
2. <result>[优化的方法]</result>的格式需要严格按照给出来的格式，否则会被判为错误。
"""

    optim_en = """
You are a large model fine-tuner. Now you need to try to optimize the information of a node. For a complex task, it has been divided into multiple nodes, each containing multiple roles that work together to complete the task of this node. Each role is backed by an LLM Agent, and you need to optimize the configuration information of one of the nodes.

Here is an example of a Node configuration in JSON format:
```json
{
    "node_name": "summary_node",
    "controller": {
        "route_type": "order",
        "route_system_prompt": "",
        "route_last_prompt": ""
    },
    "begin_role": "role_summary",
    "node_description": "Summarize the findings from the previous step",
    "node_roles_description": {
        "role_summary": "The role needs to summarize the key findings from the previous step."
    }
}
```

Here are the relevant explanations for the Node configuration:
- The fields in the "controller" indicate the scheduling method of the model. If there is only one role, this item does not need to be optimized:
  - "route_type" indicates the scheduling method, which has three values: "random" means random scheduling, "order" means sequential scheduling, and "llm" means scheduling determined by the LLM model.
  - "route_system_prompt" and "route_last_prompt" are used when "route_type" is "llm" and are respectively the system prompt and last prompt given to the LLM model responsible for scheduling.
- "begin_role" is a string indicating the name of the starting role of this node.
- "roles" is a dictionary where the key is the role name, and the value is the prompt used by this role.

Next, I will give you a Node configuration and several modification suggestions. You need to modify the Node configuration based on the suggestions:

## Current Node Config
{node_config}

## Suggestions
{suggestions}

When providing the modification plan, you need to give the optimized result in the following format. It is a list, each element is a dict, and the dict contains an action field indicating the operation on the Node, as well as other fields as follows:
```json
[
    {
        # Add a role named role_check, you need to provide role_name, role_description, role_prompt
        "action": "add_role",
        "role_name": "role_check",
        "role_description": "Check the result of the previous step",
        "role_prompt": "Output your thinking steps firstly, and if the answer is correct, output <result>1</result>, if the answer is incorrect, output <result>0</result>, <answer></answer>"
    },
    {
        # Delete a role, you need to provide role_name
        "action": "delete_role",
        "role_name": "role_analyse"
    },
    {
        # Update the description of the role_summary node
        "action": "update_role_description",
        "role_name": "role_summary",
        "role_description": "The role needs to summarize the key findings from the previous step concisely and present the final result within <result></result> tags."
    },
    {
        # Update the transfer method between roles, you need to provide route_type, route_system_prompt, route_last_prompt
        "action": "update_controller",
        "route_type": "order",
        "route_system_prompt": "",
        "route_last_prompt": ""
    },
    {
        # Update the node description
        "action": "update_node_description",
        "node_description": "Summarize the findings from the previous step and output the final result. The results are usually between 1 and 5 words."
    }
]
```

Your optimized result should be enclosed in <result></result>, that is, the content inside <result></result> should be a JSON-formatted list, which should be able to be directly loaded by json.loads().

Note:
1. If you think the current configuration is already excellent and does not need modification, you can directly output an empty list.
2. The format of <result>[optimization method]</result> needs to strictly follow the given format, otherwise, it will be judged as incorrect.
"""

    last_prompt = backward_en

    llm_config = {
        "LLM_type": "OpenAI",
        "model": "gpt-4-turbo-2024-04-09",
        "temperature": 0.3,
        "log_path": "logs/trainer_god",
        "ACTIVE_MODE": True,
        "SAVE_LOGS": True,
    }
    llm = OpenAILLM(LLMConfig(llm_config))
    print(last_prompt)

    response, cont = llm.get_response(
        chat_messages=None, system_prompt="", last_prompt=last_prompt, stream=False
    )

    print("\n\n\n" + cont)
