import os
import json
from copy import deepcopy
from typing import Any, List
from abc import ABC, abstractmethod

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")


class BaseDataset(ABC):

    def __init__(self, data: List[Any]):
        """
        Initialize the dataset with a list of data items.

        Args:
        data (List[Any]): A list of data items.
        """
        self.data = data
        self.metric_name = "score"
        self.metric_description = ""

    def load(cls, file_path: str):
        """
        Load data from a JSON file.

        Args:
        file_path (str): The path to the JSON file.

        Returns:
        List[Any]: The data loaded from the file.

        Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No file found at the specified path: {file_path}")

        # Determine the file format based on its extension
        _, file_extension = os.path.splitext(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                # Handle JSONL: read each line as a separate JSON object
                if file_extension.lower() == ".jsonl":
                    data = [json.loads(line.strip()) for line in file if line.strip()]
                # Handle JSON: read the entire file as a single JSON object
                elif file_extension.lower() == ".json":
                    data = json.load(file)
                else:
                    raise ValueError(
                        "Unsupported file format. Please provide a .json or .jsonl file."
                    )
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding JSON from {file_path}: {e}")

        return data

    @abstractmethod
    def __getitem__(self, idx: int) -> Any:
        """
        Abstract method to get an item by index.

        Args:
        idx (int): The index of the item.

        Returns:
        The item at the specified index.
        """
        pass

    @abstractmethod
    def get_case_dict(self, idx: int) -> dict:
        """
        Abstract method to get a case-specific dict by index.

        Args:
        idx (int): The index of the case-specific dict.

        Returns:
        The case-specific dict at the specified index.
        """
        pass

    def __len__(self) -> int:
        """
        Return the number of items in the dataset.

        Returns:
        The number of items.
        """
        return len(self.data)

    def to_list(self) -> List[Any]:
        """
        Return a deep copy of the dataset's data.

        Returns:
        A deep copy of the data list.
        """
        return deepcopy(self.data)

    def evaluate(self):
        """
        Evaluate the dataset.

        Raises:
        NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError
