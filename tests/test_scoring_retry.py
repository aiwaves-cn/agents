"""Run complete production evaluators; only provider and sleep are mocked.

AGENTS_SOURCE_ROOT selects an unchanged baseline or candidate source tree.
Dataset data is supplied directly through the real BaseDataset constructor:
these tests exercise evaluation, not the unrelated bundled-corpus loaders.
"""
import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import call, patch


def load_evaluators():
    source_root = Path(os.environ.get(
        "AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1])
    ))
    root = source_root / "src" / "agents"
    prefix = "_scoring_retry_contract"
    modules = {}
    for suffix, directory in (
        ("", root), (".datasets", root / "datasets"),
        (".agents", root / "agents"), (".utils", root / "utils"),
    ):
        package = types.ModuleType(prefix + suffix)
        package.__path__ = [str(directory)]
        modules[package.__name__] = package
    llm = types.ModuleType(prefix + ".agents.llm")

    def no_live_call(*args, **kwargs):
        raise AssertionError("Live provider requests are forbidden")

    llm.completion_with_backoff = no_live_call
    modules[llm.__name__] = llm
    loaded = {}
    with patch.dict(sys.modules, modules):
        for relative in (
            "datasets/base", "utils/text", "datasets/creative_writing",
            "datasets/software_dev",
        ):
            name = prefix + "." + relative.replace("/", ".")
            spec = importlib.util.spec_from_file_location(
                name, root / (relative + ".py")
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[relative] = module
    return loaded


def response(scores):
    return types.SimpleNamespace(choices=[
        types.SimpleNamespace(message=types.SimpleNamespace(
            content="<score>" + str(score) + "</score>"
        )) for score in scores
    ])


class RetryContract:
    """Shared boundary scenarios, without reproducing the scoring algorithm."""

    def setUp(self):
        loaded = load_evaluators()
        self.module = loaded["datasets/" + self.module_name]
        dataset_class = getattr(self.module, self.class_name)
        self.dataset = dataset_class.__new__(dataset_class)
        loaded["datasets/base"].BaseDataset.__init__(
            self.dataset, [{"prompt": "Write a program printing hello."}]
        )
        self.answer = "print('hello')"

    def evaluate(self):
        if self.module_name == "software_dev":
            return self.dataset.evaluate(0, self.answer)
        return self.dataset.evaluate(self.answer)

    def test_persistent_provider_failure_preserves_final_exception(self):
        errors = [RuntimeError("provider failure " + str(i)) for i in range(3)]
        with patch.object(self.module, "completion_with_backoff", side_effect=errors) as provider, patch.object(self.module.time, "sleep") as sleep:
            with self.assertRaises(RuntimeError) as caught:
                self.evaluate()
            self.assertIs(caught.exception, errors[-1])
            self.assertEqual(provider.call_count, 3)
            self.assertEqual(sleep.call_args_list, [call(10), call(10)])

    def test_persistent_malformed_score_preserves_real_parser_error(self):
        with patch.object(self.module, "completion_with_backoff", return_value=response(["bad"])) as provider, patch.object(self.module.time, "sleep") as sleep:
            with self.assertRaises(ValueError) as caught:
                self.evaluate()
            self.assertIn("bad", str(caught.exception))
            self.assertEqual(provider.call_count, 3)
            self.assertEqual(sleep.call_args_list, [call(10), call(10)])

    def test_provider_failure_then_recovery(self):
        effects = [RuntimeError("temporary"), response(self.scores)]
        with patch.object(self.module, "completion_with_backoff", side_effect=effects) as provider, patch.object(self.module.time, "sleep") as sleep:
            self.assertEqual(self.evaluate(), self.expected)
            self.assertEqual(provider.call_count, 2)
            sleep.assert_called_once_with(10)

    def test_malformed_score_then_recovery(self):
        effects = [response(["bad"]), response(self.scores)]
        with patch.object(self.module, "completion_with_backoff", side_effect=effects) as provider, patch.object(self.module.time, "sleep") as sleep:
            self.assertEqual(self.evaluate(), self.expected)
            self.assertEqual(provider.call_count, 2)
            sleep.assert_called_once_with(10)

    def test_last_allowed_attempt_can_succeed(self):
        effects = [RuntimeError("first"), RuntimeError("second"), response(self.scores)]
        with patch.object(self.module, "completion_with_backoff", side_effect=effects) as provider, patch.object(self.module.time, "sleep") as sleep:
            self.assertEqual(self.evaluate(), self.expected)
            self.assertEqual(provider.call_count, 3)
            self.assertEqual(sleep.call_args_list, [call(10), call(10)])

    def test_normal_five_choices_keep_metric_and_request_contract(self):
        with patch.object(self.module, "completion_with_backoff", return_value=response(self.scores)) as provider, patch.object(self.module.time, "sleep") as sleep:
            self.assertEqual(self.evaluate(), self.expected)
            provider.assert_called_once()
            kwargs = provider.call_args.kwargs
            self.assertEqual(kwargs["n"], 5)
            self.assertEqual(kwargs["model"], "gpt-4-turbo-2024-04-09")
            self.assertEqual(kwargs["api_key"], "")
            self.assertEqual(kwargs["base_url"], "")
            self.assertEqual(kwargs["messages"][0]["role"], "user")
            self.assertIn(self.answer, kwargs["messages"][0]["content"])
            sleep.assert_not_called()


class CreativeWritingRetryTests(RetryContract, unittest.TestCase):
    module_name = "creative_writing"
    class_name = "CreativeWritingDataset"
    scores = [1, 3, 5, 7, 9]
    expected = (5.0, {"scores": [1, 3, 5, 7, 9], "average_score": 5.0})


class SoftwareDevRetryTests(RetryContract, unittest.TestCase):
    module_name = "software_dev"
    class_name = "SoftwareDevDataset"
    scores = [1, 2, 3, 4, 4]
    expected = (2.8, {"Executability Metric": 2.8})


if __name__ == "__main__":
    unittest.main()
