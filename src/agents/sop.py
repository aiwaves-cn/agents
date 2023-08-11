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
import json
from component import *
import time

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

        self.shared_memory = {"chat_history":[]}
        self.controller_dict = {}
        self.nodes = self.init_nodes(sop)
        self.init_relation(sop)
        self.controller = controller(self.controller_dict)
        
        self.agents = {}

    def init_nodes(self, sop):
        # node_sop: a list of the node
        node_sop = sop["nodes"]
        nodes_dict = {}
        for node in node_sop.values():
            
            # str
            name = node["name"]
            
            # true or false
            is_interactive = node["is_interactive"]
            
            """
            agent_states:
            {
                role1:{
                    component1:{
                        component_key: component_value
                        component_key2:componnt_value 
                    }
                }
            }
            """
            agent_states = self.init_states(node["agent_states"])
            
            # config ["style","rule",......]
            config = node["config"]
            
            # contrller  {judge_system_prompt:,judge_last_prompt: ,call_system_prompt: , call_last_prompt}
            
            if "controller" in node:
                self.controller_dict[name] = node["controller"] 
            
            now_node = Node(name=name,
                            is_interactive=is_interactive,
                            config=config,
                            agent_states=agent_states)
            nodes_dict[name] = now_node
            
            if "root" in node.keys() and node["root"]:
                self.root = now_node
        return nodes_dict

    def init_states(self, agent_states_dict: dict):
        agent_states = {}
        for key, value in agent_states_dict.items():
            component_dict = {}
            for component, component_args in value.items():
                if component:
                    
                    # "role" "style"
                    if component == "style":
                        component_dict["style"] = StyleComponent(
                            component_args)
                        
                        # "task"
                    elif component == "task":
                        component_dict["task"] = TaskComponent(component_args)
                        
                        # "rule"
                    elif component == "rule":
                        component_dict["rule"] = RuleComponent(component_args)
                        
                        # "demonstration"
                    elif component == "demonstration":
                        component_dict[
                            "demonstration"] = DemonstrationComponent(
                                component_args)
                            
                    # "output"
                    elif component == "output":
                        component_dict["output"] = OutputComponent(
                            component_args)
                        
                     # "demonstrations"   
                    elif component == "cot":
                        component_dict["cot"] = CoTComponent(component_args)

                    #=================================================================================#

                    elif component == "Top_Category_ShoppingComponent":
                        component_dict[
                            "Top_Category_Shopping"] = Top_Category_ShoppingComponent(
                            )
                            
                    elif component == "User_Intent_ShoppingComponent":
                        component_dict[
                            "User_Intent_ShoppingComponent"] = User_Intent_ShoppingComponent(
                            )
                            
                            
                    elif component == "RecomComponent":
                        component_dict["RecomComponent"] = RecomComponent()
                        
                    # "output"
                    elif component == "StaticComponent":
                        component_dict["StaticComponent"] = StaticComponent(
                            component_args)
                        
                    # "top_k"  "type" "knowledge_base" "system_prompt" "last_prompt"                        
                    elif component == "KnowledgeBaseComponent":
                        component_dict["tool"] = KnowledgeBaseComponent(
                            component_args)
                        
                    elif component == "MatchComponent":
                        component_dict["MatchComponent"] = MatchComponent()
                        
                    elif component == "SearchComponent":
                        component_dict["SearchComponent"] = SearchComponent()
                        
                    # "short_memory_extract_words"  "long_memory_extract_words" "system_prompt" "last_prompt" 
                    elif component == "ExtractComponent":
                        component_dict["ExtractComponent"] = ExtractComponent(
                            component_args)

            agent_states[key] = component_dict
        return agent_states
    

    def init_relation(self, sop):
        relation = sop["relation"]
        for key, value in relation.items():
            for keyword, next_node in value.items():
                self.nodes[key].next_nodes[keyword] = self.nodes[next_node]
    
    
    def step(self,current_node):
        if len(current_node.next_nodes) == 1:
            next_node = "0"
        else:
            next_node = self.controller.judge(current_node,self.shared_memory["chat_history"])
        next_node = current_node.next_nodes[next_node]
        
        if len(self.agents.keys())==1:
            next_role = list(self.agents.keys())[0]
        else:
            next_role = self.controller.allocate_task(next_node,self.shared_memory["chat_history"])
        
        return next_node,next_role
    
    def run(self,role="user",name="A神"):
        current_node = self.root
        while True:
            print(current_node.name)
            query = input(f"{name}({role}):")
            current_memory = {"role":"user","content":f"{name}({role}):{query}"}
            self.shared_memory["chat_history"].append(current_memory)
            while True:
                
                next_node,next_role = self.step(current_node)
                flag =  next_node.is_interactive
                current_node = next_node
                if next_role == role:
                    break
                current_agent = self.agents[next_role]
                current_agent = self.agents[next_role]
                response = current_agent.step(query,role,name,current_node,self.temperature)
                print(f"{current_agent.name}({current_agent.role}):",end="")
                all = f"{current_agent.name}({current_agent.role}):"
                for res in response:
                    all+=res
                    print(res,end="")
                    time.sleep(0.02)
                print()
                self.shared_memory["chat_history"].append({"role":"assistant","content":all})
                
                if flag:
                    break
            


class Node():

    def __init__(self,
                 name: str = None,
                 agent_states: dict = None,
                 is_interactive=False,
                 config: list = None):

        self.next_nodes = {}
        self.agent_states = agent_states
        self.is_interactive = is_interactive
        self.name = name
        self.config = config

    def get_state(self, role, args_dict):
        system_prompt, last_prompt = self.compile(role, args_dict)
        current_role_state = f"目前的角色为：{role}，它的system_prompt为{system_prompt},last_prompt为{last_prompt}"
        return current_role_state

    def compile(self, role, args_dict: dict):
        components = self.agent_states[role]
        system_prompt = ""
        last_prompt = ""
        res_dict = {}
        for component_name in self.config:
            if component_name not in components:
                continue
            component = components[component_name]
            if isinstance(component, OutputComponent):
                last_prompt = last_prompt + "\n" + component.get_prompt(
                    args_dict)
            elif isinstance(component, PromptComponent):
                system_prompt = system_prompt + "\n" + component.get_prompt(
                    args_dict)
            elif isinstance(component, ToolComponent):
                response = component.func(args_dict)
                args_dict.update(response)
                res_dict.update(response)
        return system_prompt, last_prompt, res_dict


class controller:
    def __init__(self,controller_dict) -> None:
        # {judge_system_prompt:,judge_last_prompt: ,judge_extract_words:,call_system_prompt: , call_last_prompt: ,call_extract_words:}
        self.controller_dict = controller_dict
        
    
    def judge(self,node:Node,chat_history,args_dict=None):
        controller_dict = self.controller_dict[node.name]
        system_prompt = controller_dict["judge_system_prompt"]
        last_prompt = controller_dict["judge_last_prompt"]
        extract_words = controller_dict["judge_extract_words"]
        response = get_gpt_response_rule(chat_history,system_prompt,last_prompt,args_dict=args_dict)
        next_node = extract(response,extract_words)
        return next_node
    
    def allocate_task(self,node:Node,chat_history,args_dict=None): 
        controller_dict = self.controller_dict[node.name]
        system_prompt = controller_dict["call_system_prompt"]
        last_prompt = controller_dict["call_last_prompt"]
        extract_words = controller_dict["call_extract_words"]
        response = get_gpt_response_rule(chat_history,system_prompt,last_prompt,args_dict=args_dict)
        next_role = extract(response,extract_words)
        return next_role