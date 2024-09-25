import os
import re
import string
from collections import Counter

from .base import BaseDataset, DATA_PATH


def normalize_answer(s):
    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def f1_score(prediction, ground_truth):
    normalized_prediction = normalize_answer(prediction)
    normalized_ground_truth = normalize_answer(ground_truth)

    ZERO_METRIC = (0, 0, 0)

    if (
        normalized_prediction in ["yes", "no", "noanswer"]
        and normalized_prediction != normalized_ground_truth
    ):
        return ZERO_METRIC
    if (
        normalized_ground_truth in ["yes", "no", "noanswer"]
        and normalized_prediction != normalized_ground_truth
    ):
        return ZERO_METRIC

    prediction_tokens = normalized_prediction.split()
    ground_truth_tokens = normalized_ground_truth.split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return ZERO_METRIC
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1, precision, recall


class HotpotQADataset(BaseDataset):
    def __init__(self, split: str = "train"):
        data_file = os.path.join(DATA_PATH, "hotpotqa", f"{split}.json")
        data = self.load(data_file)
        super().__init__(data)
        self.split = split

        self.metric_name = "f1"
        self.metric_description = "The F1 score ranges from 0 to 1, where 1 indicates perfect precision and recall, and 0 indicates the worst performance."

    def __getitem__(self, idx: int) -> str:
        """
        Retrieve a question by its index.

        Args:
        idx (int): The index of the question.

        Returns:
        str: The question text.
        """
        return self.data[idx]["question"]

    def get_case_dict(self, idx: int):
        """
        Create a dictionary representing a case at a specific index, including the ground truth if available.

        Args:
        idx (int): The index of the case.

        Returns:
        Dict[str, Any]: A dictionary with case details.
        """
        return {
            "case_id": "hotpotqa_" + self.split + "_" + str(idx),
            "case_name": "hotpotqa_" + self.split + "_" + str(idx),
            "task_id": "hotpotqa",
            "function_ids": "no use now",
            "KB_id": "no use now",
            "input": {"input_data": {"question": self.data[idx]["question"]}},
            "ground_truth": self.data[idx].get("answer", None),
            "idx": idx,
            "metric_name": self.metric_name,
            "metric_description": self.metric_description,
            "task_description": "Answer the question based on the provided context."
        }

    def evaluate(self, idx: int, answer: str):
        """
        Evaluate the provided answer for a given index against the ground truth.

        Args:
        idx (int): The index of the question being evaluated.
        answer (str): The answer provided by a model or user.

        Returns:
        Tuple[bool, Dict[str, Any]]: A tuple containing a boolean exact match result and a dictionary with evaluation details.
        """
        pred = normalize_answer(answer)
        gt = normalize_answer(self.data[idx]["answer"])
        em = pred == gt
        f1 = f1_score(pred, gt)[0]
        return em, {"em": em, "f1": f1, "gt": gt, "pred": pred}
