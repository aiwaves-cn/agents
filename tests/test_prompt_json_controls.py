"""Actual OptimUtils -> PromptOptimizer -> prompt_formatter parsing contract.

Only unused SDK/runtime imports are isolated. No parsing, escaping, variable
validation, logger, provider, or filesystem operation is replaced in the tests.
"""
import importlib.util
import io
import json
import logging
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


def load_components():
    root = Path(os.environ.get(
        "AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1])
    )) / "src/agents"
    modules = {}
    for name in ("agents", "agents.optimization", "agents.evaluation", "agents.task", "agents.utils", "agents.agents"):
        module = types.ModuleType(name)
        module.__path__ = [str(root / name.removeprefix("agents").lstrip(".").replace(".", "/"))]
        modules[name] = module

    class RuntimeBoundary:
        def __init__(self, *args, **kwargs):
            raise AssertionError("Unused SDK/runtime construction is forbidden")

    for name, attributes in {
        "agents.evaluation.case": ("Case",),
        "agents.evaluation.state": ("State",),
        "agents.task.sop": ("SOP",),
        "agents.task.node": ("Node",),
        "agents.task.solution": ("Solution", "SolutionConfig"),
        "agents.agents.llm": ("LLMConfig", "OpenAILLM"),
        "agents.optimization.optimizer": ("Optimizer", "OptimizerConfig"),
    }.items():
        module = types.ModuleType(name)
        for attribute in attributes:
            setattr(module, attribute, RuntimeBoundary)
        modules[name] = module
    modules["agents"].SOP = RuntimeBoundary
    modules["agents"].OpenAILLM = RuntimeBoundary
    modules["agents"].DEFAULT_NODE_PROMPT_TEMPLATES = {}
    modules["agents.evaluation"].Case = RuntimeBoundary
    prompts = types.ModuleType("agents.utils.prompts")
    prompts.DEFAULT_NODE_PROMPT_TEMPLATES = {}
    modules[prompts.__name__] = prompts
    loaded = {}
    with patch.dict(sys.modules, modules):
        for filename in ("prompt_formatter", "utils", "prompt_optimizer"):
            name = "agents.optimization." + filename
            spec = importlib.util.spec_from_file_location(
                name, root / "optimization" / (filename + ".py")
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            setattr(modules["agents.optimization"], filename, module)
            loaded[filename] = module
    return loaded


class PromptJsonControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.components = load_components()

    def setUp(self):
        self.utils = self.components["utils"].OptimUtils
        self.optimizer = self.components["prompt_optimizer"].PromptOptimizer
        self.log = io.StringIO()
        self.logger = logging.Logger("prompt-json-controls")
        self.logger.addHandler(logging.StreamHandler(self.log))

    def check_prompt(self, raw, old):
        return self.optimizer.check_if_new_prompt_legal(raw, old, logger=self.logger)

    def test_all_json_control_characters_preserve_string_content(self):
        for value in range(32):
            with self.subTest(codepoint=value):
                content = "before" + chr(value) + "after"
                raw = '{"TASK": "' + content + '"}'
                fixed = self.utils.escape_special_chars_in_json_string(raw)
                self.assertEqual(json.loads(fixed), {"TASK": content})

    def test_real_prompt_validation_accepts_repaired_controls_and_variables(self):
        old = {"TASK": "Original instruction for {name}"}
        for value in (0, 11, 31):
            with self.subTest(codepoint=value):
                content = "Updated" + chr(value) + " instruction for {name}"
                raw = '{"TASK": "' + content + '"}'
                legal, new_prompt, original = self.check_prompt(raw, old)
                self.assertTrue(legal)
                self.assertEqual(new_prompt, {"TASK": content})
                self.assertEqual(original, old)
                self.assertEqual(old, {"TASK": "Original instruction for {name}"})

    def test_existing_named_controls_remain_supported_by_real_caller(self):
        old = {"TASK": "Instruction"}
        content = "line1\nline2\tcolumn\rreturn\bback\fform"
        raw = '{"TASK": "' + content + '"}'
        self.assertEqual(self.check_prompt(raw, old), (True, {"TASK": content}, old))

    def test_valid_json_escapes_unicode_and_outside_whitespace_are_unchanged(self):
        data = {"TASK": '你好 "quoted" \\ path\nline\tcolumn', "value": [1, True, None]}
        raw = "\n\t" + json.dumps(data, ensure_ascii=False, indent=2) + "\r\n"
        fixed = self.utils.escape_special_chars_in_json_string(raw)
        self.assertEqual(fixed, raw)
        self.assertEqual(json.loads(fixed), data)

    def test_real_caller_retains_template_variable_rejection(self):
        old = {"TASK": "Instruction for {name}"}
        raw = '{"TASK": "Changed\u0000 instruction for {other}"}'
        legal, new_prompt, original = self.check_prompt(raw, old)
        self.assertFalse(legal)
        self.assertIsNone(new_prompt)
        self.assertEqual(original, old)
        self.assertIn("Variable other", self.log.getvalue())

    def test_malformed_json_is_still_rejected(self):
        old = {"TASK": "Instruction"}
        self.assertEqual(self.check_prompt('{"TASK": "unfinished}', old), (False, None, old))

    def test_valid_prompt_passes_unchanged(self):
        old = {"TASK": "Original {name}"}
        raw = json.dumps({"TASK": "Updated {name}"})
        self.assertEqual(self.check_prompt(raw, old), (True, {"TASK": "Updated {name}"}, old))


if __name__ == "__main__":
    unittest.main()
