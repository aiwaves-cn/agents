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
from component import *
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
                 extract_words: str = "",
                 next_nodes: dict = {},
                 done=False,
                 user_input:str= "",
                 **components):
        """_summary_

        Args:
            tool (Tool, optional): _description_. Defaults to None.
            node_type (str, optional): _description_. Defaults to None.
            extract_words (str, optional): _description_. Defaults to "".
            next_nodes (dict, optional): _description_. Defaults to {}.
            done (bool, optional): _description_. Defaults to False.
            user_input (str, optional): _description_. Defaults to "".
            components(dict) : "style"  *"task"*  "rule" "demonstration"  "input" "kb_tool" *"output"*
        """
        self.prompt = ""
        if tool != None:
            tool = Tool(type)
        self.node_type = node_type
        self.next_nodes = next_nodes
        self.components = components
        self.user_input = user_input
        self.system_prompt,self.last_prompt= self.get_prompt()
        self.extract_words = extract_words
        self.done = done

    def set_user_input(self,user_input):
        self.user_input = user_input


    def get_prompt(self):
        prompt = ""
        last_prompt = ""
        for value in self.components.values():
            if isinstance(value,InputComponent) or isinstance(value,KnowledgeBaseComponent):
                value.input = self.user_input
                prompt = prompt +"\n" + value.get_prompt()
            elif not isinstance(value,OutputComponent):
                prompt =prompt +"\n" + value.get_prompt()
            else:
                last_prompt += value.get_prompt()
        return prompt,last_prompt
    
