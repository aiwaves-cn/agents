"""Regression tests for preserving independent exchanges in log files."""
import datetime
import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "src/agents/utils/files.py"
SPEC = importlib.util.spec_from_file_location("agents_log_files", MODULE_PATH)
log_files = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(log_files)
FIXED_TIME = datetime.datetime(2026, 11, 7, 18, 0, 0)


class LogFilenameTests(unittest.TestCase):
    def setUp(self):
        self.temp_root = Path(tempfile.gettempdir()).resolve()
        self.fixture = tempfile.TemporaryDirectory(prefix="agents-log-test-")
        self.directory = Path(self.fixture.name).resolve()
        self.assertIn(self.temp_root, self.directory.parents)

    def tearDown(self):
        self.assertIn(self.temp_root, self.directory.parents)
        self.fixture.cleanup()

    def read_logs(self):
        return [json.loads(path.read_text(encoding="utf-8"))
                for path in self.directory.glob("*.json")]

    def test_exchanges_in_same_second_are_preserved(self):
        with patch.object(log_files.datetime, "datetime") as clock:
            clock.now.return_value = FIXED_TIME
            log_files.save_logs(str(self.directory), ["first"], "reply one")
            log_files.save_logs(str(self.directory), ["second"], "reply two")
        logs = self.read_logs()
        self.assertEqual(len(logs), 2)
        self.assertCountEqual(logs, [
            {"input": ["first"], "output": "reply one"},
            {"input": ["second"], "output": "reply two"},
        ])

    def test_existing_timestamp_log_is_not_overwritten(self):
        existing = self.directory / "2026-11-07-18-00-00.json"
        original = '{"input": ["existing"], "output": "keep me"}'
        existing.write_text(original, encoding="utf-8")
        with patch.object(log_files.datetime, "datetime") as clock:
            clock.now.return_value = FIXED_TIME
            log_files.save_logs(str(self.directory), ["new"], "new reply")
        self.assertEqual(existing.read_text(encoding="utf-8"), original)
        self.assertEqual(len(self.read_logs()), 2)

    def test_concurrent_exchanges_have_independent_json_logs(self):
        def save(index):
            log_files.save_logs(str(self.directory), [index], {"reply": index})

        with patch.object(log_files.datetime, "datetime") as clock:
            clock.now.return_value = FIXED_TIME
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(save, range(8)))
        self.assertEqual(len(list(self.directory.glob("*.json"))), 8)
        self.assertCountEqual(self.read_logs(), [
            {"input": [index], "output": {"reply": index}}
            for index in range(8)
        ])

    def test_unicode_payload_round_trips(self):
        log_files.save_logs(str(self.directory), ["你好"], {"回答": "世界"})
        self.assertEqual(self.read_logs(), [
            {"input": ["你好"], "output": {"回答": "世界"}},
        ])

    def test_logs_remain_discoverable_by_timestamp_prefix(self):
        with patch.object(log_files.datetime, "datetime") as clock:
            clock.now.return_value = FIXED_TIME
            log_files.save_logs(str(self.directory), ["question"], "answer")
        self.assertEqual(len(list(self.directory.glob("2026-11-07-18-00-00*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
