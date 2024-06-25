# coding=utf-8
# Copyright 2024 The AIWaves Inc. team.

#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Optional, Union

from ..utils.retrievers import AutoRetriever
from ..utils.embeddings import EmbeddingModelType, BaseEmbedding, OpenAIEmbedding
from ..utils.storages import StorageType
from ..utils.config import Config

DEFAULT_TOP_K_RESULTS = 1
DEFAULT_SIMILARITY_THRESHOLD = 0.75


class KnowledgeBaseConfig(Config):
    def __init__(self, config_path_or_dict: Union[str, dict]):
        super().__init__(config_path_or_dict)
        self.content_input_paths: Union[str, List[str]] = self.config_dict.get(
            "content_input_paths", []
        )
        self.url: Optional[str] = self.config_dict.get("url", "http://localhost:19530")
        self.api_key: Optional[str] = self.config_dict.get("api_key", "root:Milvus")
        self.vector_storage_local_path: Optional[str] = self.config_dict.get(
            "vector_storage_local_path", None
        )

        storage_type: Optional[str] = self.config_dict.get("storage_type", "milvus")
        if storage_type == "milvus":
            self.storage_type = StorageType.MILVUS
        elif storage_type == "qdrant":
            self.storage_type = StorageType.QDRANT
        else:
            raise KeyError(
                f"Invalid storage type {storage_type}, the valid options are 'milvus' and 'qdrant'."
            )

        embedding_model: Optional[BaseEmbedding] = self.config_dict.get(
            "embedding_model", "text-embedding-3-small"
        )
        if embedding_model == "text-embedding-3-small":
            self.embedding_model = OpenAIEmbedding(
                model_type=EmbeddingModelType.SMALL_3
            )
        elif embedding_model == "text-embedding-3-large":
            self.embedding_model = OpenAIEmbedding(
                model_type=EmbeddingModelType.LARGE_3
            )
        elif embedding_model == "text-embedding-ada-002":
            self.embedding_model = OpenAIEmbedding(model_type=EmbeddingModelType.ADA_2)
        else:
            raise KeyError(
                f"Invalid embedding model {embedding_model}, the valid options are 'text-embedding-3-small', 'text-embedding-3-large' and 'text-embedding-ada-002'."
            )

        self.top_k: Optional[int] = self.config_dict.get("top_k", DEFAULT_TOP_K_RESULTS)
        self.similarity_threshold: Optional[float] = self.config_dict.get(
            "similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD
        )
        self.return_detailed_info: Optional[bool] = self.config_dict.get(
            "return_detailed_info", False
        )


class KnowledgeBase:

    def __init__(self, config: KnowledgeBaseConfig):
        self.config = config
        self.retriever = AutoRetriever(
            url_and_api_key=(self.config.url, self.config.api_key),
            vector_storage_local_path=self.config.vector_storage_local_path,
            storage_type=self.config.storage_type,
            embedding_model=self.config.embedding_model,
        )
        self.content_input_paths = self.config.content_input_paths
        self.top_k = self.config.top_k
        self.similarity_threshold = self.config.similarity_threshold
        self.return_detailed_info = self.config.return_detailed_info

        name = "knowledge_base_retriever"
        description = "Performs an auto local retriever for information. Given a query, this function will retrieve the information from the local vector storage, and return the retrieved information back. It is useful for information retrieve."
        parameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Question you want to be answered.",
                }
            },
            "required": ["query"],
        }
        self.kb_specification = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }

    def retrieve(self, query: str):
        output = self.retriever.run_vector_retriever(
            query=query,
            content_input_paths=self.content_input_paths,
            top_k=self.top_k,
            similarity_threshold=self.similarity_threshold,
            return_detailed_info=self.return_detailed_info,
        )
        return output["retrieved context"]

    def retrieve_from_file(
        self,
        query: str,
        file_path: str,
        top_k: int = 1,
        similarity_threshold: float = 0.3,
        return_detailed_info: bool = False,
    ):
        output = self.retriever.run_vector_retriever(
            query=query,
            content_input_paths=[file_path],
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            return_detailed_info=return_detailed_info,
        )
        return output["retrieved context"]
