"""Real Agent/LLM/Action/Memory modules, offline completion SDK boundary.

The fake SDK supplies response objects only; production code builds prompts,
extracts response content, handles the label and constructs/serializes Action.
No production text-processing method is patched or reimplemented here.
"""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


def load_modules(source_root):
    root = Path(source_root) / "src/agents"
    prefix = "_agent_content_prefix"
    modules = {}
    for suffix in ("", ".agents", ".utils", ".utils.storages",
                   ".utils.storages.key_value_storages", ".tools"):
        module = types.ModuleType(prefix + suffix)
        module.__path__ = [str(root / suffix.lstrip(".").replace(".", "/"))]
        modules[module.__name__] = module

    def forbidden(*args, **kwargs):
        raise AssertionError("Unexpected model, tool, embedding or retrieval call")

    class SDKMessage(dict):
        @property
        def tool_calls(self):
            return self.get("tool_calls")

    class SDKResponse:
        """Provider-output boundary, not the actual installed SDK type."""
        def __init__(self, content):
            self.choices = [types.SimpleNamespace(message=SDKMessage(content=content))]

        def json(self):
            return {"choices": [{"message": dict(self.choices[0].message)}],
                    "usage": {"total_tokens": 1}}

    sdk = types.ModuleType("litellm")
    sdk.Message = SDKMessage
    sdk.utils = types.SimpleNamespace(ModelResponse=SDKResponse)
    sdk.OpenAIError = type("OfflineProviderError", (Exception,), {})
    sdk.completion = forbidden
    modules["litellm"] = sdk
    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda: False  # Do not load credentials from any file.
    modules["dotenv"] = dotenv
    torch = types.ModuleType("torch")
    torch.Tensor = type("UnusedTensor", (), {})
    modules["torch"] = torch
    text2vec = types.ModuleType("text2vec")
    text2vec.semantic_search = forbidden
    modules["text2vec"] = text2vec
    embeddings = types.ModuleType(prefix + ".utils.embeddings")
    embeddings.get_embedding = forbidden
    modules[embeddings.__name__] = embeddings
    modules[prefix + ".tools"].Tool = type("UnusedTool", (), {"__init__": forbidden})
    modules[prefix + ".tools"].AVAILABLE_TOOLS = {}

    loaded = {}
    with patch.dict(sys.modules, modules):
        for relative in ("utils/config", "utils/prompts", "utils/files",
                         "utils/storages/key_value_storages/base",
                         "utils/storages/key_value_storages/in_memory",
                         "utils/storages/key_value_storages/json",
                         "agents/llm", "agents/memory", "agents/toolkit",
                         "agents/environment", "agents/action", "agents/agent"):
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
    return loaded, sdk, SDKResponse


class AgentContentPrefixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.loaded, cls.sdk, cls.response_type = load_modules(root)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        previous_directory = os.getcwd()
        os.chdir(self.temp.name)
        self.addCleanup(os.chdir, previous_directory)
        environment_patch = patch.dict(os.environ, {"OPENAI_API_KEY": "offline-boundary",
                                                    "OPENAI_BASE_URL": ""})
        environment_patch.start()
        self.addCleanup(environment_patch.stop)
        agent_module = self.loaded["agents/agent"]
        config = agent_module.AgentConfig({
            "agent_name": "writer", "agent_roles": {"answer": "assistant"},
            "LLM_config": {"SAVE_LOGS": False, "model": "offline-boundary"},
            "memory": {"long_term_memory": {
                "json_path": str(Path(self.temp.name) / "memory/writer.jsonl")}},
        })
        self.agent = agent_module.Agent(config)
        env_module = self.loaded["agents/environment"]
        self.environment = env_module.Environment(env_module.EnvironmentConfig({}))
        # Inert node/config data; real Agent.compile reads these fields.
        self.node = types.SimpleNamespace(
            node_name="answer", is_begin=False, begin_role="assistant", begin_query="",
            name_role_hash={"writer": "assistant"},
            node_primary_prompts={"assistant": {"TASK": "Answer naturally"}},
            node_prompt_paddings={}, node_prompt_templates={},
            node_prompts={"writer": {"TASK": "Return the requested text"}},
            node_description="Offline reply scenario", kb=None,
        )

    def get_action(self, provider_content, expected):
        response = self.response_type(provider_content)
        completion = Mock(return_value=response)
        with patch.object(self.sdk, "completion", completion):
            with contextlib.redirect_stdout(io.StringIO()):
                action = self.agent.step(self.node, self.environment)
        completion.assert_called_once()
        self.assertIsInstance(action, self.loaded["agents/action"].Action)
        self.assertIsInstance(action.config, self.loaded["agents/action"].ActionConfig)
        self.assertEqual(action.content, expected)
        self.assertEqual(action.config.content, expected)
        self.assertEqual(action.to_dict()["content"], expected)
        self.assertIs(action.response, response)
        self.assertEqual(response.choices[0].message["content"], provider_content)
        self.assertEqual(action.agent_role, "assistant")
        self.assertEqual(action.tools_results_dict, {})
        self.assertEqual(action.system_prompt, "Offline reply scenario")
        self.assertIn("Return the requested text", action.last_prompt)
        self.assertIs(completion.call_args.kwargs["stream"], False)
        self.assertNotIn("tools", completion.call_args.kwargs)
        self.assertEqual(completion.call_args.kwargs["messages"][0],
                         {"role": "system", "content": "Offline reply scenario"})
        return action

    def test_unprefixed_reply_characters_are_preserved(self):
        for text in ("Stop", "Open", "Keep", "The result is token", "中文 token", "token 中文"):
            with self.subTest(text=text):
                self.get_action(text, text)

    def test_exact_leading_label_is_removed_without_truncating_body(self):
        for text, expected in (("Speak content: Open", "Open"),
                               ("Speak content:Stop", "Stop"),
                               ("Speak content: 中文 token", "中文 token")):
            with self.subTest(text=text):
                self.get_action(text, expected)

    def test_internal_or_trailing_label_is_not_removed(self):
        self.get_action("Report: Speak content: Open", "Report: Speak content: Open")
        self.get_action("Answer Speak content:", "Answer Speak content:")

    def test_case_mismatched_label_is_not_a_new_alias(self):
        self.get_action("speak content: Open", "speak content: Open")

    def test_only_one_exact_leading_label_is_removed(self):
        self.get_action("Speak content: Speak content: Open", "Speak content: Open")

    def test_existing_llm_and_agent_whitespace_trimming_is_preserved(self):
        self.get_action(" \nSpeak content: \tOpen\n ", "Open")
        self.get_action(" \nOpen\t ", "Open")

    def test_empty_and_whitespace_only_controls(self):
        for text in ("", " \n\t ", "Speak content:", "Speak content: \t"):
            with self.subTest(text=text):
                self.get_action(text, "")

    def test_user_input_bypasses_provider_and_label_handling(self):
        self.agent.is_user = True
        completion = Mock(side_effect=AssertionError("User input must not call a provider"))
        text = "  Speak content: Stop  "
        with patch.object(self.sdk, "completion", completion):
            action = self.agent.step(self.node, self.environment, user_input=text)
        completion.assert_not_called()
        self.assertEqual(action.content, text)
        self.assertEqual(action.to_dict()["content"], text)
        self.assertTrue(action.is_user)
        self.assertEqual(action.latency, 0)

    def test_configured_begin_query_uses_real_step_without_provider(self):
        for text, expected in (("Stop", "Stop"),
                               ("Speak content: Stop", "Stop"),
                               ("Speak content: Speak content: Open", "Speak content: Open")):
            with self.subTest(text=text):
                self.node.is_begin = True
                self.node.begin_query = text
                completion = Mock(side_effect=AssertionError("begin_query must not call a provider"))
                with patch.object(self.sdk, "completion", completion):
                    with contextlib.redirect_stdout(io.StringIO()):
                        action = self.agent.step(self.node, self.environment)
                completion.assert_not_called()
                self.assertEqual(action.content, expected)
                self.assertEqual(action.to_dict()["content"], expected)
                self.assertTrue(action.is_agent_begin)
                self.assertTrue(action.is_node_begin)
                self.assertEqual(action.latency, 0)

    def test_begin_query_leading_whitespace_does_not_add_label_recognition(self):
        # Unlike provider text, begin_query does not pass through LLM.get_response.
        self.node.is_begin = True
        self.node.begin_query = " \nSpeak content: Stop\n "
        completion = Mock(side_effect=AssertionError("begin_query must not call a provider"))
        with patch.object(self.sdk, "completion", completion):
            with contextlib.redirect_stdout(io.StringIO()):
                action = self.agent.step(self.node, self.environment)
        completion.assert_not_called()
        self.assertEqual(action.content, "Speak content: Stop")


if __name__ == "__main__":
    unittest.main()
