"""Offline regression against real dataset modules, without agent/SDK imports.

AGENTS_SOURCE_ROOT selects a repository root containing src/agents. The only
substitute is the unused LLM boundary; calling it fails immediately.
"""
import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


def load_dataset_module(source_root):
    root = Path(source_root) / "src" / "agents"
    prefix = "_creative_split_regression"
    packages = {
        prefix: root,
        prefix + ".datasets": root / "datasets",
        prefix + ".agents": root / "agents",
    }
    modules = {}
    for name, path in packages.items():
        package = types.ModuleType(name)
        package.__path__ = [str(path)]
        modules[name] = package
    llm = types.ModuleType(prefix + ".agents.llm")

    def no_llm(*args, **kwargs):
        raise AssertionError("This dataset regression must not call an LLM")

    llm.completion_with_backoff = no_llm
    modules[llm.__name__] = llm
    with patch.dict(sys.modules, modules):
        for filename in ("base", "creative_writing"):
            name = prefix + ".datasets." + filename
            spec = importlib.util.spec_from_file_location(
                name, root / "datasets" / (filename + ".py")
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        return module


class CreativeWritingSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_root = os.environ.get("AGENTS_SOURCE_ROOT")
        if source_root is None:
            source_root = Path(__file__).resolve().parents[1]
        cls.dataset = load_dataset_module(source_root).CreativeWritingDataset

    def test_training_case_identity_matches_original_file_row(self):
        complete = self.dataset(split="all")
        train = self.dataset(split="train")
        self.assertEqual(len(complete), 100)
        self.assertEqual(len(train), 20)
        for idx in range(len(train)):
            with self.subTest(idx=idx):
                self.assertEqual(train[idx], complete[idx])
                case = train.get_case_dict(idx)
                self.assertEqual(case["case_id"], "creative_writing_" + str(idx))
                self.assertEqual(case, complete.get_case_dict(idx))

    def test_train_and_test_ids_partition_the_complete_dataset(self):
        complete = self.dataset(split="all")
        train = self.dataset(split="train")
        test = self.dataset(split="test")
        train_ids = {train.get_case_dict(i)["case_id"] for i in range(len(train))}
        test_ids = {test.get_case_dict(i)["case_id"] for i in range(len(test))}
        all_ids = {complete.get_case_dict(i)["case_id"] for i in range(len(complete))}
        self.assertEqual(train_ids & test_ids, set())
        self.assertEqual(train_ids | test_ids, all_ids)

    def test_test_and_explicit_range_keep_original_row_identity(self):
        complete = self.dataset(split="all")
        test = self.dataset(split="test")
        subset = self.dataset(split="all", range_idx=[23, 25])
        self.assertEqual(len(test), 80)
        self.assertEqual(len(subset), 2)
        for idx in range(len(test)):
            case = test.get_case_dict(idx)
            self.assertEqual(case["case_id"], complete.get_case_dict(20 + idx)["case_id"])
            self.assertEqual(case["input"], complete.get_case_dict(20 + idx)["input"])
            self.assertEqual(case["idx"], idx)
        for idx in range(len(subset)):
            case = subset.get_case_dict(idx)
            self.assertEqual(case["case_name"], complete.get_case_dict(23 + idx)["case_name"])
            self.assertEqual(case["input"], complete.get_case_dict(23 + idx)["input"])


if __name__ == "__main__":
    unittest.main()
