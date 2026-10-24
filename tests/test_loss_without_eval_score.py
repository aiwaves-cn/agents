"""Complete loss/config/case/prompt extraction with a fixed offline reply boundary."""
import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


class OfflineReply:
    """A deterministic response fixture, not a model or SDK client."""
    def __init__(self, *args, **kwargs):
        self.response = "<requirement_for_previous>保留正确结果</requirement_for_previous>"
        self.prompts = []

    def get_response(self, **kwargs):
        self.prompts.append(kwargs["last_prompt"])
        return None, self.response


def load_modules(source_root):
    root = Path(source_root) / "src" / "agents"
    modules = {}
    # Production optimization modules use absolute 'agents' imports.
    for suffix in ("", ".agents", ".utils", ".optimization", ".evaluation", ".task"):
        name = "agents" + suffix
        package = types.ModuleType(name)
        package.__path__ = [str(root / suffix.lstrip("."))]
        modules[name] = package

    class UnusedRuntime:
        def __init__(self, *args, **kwargs):
            raise AssertionError("No agent/node/solution runtime or online dependency allowed")

    modules["agents"].LLMConfig = lambda config: config
    modules["agents"].OpenAILLM = OfflineReply
    modules["agents"].SOP = UnusedRuntime
    modules["agents"].AgentConfig = UnusedRuntime
    modules["agents"].ActionConfig = UnusedRuntime
    for name in ("Agent", "Action", "Environment"):
        setattr(modules["agents.agents"], name, UnusedRuntime)
    for name, fields in (("agents.task.node", ("Node", "NodeConfig")),
                         ("agents.task.sop", ("SOP",)),
                         ("agents.task.solution", ("Solution", "SolutionConfig"))):
        module = types.ModuleType(name)
        for field in fields:
            setattr(module, field, UnusedRuntime)
        modules[name] = module

    loaded = {}
    with patch.dict(sys.modules, modules):
        for relative in ("utils/config", "utils/prompts", "optimization/optimizer",
                         "evaluation/state", "evaluation/trajectory", "evaluation/case",
                         "optimization/prompt_formatter", "optimization/utils", "optimization/loss"):
            name = "agents." + relative.replace("/", ".")
            spec = importlib.util.spec_from_file_location(name, root / (relative + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[relative] = module
            parent, attr = name.rsplit(".", 1)
            setattr(sys.modules[parent], attr, module)
            if relative == "utils/prompts":
                modules["agents"].DEFAULT_NODE_PROMPT_TEMPLATES = module.DEFAULT_NODE_PROMPT_TEMPLATES
    return loaded["optimization/loss"], loaded["evaluation/case"]


class LossWithoutEvalScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.loss_module, cls.case_module = load_modules(root)

    def run_case(self, has_ground_truth, has_eval_score):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "optimizer_config.json"
            fixture = (Path(__file__).resolve().parents[1] / "examples" /
                       "creative_writing" / "configs" / "optimizer_config.json")
            shutil.copyfile(fixture, path)
            config = self.loss_module.LossConfig(str(path))
            calculator = self.loss_module.LossCalculator(
                config, has_ground_truth=has_ground_truth, has_eval_score=has_eval_score)
            case = self.case_module.Case({
                "case_id": "loss_case", "case_name": "loss_case", "task_id": "offline",
                "task_description": "输出正确答案", "function_ids": "unused", "KB_id": "unused",
                "input": {}, "result": "answer", "ground_truth": "answer",
                "dataset_eval": {"score": 0.75, "metric_name": "f1", "metric_description": "F1 reference"},
            })
            if not has_eval_score:
                calculator.llm.response += "<score>7</score>"
            result = calculator.calculate_loss(case)
            self.assertIsNone(result)
            self.assertEqual(len(calculator.llm.prompts), 1)
            self.assertEqual(case.loss.requirement_for_previous, "保留正确结果")
            self.assertEqual(case.loss.score, 0.75 if has_eval_score else 7.0)
            self.assertEqual(case.loss.score_info, "F1 reference" if has_eval_score else "")
            self.assertEqual(case.loss.prompt, calculator.llm.prompts[0])
            self.assertNotIn("{score_info}", case.loss.prompt)

    def test_no_eval_score_with_ground_truth(self):
        self.run_case(True, False)

    def test_no_eval_score_without_ground_truth(self):
        self.run_case(False, False)

    def test_existing_eval_score_with_ground_truth_is_preserved(self):
        self.run_case(True, True)

    def test_existing_eval_score_without_ground_truth_is_preserved(self):
        self.run_case(False, True)


if __name__ == "__main__":
    unittest.main()
