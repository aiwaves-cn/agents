import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseKeyValueStorage


class JsonStorage(BaseKeyValueStorage):
    r"""A concrete implementation of the :obj:`BaseKeyValueStorage` using JSON
    files. Allows for persistent storage of records in a human-readable format.

    Args:
        path (Path, optional): Path to the desired JSON file. If `None`, a
            default path `./chat_history.json` will be used.
            (default: :obj:`None`)
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self.json_path = path or Path("./chat_history.json")
        self.json_path.touch()

    def save(self, records: List[Dict[str, Any]]) -> None:
        r"""Saves a batch of records to the key-value storage system.

        Args:
            records (List[Dict[str, Any]]): A list of dictionaries, where each
                dictionary represents a unique record to be stored.
        """
        with self.json_path.open("a") as f:
            f.writelines([json.dumps(r, cls=json.JSONEncoder) + "\n" for r in records])

    def load(self) -> List[Dict[str, Any]]:
        r"""Loads all stored records from the key-value storage system.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                represents a stored record.
        """
        with self.json_path.open("r") as f:
            return [json.loads(r) for r in f.readlines()]

    def clear(self) -> None:
        r"""Removes all records from the key-value storage system."""
        with self.json_path.open("w"):
            pass
