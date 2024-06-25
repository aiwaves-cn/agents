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
"""
The Memory class is a class that represents the memory of an agent.
It is used to store the agent's long-term experiences and knowledge, 
and can be updated in the optimization stage.
"""
import os
import torch
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional
from text2vec import semantic_search

from .llm import completion_with_backoff
from ..utils.storages import (
    InMemoryKeyValueStorage,
    JsonStorage,
)
from ..utils.embeddings import get_embedding
from ..utils.prompts import *


class Memory(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_memory():
        pass

    @staticmethod
    def encode_memory(massages: list, agent_name=None):
        """Convert a sequence of messages to strings and encode them into one string."""
        encoded_memory = ""
        for message in massages:
            name = message.get("name")
            if agent_name and name and agent_name == name:
                name = f"you({agent_name})"
            role, content = message["role"], message["content"]
            single_message = SINGLE_MESSAGE_TEMPLATE.format(
                name=name, role=role, content=content
            )
            encoded_memory += "\n" + single_message
        return encoded_memory

    @staticmethod
    def get_relevant_memory(query: str, history: list, embeddings: torch.Tensor):
        """
        Retrieve a list of key history entries based on a query using semantic search.

        Args:
            query (str): The input query for which key history is to be retrieved.
            history (list): A list of historical key entries.
            embeddings (numpy.ndarray): An array of embedding vectors for historical entries.

        Returns:
            list: A list of key history entries most similar to the query.
        """
        top_k = eval(os.environ["TOP_K"]) if "TOP_K" in os.environ else 5
        relevant_memory = []
        query_embedding = get_embedding(query)
        hits = semantic_search(
            query_embedding, embeddings, top_k=min(top_k, embeddings.shape[0])
        )
        hits = hits[0]
        for hit in hits:
            matching_idx = hit["corpus_id"]
            try:
                relevant_memory.append(history[matching_idx])
            except:
                return []
        return relevant_memory


class ShortTermMemory(Memory):
    """An implementation of the :obj:`Memory` abstract base class for
    maintaining a record of chat histories.

    Args:
        config (dict): A dictionary containing configuration
        storage (BaseKeyValueStorage, optional): A storage mechanism for
            storing chat history. If `None`, an :obj:`InMemoryKeyValueStorage`
            will be used. (default: :obj:`None`)
        window_size (int, optional): Specifies the number of recent chat
            messages to retrieve. If not provided, the entire chat history
            will be retrieved. (default: :obj:`None`)
    """

    def __init__(
        self,
        config: dict = {},
        messages: list = [],
        storage: InMemoryKeyValueStorage = None,
        window_size: Optional[int] = None,
    ):
        self.config = config
        self.storage = storage or InMemoryKeyValueStorage()
        self.storage.save(
            messages
        )  # list of gpt-format messages e.g.  [{"name": "" , "role": "", "content": ""}]
        self.window_size = window_size

    def __len__(self):
        return len(self.storage)

    def get_memory(self):
        return self.storage.load()

    def append_memory(self, message):
        self.storage.save([message])

    def update_memory(self, config, messages):
        self.config = config
        self.storage.clear()
        self.storage.save(messages)

    def get_memory_string(self, agent_name=None):
        encoded_memory = Memory.encode_memory(self.get_memory(), agent_name)
        return encoded_memory

    def get_memory_embedding(self):
        encoded_memory = self.get_memory_string()
        embed = get_embedding(encoded_memory)
        return embed

    def get_memory_summary(self):
        encoded_memory = self.get_memory_string()

        # Using GPT-3.5 to summarize the conversation
        response = completion_with_backoff(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": SUMMARY_PROMPT_TEMPLATE.format(
                        conversation=encoded_memory
                    ),
                },
            ],
            temperature=0,
        )
        summary = response.choices[0].message["content"].strip()
        return summary

    def to_dict(self):
        return {
            "config": self.config,
            "memory": self.get_memory(),
        }

    @staticmethod
    def load_from_json(json_dict):
        return ShortTermMemory(
            config=json_dict["config"],
            messages=json_dict["memory"],
        )


class LongTermMemory(Memory):

    def __init__(
        self,
        config: dict,
        json_path: str,
        chunk_list: list = [],
        storage: JsonStorage = None,
        window_size: Optional[int] = 3,
    ):
        self.config = config
        self.json_path = json_path
        if storage:
            self.storage = storage
        else:
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            self.storage = JsonStorage(Path(json_path))
            self.storage.save(chunk_list)
        self.window_size = window_size

    def get_memory(self):
        return self.storage.load()

    def update_memory(self, config, chunk_list):
        self.config = config
        self.storage.clear()
        self.storage.save(chunk_list)

    def append_memory(self, chunk):
        self.storage.save([chunk])

    def append_memory_from_short_term_memory(self, short_term_memory: ShortTermMemory):
        if len(short_term_memory) >= self.window_size:
            memory = short_term_memory.get_memory()
            self.storage.save([Memory.encode_memory(memory[-self.window_size :])])

    def to_dict(self):
        return {
            "config": self.config,
            "memory": self.get_memory(),
        }

    @staticmethod
    def load_from_json(json_dict):
        return LongTermMemory(
            config=json_dict["config"],
            chunk_list=json_dict["memory"],
        )
