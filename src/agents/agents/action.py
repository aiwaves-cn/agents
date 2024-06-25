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
"""The Action class is a class that represents an action of an agent."""
import litellm
from typing import Dict, Union

from ..utils.config import Config


class ActionConfig(Config):
    required_fields = [
        "agent_name",
        "agent_role",
        "is_user",
        "is_node_begin",
        "is_agent_begin",
        "used_prompt_templates",
        "prompts_order",
        "system_prompt",
        "last_prompt",
        "tools_results_dict",
        "history_messages",
        "response",
        "content",
        "latency",
        "start_time_ms",
        "end_time_ms",
    ]

    def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
        super().__init__(config_path_or_dict)
        self._validate_config()

        self.agent_name: str = self.config_dict["agent_name"]
        self.agent_role: str = self.config_dict["agent_role"]
        self.is_user: bool = self.config_dict["is_user"]
        self.is_node_begin: bool = self.config_dict["is_node_begin"]
        self.is_agent_begin: bool = self.config_dict["is_agent_begin"]
        self.used_prompt_templates: dict = self.config_dict["used_prompt_templates"]
        self.prompts_order: list = self.config_dict["prompts_order"]
        self.system_prompt: str = self.config_dict["system_prompt"]
        self.last_prompt: str = self.config_dict["last_prompt"]
        self.tools_results_dict: Dict[str, dict] = self.config_dict["tools_results_dict"]
        self.history_messages: list = self.config_dict["history_messages"]
        self.response: Union[litellm.utils.ModelResponse, dict] = self.config_dict["response"]
        self.content: str = self.config_dict["content"]
        self.latency: float = self.config_dict["latency"]
        self.start_time_ms: int = self.config_dict["start_time_ms"]
        self.end_time_ms: int = self.config_dict["end_time_ms"]


class Action:
    """
    The basic action unit of agent
    """

    def __init__(self, config: ActionConfig):
        self.config = config

        # agent相关
        self.agent_name = self.config.agent_name
        self.agent_role = self.config.agent_role
        self.is_user = self.config.is_user

        # node相关
        self.is_node_begin = self.config.is_node_begin
        self.is_agent_begin = self.config.is_agent_begin

        # 输入输出相关
        self.used_prompt_templates = self.config.used_prompt_templates
        self.prompts_order = self.config.prompts_order
        self.system_prompt = self.config.system_prompt
        self.last_prompt = self.config.last_prompt
        self.tools_results_dict = self.config.tools_results_dict
        self.history_messages = self.config.history_messages

        # prompt输入大模型后生成的回复，是一个response对象，但是序列化为json后此项信息全部保留到了response_json中
        self.response = self.config.response
        # response对象中的content，即大模型生成的回复的字符串对象
        self.content = self.config.content

        if isinstance(self.response, litellm.utils.ModelResponse):
            # response对象的json格式
            self.response_json = self.response.json()
            # prompt中的token数量
            self.token_usage = self.response_json.get("usage")
        else:
            self.response_json = None
            self.token_usage = None

        # 时间相关
        self.latency = self.config.latency
        self.start_time_ms = self.config.start_time_ms
        self.end_time_ms = self.config.end_time_ms

    def to_dict(self):
        return {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "is_user": self.is_user,
            "is_node_begin": self.is_node_begin,
            "is_agent_begin": self.is_agent_begin,
            "content": self.content,
            "used_prompt_templates": self.used_prompt_templates,
            "prompts_order": self.prompts_order,
            "system_prompt": self.system_prompt,
            "last_prompt": self.last_prompt,
            "history_messages": self.history_messages,
            "tools_results_dict": self.tools_results_dict,
            "response_json": self.response_json,
            "token_usage": self.token_usage,
            "latency": self.latency,
            "start_time_ms": self.start_time_ms,
            "end_time_ms": self.end_time_ms,
        }
