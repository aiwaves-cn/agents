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
class SOP:
    def __init__(self,json_path):
        with open(json_path) as f:
            sop = json.load(f)
        self.root = None
        self.nodes = self.init_nodes(sop)
        self.init_relation(sop)
        
    
    def init_nodes(self,sop):
        node_sop = sop["node"]
        nodes_dict = {}
        for i,node in enumerate(node_sop):
            node = node_sop[node]
            name = node["name"]
            node_type = node["node_type"]
            extract_word = node["extract_word"]
            done = node["done"]
            components_dict = self.init_components(node["components"])
            
            now_node = Node(name=name,node_type=node_type,extract_words=extract_word,done=done,components=components_dict)
            nodes_dict[name] = now_node
            if i == 0:
                self.root = now_node
        return nodes_dict
            
    
    def init_components(self,components_dict:dict):
        args_dict = {}
        for key,value in components_dict.items():
            value = components_dict[key]
            if value:
                if key == "style":
                    args_dict["style"] = StyleComponent(value["agent"],value["style"])
                elif key == "task":
                    args_dict["task"] = TaskComponent(value["task"])
                elif key == "rule":
                    args_dict["rule"] = RuleComponent(value["rule"])
                elif key == "demonstration":
                    args_dict["demonstration"] = DemonstrationComponent(value["demonstration"])
                elif key == "input":
                    args_dict["input"] = InputComponent()
                elif key == "tool":
                    args_dict["tool"] = KnowledgeBaseComponent(value["knowledge_base"])
                elif key == "output":
                    args_dict["output"] = OutputComponent(value["output"])
        return args_dict
                    
    def init_relation(self,sop):
        relation = sop["relation"]
        for key,value in relation.items():
            for keyword,next_node in value.items():
                self.nodes[key].next_nodes[keyword] = self.nodes[next_node]
            

class Tool():

    def __init__(self, type, **args):
        if type == "kb":
            database = database


class Node():

    def __init__(self,
                 name:str = None,
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
            components(dict) : "style"  *"task"*  "rule" "demonstration"  "input" "tool" *"output"*
        """
        self.prompt = ""
        self.node_type = node_type
        self.next_nodes = next_nodes
        self.components = components["components"]
        self.user_input = user_input
        self.system_prompt,self.last_prompt= self.get_prompt()
        self.extract_words = extract_words
        self.done = done
        self.name = name
        
    def set_user_input(self,user_input):
        self.user_input = user_input


    def get_prompt(self):
        prompt = ""
        last_prompt = ""
        for value in self.components.values():
            if isinstance(value,InputComponent) or isinstance(value,KnowledgeBaseComponent):
                value.input = self.user_input
                prompt = prompt +"\n" + value.get_prompt()
            elif isinstance(value,OutputComponent):
                last_prompt += value.get_prompt()
            else:
                prompt =prompt +"\n" + value.get_prompt()
        return prompt,last_prompt
    
