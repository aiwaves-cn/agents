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
"""The Environment class is a class that represents the environment of an agent team, 
like an office for a team of agents.
The agents in the team have shared memory and toolkit, 
those are stored in the environment.
The communication between the agents is also done through the environment.
"""
from .memory import ShortTermMemory, LongTermMemory
from .toolkit import Toolkit
from typing import Dict, Union

from ..utils.config import Config


class EnvironmentConfig(Config):

    required_fields = []

    def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
        super().__init__(config_path_or_dict)
        self._validate_config()

        self.environment_type: str = self.config_dict.get(
            "environment_type", "cooperative"
        )
        assert self.environment_type in ["cooperative", "competitive"]
        self.shared_memory: Dict[str, dict] = self.config_dict.get(
            "shared_memory", None
        )
        self.shared_toolkit: dict = self.config_dict.get("shared_toolkit", None)


class Environment:
    def __init__(self, config: EnvironmentConfig):
        self.config = config
        self.environment_type = self.config.environment_type
        if self.config.shared_memory:
            short_term_memory = ShortTermMemory(
                config=self.config.shared_memory.get("short_term_memory", {}),
                messages=[],
            )
            long_term_memory = LongTermMemory(
                config=self.config.shared_memory.get("long_term_memory", {}),
                json_path=f"memory/environment.jsonl",
                chunk_list=[],
            )
            self.shared_memory = {
                "summary": self.config.shared_memory.get("summary", ""),
                "short_term_memory": short_term_memory,
                "long_term_memory": long_term_memory,
            }
        else:
            self.shared_memory = {
                "summary": "",
                "short_term_memory": ShortTermMemory(config={}, messages=[]),
                "long_term_memory": LongTermMemory(
                    config={}, json_path=f"memory/environment.jsonl", chunk_list=[]
                ),
            }
        self.shared_toolkit: Toolkit = (
            Toolkit.from_config(self.config.shared_toolkit)
            if self.config.shared_toolkit
            else None
        )

    def summary(self):
        pass

    def to_dict(self):
        # FIXME: Environment to_dict error
        return {
            "environment_type": self.environment_type,
            "shared_memory": {
                "summary": self.shared_memory["summary"],
                "short_term_memory": self.shared_memory["short_term_memory"].to_dict(),
                "long_term_memory": self.shared_memory["long_term_memory"].to_dict(),
            },
            "shared_toolkit": self.shared_toolkit.to_dict(),
        }

    @staticmethod
    def load_from_json(json_data):
        # FIXME: Environment load from json error
        # environment type 和 config通过原始加载方法就能导入
        loaded_environment = Environment.from_config(json_data["config"])

        # 加载具体的memory
        loaded_environment.shared_memory["summary"] = json_data["shared_memory"][
            "summary"
        ]
        loaded_environment.shared_memory["short_term_memory"] = (
            ShortTermMemory.load_from_json(
                json_data["shared_memory"]["short_term_memory"]
            )
        )
        loaded_environment.shared_memory["long_term_memory"] = (
            LongTermMemory.load_from_json(
                json_data["shared_memory"]["long_term_memory"]
            )
        )
        return loaded_environment
