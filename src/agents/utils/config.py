import json
from abc import ABC
from typing import Union


class Config(ABC):

    required_fields = []

    def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
        self.config_dict: dict = self.load(config_path_or_dict)

    def _validate_config(self):
        missing = [
            field for field in self.required_fields if field not in self.config_dict
        ]
        if missing:
            raise ValueError(f"Missing required config fields: {missing}")

    def load(self, config_path_or_dict: Union[str, dict]) -> dict:
        if not config_path_or_dict:
            return {}

        try:
            if isinstance(config_path_or_dict, str):
                with open(config_path_or_dict, encoding="utf-8") as f:
                    config = json.load(f)
            elif isinstance(config_path_or_dict, dict):
                config = config_path_or_dict
            else:
                raise TypeError("config_path_or_dict should be a path or a dict")
        except Exception as e:
            raise IOError(f"An error occurred while loading the configuration: {e}")

        return config

    def dump(self, save_path):
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise IOError(f"An error occurred while saving the configuration: {e}")

    def dumps(self):
        try:
            return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)
        except Exception as e:
            raise ValueError(
                f"An error occurred while serializing the configuration: {e}"
            )

    def to_dict(self) -> dict:
        return {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_") and k != "config_dict"
        }

    @classmethod
    def generate_config(cls):
        raise NotImplementedError

    @staticmethod
    def check_config():
        raise NotImplementedError
