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

            def __init__(self, **kwargs):
                self.name = kwargs["collection_name"]
                self.calls.append(kwargs)
                self.collections.setdefault(self.name, [])

            def add(self, records, **kwargs):
                self.collections[self.name].extend(records)

            def status(self):
                return vectors.VectorDBStatus(2, len(self.collections[self.name]))

            def query(self, query, **kwargs):
                # Database boundary supplies ranked records; real retriever
                # performs payload conversion, thresholding and aggregation.
                return [vectors.VectorDBQueryResult(record, 1.0)
                        for record in self.collections[self.name][:query.top_k]]

            def clear(self):
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
    def get_output_dim(self):
        return 2

    def embed(self, obj):
        return [0.25, 0.75]

    def embed_list(self, objs):
        return [[0.25, 0.75] for _ in objs]


class AutoRetrieverPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.auto_module, cls.storage_type, cls.offline_storage = load_components(source_root)

    def setUp(self):
        self.offline_storage.collections.clear()
        self.offline_storage.calls.clear()
        self.auto = self.auto_module.AutoRetriever(embedding_model=OfflineEmbedding(),
            url_and_api_key=("offline", "unused"))

    def test_same_filename_in_distinct_directories_has_distinct_collection(self):
        self.assertNotEqual(self.auto._collection_name_generator("first/records.json"),
                            self.auto._collection_name_generator("second/records.json"))

    def test_two_existing_local_files_merge_without_sharing_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for subdir, text in (("first", "alpha"), ("second", "beta")):
                path = Path(directory) / subdir / "records.json"
                path.parent.mkdir()
                path.write_text(json.dumps([text]), encoding="utf-8")
                paths.append(str(path))
            output = self.auto.run_vector_retriever("question", paths)
            self.assertEqual(output, {"query": "question", "retrieved context": "\nalpha\nbeta"})
            self.assertEqual(len(self.offline_storage.collections), 2)
            stored_paths = [records[0].payload["content path"]
                            for records in self.offline_storage.collections.values()]
            self.assertEqual(set(stored_paths), set(paths))

    def test_local_name_is_stable_and_obeys_existing_character_length_limit(self):
        path = "input/" + "records" * 12 + ".json"
        name = self.auto._collection_name_generator(path)
        self.assertEqual(name, self.auto._collection_name_generator(path))
        self.assertEqual(name, self.auto._collection_name_generator(os.path.abspath(path)))
        self.assertLessEqual(len(name), 30)
        self.assertRegex(name, r"^[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*$")
        self.assertFalse(self.auto.is_url)

    def test_url_naming_branch_is_unchanged(self):
        self.assertEqual(self.auto._collection_name_generator("https://example.com/docs"), "example_com_docs")
        self.assertTrue(self.auto.is_url)

    def test_single_local_file_detailed_output_and_qdrant_selection(self):
        self.auto.storage_type = self.storage_type.QDRANT
        self.auto.vector_storage_local_path = "offline-vector-dir"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "one.json"
            path.write_text('["answer"]', encoding="utf-8")
            output = self.auto.run_vector_retriever("question", str(path), return_detailed_info=True)
            info = {"similarity score": "1.0", "content path": str(path), "metadata": {}, "text": "answer"}
            self.assertEqual(output, {"query": "question", "retrieved context": "\n" + str(info)})
            self.assertEqual(self.offline_storage.calls[0]["path"], "offline-vector-dir")

    def test_empty_paths_still_raise_before_storage_initialization(self):
        with self.assertRaises(ValueError):
            self.auto.run_vector_retriever("question", [])
        self.assertEqual(self.offline_storage.calls, [])


if __name__ == "__main__":
    unittest.main()
