from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseKeyValueStorage(ABC):
    r"""An abstract base class for key-value storage systems. Provides a
    consistent interface for saving, loading, and clearing data records without
    any loss of information.

    An abstract base class designed to serve as a foundation for various
    key-value storage systems. The class primarily interacts through Python
    dictionaries.

    This class is meant to be inherited by multiple types of key-value storage
    implementations, including, but not limited to, JSON file storage, NoSQL
    databases like MongoDB and Redis, as well as in-memory Python dictionaries.
    """

    @abstractmethod
    def save(self, records: List[Dict[str, Any]]) -> None:
        r"""Saves a batch of records to the key-value storage system.

        Args:
            records (List[Dict[str, Any]]): A list of dictionaries, where each
                dictionary represents a unique record to be stored.
        """
        pass

    @abstractmethod
    def load(self) -> List[Dict[str, Any]]:
        r"""Loads all stored records from the key-value storage system.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                represents a stored record.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        r"""Removes all records from the key-value storage system."""
        pass
