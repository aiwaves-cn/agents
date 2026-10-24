"""Exercise the complete real MATH evaluator with a controlled provider boundary."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
import pandas  # Preload existing dependency before isolating package imports.

def load_math():
    root=Path(__file__).resolve().parents[1]/'src/agents'
    prefix='_math_retry_contract'
    modules={}
    for suffix in ('','.datasets','.agents'):
        m=types.ModuleType(prefix+suffix);m.__path__=[str(root/suffix.lstrip('.'))];modules[m.__name__]=m
    llm=types.ModuleType(prefix+'.agents.llm')
    def no_live_call(*a,**k):
        raise AssertionError('Live model request is forbidden')
    llm.completion_with_backoff=no_live_call;modules[llm.__name__]=llm
    with patch.dict(sys.modules,modules):
        for rel in ('datasets/base','datasets/math'):
            name=prefix+'.'+rel.replace('/','.')
            spec=importlib.util.spec_from_file_location(name,root/(rel+'.py'))
            m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return m

class MathRetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module=load_math()
    def setUp(self):
        self.dataset=self.module.MATHDataset.__new__(self.module.MATHDataset)
        self.dataset.data=[{'problem':'What is 1 + 1?','solution':'2'}]
    def response(self,verdict):
        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='<verdict>'+verdict+'</verdict>'))])
    def test_exhaustion_preserves_final_provider_exception(self):
        errors=[RuntimeError('provider unavailable '+str(i)) for i in range(20)]
        with patch.object(self.module,'completion_with_backoff',side_effect=errors) as call,patch.object(self.module.time,'sleep') as sleep:
            with self.assertRaises(RuntimeError) as caught:
                self.dataset.evaluate(0,'2')
            self.assertIs(caught.exception,errors[-1])
            self.assertEqual(call.call_count,20)
            self.assertEqual(sleep.call_count,19)
    def test_transient_failure_then_correct(self):
        with patch.object(self.module,'completion_with_backoff',side_effect=[RuntimeError('temporary'),self.response('correct')]) as call,patch.object(self.module.time,'sleep') as sleep:
            self.assertEqual(self.dataset.evaluate(0,'2'),(1,{'score':1}))
            self.assertEqual(call.call_count,2);sleep.assert_called_once_with(10)
    def test_incorrect_answer_control(self):
        with patch.object(self.module,'completion_with_backoff',return_value=self.response('incorrect')),patch.object(self.module.time,'sleep') as sleep:
            self.assertEqual(self.dataset.evaluate(0,'3'),(0,{'score':0}));sleep.assert_not_called()
    def test_last_allowed_attempt_can_succeed(self):
        effects=[RuntimeError('temporary') for _ in range(19)]+[self.response('correct')]
        with patch.object(self.module,'completion_with_backoff',side_effect=effects) as call,patch.object(self.module.time,'sleep') as sleep:
            self.assertEqual(self.dataset.evaluate(0,'2'),(1,{'score':1}))
            self.assertEqual(call.call_count,20);self.assertEqual(sleep.call_count,19)
if __name__=='__main__':
    unittest.main()
