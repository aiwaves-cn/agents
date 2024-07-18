# coding=utf-8
# Copyright 2024 The AIWaves Inc. team.

#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Case class defines a test case."""
import json
import os

from .trajectory import Trajectory


class Case:
    def __init__(self, json_data: dict):
        """
        Initializes a Case object from a JSON dict.

        Args:
            json_data (dict): The JSON data to initialize the Case object.
        """
        # raw data, it will not be saved when dump
        try:
            self.raw_data = json_data

            self.case_id: str = json_data["case_id"]
            self.case_name: str = json_data["case_name"]

            self.task_id: str = json_data["task_id"]
            self.task_description = json_data["task_description"]

            self.function_ids: str = json_data["function_ids"]
            self.KB_id: str = json_data["KB_id"]

            self.input: dict = json_data["input"]
            self.ground_truth: dict = json_data.get("ground_truth")

            # fields that not available until they are run
            self.result: dict = json_data.get("result", {})  # 客户期望的直接的输出结果
            self.trajectory: Trajectory = Trajectory.load_from_json(
                json_data.get("trajectory", [])
            )

            # fields that not available until they are evaluated or optimized
            self.dataset_eval: DatasetEvaluation = DatasetEvaluation(
                **json_data.get("dataset_eval", {})
            )  # Dataset evaluation results
            self.loss: CaseLoss = CaseLoss(**json_data.get("loss", {}))  # 评估结果
            self.sop_suggestion: SOPSuggestion = SOPSuggestion(
                **json_data.get("sop_suggestion", {})
            )  # Suggestions for SOP optimization
        except Exception as e:
            print(f"Error: {e}, {json_data}")
            raise e

    @classmethod
    def read_batch_from_json(cls, json_path):
        """
        Reads a batch of cases from a JSON file and returns a list of Case objects.

        Args:
            json_path (str): The path to the JSON file containing the batch of cases.

        Returns:
            list: A list of Case objects.
        """
        with open(json_path, encoding="utf-8") as f:
            contents = json.load(f)
        return [cls(content) for content in contents]

    @classmethod
    def read_single_from_json(cls, json_path):
        """
        Reads a single case from a JSON file and returns a Case object.

        Args:
            json_path (str): The path to the JSON file containing the single case.

        Returns:
            Case: A Case object.
        """
        with open(json_path, encoding="utf-8") as f:
            content = json.load(f)
        return cls(content)

    def get_dict_for_loss_calculation(self, keys: list):
        """
        Get information needed for backward and training processes.

        Args:
            keys (list): The list of keys for the required information.

        Returns:
            dict: A dictionary containing the required information.
        """
        allowed_keys = {
            "result",
            "ground_truth",
            "history",
            "score",
            "score_info",
            "task_description",
            "f1",
            "f1_info",
        }
        for key in keys:
            if key not in allowed_keys:
                print(f"Warning: 传入了不支持的key: {key}, 处理时会跳过，支持的key有{allowed_keys}")

        ret_dict = {}
        if "result" in keys:
            ret_dict["result"] = self.result
        if "ground_truth" in keys:
            ret_dict["ground_truth"] = self.ground_truth
        if "history" in keys:
            # History contains all interaction records
            ret_dict["history"] = (
                self.trajectory.states[-1]
                .environment.shared_memory["short_term_memory"]
                .memory
            )
        if "score" in keys:
            # score will use the dataset evaluation result
            # the score info is the description of the metric which is stored in dataset
            ret_dict["score"] = self.dataset_eval.score
            ret_dict["score_info"] = self.dataset_eval.metric_description
        if "task_description" in keys:
            ret_dict["task_description"] = self.task_description
        return ret_dict

    def get_dict_for_node_optimizer(self, node_name: str, variable_names):
        """
        Get information for the NodeOptimizer.

        Args:
            node_name (str): The name of the node.
            variable_names (list): The list of variable names required by the NodeOptimizer.

        Returns:
            dict: A dictionary containing the required information for the NodeOptimizer.
        """

        def get_role_chat(cur_node_name):
            chat_str = ""
            for state in self.trajectory.states:
                if state.node.node_name != cur_node_name:
                    continue
                action = state.action
                chat_str += action.agent_role + " : " + action.content + "\n"
            return chat_str

        ret_dict = {}
        if "previous_node_summary" in variable_names:
            # Get the summary of the previous node
            if self.trajectory.states[0].node.node_name == node_name:
                ret_dict["previous_node_summary"] = "You are the first node."
            else:
                for idx in range(len(self.trajectory.states)):
                    if self.trajectory.states[idx + 1].node.node_name == node_name:
                        # idx corresponds to the last state of the previous node
                        last_state = self.trajectory.states[idx]
                        if not last_state.node_eval or not last_state.node_eval.summary:
                            # no summary, use role chat
                            ret_dict["previous_node_summary"] = get_role_chat(last_state.node.node_name)
                        else:
                            ret_dict["previous_node_summary"] = last_state.node_eval.summary
                        break

        # Iterate through all states to get the role's output information
        if "role_chat" in variable_names:
            ret_dict["role_chat"] = get_role_chat(node_name)
        return ret_dict

    def get_dict_for_sop_optimizer(self, need_variable_names):
        """
        Generate the dictionary for the SOP optimizer.

        Args:
            need_variable_names (list): The list of variable names required by the SOP optimizer.

        Returns:
            dict: A dictionary containing the required information for the SOP optimizer.
        """

        ret_dict = {}
        if "suggestion" in need_variable_names:
            ret_dict["suggestion"] = self.sop_suggestion.suggestion
        if "run_instance_summary" in need_variable_names:
            # Only the node name and the summary of each node are needed
            ret_str = ""
            for idx, state in enumerate(self.trajectory.states):
                if (idx == len(self.trajectory.states) - 1
                        or state.node.node_name != self.trajectory.states[idx + 1].node.node_name):
                    # Process at the last state of each node
                    ret_str += f"- {state.node.node_name}: {state.node_eval.summary}\n\n"

            ret_dict["run_instance_summary"] = ret_str
        if "run_instance_for_suggestion" in need_variable_names:
            # When needing to get suggestions via prompt, specific information is required
            ret_dict["run_instance_for_suggestion"] = self.sop_suggestion.suggestion
            ret_str = ""
            for idx, state in enumerate(self.trajectory.states):
                ret_str += (
                        state.node.node_name + ": " + state.action.agent_role + ": " + state.action.content + "\n\n"
                )
            ret_dict["run_instance_for_suggestion"] = ret_str
        if "loss_info" in need_variable_names:
            ret_dict["loss_info"] = f"score: {self.loss.score}\nscore_info: {self.loss.score_info}"

        if len(ret_dict) == 0:
            print(
                f"Warning: The passed need_variable_names {need_variable_names} do not contain suggestion, run_instance_summary, or run_instance_for_suggestion."
            )
        return ret_dict

    def to_dict(self):
        """
        Returns a JSON dict representation of the case. It covers all the information of the case.

        Returns:
            dict: A dictionary containing all the information of the case.
        """
        return {
            "case_id": self.case_id,
            "case_name": self.case_name,
            "task_id": self.task_id,
            "task_description": self.task_description,
            "dataset_eval": self.dataset_eval.to_dict(),
            "input": self.input,
            "ground_truth": self.ground_truth,
            "result": self.result,
            "KB_id": self.KB_id,
            "function_ids": self.function_ids,
            "loss": self.loss.to_dict(),
            "sop_suggestion": self.sop_suggestion.to_dict(),
            "trajectory": self.trajectory.to_list(),
        }

    def dump(self, save_path):
        """
        Dumps the case to a JSON file.

        Args:
            save_path (str): The path where the JSON file will be saved.
        """
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)


class CaseLoss:
    """
    The CaseLoss class is used to record the loss information of a case. It functions similarly to a dictionary,
    but is written as a class for convenience.
    """

    def __init__(self, **kwargs):
        """
        Initializes the evaluation results.

        Args:
            **kwargs: Arbitrary keyword arguments for initializing the evaluation results.
        """
        self.prompt = kwargs.get("prompt", "")
        self.response = kwargs.get("response", "")
        self.requirement_for_previous = kwargs.get("requirement_for_previous", "")
        self.score: float = kwargs.get("score", 0)
        self.score_info: str = kwargs.get("score_info", "")

    def update(self, **kwargs):
        """
        Updates the evaluation results.

        Args:
            **kwargs: Arbitrary keyword arguments for updating the evaluation results.
        """
        self.prompt = kwargs.get("prompt", self.prompt)
        self.response = kwargs.get("response", self.response)
        self.requirement_for_previous = kwargs.get("requirement_for_previous", self.requirement_for_previous)
        self.score = float(kwargs.get("score", self.score))
        self.score_info = kwargs.get("score_info", self.score_info)

    def to_dict(self):
        """
        Returns a dictionary representation of the CaseLoss object.

        Returns:
            dict: A dictionary containing the evaluation results.
        """
        return {
            "score": self.score,
            "requirement_for_previous": self.requirement_for_previous,
            "score_info": self.score_info,
            "prompt": self.prompt,
            "response": self.response,
        }


class DatasetEvaluation:
    """
    The DatasetEvaluation class is used to record the evaluation results of a dataset.
    It functions similarly to a dictionary, but is written as a class for convenience.
    """

    def __init__(self, **kwargs):
        """
        Initializes the evaluation results.

        Args:
            **kwargs: Arbitrary keyword arguments for initializing the evaluation results.
        """
        self.score: float = kwargs.get("score", 0)
        self.metric_name: str = kwargs.get("metric_name", "")
        self.metric_description: str = kwargs.get("metric_description", "")
        self.standard_eval_result: dict = kwargs.get("standard_eval_result", {})

    def update(self, **kwargs):
        """
        Updates the evaluation results.

        Args:
            **kwargs: Arbitrary keyword arguments for updating the evaluation results.
        """
        self.score: float = float(kwargs.get("score", self.score))
        self.metric_name: str = kwargs.get("metric_name", self.metric_name)
        self.metric_description: str = kwargs.get(
            "metric_description", self.metric_description
        )
        self.standard_eval_result: dict = kwargs.get(
            "standard_eval_result", self.standard_eval_result
        )

    def to_dict(self):
        """
        Returns a dictionary representation of the DatasetEvaluation object.

        Returns:
            dict: A dictionary containing the evaluation results.
        """
        return {
            "score": self.score,
            "metric_name": self.metric_name,
            "metric_description": self.metric_description,
            "standard_eval_result": self.standard_eval_result,
        }


class SOPSuggestion:
    """
    The SOPSuggestion class is used to record the suggestion information for SOP.
    It functions similarly to a dictionary, but is written as a class for convenience.
    """

    def __init__(self, **kwargs):
        """
        Initializes the SOP suggestion information.

        Args:
            **kwargs: Arbitrary keyword arguments for initializing the SOP suggestion information.
        """
        self.prompt = kwargs.get("prompt", "")
        self.response = kwargs.get("response", "")
        self.suggestion = kwargs.get("suggestion", "")
        self.analyse = kwargs.get("analyse", "")

    def update(self, **kwargs):
        """
        Updates the SOP suggestion information.

        Args:
            **kwargs: Arbitrary keyword arguments for updating the SOP suggestion information.
        """
        self.prompt = kwargs.get("prompt", self.prompt)
        self.response = kwargs.get("response", self.response)
        self.suggestion = kwargs.get("suggestion", self.suggestion)
        self.analyse = kwargs.get("analyse", self.analyse)

    def to_dict(self):
        """
        Returns a dictionary representation of the SOPSuggestion object.

        Returns:
            dict: A dictionary containing the SOP suggestion information.
        """
        return {
            "prompt": self.prompt,
            "response": self.response,
            "suggestion": self.suggestion,
            "analyse": self.analyse,
        }
