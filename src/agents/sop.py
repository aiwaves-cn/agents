# coding=utf-8
# Copyright 2023  The AIWaves Inc. team.

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

"""standard operation procedure of an LLM Autonomous agent"""
from abc import abstractmethod
import json
from utils import *
class SOP():

    def __init__(self,file_path):
        self.nodes = self.load_json(file_path)

    def load_json(file_path):
        json.loads(file_path)

class Tool():

    def __init__(self, type, **args):
        if type == "kb":
            database = database


class Node():

    def __init__(self,
                 tool: Tool = None,
                 node_type: str = None,
                 last_prompt: str = None,
                 need_response: bool = None,
                 extract_words: str = None,
                 next_nodes: dict = None,
                 done=False,
                 **args):
        self.prompt = ""
        if tool != None:
            tool = Tool(type)
            tool_prompt = tool.get_prompt()
        self.node_type = node_type
        self.next_nodes = next_nodes
        self.args = args
        self.system_prompt = self.get_prompt()
        self.last_prompt = last_prompt
        self.extract_words = extract_words
        self.need_response = need_response
        self.done = done

    def get_component(self):
        components = []
        for i in self.args:
            if i in ["judge", "extract", "style", "rule", "demonstration"]:
                components.append(self.args[i])
        return components

    def get_prompt(self):
        components = self.get_component()
        prompt = ""
        for i in components:
            prompt += i.prompt
        return prompt

    def add_component_system(self, component):
        self.system_prompt += component.get_prompt()

    def add_component_last(self, component):
        self.last_prompt += component.get_prompt()
        
    def set_system_prompt(self,prompt):
        self.system_prompt = prompt

    def set_last_prompt(self,prompt):
        self.last_prompt = prompt