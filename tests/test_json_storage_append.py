"""Exercise real key-value modules and temporary files, without filesystem mocks."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


def load_storages():
    source_root = Path(os.environ.get(
        "AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1])
    ))
    directory = source_root / "src/agents/utils/storages/key_value_storages"
    prefix = "_json_storage_append_contract"
    package = types.ModuleType(prefix)
    package.__path__ = [str(directory)]
    loaded = {}
    # Isolate only eager SDK imports in the enclosing agents package.
    with patch.dict(sys.modules, {prefix: package}):
        for filename in ("base", "in_memory", "json"):
            name = prefix + "." + filename
            spec = importlib.util.spec_from_file_location(
                name, directory / (filename + ".py")
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[filename] = module
    return loaded


class JsonStorageAppendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = load_storages()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "history.json"
        self.storage_class = self.modules["json"].JsonStorage
        self.first = {"role": "user", "content": "你好\nsecond line", "meta": {"turn": 1}}
        self.second = {"role": "assistant", "content": "hello", "done": False}
        self.third = {"role": "user", "content": "next", "value": None}

    def encode(self, record):
        return json.dumps(record).encode("ascii")

    def assert_append_roundtrip(self, original, expected_old):
        self.path.write_bytes(original)
        storage = self.storage_class(self.path)
        # The existing implementation already accepts this exact file input.
        self.assertEqual(storage.load(), expected_old)
        self.assertIsNone(storage.save([self.second, self.third]))
        expected = expected_old + [self.second, self.third]
        self.assertEqual(storage.load(), expected)
        self.assertEqual(self.storage_class(self.path).load(), expected)
        self.assertTrue(self.path.read_bytes().startswith(original))

    def test_append_to_loadable_single_record_without_final_newline(self):
        self.assert_append_roundtrip(self.encode(self.first), [self.first])

    def test_append_to_loadable_multiple_records_without_final_newline(self):
        previous = {"role": "system", "content": "instructions"}
        original = self.encode(previous) + b"\r\n" + self.encode(self.first)
        self.assert_append_roundtrip(original, [previous, self.first])

    def test_append_after_loadable_record_with_trailing_json_whitespace(self):
        self.assert_append_roundtrip(self.encode(self.first) + b" \t", [self.first])

    def test_existing_line_endings_do_not_add_blank_records(self):
        for ending in (b"\n", b"\r\n", b"\r"):
            with self.subTest(ending=ending):
                self.assert_append_roundtrip(self.encode(self.first) + ending, [self.first])

    def test_save_empty_batch_preserves_unterminated_file_bytes(self):
        original = self.encode(self.first)
        self.path.write_bytes(original)
        storage = self.storage_class(self.path)
        self.assertIsNone(storage.save([]))
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(storage.load(), [self.first])

    def test_fresh_save_reopen_append_clear_and_reuse(self):
        storage = self.storage_class(self.path)
        self.assertEqual(storage.load(), [])
        self.assertIsNone(storage.save([self.first]))
        reopened = self.storage_class(self.path)
        self.assertEqual(reopened.load(), [self.first])
        self.assertIsNone(reopened.save([self.second]))
        self.assertEqual(self.storage_class(self.path).load(), [self.first, self.second])
        self.assertIsNone(reopened.clear())
        self.assertEqual(self.path.read_bytes(), b"")
        self.assertEqual(self.storage_class(self.path).load(), [])
        reopened.save([self.third])
        self.assertEqual(self.storage_class(self.path).load(), [self.third])

    def test_serialization_failure_does_not_modify_existing_records(self):
        original = self.encode(self.first)
        self.path.write_bytes(original)
        storage = self.storage_class(self.path)
        with self.assertRaises(TypeError):
            storage.save([self.second, {"unsupported": object()}])
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(storage.load(), [self.first])

    def test_in_memory_and_json_keep_batch_order_and_clear_contract(self):
        stores = [
            self.modules["in_memory"].InMemoryKeyValueStorage(),
            self.storage_class(self.path),
        ]
        for storage in stores:
            with self.subTest(storage=type(storage).__name__):
                self.assertIsInstance(storage, self.modules["base"].BaseKeyValueStorage)
                storage.save([self.first])
                storage.save([self.second, self.third])
                self.assertEqual(storage.load(), [self.first, self.second, self.third])
                storage.clear()
                self.assertEqual(storage.load(), [])


if __name__ == "__main__":
    unittest.main()
