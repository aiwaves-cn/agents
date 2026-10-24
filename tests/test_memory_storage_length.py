"""Full Memory/key-value modules with real records/files and no model runtime."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


def load_modules(source_root):
    root = Path(source_root) / "src" / "agents"
    prefix = "_memory_storage_length"
    modules = {}
    for suffix in ("", ".agents", ".utils", ".utils.storages", ".utils.storages.key_value_storages"):
        package = types.ModuleType(prefix + suffix)
        package.__path__ = [str(root / suffix.lstrip(".").replace(".", "/"))]
        modules[package.__name__] = package

    def no_model(*args, **kwargs):
        raise AssertionError("No embedding, semantic search or LLM allowed")

    torch = types.ModuleType("torch")
    torch.Tensor = type("UnusedTensor", (), {})
    text2vec = types.ModuleType("text2vec")
    text2vec.semantic_search = no_model
    modules.update(torch=torch, text2vec=text2vec)
    for suffix, function in ((".agents.llm", "completion_with_backoff"),
                             (".utils.embeddings", "get_embedding")):
        module = types.ModuleType(prefix + suffix)
        setattr(module, function, no_model)
        modules[module.__name__] = module

    loaded = {}
    with patch.dict(sys.modules, modules):
        for relative in ("utils/storages/key_value_storages/base",
                         "utils/storages/key_value_storages/in_memory",
                         "utils/storages/key_value_storages/json", "utils/prompts", "agents/memory"):
            name = prefix + "." + relative.replace("/", ".")
            spec = importlib.util.spec_from_file_location(name, root / (relative + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[relative] = module
            if relative.endswith("/in_memory"):
                modules[prefix + ".utils.storages"].InMemoryKeyValueStorage = module.InMemoryKeyValueStorage
            if relative.endswith("/json"):
                modules[prefix + ".utils.storages"].JsonStorage = module.JsonStorage
    return loaded["agents/memory"], loaded["utils/storages/key_value_storages/json"].JsonStorage


class MemoryStorageLengthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.memory_module, cls.storage_type = load_modules(root)

    def setUp(self):
        self.storage_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage_directory.cleanup)
        self.directory = Path(self.storage_directory.name)
        self.messages = [{"name": "agent", "role": "user", "content": text}
                         for text in ("alpha", "beta", "gamma")]

    def test_file_backed_short_term_length_tracks_append_and_update(self):
        storage = self.storage_type(self.directory / "short.jsonl")
        memory = self.memory_module.ShortTermMemory(messages=self.messages[:2], storage=storage)
        self.assertIs(memory.storage, storage)
        self.assertEqual(len(memory), 2)
        memory.append_memory(self.messages[2])
        self.assertEqual(len(memory), 3)
        self.assertEqual(memory.get_memory(), self.messages)
        memory.update_memory({"updated": True}, self.messages[:1])
        self.assertEqual(len(memory), 1)
        self.assertEqual(storage.load(), self.messages[:1])

    def test_empty_file_backed_short_term_length_is_zero(self):
        storage = self.storage_type(self.directory / "empty.jsonl")
        memory = self.memory_module.ShortTermMemory(messages=[], storage=storage)
        self.assertEqual(memory.get_memory(), [])
        self.assertEqual(len(memory), 0)

    def test_real_long_term_append_accepts_file_backed_short_term(self):
        short_storage = self.storage_type(self.directory / "short.jsonl")
        short = self.memory_module.ShortTermMemory(messages=self.messages[:2], storage=short_storage)
        long_storage = self.storage_type(self.directory / "long.jsonl")
        long = self.memory_module.LongTermMemory(
            config={}, json_path=str(self.directory / "long.jsonl"), storage=long_storage, window_size=3)
        long.append_memory_from_short_term_memory(short)
        self.assertEqual(long.get_memory(), [])
        short.append_memory(self.messages[2])
        long.append_memory_from_short_term_memory(short)
        saved = long.get_memory()
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0], self.memory_module.Memory.encode_memory(self.messages))

    def test_default_in_memory_length_and_record_round_trip_are_unchanged(self):
        memory = self.memory_module.ShortTermMemory(config={"label": "control"}, messages=self.messages[:2])
        self.assertEqual(len(memory), 2)
        memory.append_memory(self.messages[2])
        restored = self.memory_module.ShortTermMemory.load_from_json(memory.to_dict())
        self.assertEqual(len(restored), 3)
        self.assertEqual(restored.get_memory(), self.messages)
        memory.update_memory({}, [])
        self.assertEqual(len(memory), 0)


if __name__ == "__main__":
    unittest.main()
