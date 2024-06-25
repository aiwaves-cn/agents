from enum import Enum

from .key_value_storages.base import BaseKeyValueStorage
from .key_value_storages.in_memory import InMemoryKeyValueStorage
from .key_value_storages.json import JsonStorage
from .vectordb_storages.base import (
    BaseVectorStorage,
    VectorRecord,
    VectorDBQuery,
    VectorDBQueryResult,
)
from .vectordb_storages.qdrant import QdrantStorage
from .vectordb_storages.milvus import MilvusStorage

__all__ = [
    "BaseKeyValueStorage",
    "InMemoryKeyValueStorage",
    "JsonStorage",
    "VectorRecord",
    "BaseVectorStorage",
    "VectorDBQuery",
    "VectorDBQueryResult",
    "QdrantStorage",
    "MilvusStorage",
]


class StorageType(Enum):
    MILVUS = "milvus"
    QDRANT = "qdrant"
