"""Full VectorRetriever + UnstructuredIO control flow, SDK calls at boundaries.

Real temporary file opening/closing, JSON parsing, chunk dispatch, vector DTOs
and record construction execute. Partition/chunk SDK, embedding and storage are
explicit offline boundaries, NOT a claim of actual PDF/text parser validation.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


def load_components(source_root):
    root = Path(source_root) / "src/agents/utils"
    modules = {}
    for name in ("agents", "agents.utils", "agents.utils.retrievers",
                 "agents.utils.storages", "agents.utils.storages.vectordb_storages"):
        module = types.ModuleType(name)
        module.__path__ = []
        modules[name] = module
    embeddings = types.ModuleType("agents.utils.embeddings")

    class ForbiddenOnlineConstructor:
        def __init__(self, *args, **kwargs):
            raise AssertionError("Online embedding construction is forbidden")

    embeddings.BaseEmbedding = ForbiddenOnlineConstructor
    embeddings.OpenAIEmbedding = ForbiddenOnlineConstructor
    modules[embeddings.__name__] = embeddings

    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    with patch.dict(sys.modules, modules):
        vectors = load("agents.utils.storages.vectordb_storages.base",
                       root / "storages/vectordb_storages/base.py")
        for name in ("BaseVectorStorage", "VectorDBQuery", "VectorRecord"):
            setattr(modules["agents.utils.storages"], name, getattr(vectors, name))
        load("agents.utils.retrievers.base", root / "retrievers/base.py")
        unstructured = load("agents.utils.unstructured_io", root / "unstructured_io.py")
        retriever = load("agents.utils.retrievers.vector_retriever", root / "retrievers/vector_retriever.py")
    return vectors, unstructured, retriever


class ElementBoundaryValue:
    def __init__(self, text, metadata):
        self.text = text
        self.metadata = types.SimpleNamespace(to_dict=lambda: dict(metadata))

    def __str__(self):
        return self.text


class OfflineEmbedding:
    def __init__(self):
        self.batches = []

    def embed_list(self, objs):
        self.batches.append(objs)
        return [[0.25, 0.75] for _ in objs]


class LocalFileDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("AGENTS_SOURCE_ROOT", str(Path(__file__).resolve().parents[1]))
        cls.vectors, cls.unstructured, cls.retriever_module = load_components(root)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.embedding = OfflineEmbedding()
        self.retriever = self.retriever_module.VectorRetriever(self.embedding)
        vectors = self.vectors

        class OfflineStorage(vectors.BaseVectorStorage):
            def __init__(self):
                self.records = []

            def add(self, records, **kwargs):
                self.records.extend(records)

            def delete(self, ids, **kwargs):
                raise AssertionError("Deletion is outside this contract")

            def status(self):
                return vectors.VectorDBStatus(2, len(self.records))

            def query(self, query, **kwargs):
                raise AssertionError("Queries and empty-result policy are outside this contract")

            def clear(self):
                raise AssertionError("Collection management is outside this contract")

            def load(self):
                raise AssertionError("Database loading is forbidden")

            @property
            def client(self):
                raise AssertionError("No database client is used")

        self.storage = OfflineStorage()
        self.elements = [ElementBoundaryValue("partition boundary", {"page": 1})]
        self.chunks = [ElementBoundaryValue("first chunk", {"page": 1}),
                       ElementBoundaryValue("second chunk", {"page": 2})]
        self.opened_files = []
        self.read_bytes = []

        def partition_boundary(file, **kwargs):
            self.assertFalse(file.closed)
            self.opened_files.append(file)
            self.read_bytes.append(file.read())
            return self.elements

        self.partition = Mock(side_effect=partition_boundary)
        self.html = Mock(return_value=self.elements)
        self.chunk = Mock(return_value=self.chunks)
        sdk_modules = {}
        for name in ("unstructured", "unstructured.partition", "unstructured.chunking"):
            module = types.ModuleType(name)
            module.__path__ = []
            sdk_modules[name] = module
        for name, exports in {
            "unstructured.__version__": {"__version__": "0.10.30"},
            "unstructured.partition.auto": {"partition": self.partition},
            "unstructured.partition.html": {"partition_html": self.html},
            "unstructured.chunking.title": {"chunk_by_title": self.chunk},
        }.items():
            module = types.ModuleType(name)
            module.__dict__.update(exports)
            sdk_modules[name] = module
        # The real adapter's version check still executes using packaging.version.
        self.sdk_patch = patch.dict(sys.modules, sdk_modules)
        self.sdk_patch.start()
        self.addCleanup(self.sdk_patch.stop)

    def test_local_non_json_files_reach_real_adapter_and_record_path(self):
        # PDF fixture tests extension dispatch only, not PDF validity/parsing.
        for filename, content in (("notes.TXT", "你好 local text".encode("utf-8")),
                                  ("paper.pdf", b"%PDF-1.4\nSDK boundary fixture\n")):
            with self.subTest(filename=filename):
                self.storage.records.clear()
                path = self.directory / filename
                path.write_bytes(content)
                self.retriever.process(str(path), self.storage, max_characters=120)
                self.assertEqual(self.read_bytes[-1], content)
                self.assertTrue(self.opened_files[-1].closed)
                self.assertEqual(self.partition.call_args.kwargs.keys(), {"file"})
                self.chunk.assert_called_with(self.elements, max_characters=120)
                self.html.assert_not_called()
                self.assertEqual(self.embedding.batches[-1], ["first chunk", "second chunk"])
                self.assertEqual([r.payload["text"] for r in self.storage.records], ["first chunk", "second chunk"])
                self.assertTrue(all(isinstance(r, self.vectors.VectorRecord) for r in self.storage.records))
                self.assertTrue(all(r.payload["content path"] == str(path) for r in self.storage.records))
                self.assertEqual([r.payload["metadata"]["page"] for r in self.storage.records], [1, 2])
                self.assertTrue(all(isinstance(r.payload["metadata"].get("last_modified"), str) for r in self.storage.records))

    def test_missing_local_file_raises_file_error_before_embedding(self):
        path = self.directory / "missing.txt"
        with self.assertRaises(FileNotFoundError):
            self.retriever.process(str(path), self.storage)
        self.partition.assert_not_called()
        self.assertEqual(self.storage.records, [])

    def test_sdk_partition_failure_keeps_real_adapter_exception_chain(self):
        path = self.directory / "notes.txt"
        path.write_text("local text", encoding="utf-8")
        failure = ValueError("partition boundary failure")
        self.partition.side_effect = failure
        with self.assertRaisesRegex(Exception, "Failed to parse the unstructured file") as caught:
            self.retriever.process(str(path), self.storage)
        self.assertIs(caught.exception.__cause__, failure)
        self.assertTrue(self.partition.call_args.kwargs["file"].closed)
        self.assertEqual(self.storage.records, [])
        self.assertEqual(self.embedding.batches, [])

    def test_local_json_and_jsonl_keep_dedicated_loader(self):
        for filename in ("records.json", "records.JSON", "records.jsonl", "records.JSONL"):
            with self.subTest(filename=filename):
                self.storage.records.clear()
                path = self.directory / filename
                if filename.lower().endswith("jsonl"):
                    path.write_text('"first"\n\n"second"\n', encoding="utf-8")
                else:
                    path.write_text(json.dumps(["first", "second"]), encoding="utf-8")
                self.retriever.process(str(path), self.storage)
                self.assertEqual([r.payload["text"] for r in self.storage.records], ["first", "second"])
                self.assertTrue(all(r.payload["content path"] == str(path) for r in self.storage.records))
                self.partition.assert_not_called()
                self.chunk.assert_not_called()

    def test_non_list_json_retains_existing_error(self):
        path = self.directory / "object.json"
        path.write_text('{"text":"value"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Expected a list"):
            self.retriever.process(str(path), self.storage)
        self.partition.assert_not_called()

    def test_url_with_json_suffix_keeps_url_dispatch(self):
        url = "https://example.invalid/records.json"
        self.retriever.process(url, self.storage, combine_text_under_n_chars=25)
        self.html.assert_called_once_with(url=url)
        self.partition.assert_not_called()
        self.chunk.assert_called_once_with(self.elements, combine_text_under_n_chars=25)
        self.assertTrue(all(r.payload["content path"] == url for r in self.storage.records))


if __name__ == "__main__":
    unittest.main()
