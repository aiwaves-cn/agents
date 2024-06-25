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
"""The task module is responsible for the task that the agent should solve"""
import copy
import json
from typing import Union
from ..agents import LLMConfig, OpenAILLM

from ..utils.config import Config
from ..utils.prompts import TASK_CONFIG_GENERATION_PROMPT_TEMPLATE


class TaskConfig(Config):
    required_fields = []

    def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
        super().__init__(config_path_or_dict)
        self._validate_config()

        self.task_name = self.config_dict.get("task_name", None)
        self.task_type = self.config_dict.get("task_type", None)
        self.task_description = self.config_dict.get("task_description", None)

    @classmethod
    def generate_config(cls, query):
        llm_config = {
            "LLM_type": "OpenAI",
            "model": "gpt-4-turbo-2024-04-09",
            "temperature": 0.3,
            "log_path": "logs/generate_config/task",
        }
        llm = OpenAILLM(LLMConfig(llm_config))
        system_prompt = "You are a helpful assistant designed to output JSON."
        last_prompt = TASK_CONFIG_GENERATION_PROMPT_TEMPLATE.format(query=query)

        response, content = llm.get_response(
            chat_messages=None,
            system_prompt=system_prompt,
            last_prompt=last_prompt,
            response_format={"type": "json_object"},
        )
        # Converting the JSON format string to a JSON object
        json_config = json.loads(content.strip("`").strip("json").strip())

        return cls(
            config_path_or_dict={
                "task_name": json_config["task_name"],
                "task_type": json_config["task_type"],
                "task_description": json_config["task_description"],
            }
        )


class Task:
    def __init__(self, config: TaskConfig):
        self.config = config
        self.task_name = self.config.task_name
        self.task_type = self.config.task_type
        self.task_description = self.config.task_description

    def to_config(self) -> TaskConfig:
        return TaskConfig(config_path_or_dict=self.config.to_dict())

    def dump(self, save_path):
        save_config: TaskConfig = copy.deepcopy(self.config)

        # 运行时这些字段可能发生变化，根据此类的实际信息进行更新
        save_config.task_name = self.task_name
        save_config.task_type = self.task_type
        save_config.task_description = self.task_description

        save_config.dump(save_path)
