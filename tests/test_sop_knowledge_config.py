"""Load full real SOP module and Config; never construct agent/LLM runtimes.

Requires the repository's existing bidict dependency, with no replacement.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


def load_sop(source_root):
    root = Path(source_root) / "src" / "agents"
    modules = {}
    for name, path in (("agents", root), ("agents.agents", root / "agents"),
                       ("agents.task", root / "task"), ("agents.utils", root / "utils")):
        package = types.ModuleType(name)
        package.__path__ = [str(path)]
        modules[name] = package

    class UnusedRuntime:
        def __init__(self, *args, **kwargs):
            raise AssertionError("Runtime construction is outside configuration round-trip tests")

    for name, attributes in (
        ("agents.agents.llm", ("OpenAILLM", "LLMConfig")),
        ("agents.agents.agent_team", ("AgentTeam",)),
        ("agents.agents.environment", ("Environment",)),
        ("agents.agents.memory", ("Memory", "ShortTermMemory", "LongTermMemory")),
        ("agents.task.node", ("NodeConfig", "Node")),
        ("agents.knowledge_bases", ("KnowledgeBaseConfig", "KnowledgeBase")),
    ):
        module = types.ModuleType(name)
        for attribute in attributes:
            setattr(module, attribute, UnusedRuntime)
        modules[name] = module

    with patch.dict(sys.modules, modules):
        name = "agents.task.sop"
        spec = importlib.util.spec_from_file_location(name, root / "task" / "sop.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return module


class SOPKnowledgeConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.sop = load_sop(source_root)

    def base(self):
        return {"nodes": {}, "edges": {}, "root": "node", "end": "end_node"}

    def knowledge(self):
        return {"content_input_paths": ["knowledge/records.json"], "storage_type": "qdrant",
                "vector_storage_local_path": "vectors", "embedding_model": "text-embedding-3-small",
                "top_k": 3, "similarity_threshold": 0.4, "return_detailed_info": True}

    def test_current_serialized_field_is_read(self):
        config = self.base()
        config["global_kb"] = self.knowledge()
        self.assertEqual(self.sop.SOPConfig(config).global_kb, config["global_kb"])

    def test_legacy_input_survives_real_json_dump_and_reload(self):
        config = self.base()
        config["kb"] = self.knowledge()
        original = self.sop.SOPConfig(config)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sop.json"
            original.dump(str(path))
            serialized = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(serialized["global_kb"], self.knowledge())
            restored = self.sop.SOPConfig(str(path))
            self.assertEqual(restored.global_kb, original.global_kb)

    def test_dictionary_round_trip_preserves_global_knowledge_fields(self):
        config = self.base()
        config["kb"] = self.knowledge()
        original = self.sop.SOPConfig(config)
        restored = self.sop.SOPConfig(original.to_dict())
        self.assertEqual(restored.global_kb, self.knowledge())
        self.assertEqual(restored.root, original.root)
        self.assertEqual(restored.edges, original.edges)

    def test_legacy_kb_input_remains_supported(self):
        config = self.base()
        config["kb"] = self.knowledge()
        config["global_kb"] = None
        self.assertEqual(self.sop.SOPConfig(config).global_kb, self.knowledge())

    def test_absent_or_explicit_null_global_kb_stays_disabled(self):
        self.assertIsNone(self.sop.SOPConfig(self.base()).global_kb)
        config = self.base()
        config["global_kb"] = None
        self.assertIsNone(self.sop.SOPConfig(config).global_kb)

    def test_required_sop_fields_still_validated(self):
        with self.assertRaisesRegex(ValueError, "root"):
            self.sop.SOPConfig({"nodes": {}, "edges": {}})


if __name__ == "__main__":
    unittest.main()
