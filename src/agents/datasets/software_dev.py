import os
import time

from .base import BaseDataset, DATA_PATH
from ..agents.llm import completion_with_backoff
from ..utils.text import *

SOFTWARE_DEV_FILE = "SoftwareDev.jsonl"


class SoftwareDevDataset(BaseDataset):
    def __init__(self):
        data_file = os.path.join(DATA_PATH, "software_dev", SOFTWARE_DEV_FILE)
        data = self.load(data_file)
        super().__init__(data[:7])

        self.metric_name = "Executability Metric"
        self.metric_description = "Executability Metric is automatically scored by GPT-4 ranging from '1' to '4'. A score of '1' signifies complete failure, '2' denotes executable code, '3' represents largely satisfying expected workflow, and '4' indicates a perfect match with expectations."

    def __getitem__(self, idx: int) -> str:
        """
        Retrieve a question by its index.

        Args:
        idx (int): The index of the question.

        Returns:
        str: The question text.
        """
        return self.data[idx]["prompt"]

    def get_case_dict(self, idx: int):
        """
        Create a dictionary representing a case at a specific index, including the ground truth if available.

        Args:
        idx (int): The index of the case.

        Returns:
        Dict[str, Any]: A dictionary with case details.
        """
        try:
            return {
                "case_id": "software_dev_" + str(self.data[idx]["task_id"]),
                "case_name": self.data[idx]["task_name"],
                "task_id": "software_dev",
                "task_description": self.data[idx]["task_description"] if "task_description" in self.data[idx] else self.data[idx]["prompt"],
                "function_ids": "no use now",
                "KB_id": "no use now",
                "input": {"input_data": {"prompt": self.data[idx]["prompt"]}},
                "ground_truth": self.data[idx].get("answer", None),
                "idx": idx,
                "metric_name": self.metric_name,
                "metric_description": self.metric_description,
            }
        except Exception as e:
            print(f"Error: {e}, {self.data[idx]}")
            raise e

    def evaluate(self, idx: int, answer: str):
        """
        Evaluate the executability metric of the project code.
        Args:
        answer (str): The model-generated output for the text at the given index.
        kwargs: Additional keyword arguments, (like index) which are not used in this method.

        Returns:
        Dict[str, Any]: A dictionary containing evaluation results.
        """

        task = self.data[idx]["prompt"]

        prompt = f"""

Analyze the following project code, output the  in the format of <score>s</score>, where s is an integer ranging from 1 to 4. A score of 1 signifies complete failure, 2 denotes executable code, 3 represents largely satisfying expected workflow, and 4 indicates a perfect match with expectations.
{answer}
"""
        messages = [{"role": "user", "content": prompt}]
        cnt = 0
        while cnt < 3:
            try:
                score_outputs = completion_with_backoff(
                    messages=messages,
                    n=5,
                    model="gpt-4-turbo-2024-04-09",
                    api_key="",
                    base_url="",
                )
                scores = []
                for score_output in score_outputs.choices:
                    score_output = score_output.message.content
                    score = extract(score_output, "score")
                    if score:
                        scores.append(int(score))
                    else:
                        print(f"Error matching score output: {score_output}")
                break
            except:
                time.sleep(10)
                cnt += 1
        return sum(scores) / len(scores), {
            "Executability Metric": sum(scores) / len(scores) if scores else 0,
        }
