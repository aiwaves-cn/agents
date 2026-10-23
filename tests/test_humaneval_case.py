"""Exercise real JSONL -> dataset -> Case conversion without running code or LLMs."""
import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


def load_modules(source_root):
    root = Path(source_root) / "src" / "agents"
    prefix = "_humaneval_case_regression"
    modules = {}
    for suffix in ("", ".datasets", ".evaluation", ".utils"):
        module = types.ModuleType(prefix + suffix)
        module.__path__ = [str(root / suffix.lstrip("."))]
        modules[module.__name__] = module

    def unused_boundary(*args, **kwargs):
        raise AssertionError("No code execution, score estimation or progress UI allowed")

    # These collaborators are irrelevant to parsing and must never be invoked.
    numpy = types.ModuleType("numpy")
    numpy.ndarray = type("UnusedArray", (), {})
    tqdm = types.ModuleType("tqdm")
    tqdm.tqdm = unused_boundary
    modules.update(numpy=numpy, tqdm=tqdm)
    execution = types.ModuleType(prefix + ".utils.execution")
    for name in ("time_limit", "swallow_io", "create_tempdir", "reliability_guard"):
        setattr(execution, name, unused_boundary)
    modules[execution.__name__] = execution
    state = types.ModuleType(prefix + ".evaluation.state")
    state.State = type("UnusedState", (), {"load_from_json": staticmethod(unused_boundary)})
    modules[state.__name__] = state

    loaded = {}
    with patch.dict(sys.modules, modules):
        for relative in ("datasets/base", "datasets/humaneval", "evaluation/trajectory", "evaluation/case"):
            name = prefix + "." + relative.replace("/", ".")
            spec = importlib.util.spec_from_file_location(name, root / (relative + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[relative] = module
    return loaded["datasets/humaneval"].HumanEvalDataset, loaded["evaluation/case"].Case


class HumanEvalCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.dataset_type, cls.case_type = load_modules(root)

    def test_real_dataset_rows_can_be_parsed_as_training_cases(self):
        dataset = self.dataset_type()
        for idx in (0, len(dataset) // 2, len(dataset) - 1):
            with self.subTest(idx=idx):
                case = self.case_type(dataset.get_case_dict(idx))
                self.assertEqual(case.task_description, dataset[idx])
                self.assertEqual(case.case_id, dataset.data[idx]["task_id"])
                self.assertEqual(case.ground_truth, dataset.data[idx]["canonical_solution"])
                self.assertEqual(case.trajectory.states, [])

    def test_description_is_retained_in_saved_case_representation(self):
        dataset = self.dataset_type()
        case = self.case_type(dataset.get_case_dict(0))
        saved = case.to_dict()
        restored = self.case_type(saved)
        self.assertEqual(saved["task_description"], dataset.data[0]["prompt"])
        self.assertEqual(restored.task_description, case.task_description)
        self.assertEqual(restored.input, case.input)

    def test_dataset_inputs_answers_and_local_indices_are_preserved(self):
        dataset = self.dataset_type()
        self.assertGreater(len(dataset), 1)
        for idx in (0, len(dataset) - 1):
            with self.subTest(idx=idx):
                row = dataset.data[idx]
                result = dataset.get_case_dict(idx)
                self.assertEqual(dataset[idx], row["prompt"])
                self.assertEqual(result["idx"], idx)
                self.assertEqual(result["input"], {"input_data": {"prompt": row["prompt"]}})
                self.assertEqual(result["ground_truth"], row["canonical_solution"])
                self.assertEqual(result["metric_name"], "passed")


if __name__ == "__main__":
    unittest.main()
