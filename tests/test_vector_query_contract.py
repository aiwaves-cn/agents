"""Real retriever and vector DTOs; embedding/storage are offline boundaries."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


def load_components(source_root):
    root = Path(source_root) / "src" / "agents" / "utils"
    modules = {}
    for name in ("agents", "agents.utils", "agents.utils.retrievers",
                 "agents.utils.storages", "agents.utils.storages.vectordb_storages"):
        package = types.ModuleType(name)
        package.__path__ = []
        modules[name] = package

    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    class UnusedOnlineDependency:
        def __init__(self, *args, **kwargs):
            raise AssertionError("Online dependencies must not be initialized")

    embeddings = types.ModuleType("agents.utils.embeddings")
    embeddings.BaseEmbedding = UnusedOnlineDependency
    embeddings.OpenAIEmbedding = UnusedOnlineDependency
    modules[embeddings.__name__] = embeddings
    unstructured = types.ModuleType("agents.utils.unstructured_io")
    unstructured.UnstructuredIO = UnusedOnlineDependency
    modules[unstructured.__name__] = unstructured
    with patch.dict(sys.modules, modules):
        vectors = load("agents.utils.storages.vectordb_storages.base",
                       root / "storages" / "vectordb_storages" / "base.py")
        storage_exports = sys.modules["agents.utils.storages"]
        for name in ("BaseVectorStorage", "VectorDBQuery", "VectorRecord"):
            setattr(storage_exports, name, getattr(vectors, name))
        load("agents.utils.retrievers.base", root / "retrievers" / "base.py")
        retriever = load("agents.utils.retrievers.vector_retriever",
                         root / "retrievers" / "vector_retriever.py")
    return vectors, retriever


class OfflineEmbedding:
    def __init__(self):
        self.queries = []

    def embed(self, obj):
        self.queries.append(obj)
        return [0.25, 0.75]

    def embed_list(self, objs):
        return [[0.25, 0.75] for _ in objs]


class VectorQueryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.vectors, cls.retrievers = load_components(source_root)

    def setUp(self):
        vectors = self.vectors

        class OfflineStorage(vectors.BaseVectorStorage):
            def __init__(self):
                self.records = []
                self.results = []
                self.last_query = None
                self.last_kwargs = None
                self.loads = 0

            def add(self, records, **kwargs):
                self.records.extend(records)

            def delete(self, ids, **kwargs):
                raise AssertionError("Deletion is outside this test")

            def status(self):
                return vectors.VectorDBStatus(2, len(self.records))

            def query(self, query, **kwargs):
                self.last_query, self.last_kwargs = query, kwargs
                return self.results

            def clear(self):
                self.records.clear()

            def load(self):
                self.loads += 1

            @property
            def client(self):
                raise AssertionError("No vector database client is used")

        self.storage = OfflineStorage()
        self.embedding = OfflineEmbedding()
        self.retriever = self.retrievers.VectorRetriever(self.embedding)

    def result(self, score, payload):
        return self.vectors.VectorDBQueryResult.construct(score, [1.0, 2.0], "row-7", payload)

    def test_empty_storage_raises_documented_value_error(self):
        with self.assertRaises(ValueError):
            self.retriever.query("question", self.storage)

    def test_supported_empty_json_input_then_query_raises_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.json"
            path.write_text(json.dumps([]), encoding="utf-8")
            self.retriever.process(str(path), self.storage)
            self.assertEqual(self.storage.records, [])
            with self.assertRaises(ValueError):
                self.retriever.query("question", self.storage)

    def test_result_mapping_and_query_arguments_are_preserved(self):
        payload = {"content path": "cases.json", "metadata": {"row": 7}, "text": "answer"}
        result = self.result(0.9, payload)
        self.assertEqual(result.record.id, "row-7")
        self.assertEqual(result.record.vector, [1.0, 2.0])
        self.assertEqual(result.record.payload, payload)
        self.storage.results = [result, self.result(0.8, {"text": "second"})]
        self.assertEqual(self.retriever.query("question", self.storage, top_k=2, filter="local"), [
            {"similarity score": "0.9", "content path": "cases.json", "metadata": {"row": 7}, "text": "answer"},
            {"similarity score": "0.8", "content path": "", "metadata": {}, "text": "second"},
        ])
        self.assertEqual(self.storage.last_query.query_vector, [0.25, 0.75])
        self.assertEqual(self.storage.last_query.top_k, 2)
        self.assertEqual(self.storage.last_kwargs, {"filter": "local"})
        self.assertEqual(self.storage.loads, 1)
        self.assertEqual(self.embedding.queries, ["question"])

    def test_nonempty_results_below_threshold_keep_fallback(self):
        self.storage.results = [self.result(0.2, {"content path": "cases.json", "text": "low"})]
        output = self.retriever.query("question", self.storage)
        self.assertEqual(len(output), 1)
        self.assertIn("No suitable information retrieved from cases.json", output[0]["text"])

    def test_missing_payload_keeps_value_error(self):
        self.storage.results = [self.result(0.9, None)]
        with self.assertRaisesRegex(ValueError, "Payload"):
            self.retriever.query("question", self.storage)

    def test_invalid_top_k_keeps_value_error_before_clients(self):
        with self.assertRaises(ValueError):
            self.retriever.query("question", self.storage, top_k=0)
        self.assertEqual(self.storage.loads, 0)
        self.assertEqual(self.embedding.queries, [])


if __name__ == "__main__":
    unittest.main()
