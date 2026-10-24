"""Actual NodeEval and State/Trajectory JSON output, without agent execution."""
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
    prefix = "_node_eval_summary"
    modules = {}
    for suffix in ("", ".agents", ".task", ".evaluation"):
        package = types.ModuleType(prefix + suffix)
        package.__path__ = [str(root / suffix.lstrip("."))]
        modules[package.__name__] = package

    class UnusedRuntime:
        def __init__(self, *args, **kwargs):
            raise AssertionError("No agent, tool, environment or model runtime allowed")

    modules[prefix].AgentConfig = UnusedRuntime
    modules[prefix].ActionConfig = UnusedRuntime
    for name in ("Agent", "Action", "Environment"):
        setattr(modules[prefix + ".agents"], name, UnusedRuntime)
    node = types.ModuleType(prefix + ".task.node")
    node.Node = UnusedRuntime
    node.NodeConfig = UnusedRuntime
    modules[node.__name__] = node

    loaded = {}
    with patch.dict(sys.modules, modules):
        for filename in ("state", "trajectory"):
            name = prefix + ".evaluation." + filename
            spec = importlib.util.spec_from_file_location(name, root / "evaluation" / (filename + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[filename] = module
    return loaded["state"], loaded["trajectory"]


class MetadataBoundary:
    """Serialization collaborator only; not a live agent, node or action."""
    node_name = "reasoning"

    def to_dict(self, *args):
        return {"label": "metadata-boundary"}


class NodeEvalSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.state_module, cls.trajectory_module = load_modules(root)

    def test_node_eval_json_round_trip_retains_all_constructor_fields(self):
        expected = {"node_name": "reasoning", "prompt": "评估提示", "content": "原始响应",
                    "summary": "已确认的节点摘要", "evaluation": "结果正确"}
        evaluation = self.state_module.NodeEval(**expected)
        serialized = json.loads(json.dumps(evaluation.to_dict(), ensure_ascii=False))
        restored = self.state_module.NodeEval(**serialized)
        self.assertEqual(restored.to_dict(), expected)
        self.assertEqual(restored.summary, expected["summary"])

    def test_updated_summary_reaches_actual_trajectory_json_file(self):
        boundary = MetadataBoundary()
        state = self.state_module.State(boundary, boundary, boundary, boundary)
        state.node_eval.update("prompt", "response", "跨文件保留摘要", "evaluation")
        trajectory = self.trajectory_module.Trajectory([state])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trajectory.json"
            trajectory.dump(path)
            saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved[0]["node_eval"]["summary"], "跨文件保留摘要")
        restored_eval = self.state_module.NodeEval(**saved[0]["node_eval"])
        self.assertEqual(restored_eval.summary, state.node_eval.summary)
        self.assertEqual(saved, trajectory.to_list())

    def test_empty_trajectory_json_output_is_unchanged(self):
        trajectory = self.trajectory_module.Trajectory([])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.json"
            trajectory.dump(path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), [])
        self.assertEqual(trajectory.to_list(), [])

    def test_other_backward_record_fields_still_round_trip(self):
        original = self.state_module.StateBackward(prompt="p", response="r", suggestion="s",
                                                  requirement_for_previous="previous", analyse="a")
        data = json.loads(json.dumps(original.to_dict()))
        restored = self.state_module.StateBackward(**data)
        self.assertEqual(restored.to_dict(), data)


if __name__ == "__main__":
    unittest.main()
