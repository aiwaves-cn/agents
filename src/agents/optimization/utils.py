import os.path
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents import DEFAULT_NODE_PROMPT_TEMPLATES, OpenAILLM, SOP
from agents.evaluation.case import Case
from agents.task.sop import SOP
from agents.optimization import prompt_formatter
from agents.task.solution import Solution, SolutionConfig
import re
import json
import copy


def red_print(content):
    print(f"\033[31m{content}\033[0m")


def yellow_print(content):
    print(f"\033[93m{content}\033[0m")


eval_node_prompt_cn = """
现在你需要对当前的Node的表现情况进行评估。
多个Node会组合起来完成一个任务，每个Node都有自己的任务描述，你可以在node_description中找到。
每个Node中会有多个role，每个role都会输出一些信息。

你需要给出评估结果，评估结果应该包含以下几个部分：
- summary: 仅需总结当前Node下各个role的输出信息，让我能够快速了解当前Node的表现而无需查看详细的role输出。在总结时，对于使用模型输出的被<result></result>包裹的部分，你应该尽量保证其内容不变。其他部分的内容则需要总结概括，保证其简洁明了。
- evaluation: 对当前Node的表现进行评价，简要描述当前Node的表现是否符合预期，需要综合考量Node的任务描述和实际表现，以及前后Node的关系

如下是具体的信息：
## Current Node Config
<node_config>{node_config}</node_config>

## Previous Node Summary
<previous_node_summary>{previous_node_summary}</previous_node_summary>

## Current Node Run Instance
<run_instance>{role_chat}</run_instance>

注意：
1. 评估结果请使用<result></result>包裹，被包裹的内容应该可以直接被解析为json。具体来说，你要输出一个字典，其中包含summary和evaluation两个key，对应的value是字符串.
2. 评估结果必须包含summary和evaluation两部分，否则会被判为错误。
"""

eval_node_prompt = """
Now you need to evaluate the current Node's performance.

Multiple Nodes work together to complete a task, with each Node having its own task description, which can be found in the node_description. Each Node contains multiple roles, and each role outputs some information.

You need to provide an evaluation result, which should include the following parts:
- summary: Summarize the output information of each role under the current Node, allowing me to quickly understand the Node's performance without checking the detailed role outputs. When summarizing, for the parts enclosed by <result></result> that use model outputs, you should try to keep their content unchanged. Other parts should be summarized concisely and clearly.
- evaluation: Evaluate the current Node's performance, briefly describing whether the current Node's performance meets expectations, considering the Node's task description, actual performance, and the relationship between preceding and succeeding Nodes.

Below is the specific information:
## Current Node Config
<node_config>{node_config}</node_config>

## Previous Node Summary
<previous_node_summary>{previous_node_summary}</previous_node_summary>

## Current Node Run Instance
<run_instance>{role_chat}</run_instance>

Note:
1. Please use <result></result> to enclose the evaluation result, and the enclosed content should be directly parsable as JSON. Specifically, you need to output a dictionary containing two keys: summary and evaluation, with their corresponding values being strings.
2. The evaluation result must include both summary and evaluation parts, otherwise, it will be considered incorrect.
"""


class OptimUtils:
    @staticmethod
    def case_forward(case: Case, solution_or_path, save_file_path, dataset_eval_func):
        """
        forward case to get the result and save it to the file.

        Args:
            case: the case to be forwarded
            solution_or_path: the path of the latest solution, load it to deal with the case
            save_file_path: the path to save the case, if it is None, the case will not be saved
            dataset_eval_func: the function to evaluate the case, if it is None, the case will not be evaluated
        """
        if isinstance(solution_or_path, str):
            current_solution = Solution(config=SolutionConfig(str(solution_or_path)))
        elif isinstance(solution_or_path, Solution):
            # 如果是Solution对象，那么就直接使用，但是要深拷贝一份，因为一个solution对应一个case
            current_solution = copy.deepcopy(solution_or_path)
        else:
            raise ValueError(
                "in case_forward(), solution_or_path must be a path or a Solution object"
            )

        current_solution.sop.update_nodes_from_case(case.input)
        trajectory = current_solution.run(mode="train")
        case.trajectory = trajectory
        last_state = case.trajectory.states[-1]

        # case.result cannot be empty, if the result is not wrapped in result, then use content directly
        case.result = OptimUtils.extract_data_from_response(
            last_state.action.content, ["result"], None, last_state.action.content
        ).get("result")
        if case.result == "":
            case.result = last_state.action.content

        # Evaluate with the dataset's evaluator
        if dataset_eval_func:
            eval_input_data = {"answer": case.result, "idx": case.raw_data["idx"]}
            _, dateset_eval_result = dataset_eval_func(**eval_input_data)
            metric_name = case.raw_data.get("metric_name", None)
            dataset_eval_dict = {
                "metric_name": metric_name,
                "score": dateset_eval_result[metric_name],
                "metric_description": case.raw_data["metric_description"],
                "standard_eval_result": dateset_eval_result,
            }
            case.dataset_eval.update(**dataset_eval_dict)

        if save_file_path:
            case.dump(save_file_path)

    @staticmethod
    def parallel_case_forward(
            case_list,
            solution,
            parallel_max_num,
            save_case_dir,
            dataset_eval_func=None,
            logger=None,
    ):
        """
        Executes forward pass for each case in parallel and saves the results.

        Args:
            case_list (list[Case]): List of cases to be processed.
            solution (Solution): The solution configuration to use for the forward pass.
            parallel_max_num (int): Maximum number of parallel processes.
            save_case_dir (str): Directory to save the processed cases.
            dataset_eval_func (function, optional): Function for dataset evaluation. Defaults to None.
            logger (logging.Logger, optional): Logger for logging information and errors. Defaults to None.
        """
        def case_forward(case):
            save_case_path = os.path.join(str(save_case_dir), f"{case.case_id}.json")
            OptimUtils.case_forward(case, solution, save_case_path, dataset_eval_func)
            print(f"case {case.case_id} finished, <score>{case.dataset_eval.score}</score>")

        with ThreadPoolExecutor(max_workers=parallel_max_num) as executor:
            futures = [executor.submit(case_forward, case) for case in case_list]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"in parallel forward, Error processing case: {e}")

    @staticmethod
    def node_eval(case: Case, solution: Solution, llm: OpenAILLM, logger):
        """
        Evaluates the node and saves the result to the file.

        Args:
            case (Case): The case to be evaluated.
            solution (Solution): The solution configuration.
            llm (OpenAILLM): The large language model instance.
            logger (logging.Logger): Logger for logging information and errors.
        """
        if logger:
            logger.debug("Start Node evaluation, case id is " + case.case_id)
        assert case.trajectory is not None and len(case.trajectory.states) > 0, \
            "case.trajectory is None or len is 0, please forward the case first"
        input_dict = {}

        cur_node_name = None
        start_idx = 0
        previous_node_summary = "You are the first node."
        for idx, state in enumerate(case.trajectory.states):
            # If the node_name changes, it's a new node
            if state.node.node_name != cur_node_name:
                start_idx = idx
                cur_node_name = state.node.node_name

            # If it's the last state of the current node, then it needs to be evaluated
            if (idx == len(case.trajectory.states) - 1
                    or case.trajectory.states[idx + 1].node.node_name != cur_node_name):
                # Obtain the output of all roles of the current node
                role_chat = ""
                for i in range(start_idx, idx + 1):
                    role_chat += (case.trajectory.states[i].action.agent_role + " : "
                                  + case.trajectory.states[i].action.content + "\n")
                input_dict["role_chat"] = role_chat
                input_dict["node_config"] = {
                    "node_name": solution.sop.nodes[cur_node_name].node_name,
                    "node_description": solution.sop.nodes[cur_node_name].node_description,
                }
                input_dict["previous_node_summary"] = previous_node_summary

                eval_prompt = eval_node_prompt.format(**input_dict)
                response, content = llm.get_response(
                    chat_messages=None,
                    system_prompt="",
                    last_prompt=eval_prompt,
                    stream=False,
                )

                # To extract the result, first extract the part of the result package, then convert it to json,
                # and input it into the state, specifically a summary and an evaluation
                eval_result = OptimUtils.extract_data_from_response(content, ["result"])
                try:
                    eval_result = json.loads(eval_result["result"])
                except:
                    logger.error(
                        "Error in node evaluation, case id is " + case.case_id
                        + ", the result is not a legal json string, the result is: " + content
                    )
                    eval_result = {
                        "summary": content,
                        "evaluation": "Error in node evaluation, the result is not a legal json string"
                    }
                    continue

                # This is where each state is assigned, but in reality it should only be assigned once per node
                for i in range(start_idx, idx + 1):
                    case.trajectory.states[i].node_eval.update(
                        eval_prompt, content, eval_result["summary"], eval_result["evaluation"])
                if previous_node_summary == "You are the first node.":
                    previous_node_summary = cur_node_name + ": " + eval_result["summary"]
                else:
                    previous_node_summary += "\n" + cur_node_name + ": " + eval_result["summary"]

        if logger:
            logger.debug("Node evaluation finished, case id is " + case.case_id)

    @staticmethod
    def escape_special_chars_in_json_string(json_string):
        """
            Escapes special characters in a JSON string.

            In the JSON strings provided by large models, there may be special characters that are not escaped. These strings can be output by Python but cannot be directly saved as JSON. This function escapes these characters.

            The function uses a regular expression to find all string patterns.

            Regular expression explanation:
            - "([^"\\]*(?:\\.[^"\\]*)*)": Matches any text within quotes, skipping already escaped quotes and backslashes.
              - "...": Matches content enclosed by double quotes.
              - [^"\\]*: Matches any sequence of characters that are neither double quotes nor backslashes.
              - (?:\\.[^"\\]*)*: Matches a backslash followed by any character (\\. where the dot represents any single character), followed by more sequences of characters that are neither double quotes nor backslashes. This non-capturing group (?:...) allows for the presence of backslash escape sequences, such as \" or \\, without breaking the entire string match.

            The function replaces unescaped special characters in the matched content with their escaped forms.

            Args:
                json_string (str): The JSON string that may contain unescaped special characters.

            Returns:
                str: The JSON string with special characters escaped.
            """

        def replace_special_chars(match):
            # Replace all unescaped special characters in the content of the match with their escaped form
            escaped_string = match.group(0)
            escaped_string = escaped_string.replace("\n", "\\n")
            escaped_string = escaped_string.replace("\t", "\\t")
            escaped_string = escaped_string.replace("\r", "\\r")
            escaped_string = escaped_string.replace("\b", "\\b")
            escaped_string = escaped_string.replace("\f", "\\f")
            return escaped_string

        r'"([^"\\]*(?:\\.[^"\\]*)*)"'
        fixed_json_string = re.sub(
            r'"([^"\\]*(?:\\.[^"\\]*)*)"', replace_special_chars, json_string
        )
        return fixed_json_string

    @staticmethod
    def find_outermost_tags(ss: str, tag):
        """
        Find the outermost tags in the given string.

        This function matches the outermost tags in the provided string using a greedy matching method,
        ignoring nested tags.

        Args:
            ss (str): The string to search for tags.
            tag (str): The tag to search for.

        Returns:
            list: A list of strings that are matched by the outermost tags.
        """
        pattern = rf"<{tag}>([\s\S]*)</{tag}>"
        matches = re.findall(pattern, ss, re.DOTALL)
        return matches

    @staticmethod
    def extract_data_from_response(
            content: str, tag_list=None, logger=None, default_value=None
    ):
        """
        Extract specific components from a string based on provided tags.

        This function searches for specific tags in the provided content and extracts the data within the
        outermost matching tags. If a tag from the tag_list is not found in the content, it will not appear
        in the returned dictionary. If multiple tags are found, only the first one is used.

        Args:
            content (str): The string to extract data from.
            tag_list (list[str], optional): A list of tags to search for. Defaults to
                ["score", "suggestion", "requirement_for_previous", "result"].
            logger (Logger, optional): Logger instance for logging errors. Defaults to None.
            default_value (any, optional): Default value to assign if a tag is not found. Defaults to None.

        Returns:
            dict: A dictionary containing the extracted data, where keys are tags and values are the extracted
                content.
        """
        if tag_list is None:
            print("tag_list is None, now set it to default value")
            tag_list = ["score", "suggestion", "requirement_for_previous", "result"]

        ret_dict = {}
        for tag in tag_list:
            matching_list = OptimUtils.find_outermost_tags(content, tag)
            if len(matching_list) > 1:
                if logger:
                    logger.error(f"Multiple {tag} tags found in content, using the first one. Content: {content}")
                ret_dict[tag] = matching_list[0]
            if len(matching_list) > 0:
                ret_dict[tag] = matching_list[0]

        # Check for missing items
        for key in tag_list:
            if key not in ret_dict.keys():
                print(
                    "\033[31m"
                    + f"!!! Failed to find the value for {key} in the model's output. Setting it to default_value ({default_value}).\n\nExtracting from the following content: {content}"
                    + "\033[0m"
                )
                if default_value is not None:
                    # None indicates that there is no key, if it is "", it means that there is such a key, but the value is an empty string
                    ret_dict[key] = default_value
        return ret_dict

    @staticmethod
    def parallel_execution(functions, max_workers=8):
        """
        Parallelly execute a list of partial functions pre-filled with parameters.

        This method runs a list of partially filled functions in parallel using a ThreadPoolExecutor.
        It collects the results of each function execution and returns them in a list.

        Args:
            functions (list): A list of partial functions pre-filled with parameters.
            max_workers (int, optional): The maximum number of workers in ThreadPoolExecutor. Defaults to 8.

        Returns:
            list: A list of results from the execution of the functions.
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks to the thread pool and get the future object
            futures = [executor.submit(func) for func in functions]

            results = []
            for future in futures:
                try:
                    # Call the future.result() method to wait for each task to complete and add the result to the results list.
                    results.append(future.result())
                except Exception as exc:
                    func = functions[futures.index(future)]
                    print(
                        f"error in parallel, Function {func.func.__name__} with args {func.args}, kwargs {func.keywords} generated an exception: {exc}"
                    )
                    results.append(None)
            return results
