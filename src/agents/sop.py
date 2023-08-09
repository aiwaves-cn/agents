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
    """
    input:the json of the sop
    output: a sop graph
    """
    def __init__(self, json_path):
        with open(json_path) as f:
            sop = json.load(f)
        self.sop = sop
        self.root = None
        self.temperature = sop["temperature"] if "temperature" in sop else 0.3
        self.active_mode = sop["active_mode"] if "active_mode" in sop else False
        self.log_path = sop["log_path"] if "log_path" in sop else "logs"
        
        self.shared_memory = {}
        self.nodes = self.init_nodes(sop)
        self.init_relation(sop)

    def init_nodes(self, sop):
        # node_sop: a list of the node
        node_sop = sop["nodes"]
        nodes_dict = {}
        for node in node_sop.values():
            name = node["name"]
            node_type = node["node_type"]
            is_interactive = node["is_interactive"]
            transition_rule = node["transition_rule"]
            agent_states = self.init_states(node["agent_states"])
            config = node["config"]
            now_node = Node(name=name,
                            node_type=node_type,
                            is_interactive= is_interactive,
                            config = config,
                            transition_rule = transition_rule,
                            agent_states = agent_states)
            nodes_dict[name] = now_node
            if "root" in node.keys() and node["root"]:
                self.root = now_node
        return nodes_dict

    def init_states(self, agent_states_dict: dict):
        agent_states = {}
        for key, value in agent_states_dict.items():
            component_dict = {}
            for component , component_args in value.items():
                if component:
                    if component == "style":
                        component_dict["style"] = StyleComponent(
                            component_args["agent"], component_args["style"])
                    elif component == "task":
                        component_dict["task"] = TaskComponent(component_args["task"])
                    elif component == "rule":
                        component_dict["rule"] = RuleComponent(component_args["rule"])
                    elif component == "demonstration":
                        component_dict["demonstration"] = DemonstrationComponent(
                            component_args["demonstration"])
                    elif component == "output":
                        component_dict["output"] = OutputComponent(component_args["output"])
                    elif component == "cot":
                        component_dict["cot"] = CoTComponent(component_args["demonstration"])                    
                    elif component == "Information_KnowledgeComponent":
                        component_dict[
                            "knowledge"] = Information_KnowledgeComponent()
                    elif component == "kb":
                        component_dict["tool"] = KnowledgeBaseComponent(
                            component_args["knowledge_base"])
            agent_states[key] = component_dict
        return agent_states

    def init_relation(self, sop):
        relation = sop["relation"]
        for key, value in relation.items():
            for keyword, next_node in value.items():
                self.nodes[key].next_nodes[keyword] = self.nodes[next_node]


class Node():

    def __init__(self,
                 name: str = None,
                 agent_states:dict = None,
                 is_interactive=False,
                 config:list = None,
                 transition_rule:str = None):
        
        self.next_nodes = {}
        self.agent_states = agent_states
        self.is_interactive = is_interactive
        self.name = name
        self.config = config
        self.transition_rule = transition_rule
    
    def get_state(self,role,args_dict):
        system_prompt,last_prompt = self.compile(role,args_dict)
        current_role_state = f"目前的角色为：{role}，它的system_prompt为{system_prompt},last_prompt为{last_prompt}"
        return current_role_state
    
    
    def compile(self,role,args_dict:dict):
        components = self.agent_states[role]
        system_prompt = ""
        last_prompt = ""
        res_dict = {}
        for component_name in self.config:
            component = components[component_name]
            if isinstance(component,OutputComponent):
                last_prompt = last_prompt + "\n" +  component.get_prompt(args_dict)
            elif isinstance(component,PromptComponent):
                system_prompt = system_prompt + "\n" + component.get_prompt(args_dict)
            elif isinstance(component,ToolComponent):
                response = component.func(args_dict)
                args_dict.update(response)
                res_dict.update(response)
        return system_prompt,last_prompt,res_dict



