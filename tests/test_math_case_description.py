"""Real MATH JSON parsing and Case loss-input mapping, without LLM evaluation.

Uses the repository's existing pandas dependency; no copied parser or fake frame.
"""
import importlib.util

# Keep native pandas/NumPy loaded before patch.dict restores import state.
import pandas
import os
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


def load_modules(source_root):
    root = Path(source_root) / "src" / "agents"
    prefix = "_math_case_contract"
    modules = {}
    for suffix in ("", ".datasets", ".evaluation", ".agents"):
        module = types.ModuleType(prefix + suffix)
        module.__path__ = [str(root / suffix.lstrip("."))]
        modules[module.__name__] = module

    def unused_boundary(*args, **kwargs):
        raise AssertionError("No model calls or nonempty trajectory loading allowed")

    llm = types.ModuleType(prefix + ".agents.llm")
    llm.completion_with_backoff = unused_boundary
    modules[llm.__name__] = llm
    state = types.ModuleType(prefix + ".evaluation.state")
    state.State = type("UnusedState", (), {"load_from_json": staticmethod(unused_boundary)})
    modules[state.__name__] = state
    loaded = {}
    with patch.dict(sys.modules, modules):
        for relative in ("datasets/base", "datasets/math", "evaluation/trajectory", "evaluation/case"):
            name = prefix + "." + relative.replace("/", ".")
            spec = importlib.util.spec_from_file_location(name, root / (relative + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[relative] = module
    return loaded["datasets/math"], loaded["evaluation/case"].Case


class MathCaseDescriptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.math_module, cls.case_type = load_modules(root)

    def setUp(self):
        random_state = self.math_module.random.getstate()
        self.addCleanup(self.math_module.random.setstate, random_state)
        self.storage = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage.cleanup)
        for split in ("train", "test"):
            directory = Path(self.storage.name) / "math" / split / "algebra"
            directory.mkdir(parents=True)
            for fixture in (Path(__file__).parent / "fixtures" / "math_case_description").glob("*.json"):
                shutil.copyfile(fixture, directory / fixture.name)
        source_patch = patch.object(self.math_module, "DATA_PATH", self.storage.name)
        source_patch.start()
        self.addCleanup(source_patch.stop)

    def test_each_case_description_matches_its_loaded_problem(self):
        for split in ("train", "test"):
            dataset = self.math_module.MATHDataset(split=split, math_type="algebra")
            for idx in range(len(dataset)):
                with self.subTest(split=split, idx=idx):
                    case = self.case_type(dataset.get_case_dict(idx))
                    self.assertEqual(case.task_description, dataset[idx])

    def test_loss_input_and_saved_case_keep_the_actual_problem(self):
        dataset = self.math_module.MATHDataset(math_type="algebra")
        case = self.case_type(dataset.get_case_dict(0))
        loss_input = case.get_dict_for_loss_calculation(["task_description", "ground_truth"])
        self.assertEqual(loss_input["task_description"], dataset[0])
        self.assertEqual(loss_input["ground_truth"], dataset.data[0]["solution"])
        restored = self.case_type(case.to_dict())
        self.assertEqual(restored.task_description, dataset[0])

    def test_existing_filter_input_solution_and_indices_are_unchanged(self):
        dataset = self.math_module.MATHDataset(math_type="algebra")
        self.assertEqual(len(dataset), 2)
        self.assertEqual({row["level"] for row in dataset.data}, {"Level 5"})
        self.assertEqual({row["type"] for row in dataset.data}, {"Algebra"})
        for idx, row in enumerate(dataset.data):
            case = dataset.get_case_dict(idx)
            self.assertEqual(case["idx"], idx)
            self.assertEqual(case["input"], {"input_data": {"problem": row["problem"]}})
            self.assertEqual(case["ground_truth"], row["solution"])
            self.assertEqual(case["metric_name"], "score")


if __name__ == "__main__":
    unittest.main()
