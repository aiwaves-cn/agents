"""Full real formatter and existing configuration; no agent/model execution."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


def load_formatter(source_root):
    root = Path(source_root) / "src" / "agents"
    modules = {}
    for name in ("agents", "agents.evaluation", "agents.task"):
        package = types.ModuleType(name)
        package.__path__ = []
        modules[name] = package

    class UnusedRuntime:
        def __init__(self, *args, **kwargs):
            raise AssertionError("No State/Case/Node/SOP runtime is needed")

    modules["agents"].SOP = UnusedRuntime
    modules["agents"].DEFAULT_NODE_PROMPT_TEMPLATES = {}
    for name, attribute in (("agents.evaluation.state", "State"),
                            ("agents.evaluation.case", "Case"), ("agents.task.node", "Node")):
        module = types.ModuleType(name)
        setattr(module, attribute, UnusedRuntime)
        modules[name] = module
    path = root / "optimization" / "prompt_formatter.py"
    with patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location("_prompt_variable_selection", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class PromptVariableSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.formatter = load_formatter(root)

    def existing_config(self):
        fixture = (Path(__file__).resolve().parents[1] / "examples" /
                   "creative_writing" / "configs" / "optimizer_config.json")
        return json.loads(fixture.read_text(encoding="utf-8"))["prompt_optimizer"]["meta_prompt"]["optimization"]

    def test_explicit_empty_selection_does_not_require_order(self):
        self.assertEqual(self.formatter.get_config_needed_variables(
            {"unused": "{result}"}, specific_key_list=[]), [])

    def test_explicit_empty_selection_does_not_fall_back_to_existing_templates(self):
        config = self.existing_config()
        self.assertTrue(self.formatter.get_config_needed_variables(config))
        self.assertEqual(self.formatter.get_config_needed_variables(config, specific_key_list=[]), [])

    def test_omitted_or_none_selection_still_uses_order(self):
        config = {"order": ["first", "second"], "first": "{result}", "second": "{score}"}
        self.assertEqual(set(self.formatter.get_config_needed_variables(config)), {"result", "score"})
        self.assertEqual(set(self.formatter.get_config_needed_variables(config, None)), {"result", "score"})

    def test_nonempty_selection_still_limits_variables_without_order(self):
        config = {"first": "{result}", "second": "{score}"}
        self.assertEqual(self.formatter.get_config_needed_variables(config, ["second"]), ["score"])

    def test_unselected_default_without_order_still_raises(self):
        with self.assertRaises(AssertionError):
            self.formatter.get_config_needed_variables({"first": "{result}"})

    def test_existing_regular_and_loop_template_rendering_is_unchanged(self):
        config = {"order": ["title", "row"], "loop": ["row"],
                  "title": "{task_description}\n", "row": "{index}:{result}\n"}
        data = {"task_description": "任务", "loop_data": [
            {"index": 1, "result": "甲"}, {"index": 2, "result": "乙"}]}
        self.assertEqual(self.formatter.formulate_prompt(config, data), "任务\n1:甲\n2:乙\n")


if __name__ == "__main__":
    unittest.main()
