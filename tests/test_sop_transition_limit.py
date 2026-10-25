"""Real SOP.transit and Node/ControllerConfig; never invent an LLM response.

Optional runtime constructors and history-to-model preparation are explicit
forbidden boundaries. Model-driven branch correctness is not tested here.
"""
import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class ModelPathReached(Exception):
    pass


class ModelHistoryBoundary:
    calls = 0

    @classmethod
    def encode_memory(cls, *args, **kwargs):
        cls.calls += 1
        raise ModelPathReached('Transition reached model-history preparation')


class UnusedRuntime:
    def __init__(self, *args, **kwargs):
        raise AssertionError('Optional runtime construction is outside this test')


class NoModelResponse:
    def get_response(self, **kwargs):
        raise ModelPathReached('No provider output is synthesized')


def load_real_modules(source_root):
    root = Path(source_root) / 'src' / 'agents'
    modules = {}
    for name, location in (
        ('agents', root), ('agents.task', root / 'task'),
        ('agents.agents', root / 'agents'), ('agents.utils', root / 'utils'),
    ):
        package = types.ModuleType(name)
        package.__path__ = [str(location)]
        modules[name] = package
    for name, attributes in (
        ('agents.agents.llm', ('OpenAILLM', 'LLMConfig')),
        ('agents.agents.agent_team', ('AgentTeam',)),
        ('agents.agents.environment', ('Environment',)),
        ('agents.knowledge_bases', ('KnowledgeBaseConfig', 'KnowledgeBase')),
    ):
        module = types.ModuleType(name)
        for attribute in attributes:
            setattr(module, attribute, UnusedRuntime)
        modules[name] = module
    memory = types.ModuleType('agents.agents.memory')
    memory.Memory = ModelHistoryBoundary
    memory.ShortTermMemory = UnusedRuntime
    memory.LongTermMemory = UnusedRuntime
    modules[memory.__name__] = memory

    loaded = {}
    with patch.dict(sys.modules, modules):
        for name, relative in (
            ('agents.task.node', 'task/node.py'),
            ('agents.task.sop', 'task/sop.py'),
        ):
            spec = importlib.util.spec_from_file_location(name, root / relative)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[name] = module
    return loaded['agents.task.node'], loaded['agents.task.sop']


class SOPTransitionLimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('AGENTS_SOURCE_ROOT', str(Path(__file__).resolve().parents[1]))
        cls.node_module, cls.sop_module = load_real_modules(root)

    def fixture(self, maximum=2, transit_type='llm', current_last=False, single=False):
        NodeConfig = self.node_module.NodeConfig
        Node = self.node_module.Node
        def node(name):
            return Node(NodeConfig({
                'node_name': name, 'node_description': '', 'begin_role': 'speaker',
                'controller': {'transit_type': transit_type, 'max_chat_nums': maximum},
            }))
        current, following, third = node('current'), node('following'), node('third')
        if single:
            current.next_nodes = {'current': current}
        elif current_last:
            current.next_nodes = {'following': following, 'third': third, 'current': current}
        else:
            current.next_nodes = {'current': current, 'following': following}
        sop = self.sop_module.SOP.__new__(self.sop_module.SOP)
        sop.current_node = current
        sop.llm = NoModelResponse()
        ModelHistoryBoundary.calls = 0
        return sop, current, following

    def history(self, count):
        return [{'role': 'assistant', 'name': 'speaker', 'content': 'message'}
                for _ in range(count)]

    def assert_forced_transition(self, maximum, count, current_last=False):
        sop, _, following = self.fixture(maximum=maximum, current_last=current_last)
        result = None
        try:
            result = sop.transit(self.history(count), '', '')
        except ModelPathReached:
            pass
        self.assertIs(result, following, 'The configured upper-limit branch must decide without a model')
        self.assertEqual(ModelHistoryBoundary.calls, 0)

    def test_configured_limit_skips_model_path(self):
        self.assert_forced_transition(2, 3)

    def test_default_value_limit_skips_model_path(self):
        # ControllerConfig's existing default is ten; use that actual field value.
        maximum = self.node_module.NodeConfig.ControllerConfig({}).max_chat_nums
        self.assert_forced_transition(maximum, maximum + 1)

    def test_limit_keeps_existing_edge_order_wrap(self):
        self.assert_forced_transition(2, 3, current_last=True)

    def test_below_limit_still_enters_existing_model_path(self):
        sop, _, _ = self.fixture(maximum=2)
        with self.assertRaises(ModelPathReached):
            sop.transit(self.history(1), '', '')
        self.assertEqual(ModelHistoryBoundary.calls, 1)

    def test_exact_limit_preserves_existing_strict_comparison(self):
        sop, _, _ = self.fixture(maximum=2)
        with self.assertRaises(ModelPathReached):
            sop.transit(self.history(2), '', '')
        self.assertEqual(ModelHistoryBoundary.calls, 1)

    def test_order_controller_control(self):
        sop, _, following = self.fixture(transit_type='order')
        self.assertIs(sop.transit(self.history(0), '', ''), following)
        self.assertEqual(ModelHistoryBoundary.calls, 0)

    def test_single_loop_control(self):
        sop, current, _ = self.fixture(maximum=2, single=True)
        self.assertIs(sop.transit(self.history(3), '', ''), current)
        self.assertEqual(ModelHistoryBoundary.calls, 0)


if __name__ == '__main__':
    unittest.main()
