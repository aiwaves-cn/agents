"""Compare real Task conversion with current fields and existing file saving."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


def load_task_module(source_root):
    root = Path(source_root) / "src" / "agents"
    prefix = "_task_config_regression"
    modules = {}
    for suffix in ("", ".task", ".utils", ".agents"):
        package = types.ModuleType(prefix + suffix)
        package.__path__ = [str(root / suffix.lstrip("."))]
        modules[package.__name__] = package

    def no_model(*args, **kwargs):
        raise AssertionError("No model generation in this configuration regression")

    modules[prefix + ".agents"].LLMConfig = no_model
    modules[prefix + ".agents"].OpenAILLM = no_model
    prompts = types.ModuleType(prefix + ".utils.prompts")
    prompts.TASK_CONFIG_GENERATION_PROMPT_TEMPLATE = "unused"
    modules[prompts.__name__] = prompts
    with patch.dict(sys.modules, modules):
        for relative in ("utils/config", "task/task"):
            name = prefix + "." + relative.replace("/", ".")
            spec = importlib.util.spec_from_file_location(name, root / (relative + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
    return module


class TaskToConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.task_module = load_task_module(root)

    def make_task(self):
        return self.task_module.Task(self.task_module.TaskConfig({
            "task_name": "Original", "task_type": "old", "task_description": "原始描述"}))

    def test_conversion_uses_current_task_fields(self):
        task = self.make_task()
        task.task_name = "Updated"
        task.task_type = "new"
        task.task_description = "更新后的描述"
        self.assertEqual(task.to_config().to_dict(), {
            "task_name": "Updated", "task_type": "new", "task_description": "更新后的描述"})
        self.assertEqual(task.config.task_description, "原始描述")

    def test_conversion_matches_existing_dump_and_real_reload(self):
        task = self.make_task()
        task.task_name = "保存"
        task.task_type = None
        task.task_description = "文件保存与内存转换一致"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task.json"
            task.dump(path)
            saved = self.task_module.TaskConfig(str(path))
            self.assertEqual(task.to_config().to_dict(), saved.to_dict())
            restored = self.task_module.Task(saved)
            self.assertEqual(restored.task_description, task.task_description)
        self.assertEqual(task.config.task_name, "Original")

    def test_unchanged_task_conversion_is_a_separate_equivalent_config(self):
        task = self.make_task()
        converted = task.to_config()
        self.assertIsNot(converted, task.config)
        self.assertEqual(converted.to_dict(), task.config.to_dict())
        self.assertEqual(self.task_module.Task(converted).task_description, task.task_description)


if __name__ == "__main__":
    unittest.main()
