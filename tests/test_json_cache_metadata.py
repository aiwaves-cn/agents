"""Real AutoRetriever + VectorRetriever; deterministic embedding/DB boundaries."""
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
    for name, path in (("agents", root.parent), ("agents.utils", root),
                       ("agents.utils.retrievers", root / "retrievers"),
                       ("agents.utils.storages", root / "storages"),
                       ("agents.utils.storages.vectordb_storages", root / "storages" / "vectordb_storages")):
        package = types.ModuleType(name)
        package.__path__ = [str(path)]
        modules[name] = package

    def load(name, path, package=False):
        spec = importlib.util.spec_from_file_location(name, path,
            submodule_search_locations=[str(path.parent)] if package else None)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    class NoOnlineInitialization:
        def __init__(self, *args, **kwargs):
            raise AssertionError("No online embedding/parser allowed")

    embeddings = types.ModuleType("agents.utils.embeddings")
    embeddings.BaseEmbedding = embeddings.OpenAIEmbedding = NoOnlineInitialization
    modules[embeddings.__name__] = embeddings
    parser = types.ModuleType("agents.utils.unstructured_io")
    parser.UnstructuredIO = NoOnlineInitialization
    modules[parser.__name__] = parser

    with patch.dict(sys.modules, modules):
        vectors = load("agents.utils.storages.vectordb_storages.base",
                       root / "storages" / "vectordb_storages" / "base.py")

        class OfflineStorage(vectors.BaseVectorStorage):
            collections = {}
            calls = []
            events = []

            def __init__(self, **kwargs):
                self.name = kwargs["collection_name"]
                self.calls.append(kwargs)
                self.collections.setdefault(self.name, [])

            def add(self, records, **kwargs):
                self.events.append(("add", self.name, len(records)))
                self.collections[self.name].extend(records)

            def status(self):
                return vectors.VectorDBStatus(2, len(self.collections[self.name]))

            def query(self, query, **kwargs):
                # Database boundary supplies ranked records; real retriever
                # performs payload conversion, thresholding and aggregation.
                return [vectors.VectorDBQueryResult(record, 1.0)
                        for record in self.collections[self.name][:query.top_k]]

            def clear(self):
                self.events.append(("clear", self.name))
                self.collections[self.name].clear()

            def load(self):
                pass

            def delete(self, ids, **kwargs):
                raise AssertionError("Deletion is outside this regression")

            @property
            def client(self):
                raise AssertionError("No vector service is used")

        for filename, attribute in (("qdrant", "QdrantStorage"), ("milvus", "MilvusStorage")):
            module = types.ModuleType("agents.utils.storages.vectordb_storages." + filename)
            setattr(module, attribute, OfflineStorage)
            sys.modules[module.__name__] = module
        storage = load("agents.utils.storages", root / "storages" / "__init__.py", True)
        load("agents.utils.retrievers.base", root / "retrievers" / "base.py")
        load("agents.utils.retrievers.vector_retriever", root / "retrievers" / "vector_retriever.py")
        auto = load("agents.utils.retrievers.auto_retriever", root / "retrievers" / "auto_retriever.py")
    return auto, storage.StorageType, OfflineStorage


class OfflineEmbedding:
    def __init__(self):
        self.batches = []
        self.queries = []

    def get_output_dim(self):
        return 2

    def embed(self, obj):
        self.queries.append(obj)
        return [0.25, 0.75]

    def embed_list(self, objs):
        self.batches.append(list(objs))
        return [[0.25, 0.75] for _ in objs]


class JsonCacheMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.auto_module, cls.storage_type, cls.offline_storage = load_components(source_root)

    def setUp(self):
        self.offline_storage.collections.clear()
        self.offline_storage.calls.clear()
        self.offline_storage.events.clear()
        self.embedding = OfflineEmbedding()
        self.auto = self.auto_module.AutoRetriever(embedding_model=self.embedding,
            url_and_api_key=("offline", "unused"))
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def make_file(self, extension="json", text="alpha"):
        path = Path(self.directory.name) / ("records." + extension)
        content = json.dumps([text]) if extension == "json" else json.dumps(text) + "\n"
        path.write_text(content, encoding="utf-8")
        os.utime(path, (1700000000, 1700000000))
        return path

    def retrieve(self, path):
        return self.auto.run_vector_retriever("question", str(path))

    def stored_record(self):
        return next(iter(self.offline_storage.collections.values()))[0]

    def test_second_json_read_reuses_unchanged_records(self):
        path = self.make_file()
        first = self.retrieve(path)
        self.assertEqual(self.retrieve(path), first)
        self.assertEqual(first, {"query": "question", "retrieved context": "\nalpha"})
        self.assertEqual(self.embedding.batches, [["alpha"]])
        self.assertEqual(sum(event[0] == "clear" for event in self.offline_storage.events), 1)
        self.assertEqual(self.stored_record().payload["metadata"]["last_modified"],
                         self.auto._get_file_modified_date_from_file(str(path)))

    def test_second_jsonl_read_reuses_unchanged_records(self):
        path = self.make_file("jsonl")
        self.retrieve(path)
        self.assertEqual(self.retrieve(path)["retrieved context"], "\nalpha")
        self.assertEqual(self.embedding.batches, [["alpha"]])

    def test_changed_json_is_reindexed_and_then_reused(self):
        path = self.make_file()
        self.retrieve(path)
        path.write_text('["beta"]', encoding="utf-8")
        os.utime(path, (1700000004, 1700000004))
        self.assertEqual(self.retrieve(path)["retrieved context"], "\nbeta")
        self.assertEqual(self.retrieve(path)["retrieved context"], "\nbeta")
        self.assertEqual(self.embedding.batches, [["alpha"], ["beta"]])
        self.assertEqual(sum(event[0] == "clear" for event in self.offline_storage.events), 2)

    def test_legacy_records_without_timestamp_are_refreshed_once(self):
        path = self.make_file()
        self.retrieve(path)
        self.stored_record().payload["metadata"].pop("last_modified", None)
        self.assertEqual(self.retrieve(path)["retrieved context"], "\nalpha")
        self.assertEqual(self.retrieve(path)["retrieved context"], "\nalpha")
        self.assertEqual(self.embedding.batches, [["alpha"], ["alpha"]])

    def test_first_read_preserves_text_path_and_query_result(self):
        path = self.make_file()
        self.assertEqual(self.retrieve(path), {"query": "question", "retrieved context": "\nalpha"})
        payload = self.stored_record().payload
        self.assertEqual(payload["text"], "alpha")
        self.assertEqual(payload["content path"], str(path))
        self.assertIsInstance(payload["metadata"], dict)

    def test_preexisting_matching_timestamp_uses_existing_cache(self):
        path = self.make_file()
        self.retrieve(path)
        self.stored_record().payload["metadata"]["last_modified"] = (
            self.auto._get_file_modified_date_from_file(str(path)))
        self.assertEqual(self.retrieve(path)["retrieved context"], "\nalpha")
        self.assertEqual(self.embedding.batches, [["alpha"]])

    def test_none_payload_still_raises_existing_value_error(self):
        path = self.make_file()
        self.retrieve(path)
        self.stored_record().payload = None
        storage = self.auto._initialize_vector_storage(self.auto._collection_name_generator(str(path)))
        with self.assertRaisesRegex(ValueError, "payload is None"):
            self.auto._get_file_modified_date_from_storage(storage)


if __name__ == "__main__":
    unittest.main()


