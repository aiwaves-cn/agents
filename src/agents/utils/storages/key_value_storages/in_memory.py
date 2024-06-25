from copy import deepcopy
from typing import Any, Dict, List

from .base import BaseKeyValueStorage


class InMemoryKeyValueStorage(BaseKeyValueStorage):
    r"""A concrete implementation of the :obj:`BaseKeyValueStorage` using
    in-memory list. Ideal for temporary storage purposes, as data will be lost
    when the program ends.
    """

    def __init__(self) -> None:
        self.memory_list: List[Dict] = []

    def __len__(self) -> int:
        return len(self.memory_list)

    def save(self, records: List[Dict[str, Any]]) -> None:
        r"""Saves a batch of records to the key-value storage system.

        Args:
            records (List[Dict[str, Any]]): A list of dictionaries, where each
                dictionary represents a unique record to be stored.
        """
        self.memory_list.extend(deepcopy(records))

    def load(self) -> List[Dict[str, Any]]:
        r"""Loads all stored records from the key-value storage system.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                represents a stored record.
        """
        return deepcopy(self.memory_list)

    def clear(self) -> None:
        r"""Removes all records from the key-value storage system."""
        self.memory_list.clear()
