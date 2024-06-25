import os
import json
import itertools
import multiprocessing
import numpy as np
from tqdm import tqdm
from typing import List, Dict, Union, Optional
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import BaseDataset, DATA_PATH
from ..utils.execution import time_limit, swallow_io, create_tempdir, reliability_guard

HUMAN_EVAL_FILE = "HumanEval.jsonl"


def get_content_between_a_b(start_tag, end_tag, text):
    extracted_text = ""
    start_index = text.find(start_tag)
    while start_index != -1:
        end_index = text.find(end_tag, start_index + len(start_tag))
        if end_index != -1:
            extracted_text += text[start_index + len(start_tag) : end_index] + " "
            start_index = text.find(start_tag, end_index + len(end_tag))
        else:
            break

    return extracted_text


def estimate_pass_at_k(
    num_samples: Union[int, List[int], np.ndarray],
    num_correct: Union[List[int], np.ndarray],
    k: int,
) -> np.ndarray:
    """
    Estimates pass@k of each problem and returns them in an array.
    """

    def estimator(n: int, c: int, k: int) -> float:
        """
        Calculates 1 - comb(n - c, k) / comb(n, k).
        """
        if n - c < k:
            return 1.0
        return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

    if isinstance(num_samples, int):
        num_samples_it = itertools.repeat(num_samples, len(num_correct))
    else:
        assert len(num_samples) == len(num_correct)
        num_samples_it = iter(num_samples)

    return np.array(
        [estimator(int(n), int(c), k) for n, c in zip(num_samples_it, num_correct)]
    )


def check_correctness(
    problem: Dict, completion: str, timeout: float, completion_id: Optional[int] = None
) -> Dict:
    """
    Evaluates the functional correctness of a completion by running the test
    suite provided in the problem.

    :param completion_id: an optional completion ID so we can match
        the results later even if execution finishes asynchronously.
    """

    def unsafe_execute():

        with create_tempdir():

            # These system calls are needed when cleaning up tempdir.
            import os
            import shutil

            rmtree = shutil.rmtree
            rmdir = os.rmdir
            chdir = os.chdir

            # Disable functionalities that can make destructive changes to the test.
            reliability_guard()

            # Construct the check program and run it.
            check_program = (
                problem["prompt"]
                + completion
                + "\n"
                + problem["test"]
                + "\n"
                + f"check({problem['entry_point']})"
            )

            try:
                exec_globals = {}
                with swallow_io():
                    with time_limit(timeout):
                        exec(check_program, exec_globals)
                result.append("passed")
            except BaseException as e:
                result.append(f"failed: {e}")

            # Needed for cleaning up.
            shutil.rmtree = rmtree
            os.rmdir = rmdir
            os.chdir = chdir

    manager = multiprocessing.Manager()
    result = manager.list()

    p = multiprocessing.Process(target=unsafe_execute)
    p.start()
    p.join(timeout=timeout + 1)
    if p.is_alive():
        p.kill()

    if not result:
        result.append("timed out")

    return dict(
        task_id=problem["task_id"],
        passed=result[0] == "passed",
        result=result[0],
        completion_id=completion_id,
    )


class HumanEvalDataset(BaseDataset):

    def __init__(self):
        """
        Initializes a dataset instance for HumanEval, loading data from a JSON file specified in the configuration.
        """
        data_file = os.path.join(DATA_PATH, "humaneval", HUMAN_EVAL_FILE)
        data = self.load(data_file)
        super().__init__(data)

        self.metric_name = "passed"
        self.metric_description = "The score to indicate whether the completion passed the test suite, where 1 indicates the completion passed the test suite, and 0 indicates the completion failed the test suite."

    def __getitem__(self, idx: int) -> str:
        """
        Retrieve a programming prompt by its index.

        Args:
            idx (int): The index of the prompt.

        Returns:
            str: The prompt text.
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
        return {
            "case_id": self.data[idx]["task_id"],
            "case_name": self.data[idx]["task_id"],
            "task_id": "humaneval",
            "function_ids": "no use now",
            "KB_id": "no use now",
            "input": {
                "input_data": {
                    "prompt": self.data[idx]["prompt"],
                },
            },
            "ground_truth": self.data[idx]["canonical_solution"],
            "idx": idx,
            "metric_name": self.metric_name,
            "metric_description": self.metric_description,
        }

    def to_dict(self):
        """
        Convert the dataset to a dictionary using task IDs as keys.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary mapping task IDs to their corresponding data points.
        """
        return {data_point["task_id"]: data_point for data_point in self.data}

    def evaluate(self, idx: int, answer: str) -> Dict:
        """
        Evaluate the correctness of a completion against the ground truth.

        Args:
            idx (int): The index of the case.
            answer (str): The completion to evaluate.

        Returns:
            Dict: A dictionary containing the evaluation results.
        """
        problem = self.data[idx]
        result = check_correctness(problem, answer, timeout=3.0)
        return result, {
            "passed": 1 if result["passed"] else 0,
        }

    def overall_evaluate(
        self,
        sample_file: str,
        k: List[int] = [1, 10, 100],
        n_workers: int = 4,
        timeout: float = 3.0,
    ):
        with open(sample_file, "r", encoding="utf-8") as f:
            sample_data = [json.loads(line) for line in f]

        problems = self.to_dict()

        # Check the generated samples against test suites.
        with ThreadPoolExecutor(max_workers=n_workers) as executor:

            futures = []
            completion_id = Counter()
            n_samples = 0
            results = defaultdict(list)

            print("Reading samples...")
            for sample in tqdm(sample_data):
                task_id = sample["task_id"]
                if "```python" in sample["completion"]:
                    completion = get_content_between_a_b(
                        "```python", "```", sample["completion"]
                    )
                else:
                    completion = sample["completion"]
                args = (problems[task_id], completion, timeout, completion_id[task_id])
                future = executor.submit(check_correctness, *args)
                futures.append(future)
                completion_id[task_id] += 1
                n_samples += 1

            assert len(completion_id) == len(
                problems
            ), "Some problems are not attempted."

            print("Running test suites...")
            for future in tqdm(as_completed(futures), total=len(futures)):
                result = future.result()
                results[result["task_id"]].append((result["completion_id"], result))

        # Calculate pass@k.
        total, correct = [], []
        for result in results.values():
            result.sort()
            passed = [r[1]["passed"] for r in result]
            total.append(len(passed))
            correct.append(sum(passed))
        total = np.array(total)
        correct = np.array(correct)

        ks = k
        pass_at_k = {
            f"pass@{k}": estimate_pass_at_k(total, correct, k).mean()
            for k in ks
            if (total >= k).all()
        }
        print(f"Pass@{ks}: {pass_at_k}")

        # Finally, save the results in one file:
        def combine_results():
            for sample in sample_data:
                task_id = sample["task_id"]
                result = results[task_id].pop(0)
                sample["result"] = result[1]["result"]
                sample["passed"] = result[1]["passed"]
                yield sample

        out_file = sample_file + "_results.jsonl"
        print(f"Writing results to {out_file}...")

        with open(out_file, "w", encoding="utf-8") as fp:
            for x in tqdm(combine_results(), total=n_samples):
                fp.write((json.dumps(x) + "\n"))

        return pass_at_k
