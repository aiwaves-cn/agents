import os
import pandas as pd
from typing import Any, Dict, List
import time
import random
from .base import BaseDataset, DATA_PATH
from ..agents.llm import completion_with_backoff


def get_content_between_a_b(start_tag, end_tag, text):
    extracted_text = ""
    start_index = text.find(start_tag)
    while start_index != -1:
        end_index = text.find(end_tag, start_index + len(start_tag))
        if end_index != -1:
            extracted_text += text[start_index + len(start_tag): end_index] + " "
            start_index = text.find(start_tag, end_index + len(end_tag))
        else:
            break

    return extracted_text.strip()


def extract(text, type):
    target_str = get_content_between_a_b(f"<{type}>", f"</{type}>", text)
    return target_str


class MATHDataset(BaseDataset):
    def __init__(self, split: str = "test", math_type=None):
        """
        Initializes a dataset instance for MATH problems, loading data from the specified directory structure.

        Args:
            split (str): The dataset split, typically 'train', or 'test'.
        """
        self.split = split
        if math_type:
            root_dir = os.path.join(DATA_PATH, "math", split, math_type)
        else:
            root_dir = os.path.join(DATA_PATH, "math", split)
        data = self._load_data(root_dir)
        if split == "train":
            random.seed(666)
            random.shuffle(data)
        super().__init__(data)

        self.metric_name = "score"
        self.metric_description = "The score is 1 if the answer is correct, and 0 otherwise."

    def _load_data(self, root_dir: str) -> List[Dict[str, Any]]:
        """
        Loads data from all files in the given directory that match the expected format.

        Args:
            root_dir (str): The root directory from which to load data files.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a math problem.
        """
        data = []
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".json") or file.endswith(".jsonl"):
                    data_file = os.path.join(root, file)
                    data_point = self.load(data_file)
                    data.extend(
                        data_point if isinstance(data_point, list) else [data_point]
                    )

        df = pd.DataFrame(data)
        df.drop(df[df["type"] == "Geometry"].index, inplace=True)
        return df[df["level"] == "Level 5"].to_dict("records")

    def __getitem__(self, idx: int) -> str:
        """
        Retrieve a math problem by its index.

        Args:
        idx (int): The index of the math problem.

        Returns:
        str: The math problem text.
        """
        return self.data[idx]["problem"]

    def get_case_dict(self, idx: int) -> dict:
        """
        Create a dictionary representing a case at a specific index.

        Args:
            idx (int): The index of the case.

        Returns:
            Dict[str, Any]: A dictionary with case details.
        """
        return {
            "case_id": "math_" + self.split + "_" + str(idx),
            "case_name": "math_" + self.split + "_" + str(idx),
            "task_id": "math",
            "task_description": "A team of mathematicians must work together to solve a combinatorial geometry problem involving the placement of sea shells at the points of a star drawn in the sand. The challenge is to determine the number of distinct ways to place the shells, considering that arrangements can be equivalent under rotations and reflections. The problem exemplifies the application of symmetry in combinatorial problems and requires collaborative effort to reach the solution.",
            "function_ids": "no use now",
            "KB_id": "no use now",
            "input": {"input_data": {"problem": self.data[idx]["problem"]}},
            "ground_truth": self.data[idx]["solution"],
            "idx": idx,
            "metric_name": self.metric_name,
            "metric_description": self.metric_description,
        }

    def evaluate(self, idx: int, answer: str):
        problem = self.data[idx]["problem"]
        solution = self.data[idx]["solution"]
        prompt = f"""
You are the wise mathematics answer verifier:
You identify as math word problem answer verifier, not an assistant.
You will be provided an math word problem, the real answer for this math word problem, and the predicted answer from a generation model. You should understand the problem and validate the correctness of the generated answer in the context of the provided math word problem and the real answer.
You should not solve the problem by yourself, you only job is to act as a verifier.

On your profile and general capabilities:
Your responses should avoid being vague, controversial or off-topic.
Your logic and reasoning should be rigorous and intelligent.

The problem: {problem}

The standard solution: {solution}

The output of generation model: {answer}

Now, please give your verdict(You should first show your thinking of your verification logic and then output your final verdict,You final verdict is limited to correct or incorrect,and wrapped into the <verdict></verdict>, such as <verdict>correct</verdict>):
"""

        messages = [{"role": "user", "content": prompt}]
        flag = True
        cnt = 0
        while flag and cnt < 20:
            try:
                result_outputs = (
                    completion_with_backoff(
                        messages=messages, model="gpt-4-turbo-2024-04-09"
                    )
                    .choices[0]
                    .message.content
                )
                verdict = extract(result_outputs, "verdict")
                flag = False
            except Exception as e:
                print(e)
                time.sleep(10)
                cnt += 1

        if verdict == "correct":
            return 1, {"score": 1}
        else:
            return 0, {"score": 0}

    def mertirc(self, gold, pred, trace=None):
        problem = gold.problem
        solution = gold.solution
        answer = pred.answer
        prompt = f"""
You are the wise mathematics answer verifier:
You identify as math word problem answer verifier, not an assistant.
You will be provided an math word problem, the real answer for this math word problem, and the predicted answer from a generation model. You should understand the problem and validate the correctness of the generated answer in the context of the provided math word problem and the real answer.
You should not solve the problem by yourself, you only job is to act as a verifier.

On your profile and general capabilities:
Your responses should avoid being vague, controversial or off-topic.
Your logic and reasoning should be rigorous and intelligent.

The problem: {problem}

The standard solution: {solution}

The output of generation model: {answer}

Now, please give your verdict(You should first show your thinking of your verification logic and then output your final verdict,You final verdict is limited to correct or incorrect,and wrapped into the <verdict></verdict>, such as <verdict>correct</verdict>):
"""

        messages = [{"role": "user", "content": prompt}]
        flag = True
        cnt = 0
        while flag and cnt < 20:
            try:
                result_outputs = (
                    completion_with_backoff(
                        messages=messages, model="gpt-4-turbo-2024-04-09"
                    )
                    .choices[0]
                    .message.content
                )
                verdict = extract(result_outputs, "verdict")
                flag = False
            except Exception as e:
                print(e)
                time.sleep(10)
                cnt += 1

        if verdict == "correct":
            return 1
        else:
            return 0
