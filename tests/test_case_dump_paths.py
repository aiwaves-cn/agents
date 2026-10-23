"""Real Case.dump and JSON round trips on a temporary local filesystem."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


def load_case(source_root):
    directory = Path(source_root) / "src" / "agents" / "evaluation"
    prefix = "_case_dump_regression"
    package = types.ModuleType(prefix)
    package.__path__ = [str(directory)]
    state = types.ModuleType(prefix + ".state")

    def no_state_loading(*args, **kwargs):
        raise AssertionError("This serialization regression uses an empty trajectory")

    state.State = type("UnusedState", (), {"load_from_json": staticmethod(no_state_loading)})
    with patch.dict(sys.modules, {prefix: package, state.__name__: state}):
        for filename in ("trajectory", "case"):
            name = prefix + "." + filename
            spec = importlib.util.spec_from_file_location(name, directory / (filename + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
    return module.Case


class CaseDumpPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.case_type = load_case(root)

    def setUp(self):
        storage = tempfile.TemporaryDirectory()
        self.addCleanup(storage.cleanup)
        self.directory = Path(storage.name).resolve()
        previous_cwd = os.getcwd()
        os.chdir(self.directory)
        self.addCleanup(os.chdir, previous_cwd)
        self.case = self.case_type({
            "case_id": "case_01",
            "case_name": "往返样本",
            "task_id": "serialization",
            "task_description": "保存并读取同一个样本",
            "function_ids": "unused",
            "KB_id": "unused",
            "input": {"input_data": {"question": "π 与 UTF-8"}},
            "ground_truth": {"answer": "保留内容"},
            "result": {"answer": "保留内容", "items": [1, False, None]},
            "dataset_eval": {"score": 0.75, "metric_name": "score"},
            "loss": {"score": 0.25, "score_info": "记录"},
        })

    def check_round_trip(self, path):
        expected = self.case.to_dict()
        result = self.case.dump(path)
        self.assertIsNone(result)
        with open(path, encoding="utf-8") as stream:
            self.assertEqual(json.load(stream), expected)
        text = Path(path).read_text(encoding="utf-8")
        self.assertEqual(text, json.dumps(expected, ensure_ascii=False, indent=4))
        self.assertIn("往返样本", text)
        restored = self.case_type.read_single_from_json(path)
        self.assertEqual(restored.to_dict(), expected)

    def test_plain_relative_filename(self):
        self.check_round_trip("case.json")

    def test_plain_relative_path_object(self):
        self.check_round_trip(Path("case.json"))

    def test_explicit_current_directory(self):
        self.check_round_trip("./case.json")

    def test_nested_relative_path_creates_parents(self):
        self.check_round_trip(Path("nested") / "子目录" / "case.json")

    def test_absolute_path_creates_parents(self):
        self.check_round_trip(self.directory / "absolute" / "nested" / "case.json")


if __name__ == "__main__":
    unittest.main()
