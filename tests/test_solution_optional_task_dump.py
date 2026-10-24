"""Real SolutionConfig/Solution.dump round trips, isolating agent/SOP runtimes."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


def load_modules(source_root):
    root = Path(source_root) / "src" / "agents"
    prefix = "_solution_optional_task"
    modules = {}
    for suffix in ("", ".task", ".agents", ".utils", ".evaluation"):
        module = types.ModuleType(prefix + suffix)
        module.__path__ = [str(root / suffix.lstrip("."))]
        modules[module.__name__] = module

    def unused_runtime(*args, **kwargs):
        raise AssertionError("No LLM, agent team, SOP or State runtime is exercised")

    modules[prefix + ".agents"].LLMConfig = unused_runtime
    modules[prefix + ".agents"].OpenAILLM = unused_runtime
    for suffix, names in ((".agents.agent_team", ("AgentTeamConfig", "AgentTeam")),
                          (".task.sop", ("SOPConfig", "SOP"))):
        module = types.ModuleType(prefix + suffix)
        for name in names:
            setattr(module, name, unused_runtime)
        modules[module.__name__] = module
    state = types.ModuleType(prefix + ".evaluation.state")
    state.State = type("UnusedState", (), {})
    modules[state.__name__] = state
    prompts = types.ModuleType(prefix + ".utils.prompts")
    prompts.TASK_CONFIG_GENERATION_PROMPT_TEMPLATE = "unused"
    modules[prompts.__name__] = prompts

    loaded = {}
    with patch.dict(sys.modules, modules):
        for relative in ("utils/config", "task/task", "evaluation/trajectory", "task/solution"):
            name = prefix + "." + relative.replace("/", ".")
            spec = importlib.util.spec_from_file_location(name, root / (relative + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[relative] = module
    return loaded["task/solution"], loaded["task/task"]


class ComponentDumpBoundary:
    """File-writing collaborator only; not an AgentTeam/SOP implementation."""
    def __init__(self, label):
        self.label = label
        self.paths = []

    def dump(self, path):
        self.paths.append(str(path))
        Path(path).write_text(json.dumps({"boundary": self.label}), encoding="utf-8")


class SolutionOptionalTaskDumpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.solution_module, cls.task_module = load_modules(root)

    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage.cleanup)
        self.output = Path(self.storage.name).resolve() / "saved"
        fixture = Path(__file__).parent / "fixtures" / "chatbot_solution.json"
        self.example_config = json.loads(fixture.read_text(encoding="utf-8"))

    def make_solution(self, data):
        # The production constructor explicitly sets task=None when absent/null.
        # Bypass expensive agent/SOP initialization, not Config or dump logic.
        solution = self.solution_module.Solution.__new__(self.solution_module.Solution)
        solution.config = self.solution_module.SolutionConfig(data)
        solution.task = (self.task_module.Task(self.task_module.TaskConfig(solution.config.task))
                         if solution.config.task else None)
        solution.agent_team = ComponentDumpBoundary("agent_team")
        solution.sop = ComponentDumpBoundary("sop")
        return solution

    def assert_no_task_round_trip(self, data):
        solution = self.make_solution(data)
        self.assertIsNone(solution.task)
        self.assertIsNone(solution.dump(self.output))
        saved = json.loads((self.output / "solution.json").read_text(encoding="utf-8"))
        self.assertIsNone(saved["task"])
        restored = self.solution_module.SolutionConfig(str(self.output / "solution.json"))
        self.assertIsNone(restored.task)
        self.assertFalse((self.output / "task.json").exists())
        for component in ("agent_team", "sop"):
            self.assertEqual(Path(saved[component]), self.output / (component + ".json"))
            self.assertTrue(Path(saved[component]).is_file())
        self.assertEqual(solution.config.to_dict(),
                         self.solution_module.SolutionConfig(data).to_dict())

    def test_omitted_optional_task_round_trip(self):
        data = self.example_config
        data.pop("task")
        self.assert_no_task_round_trip(data)

    def test_explicit_null_task_round_trip(self):
        data = self.example_config
        data["task"] = None
        self.assert_no_task_round_trip(data)

    def test_present_task_still_saves_and_reloads_its_config(self):
        data = self.example_config
        data["task"] = {"task_name": "往返", "task_type": "example", "task_description": "保留任务描述"}
        solution = self.make_solution(data)
        solution.dump(self.output)
        restored = self.solution_module.SolutionConfig(str(self.output / "solution.json"))
        task_config = self.task_module.TaskConfig(restored.task)
        self.assertEqual(task_config.to_dict(), data["task"])
        self.assertTrue((self.output / "task.json").is_file())
        self.assertEqual(solution.config.task, data["task"])


if __name__ == "__main__":
    unittest.main()
