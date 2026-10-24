"""Real JSON/JSONL files through the actual inherited BaseDataset.load method."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


def load_dataset_class(source_root):
    path = Path(source_root) / "src" / "agents" / "datasets" / "base.py"
    spec = importlib.util.spec_from_file_location("_dataset_json_errors", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class FileDataset(module.BaseDataset):
        def __getitem__(self, idx):
            return self.data[idx]

        def get_case_dict(self, idx):
            return self.data[idx]

    return FileDataset


class DatasetJsonErrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.dataset_type = load_dataset_class(root)

    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage.cleanup)
        self.directory = Path(self.storage.name)
        self.dataset = self.dataset_type([])

    def write(self, name, contents):
        path = self.directory / name
        path.write_text(contents, encoding="utf-8")
        return path

    def assert_decode_error_contract(self, path, invalid_document):
        try:
            json.loads(invalid_document)
        except json.JSONDecodeError as error:
            original = error
        else:
            self.fail("Regression fixture must be malformed JSON")
        with self.assertRaises(json.JSONDecodeError) as caught:
            self.dataset.load(str(path))
        error = caught.exception
        self.assertIn(str(path), error.msg)
        self.assertIn(original.msg, error.msg)
        self.assertEqual((error.doc, error.pos, error.lineno, error.colno),
                         (original.doc, original.pos, original.lineno, original.colno))
        self.assertIsInstance(error.__cause__, json.JSONDecodeError)
        cause = error.__cause__
        self.assertEqual((cause.msg, cause.doc, cause.pos, cause.lineno, cause.colno),
                         (original.msg, original.doc, original.pos, original.lineno, original.colno))

    def test_malformed_multiline_json_preserves_decode_error(self):
        document = '[\n  {"question": "你好", "answer": }\n]'
        path = self.write("损坏.json", document)
        self.assert_decode_error_contract(path, document)

    def test_malformed_jsonl_record_preserves_decode_error(self):
        record = '{"question": "第二条", "answer": }'
        path = self.write("损坏.jsonl", '{"answer": 1}\n\n  ' + record + '  \n')
        # Existing JSONL semantics decode each stripped record independently.
        self.assert_decode_error_contract(path, record)

    def test_valid_json_is_unchanged(self):
        expected = [{"question": "你好", "answer": 3}, {"answer": None}]
        path = self.write("valid.JSON", json.dumps(expected, ensure_ascii=False))
        self.assertEqual(self.dataset.load(str(path)), expected)

    def test_valid_jsonl_still_skips_blank_lines(self):
        path = self.write("valid.JSONL", '\n {"answer": 1}\n \n {"answer": "二"} \n')
        self.assertEqual(self.dataset.load(str(path)), [{"answer": 1}, {"answer": "二"}])

    def test_missing_file_is_still_file_not_found(self):
        path = self.directory / "missing.json"
        with self.assertRaises(FileNotFoundError) as caught:
            self.dataset.load(str(path))
        self.assertIn(str(path), str(caught.exception))

    def test_existing_unsupported_extension_is_still_value_error(self):
        path = self.write("unsupported.txt", '{}')
        with self.assertRaises(ValueError) as caught:
            self.dataset.load(str(path))
        self.assertNotIsInstance(caught.exception, json.JSONDecodeError)
        self.assertIn("Unsupported file format", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
