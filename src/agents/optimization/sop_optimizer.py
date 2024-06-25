import copy
import logging
import json
from pathlib import Path

from agents import SOP, Solution, SolutionConfig
from agents.agents.llm import LLMConfig, OpenAILLM
from agents.evaluation import Case
from agents.task.node import NodeConfig, Node
from agents.optimization import prompt_formatter
from agents.optimization.optimizer import Optimizer, OptimizerConfig
from agents.optimization.utils import OptimUtils

logger = logging.getLogger(__name__)


class SOPOptimizerConfig(OptimizerConfig):
    """
    Configuration for the SOP Optimizer.

    This class parses and stores the configuration settings specific to the SOP optimizer,
    extending the generic OptimizerConfig.

    Args:
        config_path (str): Path to the configuration file.
    """

    def __init__(self, config_path):
        super().__init__(config_path)

        self.llm_config = self.sop_optimizer_setting_dict.get("llm_config")
        self.meta_prompt = self.sop_optimizer_setting_dict.get("meta_prompt")


class SOPOptimizer(Optimizer):
    """
    The SOP Optimizer class for optimizing SOPs.

    This class extends the generic Optimizer and uses the SOPOptimizerConfig to set up
    SOP optimization, including handling large language model (LLM) configurations and
    managing optimization components.

    Args:
        config (SOPOptimizerConfig): Configuration instance for the SOP optimizer.
        logger_name (str): Name of the logger.
    """

    def __init__(self, config: SOPOptimizerConfig, logger_name: str):
        super().__init__(config)
        self.config = config

        # llm
        self.llm_eval = OpenAILLM(LLMConfig(config.llm_config)) if config.llm_config else None

        # prompt
        self.meta_backward = config.meta_prompt.get("backward")
        self.meta_optim = config.meta_prompt.get("optim")

        # logger
        self.logger = logging.getLogger(logger_name) if logger_name else logging.getLogger(__name__)

    def optimize(
            self,
            case_list: list[Case],
            solution: Solution,
            save_path: Path,
            parallel_max_num):
        """
        Optimizes the SOP for the given list of cases.

        Args:
            case_list (list[Case]): List of cases to be optimized.
            solution (Solution): The solution to be optimized.
            save_path (Path): Path to save the results.
            parallel_max_num (int): Maximum number of parallel processes.

        Returns:
            tuple: The updated solution and optimization status.
        """
        self.logger.info("Start to optimize SOP")

        # 1. Perform backward pass for each case to get the necessary information
        for case in case_list:
            OptimUtils.node_eval(case, solution, self.llm_eval, self.logger)
            self.backward(case, solution, save_path / "backward")

        # 2. Construct the prompt and get the optimization method
        prompt = prompt_formatter.formulate_prompt_for_sop_optim(self.meta_optim, solution.sop, case_list)
        _, content = self.llm_eval.get_response(chat_messages=None, system_prompt="",
                                                last_prompt=prompt, stream=False)

        # print("in optimize sop, prompt is: ", prompt)
        # print("in optimize sop, response is : ", content)

        # 3. Extract results and attempt to optimize the SOP
        extracted_dict = OptimUtils.extract_data_from_response(content, self.meta_optim["extract_key"])
        result = extracted_dict["result"]
        analyse = extracted_dict["analyse"]
        solution, op_status = SOPOptimizer.try_optim_with_llm_result(solution, result, self.logger)

        # Default optimized solution: controller's transit_type is llm, transit_system_prompt and transit_last_prompt are empty
        if op_status:
            for node in solution.sop.nodes.values():
                node.controller.update({"transit_type": "llm", "transit_system_prompt": "", "transit_last_prompt": ""})

        # 4. Save the final solution and optimization information
        optim_info = {
            "optim_status": op_status,
            "result": result,
            "analyse": analyse,
            "prompt": prompt,
            "response": content,
        }
        with open(save_path / "sop_optim_info.json", "w", encoding="utf-8") as f:
            json.dump(optim_info, f, ensure_ascii=False, indent=4)

        # Reload the saved solution to avoid mismatches between config and actual data
        solution.dump(save_path)
        solution = Solution(config=SolutionConfig(f"{save_path}/solution.json"))
        self.logger.debug(
            f"Finish optimizing SOP, save the final solution to: {save_path}/solution.json. The optim_status is {op_status}"
        )
        return solution, op_status

    def backward(self, case: Case, solution: Solution, save_dir: Path = None):
        """
        Performs backward pass to evaluate the case and get suggestions for optimizing the SOP.

        Args:
            case (Case): The case to be evaluated.
            solution (Solution): The solution configuration.
            save_dir (Path, optional): The directory to save the results. Defaults to None.
        """
        prompt = prompt_formatter.formulate_prompt_for_sop_optim(
            self.meta_backward, solution.sop, [case], consider_case_loop=False)
        _, content = self.llm_eval.get_response(
            chat_messages=None, system_prompt="", last_prompt=prompt, stream=False)

        # print("in backward, prompt is: ", prompt)
        # print("in backward, response is: ", content)

        assert "suggestion" in content, f"Content does not contain suggestion field, content is {content}"
        extracted_dict = OptimUtils.extract_data_from_response(content, self.meta_backward["extract_key"])
        suggestion = extracted_dict["suggestion"]
        analyse = extracted_dict.get("analyse", "")
        suggestion_data = {
            "prompt": prompt,
            "response": content,
            "suggestion": suggestion,
            "analyse": analyse,
        }
        case.sop_suggestion.update(**suggestion_data)

        if save_dir:
            case.dump(save_dir / f"{case.case_id}.json")

    @staticmethod
    def try_optim_with_llm_result(solution: Solution, result: str, logger):
        """
        Attempts to optimize the solution using the given LLM result.

        Args:
            solution (Solution): The current solution.
            result (str): The optimization result provided by the large language model.
            logger (logging.Logger): Logger for recording information.

        Returns:
            tuple: The optimized solution and a boolean indicating the success of the optimization.
        """
        # result is empty, no optimization attempt
        if not result:
            logger.info("result is None or empty, can not optimize SOP")
            return solution, False

        # result is not empty, optimization can be attempted
        logger.debug("In SOP optim, LLM result is not None, try to use the result to optimize SOP")
        logger.debug(f"result is: {result}")

        # Attempt to parse the result and check the legality of the op_list
        op_status, reason, op_list = SOPOptimizer.check_sop_optim_op_list_legal(result, solution.sop, logger)

        # If the optimization method is not legal, no optimization attempt
        if not op_status:
            return solution, False

        # If the optimization method is legal, attempt optimization
        else:
            logger.debug("op_list is legal, try to optimize SOP")

            # Deepcopy the solution before optimization for rollback in case of errors
            deep_copy_solution = copy.deepcopy(solution)
            idx = -1
            op = None
            # Attempt each optimization, rollback if any error occurs
            try:
                for idx, op in enumerate(op_list):
                    SOPOptimizer.do_sop_optim(solution, op, logger)
            except Exception as e:
                logger.error(f"Error when optimizing SOP: {e}, the op idx is {idx}, the op is {op}")
                # On error, rollback and return the original solution with False status
                return deep_copy_solution, False
            # On successful optimization, return the optimized solution and True status
            return solution, True

    @staticmethod
    def do_sop_optim(solution: Solution, op: dict, logger):
        """
        Performs SOP optimization based on the given operation.

        Args:
            solution (Solution): The current solution.
            op (dict): The optimization operation.
            logger (logging.Logger): Logger for recording information.
        """
        # Perform optimization on the specific operation
        sop: SOP = solution.sop
        action = op["action"]
        if action == "add_node":
            new_node_name = op["node_name"]
            node_config = NodeConfig.generate_config(
                task_description=solution.task.task_description,
                node_name=new_node_name,
                node_description=op["node_description"],
                next_nodes=op["edges"][new_node_name],
            )
            # Create the new node
            new_node = Node(node_config)
            new_node.next_nodes = {}
            for next_node_name in op["edges"][new_node_name]:
                new_node.next_nodes[next_node_name] = sop.nodes[next_node_name]
            new_node.controller.update(op["controller"])

            # Add the new node to SOP, only updating the current node's information
            sop.nodes[new_node.node_name] = new_node
        elif action == "delete_node":
            op_node_name = op["node_name"]
            sop.nodes.pop(op_node_name)
            for pre_node_name, next_node_name_list in op["edges"].items():
                sop.nodes[pre_node_name].next_nodes = {}
                for next_node_name in next_node_name_list:
                    sop.nodes[pre_node_name].next_nodes[next_node_name] = sop.nodes[next_node_name]
        elif action == "update_node_description":
            op_node_name = op["node_name"]
            op_node_description = op["node_description"]
            sop.nodes[op_node_name].node_description = op_node_description
        elif action == "update_edges":
            updated_edges = op["edges"]
            for pre_node_name, next_node_name_list in updated_edges.items():
                sop.nodes[pre_node_name].next_nodes = {}
                for next_node_name in next_node_name_list:
                    sop.nodes[pre_node_name].next_nodes[next_node_name] = sop.nodes[next_node_name]
        # elif action == "update_transfer":
        #     for pre_node_name, transfer_dict in op.items():
        #         if pre_node_name == "action":
        #             continue
        #         sop.nodes[pre_node_name].controller.update(transfer_dict)
        else:
            # Error, unknown action
            logger.error(f"Unknown action {action}")
            raise ValueError(f"Unknown action {action}")

    @staticmethod
    def check_sop_optim_op_list_legal(optim_result: str, sop: SOP, logger):
        """
        Checks the legality of the SOP optimization operations provided by the LLM.

        Args:
            optim_result (str): The optimization result provided by the LLM.
            sop (SOP): The current SOP.
            logger (logging.Logger): Logger for recording information.

        Returns:
            tuple: A boolean indicating legality, a string message, and the op_list.
        """
        try:
            op_list = json.loads(optim_result)
        except Exception as e:
            logger.debug(f"Error when loading the result as JSON: {e}, the result is: {optim_result}")
            return False, "Unable to convert the optimization result string to JSON format", None

        new_node_names = ["end_node"]
        try:
            logger.debug(f"load op_list successfully, op_list is: {op_list}")
            for idx, op in enumerate(op_list):
                assert "action" in op, f"The action field is missing in operation {idx + 1}"
                action = op["action"]
                if action == "add_node":
                    assert "node_name" in op, f"The node_name field is missing in add_node operation {idx + 1}: {op}"
                    assert "node_description" in op, f"The node_description field is missing in add_node operation {idx + 1}: {op}"
                    assert "edges" in op, f"The edges field is missing in add_node operation {idx + 1}: {op}"
                    assert op["node_name"] in op[
                        "edges"], f"In add_node, the new node must have successor nodes defined, operation {idx + 1}: {op}"
                    new_node_names.append(op["node_name"])

                elif action == "delete_node":
                    assert "node_name" in op, f"The node_name field is missing in delete_node operation {idx + 1}: {op}"
                    assert "edges" in op, f"The edges field is missing in delete_node operation {idx + 1}: {op}"

                elif action == "update_node_description":
                    assert "node_name" in op, f"The node_name field is missing in update_node_description operation {idx + 1}: {op}"
                    assert "node_description" in op, f"The node_description field is missing in update_node_description operation {idx + 1}: {op}"

                elif action == "update_edges":
                    updated_edges = op["edges"]
                    for node_name in updated_edges:
                        assert node_name in sop.nodes or node_name in new_node_names, f"The from_node_name in update_edges operation is not in SOP, the from node is {node_name}, operation {idx + 1}: {op}"
                        for next_node_name in updated_edges[node_name]:
                            assert next_node_name in sop.nodes or next_node_name in new_node_names, f"The next_node_name in update_edges operation is not in SOP, the next node is {next_node_name}, operation {idx + 1}: {op}"

                # elif action == "update_transfer":
                #     for node_name in op:
                #         if node_name == "action":
                #             continue
                #         assert node_name in sop.nodes or node_name in new_node_names, f"The node_name in update_transfer operation is not in SOP, operation {idx + 1}: {op}"


        except AssertionError as ae:
            logger.error(f"Assertion error during SOP optimization result legality check: {ae}")
            logger.error(
                f"New node names: {new_node_names}, SOP node names: {[node.node_name for node in sop.nodes.values()]}")
            return False, str(ae), op_list
        except Exception as e:
            logger.error(f"Unexpected error during SOP optimization result legality check: {e}")
            return False, f"Unexpected assertion error: {e}", op_list
        return True, "legal_op_list", op_list


if __name__ == "__main__":
    # Running backward() now doesn't try to optimize the controller's transit
    prompt_backward = """
你是一个大模型精调师。现在有一个流程需要你调整，现在我会给你一个处理一个任务的标准流程(standard operation procedure, SOP)，这个SOP内部含有多个Node，每个Node都会负责完成一定的任务，从而完成整个任务。
我会给你一个SOP和一个运行实例，你需要分析这个SOP，然后给出你的优化意见。
每个node都对应了需要完成的一些任务，这个任务的描述你可以在node_description中找到。

一个SOP主要由Node组成，每个Node都会负责完成一定的任务，从而完成整个任务。每个Node都有名称，描述，后继节点。
后继节点是一个字典(edges)，key是后继节点的名称，value是后继节点的Node对象。
如下是一个SOP的例子：
```json
{
    "nodes": {
        "Affirmative_Task_Allocation_node": {
            ...
        },
        "Negative_Task_Allocation_node": {
            ...
        },
        "Debate_Order_node": {
            ...
        },
        "Debate_Random_node": {
            "node_name": "Debate_Random_node",
            "node_description": "We are now in the open debate phase, where each debater has the freedom to speak as they wish.\nThe debate topic is as follows: <debate topic>\n<Theme>should Hermione Granger develop a romantic relationship with Harry Potter or Ron Weasley?</Theme>\n <Affirmative viewpoint> Supporting Hermione and Harry together.</Affirmative viewpoint>\n<Negative viewpoint> Supporting Hermione and Ron together</Negative viewpoint>\n</debate topic>\n ",
        },
        "Judge_node": {
            ...
        }
    },
    "edges": {
        "Affirmative_Task_Allocation_node": [
            "Affirmative_Task_Allocation_node",
            "Negative_Task_Allocation_node"
        ],
        "Negative_Task_Allocation_node": [
            "Negative_Task_Allocation_node",
            "Debate_Order_node"
        ],
        "Debate_Order_node": [
            "Debate_Order_node",
            "Debate_Random_node"
        ],
        "Debate_Random_node": [
            "Debate_Random_node",
            "Judge_node"
        ],
        "Judge_node": [
            "Judge_node",
            "end_node"
        ]
    },
    "root": "Affirmative_Task_Allocation_node",
    "end": "end_node"
}
```
    
    
你需要用自然语言给出优化意见，一般来说优化这个SOP可以从5方面入手，你可以从多方面组合的给出多调意见。
1. 增加节点：如果你认为SOP中缺少了一些节点，你可以增加这些节点。而且你需要简单描述这个节点的信息，包括节点名、描述和后继节点。
2. 删除节点：如果你认为SOP中有一些节点是多余的，你可以删除这些节点。并且你需要给出需要删除的节点名称，以及需要更新的前驱节点的后继节点，用于替换删除节点的位置。
3. 更新节点描述：如果你认为SOP中的节点描述不够清晰，你可以更新这些节点的描述。你需要给出需要更新的节点名称和新的描述。
4. 更新节点间的关系：如果你认为SOP中的节点间的关系不够清晰，你可以更新这些节点间的关系。你需要给出需要更新的节点之间的关系。
    
    
我会给你一个实际的SOP配置以及一个运行实例，你需要基于这个运行实例进行分析并给出优化意见，给出的分析请使用<analyse></analyse>包裹，建议请使用<suggestion></suggestion>包裹。比如：
<analyse>Debate_Random_node实际表现效果不佳，可以尝试在其前方再加一个node</analyse>
<suggestion>在Debate_Random_node前再加一个node，这个node名为Added_Debate_Random_node, 描述信息为：“进一步辩论，使得论点论据给的更清晰”,其后继节点为本身和Debate_Random_node，控制器转移类型为"order"</suggestion>。


如下你需要处理的具体的任务信息
## SOP Config
<sop_config>
{sop_config}</sop_config>

## Run Instance
<run_instance>
{run_instance_summary}</run_instance>

## Evaluation
<evaluation>
{loss_info}</evaluation>


注意：
1. 你需要给出你的分析过程，然后给出你的优化建议，请使用自然语言描述你给出的优化建议。
2. 分析过程请用<analyse></analyse>包裹，优化建议请用<suggestion></suggestion>包裹，两者都必须存在。
2. 如果没有优化建议，请在<analyse></analyse>中给出分析结果，并给出<suggestion>There is no need for optimization.</suggestion>
3. 如果认为整体SOP没问题，只是具体的node行为需要优化的话，可以选择不优化，后续会有优化node的操作。
"""

    prompt_backward_en = """
You are a large model fine-tuner. There is a process that needs adjustment, and I will now provide you with a standard operation procedure (SOP) for handling a task. This SOP consists of multiple nodes, each responsible for completing specific tasks to accomplish the overall mission.

I will provide you with an SOP and a runtime instance. You need to analyze this SOP and provide your optimization suggestions. Each node corresponds to certain tasks, and you can find the task description in `node_description`.

An SOP mainly consists of nodes, each responsible for completing specific tasks to accomplish the overall mission. Each node has a name, description, and successor nodes. The successor nodes are a dictionary (`edges`), where the key is the successor node's name and the value is the successor node's Node object.

Here is an example of an SOP:
```json
{
    "nodes": {
        "Affirmative_Task_Allocation_node": {
            ...
        },
        "Negative_Task_Allocation_node": {
            ...
        },
        "Debate_Order_node": {
            ...
        },
        "Debate_Random_node": {
            "node_name": "Debate_Random_node",
            "node_description": "We are now in the open debate phase, where each debater has the freedom to speak as they wish.\nThe debate topic is as follows: <debate topic>\n<Theme>should Hermione Granger develop a romantic relationship with Harry Potter or Ron Weasley?</Theme>\n <Affirmative viewpoint> Supporting Hermione and Harry together.</Affirmative viewpoint>\n<Negative viewpoint> Supporting Hermione and Ron together</Negative viewpoint>\n</debate topic>\n ",
        },
        "Judge_node": {
            ...
        }
    },
    "edges": {
        "Affirmative_Task_Allocation_node": [
            "Affirmative_Task_Allocation_node",
            "Negative_Task_Allocation_node"
        ],
        "Negative_Task_Allocation_node": [
            "Negative_Task_Allocation_node",
            "Debate_Order_node"
        ],
        "Debate_Order_node": [
            "Debate_Order_node",
            "Debate_Random_node"
        ],
        "Debate_Random_node": [
            "Debate_Random_node",
            "Judge_node"
        ],
        "Judge_node": [
            "Judge_node",
            "end_node"
        ]
    },
    "root": "Affirmative_Task_Allocation_node",
    "end": "end_node"
}
```
    
You need to provide optimization suggestions in natural language. Generally, optimizing this SOP can be approached from five aspects, and you can combine multiple aspects to provide comprehensive suggestions.

1. **Add Nodes:** If you believe the SOP lacks certain nodes, you can add these nodes. You need to briefly describe the information about the new node, including the node's name, description, successor nodes.
2. **Delete Nodes:** If you think some nodes in the SOP are redundant, you can delete these nodes. You need to provide the names of the nodes to be deleted and update the predecessor nodes' successor nodes to replace the deleted node.
3. **Update Node Descriptions:** If you believe the node descriptions in the SOP are not clear enough, you can update these descriptions. You need to provide the names of the nodes to be updated and the new descriptions.
4. **Update Relationships Between Nodes:** If you think the relationships between nodes in the SOP are not clear, you can update these relationships. You need to provide the updated relationships between the nodes.

I will provide you with a specific SOP configuration and a runtime instance. You need to analyze this runtime instance and provide optimization suggestions. Please use <analyse></analyse> to wrap your analysis and <suggestion></suggestion> to wrap your suggestions. For example:
<analyse>Debate_Random_node did not perform well, and we could try adding a node before it.</analyse>
<suggestion>Add a node before Debate_Random_node named Added_Debate_Random_node with the description: "Further debate to clarify arguments." Its successor nodes are itself and Debate_Random_node, with the controller transfer type being "order".</suggestion>

Here is the specific task information you need to process:
## SOP Config
<sop_config>
{sop_config}</sop_config>

## Run Instance
<run_instance>
{run_instance_summary}</run_instance>

## Evaluation
<evaluation>
{loss_info}</evaluation>

Note:
1. You need to provide your analysis process and then give your optimization suggestions, describing them in natural language.
2. The analysis process should be wrapped in <analyse></analyse>, and optimization suggestions should be wrapped in <suggestion></suggestion>. Both must be present.
3. If there are no optimization suggestions, please provide the analysis result in <analyse></analyse> and give <suggestion>There is no need for optimization.</suggestion>.
4. If the overall SOP is fine, but specific node behaviors need optimization, you may choose not to optimize. There will be further operations to optimize the nodes later.

"""

    prompt_optim = """
你是一个大模型精调师。现在有一个流程需要你调整，现在我会给你一个处理一个任务的标准流程(standard operation procedure, SOP)，这个SOP内部含有多个Node，每个Node都会负责完成一定的任务，从而完成整个任务。
我会给你一个SOP和一个运行实例，你需要分析这个SOP，然后给出你的优化意见。
每个node都对应了需要完成的一些任务，这个任务的描述你可以在node_description中找到。

一个SOP主要由Node组成，每个Node都会负责完成一定的任务，从而完成整个任务。每个Node都有名称，描述，后继节点。
后继节点是一个字典(edges)，key是后继节点的名称，value是后继节点的Node对象。
如下是一个SOP的例子：
```json
{
    "nodes": {
        "Affirmative_Task_Allocation_node": {
            ...
        },
        "Negative_Task_Allocation_node": {
            ...
        },
        "Debate_Order_node": {
            ...
        },
        "Debate_Random_node": {
            "node_name": "Debate_Random_node",
            "node_description": "We are now in the open debate phase, where each debater has the freedom to speak as they wish.\nThe debate topic is as follows: <debate topic>\n<Theme>should Hermione Granger develop a romantic relationship with Harry Potter or Ron Weasley?</Theme>\n <Affirmative viewpoint> Supporting Hermione and Harry together.</Affirmative viewpoint>\n<Negative viewpoint> Supporting Hermione and Ron together</Negative viewpoint>\n</debate topic>\n ",
        },
        "Judge_node": {
            ...
        }
    },
    "edges": {
        "Affirmative_Task_Allocation_node": [
            "Affirmative_Task_Allocation_node",
            "Negative_Task_Allocation_node"
        ],
        "Negative_Task_Allocation_node": [
            "Negative_Task_Allocation_node",
            "Debate_Order_node"
        ],
        "Debate_Order_node": [
            "Debate_Order_node",
            "Debate_Random_node"
        ],
        "Debate_Random_node": [
            "Debate_Random_node",
            "Judge_node"
        ],
        "Judge_node": [
            "Judge_node",
            "end_node"
        ]
    },
    "root": "Affirmative_Task_Allocation_node",
    "end": "end_node"
}
```

我会给你一个SOP 以及针对这个SOP 的修改建议，你需要分析这个SOP，然后给出优化的方法。
你需要首先给出你的分析过程，然后给出你优化后的结果，分析过程请用<analyse></analyse>包裹，优化后的结果请用<result></result>包裹，其应该可以直接被解析为json。
当你认为无需优化时，请将<result></result>内部留空。
当你认为需要优化时，需要用一个json表达出你的优化结果，如下所示：
```json
[
    {
        # 增加一个名为 Affirmative_Task_Allocation_node 的node，需要给定node_name, node_description, 同时为其指定后继节点
        "action": "add_node",
        "node_name": "Affirmative_Task_Allocation_node",
        "node_description": "It is currently the debate stage, where the positive side is assigning tasks.",
        "edges": {
            "Affirmative_Task_Allocation_node": [
                "Affirmative_Task_Allocation_node",
                "Negative_Task_Allocation_node"
            ]
        }
    },
    {
        # 删除一个节点，需要给定node_name, 同时需要更新前驱节点的后继节点，被修改的边在edges给出，里面的节点应该都是被删除节点的前驱节点
        "action": "delete_node",
        "node_name": "Negative_Task_Allocation_node",
        "edges": {
            # Affirmative_Task_Allocation_node 是 Negative_Task_Allocation_node 的前驱节点，需要更新其后继节点
            "Affirmative_Task_Allocation_node": [   
                "Affirmative_Task_Allocation_node",
                "Debate_Order_node"
            ]
            ...
        }
    },
    {
        # 更改 Affirmative_Task_Allocation_node 的Node description，请注意修改后尽量不要有巨大的语义变化
        "action": "update_node_description",
        "node_name": "Affirmative_Task_Allocation_node",
        "node_description": "It is currently the debate stage, where the positive side is assigning tasks.",
    },
    {
        # 更新节点间的边，你需要注意每个node都要有自环，因此其第一个后继节点就是其本身
        "action": "update_edges",
        "edges": {
            "Debate_Order_node": [
                "Debate_Order_node",
                "Debate_Random_node"
            ]
        }
        ...
    }
]
```
    

如下是一个需要你优化的SOP的配置信息和修改建议：

## sop config
{sop_config}

## Suggestion
### Suggestion
<suggestion_{index}>
{suggestion}</suggestion_{index}>


注意：
1. 给出的结果请用<result></result>包裹，需要保证其是可以直接被保存为json的，否则会被判为错误。
2. <result></result>和<analyse></analyse>都是必须的，当不需要优化时，请将<result></result>内部留空。
3. 给出的<result></result>请严格遵守给出的示例json的格式。
4. 你可以组合使用add_node, delete_node, update_node_description, update_edges这几种action，但是请保证你的结果是合理的。
5. 当使用了add_node后，往往需要更新edges，当使用了delete_node后，往往需要更新前驱节点的后继节点。
6. 如果不是必要，尽量不要选择增加和删除节点，如果可以通过修改node_description或者调整node之间的关系来解决问题，那么这样做更好。
"""

    prompt_optim_en = """
You are a large model fine-tuner. There is a process that needs adjustment, and I will now provide you with a standard operation procedure (SOP) for handling a task. This SOP consists of multiple nodes, each responsible for completing specific tasks to accomplish the overall mission.

I will provide you with an SOP and a runtime instance. You need to analyze this SOP and provide your optimization suggestions. Each node corresponds to certain tasks, and you can find the task description in `node_description`.

An SOP mainly consists of nodes, each responsible for completing specific tasks to accomplish the overall mission. Each node has a name, description, and successor nodes. The successor nodes are a dictionary (`edges`), where the key is the successor node's name and the value is the successor node's Node object.

Here is an example of an SOP:
```json
{
    "nodes": {
        "Affirmative_Task_Allocation_node": {
            ...
        },
        "Negative_Task_Allocation_node": {
            ...
        },
        "Debate_Order_node": {
            ...
        },
        "Debate_Random_node": {
            "node_name": "Debate_Random_node",
            "node_description": "We are now in the open debate phase, where each debater has the freedom to speak as they wish.\nThe debate topic is as follows: <debate topic>\n<Theme>should Hermione Granger develop a romantic relationship with Harry Potter or Ron Weasley?</Theme>\n <Affirmative viewpoint> Supporting Hermione and Harry together.</Affirmative viewpoint>\n<Negative viewpoint> Supporting Hermione and Ron together</Negative viewpoint>\n</debate topic>\n ",
        },
        "Judge_node": {
            ...
        }
    },
    "edges": {
        "Affirmative_Task_Allocation_node": [
            "Affirmative_Task_Allocation_node",
            "Negative_Task_Allocation_node"
        ],
        "Negative_Task_Allocation_node": [
            "Negative_Task_Allocation_node",
            "Debate_Order_node"
        ],
        "Debate_Order_node": [
            "Debate_Order_node",
            "Debate_Random_node"
        ],
        "Debate_Random_node": [
            "Debate_Random_node",
            "Judge_node"
        ],
        "Judge_node": [
            "Judge_node",
            "end_node"
        ]
    },
    "root": "Affirmative_Task_Allocation_node",
    "end": "end_node"
}
```

I will provide you with an SOP and suggestions for modifications. You need to analyze this SOP and then provide optimization methods. You need to first provide your analysis process, and then provide your optimized results. The analysis process should be wrapped in <analyse></analyse>, and the optimized results should be wrapped in <result></result>, which should be directly parsable into JSON.

If you believe no optimization is needed, leave the inside of <result></result> empty.

If you believe optimization is needed, use a JSON format to express your optimized results, as shown below:
```json
[
    {
        # Add a node named Affirmative_Task_Allocation_node. Provide node_name, node_description, and specify successor nodes.
        "action": "add_node",
        "node_name": "Affirmative_Task_Allocation_node",
        "node_description": "It is currently the debate stage, where the positive side is assigning tasks.",
        "edges": {
            "Affirmative_Task_Allocation_node": [
                "Affirmative_Task_Allocation_node",
                "Negative_Task_Allocation_node"
            ]
        }
    },
    {
        # Delete a node. Provide node_name and update the predecessor node's successor nodes. The modified edges should be given, with the nodes being the predecessors of the deleted node.
        "action": "delete_node",
        "node_name": "Negative_Task_Allocation_node",
        "edges": {
            # Affirmative_Task_Allocation_node is the predecessor of Negative_Task_Allocation_node, so its successor nodes need to be updated.
            "Affirmative_Task_Allocation_node": [
                "Affirmative_Task_Allocation_node",
                "Debate_Order_node"
            ]
        }
    },
    {
        # Update the Node description of Affirmative_Task_Allocation_node. Ensure that the modified description does not have significant semantic changes.
        "action": "update_node_description",
        "node_name": "Affirmative_Task_Allocation_node",
        "node_description": "It is currently the debate stage, where the positive side is assigning tasks."
    },
    {
        # Update the edges between nodes. You need to note that each node has a self-loop, so its first successor is itself.
        "action": "update_edges",
        "edges": {
            "Debate_Order_node": [
                "Debate_Order_node",
                "Debate_Random_node"
            ]
        }
    }
]
```

Below are the configuration information and suggestions for the SOP that you need to optimize:

## sop config
{sop_config}

## Suggestion
### Suggestion
<suggestion_{index}>
{suggestion}</suggestion_{index}>

Note:
1. The results should be wrapped in <result></result>, and they need to be directly parsable into JSON. Otherwise, it will be judged as an error.
2. Both <result></result> and <analyse></analyse> are required. If no optimization is needed, leave the inside of <result></result> empty.
3. The <result></result> provided should strictly follow the format of the given example JSON.
4. You can combine actions such as add_node, delete_node, update_node_description, and update_edges. However, ensure your results are reasonable.
5. When using add_node, you often need to update edges. When using delete_node, you often need to update the predecessor node's successor nodes.
6. If not necessary, try to avoid adding and deleting nodes. If the problem can be solved by modifying the node description or adjusting the relationships between nodes, that is preferable.
"""

    last_prompt = prompt_optim_en

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

    res, cont = llm.get_response(
        chat_messages=None, system_prompt="", last_prompt=last_prompt, stream=False
    )

    print("\n\n\n" + cont)

    # save two prompts which will not be used anymore
    prompt_backward_saved = """
你是一个大模型精调师。现在有一个流程需要你调整，现在我会给你一个处理一个任务的标准流程(standard operation procedure, SOP)，这个SOP内部含有多个Node，每个Node都会负责完成一定的任务，从而完成整个任务。
我会给你一个SOP和一个运行实例，你需要分析这个SOP，然后给出你的优化意见。
每个node都对应了需要完成的一些任务，这个任务的描述你可以在node_description中找到。


一个SOP主要由Node组成，每个Node都会负责完成一定的任务，从而完成整个任务。每个Node都有名称，描述，后继节点和控制器。
后继节点是一个字典(edges)，key是后继节点的名称，value是后继节点的Node对象。
控制器是一个字典，包含了这个Node的控制信息，包括转移类型(transit_type)和转移条件(transit_system_prompt和transit_last_prompt)。转移类型有llm, order两种。order表示按序转移，会转移到edges中当前节点对应字典中的第一个非己node'。llm表示按照语言模型的输出转移，此时需要给出transit_system_prompt和 transit_last_prompt。
如下是一个SOP的例子：
```json
{
    "nodes": {
        "Affirmative_Task_Allocation_node": {
            ...
        },
        "Negative_Task_Allocation_node": {
            ...
        },
        "Debate_Order_node": {
            ...
        },
        "Debate_Random_node": {
            "node_name": "Debate_Random_node",
            "controller": {
                "transit_type": "order",
                "transit_system_prompt": "",
                "transit_last_prompt": "",
            },
            "node_description": "We are now in the open debate phase, where each debater has the freedom to speak as they wish.\nThe debate topic is as follows: <debate topic>\n<Theme>should Hermione Granger develop a romantic relationship with Harry Potter or Ron Weasley?</Theme>\n <Affirmative viewpoint> Supporting Hermione and Harry together.</Affirmative viewpoint>\n<Negative viewpoint> Supporting Hermione and Ron together</Negative viewpoint>\n</debate topic>\n ",
        },
        "Judge_node": {
            ...
        }
    },
    "edges": {
        "Affirmative_Task_Allocation_node": [
            "Affirmative_Task_Allocation_node",
            "Negative_Task_Allocation_node"
        ],
        "Negative_Task_Allocation_node": [
            "Negative_Task_Allocation_node",
            "Debate_Order_node"
        ],
        "Debate_Order_node": [
            "Debate_Order_node",
            "Debate_Random_node"
        ],
        "Debate_Random_node": [
            "Debate_Random_node",
            "Judge_node"
        ],
        "Judge_node": [
            "Judge_node",
            "end_node"
        ]
    },
    "root": "Affirmative_Task_Allocation_node",
    "end": "end_node"
}
```


你需要用自然语言给出优化意见，一般来说优化这个SOP可以从5方面入手，你可以从多方面组合的给出多调意见。
1. 增加节点：如果你认为SOP中缺少了一些节点，你可以增加这些节点。而且你需要简单描述这个节点的信息，包括节点的名称和描述，以及这个节点的后继节点和控制器的配置信息。
2. 删除节点：如果你认为SOP中有一些节点是多余的，你可以删除这些节点。并且你需要给出需要删除的节点名称，以及需要更新的前驱节点的后继节点，用于替换删除节点的位置。
3. 更新节点描述：如果你认为SOP中的节点描述不够清晰，你可以更新这些节点的描述。你需要给出需要更新的节点名称和新的描述。
4. 更新节点间的关系：如果你认为SOP中的节点间的关系不够清晰，你可以更新这些节点间的关系。你需要给出需要更新的节点之间的关系。
5. 更新节点间的转移条件：如果你认为SOP中的节点间的转移条件不够清晰，你可以更新这些节点间的转移条件。你需要给出需要更新的节点之间的转移条件。


我会给你一个实际的SOP配置以及一个运行实例，你需要基于这个运行实例进行分析并给出优化意见，给出的分析请使用<analyse></analyse>包裹，建议请使用<suggestion></suggestion>包裹。比如：
<analyse>Debate_Random_node实际表现效果不佳，可以尝试在其前方再加一个node</analyse>
<suggestion>在Debate_Random_node前再加一个node，这个node名为Added_Debate_Random_node, 描述信息为：“进一步辩论，使得论点论据给的更清晰”,其后继节点为本身和Debate_Random_node，控制器转移类型为"order"</suggestion>。


如下你需要处理的具体的任务信息
## SOP Config
<sop_config>{sop_config}</sop_config>

## Run Instance
<run_instance>{run_instance_summary}</run_instance>

## Evaluation
<evaluation>{loss_info}</evaluation>


注意：
1. 你需要给出你的分析过程，然后给出你的优化建议，请使用自然语言描述你给出的优化建议。
2. 分析过程请用<analyse></analyse>包裹，优化建议请用<suggestion></suggestion>包裹，两者都必须存在。
2. 如果没有优化建议，请在<analyse></analyse>中给出分析结果，并给出<suggestion>There is no need for optimization.</suggestion>
3. 如果认为整体SOP没问题，只是具体的node行为需要优化的话，可以选择不优化，后续会有优化node的操作。
"""

    prompt_optim_saved = """
你是一个大模型精调师。现在有一个流程需要你调整，现在我会给你一个处理一个任务的标准流程(standard operation procedure, SOP)，这个SOP内部含有多个Node，每个Node都会负责完成一定的任务，从而完成整个任务。
我会给你一个SOP和一个运行实例，你需要分析这个SOP，然后给出你的优化意见。
每个node都对应了需要完成的一些任务，这个任务的描述你可以在node_description中找到。

一个SOP主要由Node组成，每个Node都会负责完成一定的任务，从而完成整个任务。每个Node都有名称，描述，后继节点和控制器。
后继节点是一个字典(edges)，key是后继节点的名称，value是后继节点的Node对象。
控制器是一个字典，包含了这个Node的控制信息，包括转移类型(transit_type)和转移条件(transit_system_prompt和transit_last_prompt)。转移类型有llm, order两种。order表示按序转移，会转移到edges中当前节点对应字典中的第一个非己node'。llm表示按照语言模型的输出转移，此时需要给出transit_system_prompt和 transit_last_prompt。
如下是一个SOP的例子：
```json
{
    "nodes": {
        "Affirmative_Task_Allocation_node": {
            ...
        },
        "Negative_Task_Allocation_node": {
            ...
        },
        "Debate_Order_node": {
            ...
        },
        "Debate_Random_node": {
            "node_name": "Debate_Random_node",
            "controller": {
                "transit_type": "order",
                "transit_system_prompt": "",
                "transit_last_prompt": "",
            },
            "node_description": "We are now in the open debate phase, where each debater has the freedom to speak as they wish.\nThe debate topic is as follows: <debate topic>\n<Theme>should Hermione Granger develop a romantic relationship with Harry Potter or Ron Weasley?</Theme>\n <Affirmative viewpoint> Supporting Hermione and Harry together.</Affirmative viewpoint>\n<Negative viewpoint> Supporting Hermione and Ron together</Negative viewpoint>\n</debate topic>\n ",
        },
        "Judge_node": {
            ...
        }
    },
    "edges": {
        "Affirmative_Task_Allocation_node": [
            "Affirmative_Task_Allocation_node",
            "Negative_Task_Allocation_node"
        ],
        "Negative_Task_Allocation_node": [
            "Negative_Task_Allocation_node",
            "Debate_Order_node"
        ],
        "Debate_Order_node": [
            "Debate_Order_node",
            "Debate_Random_node"
        ],
        "Debate_Random_node": [
            "Debate_Random_node",
            "Judge_node"
        ],
        "Judge_node": [
            "Judge_node",
            "end_node"
        ]
    },
    "root": "Affirmative_Task_Allocation_node",
    "end": "end_node"
}
```

我会给你一个SOP 以及针对这个SOP 的修改建议，你需要分析这个SOP，然后给出优化的方法。
你需要首先给出你的分析过程，然后给出你优化后的结果，分析过程请用<analyse></analyse>包裹，优化后的结果请用<result></result>包裹，其应该可以直接被解析为json。
当你认为无需优化时，请将<result></result>内部留空。
当你认为需要优化时，需要用一个json表达出你的优化结果，如下所示：
```json
[
    {
        # 增加一个名为 Affirmative_Task_Allocation_node 的node，需要给定node_name, node_description, controller, 同时为其指定后继节点
        "action": "add_node",
        "node_name": "Affirmative_Task_Allocation_node",
        "node_description": "It is currently the debate stage, where the positive side is assigning tasks.",
        "controller": {
            "transit_type": "order",
        },
        "edges": {
            "Affirmative_Task_Allocation_node": [
                "Affirmative_Task_Allocation_node",
                "Negative_Task_Allocation_node"
            ]
        }
    },
    {
        # 删除一个节点，需要给定node_name, 同时需要更新前驱节点的后继节点，被修改的边在edges给出，里面的节点应该都是被删除节点的前驱节点
        "action": "delete_node",
        "node_name": "Negative_Task_Allocation_node",
        "edges": {
            # Affirmative_Task_Allocation_node 是 Negative_Task_Allocation_node 的前驱节点，需要更新其后继节点
            "Affirmative_Task_Allocation_node": [   
                "Affirmative_Task_Allocation_node",
                "Debate_Order_node"
            ]
            ...
        }
    },
    {
        # 更改 Affirmative_Task_Allocation_node 的Node description
        "action": "update_node_description",
        "node_name": "Affirmative_Task_Allocation_node",
        "node_description": "It is currently the debate stage, where the positive side is assigning tasks.",
    },
    {
        # 更新节点间的边
        "action": "update_edges",
        "Debate_Order_node": [
            "Debate_Order_node",
            "Debate_Random_node"
        ]
        ...
    },
    {
        # 更新节点间的转移条件
        "action": "update_transfer",
        "Debate_Order_node": {
            "transit_type": "llm",
            "transit_system_prompt": "If all three affirmative debaters and three negative debaters have present their arguments, please consider to transit to the next node, otherwise stay at the current node.",
            "transit_last_prompt": "",
        }
        ...
    }
]
```


如下是一个需要你优化的SOP的配置信息和修改建议：

## sop config
{sop_config}

## Suggestion
### Suggestion
<suggestion_{index}>
{suggestion}</suggestion_{index}>


注意：
1. 给出的结果请用<result></result>包裹，需要保证其是可以直接被保存为json的，否则会被判为错误。
2. <result></result>和<analyse></analyse>都是必须的，当不需要优化时，请将<result></result>内部留空。
3. 给出的<result></result>请严格遵守给出的示例json的格式。
4. 你可以组合使用add_node, delete_node, update_node_description, update_edges, update_transfer这几种action，但是请保证你的结果是合理的。
5. 当使用了add_node后，往往需要更新edges，当使用了delete_node后，往往需要更新前驱节点的后继节点。
6. 如果不是必要，尽量不要选择增加和删除节点，如果可以通过修改node_description或者调整node之间的关系来解决问题，那么这样做更好。
"""
