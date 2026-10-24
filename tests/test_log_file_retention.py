"""Real local files and mtimes through the complete log-retention functions."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


def load_file_module(source_root):
    path = Path(source_root) / "src" / "agents" / "utils" / "files.py"
    spec = importlib.util.spec_from_file_location("_file_retention_regression", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LogFileRetentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.module = load_file_module(root)

    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage.cleanup)
        self.directory = Path(self.storage.name)

    def make_file(self, name, mtime):
        path = self.directory / name
        path.write_text("保留内容", encoding="utf-8")
        os.utime(path, (mtime, mtime))
        return path

    def make_three_files(self):
        oldest = self.make_file("z-oldest.json", 1600000000)
        middle = self.make_file("m-middle.json", 1600000100)
        newest = self.make_file("a-newest.json", 1600000200)
        return oldest, middle, newest

    def test_delete_oldest_uses_mtime_not_enumeration_order(self):
        oldest, middle, newest = self.make_three_files()
        # os.listdir makes no chronology guarantee; only this boundary is fixed.
        with patch.object(self.module.os, "listdir", return_value=[newest.name, oldest.name, middle.name]):
            self.module.delete_oldest_files(str(self.directory), 1)
        self.assertFalse(oldest.exists())
        self.assertTrue(middle.exists())
        self.assertEqual(newest.read_text(encoding="utf-8"), "保留内容")

    def test_threshold_route_removes_the_oldest_excess_files(self):
        oldest, middle, newest = self.make_three_files()
        with patch.object(self.module.os, "listdir", return_value=[newest.name, middle.name, oldest.name]):
            self.module.delete_files_if_exceed_threshold(str(self.directory), 1)
        self.assertFalse(oldest.exists())
        self.assertFalse(middle.exists())
        self.assertTrue(newest.exists())

    def test_save_logs_retains_newer_existing_logs_and_writes_json(self):
        existing = [self.make_file("existing_%02d.json" % i, 1600000000 + 100 * i)
                    for i in range(21)]
        messages = [{"role": "user", "content": "输入"}]
        with patch.object(self.module.os, "listdir", return_value=[p.name for p in reversed(existing)]):
            self.module.save_logs(str(self.directory), messages, "输出")
        self.assertFalse(existing[0].exists())
        self.assertTrue(existing[-1].exists())
        created = [p for p in self.directory.iterdir() if not p.name.startswith("existing_")]
        self.assertEqual(len(created), 1)
        with created[0].open(encoding="utf-8") as stream:
            self.assertEqual(json.load(stream), {"input": messages, "output": "输出"})

    def test_at_threshold_preserves_files_and_subdirectories(self):
        files = self.make_three_files()
        child = self.directory / "subdirectory"
        child.mkdir()
        with patch.object(self.module.os, "listdir", return_value=[child.name] + [p.name for p in files]):
            self.module.delete_files_if_exceed_threshold(str(self.directory), 3)
        self.assertTrue(child.is_dir())
        self.assertTrue(all(p.is_file() for p in files))

    def test_oversized_delete_count_ignores_subdirectories(self):
        files = self.make_three_files()
        child = self.directory / "subdirectory"
        child.mkdir()
        with patch.object(self.module.os, "listdir", return_value=[child.name] + [p.name for p in reversed(files)]):
            self.module.delete_oldest_files(str(self.directory), 10)
        self.assertTrue(child.is_dir())
        self.assertFalse(any(p.exists() for p in files))


if __name__ == "__main__":
    unittest.main()
