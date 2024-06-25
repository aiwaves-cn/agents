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
"""The Toolkit class is a class that represents the toolkit of an agent.
It can be updated in the optimization stage.
"""
import json
from typing import Dict, List

from ..tools import Tool, AVAILABLE_TOOLS


class Toolkit:
    def __init__(self, config: dict, **kwargs):
        self.config = config
        self.tools: Dict[str, Tool] = kwargs.get("tools", {})
        self.tool_specifications: List[dict] = kwargs.get("tool_specifications", None)

    @classmethod
    def from_config(cls, config_path_or_dict):
        if isinstance(config_path_or_dict, str):
            with open(config_path_or_dict, encoding="utf-8") as f:
                config = json.load(f)
        elif isinstance(config_path_or_dict, dict):
            config = config_path_or_dict
        else:
            raise ValueError("config_path_or_dict should be a path or a dict")

        tools = {}
        tool_specifications = []
        for tool_name, tool_config in config.items():
            if tool_name in AVAILABLE_TOOLS:
                tool: Tool = AVAILABLE_TOOLS[tool_name](**tool_config)
                tools[tool_name] = tool
                tool_specifications.append(
                    {
                        "type": tool.type,
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters,
                        },
                    }
                )
            else:
                raise ValueError(
                    f"Tool {tool_name} is not available, the available tools are {AVAILABLE_TOOLS.keys()}"
                )
        if len(tool_specifications) == 0:
            tool_specifications = None

        toolkit = cls(
            config=config, tools=tools, tool_specifications=tool_specifications
        )
        return toolkit

    def to_dict(self):
        return {
            "tools": {
                tool_name: tool.to_dict() for tool_name, tool in self.tools.items()
            },
            "tool_specifications": self.tool_specifications,
        }

    def generate_config():
        # generate the config (especially the prompts)
        pass
