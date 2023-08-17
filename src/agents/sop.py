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
from datebase import TaskConfig
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
        self.agents_role_name = {}

        self.config = {}
        self.temperature = sop["temperature"] if "temperature" in sop else 0.3
        self.active_mode = sop["active_mode"] if "active_mode" in sop else False
        self.log_path = sop["log_path"] if "log_path" in sop else "logs"

        self.environment_prompt = sop["environment_prompt"]
        self.shared_memory = {"chat_history": [],"summary":""}
        self.controller_dict = {}
        self.nodes = self.init_nodes(sop)
        self.init_relation(sop)
        self.current_node = self.root

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
            config = self.config

            # contrller  {judge_system_prompt:,judge_last_prompt: ,call_system_prompt: , call_last_prompt}

            if "controller" in node:
                self.controller_dict[name] = node["controller"]

            now_node = Node(name=name,
                            is_interactive=is_interactive,
                            config=config,
                            environment_prompt=self.environment_prompt,
                            agent_states=agent_states)
            nodes_dict[name] = now_node

            if "root" in node.keys() and node["root"]:
                self.root = now_node
        return nodes_dict

    def init_states(self, agent_states_dict: dict):
        agent_states = {}
        for role, components in agent_states_dict.items():
            component_dict = {}
            for component, component_args in components.items():
                if component:

                    # "role" "style"
                    if component == "style":
                        component_dict["style"] = StyleComponent(
                            component_args["role"], component_args["name"],
                            component_args["style"])
                        if component_args["name"] not in self.agents_role_name:
                            self.agents_role_name[component_args["name"]] = role

                        # "task"
                    elif component == "task":
                        component_dict["task"] = TaskComponent(
                            component_args["task"])

                        # "rule"
                    elif component == "rule":
                        component_dict["rule"] = RuleComponent(
                            component_args["rule"])

                        # "demonstration"
                    elif component == "demonstration":
                        component_dict[
                            "demonstration"] = DemonstrationComponent(
                                component_args["demonstrations"])

                    # "output"
                    elif component == "output":
                        component_dict["output"] = OutputComponent(
                            component_args["output"])

                    elif component == "last":
                        component_dict["last"] = LastComponent(
                            component_args["last_prompt"])

                    # "demonstrations"
                    elif component == "cot":
                        component_dict["cot"] = CoTComponent(
                            component_args["demonstrations"])

                    #=================================================================================#

                    # "output"
                    elif component == "StaticComponent":
                        component_dict["StaticComponent"] = StaticComponent(
                            component_args["output"])

                    # "top_k"  "type" "knowledge_base" "system_prompt" "last_prompt"
                    elif component == "KnowledgeBaseComponent":
                        component_dict["tool"] = KnowledgeBaseComponent(
                            component_args["top_k"], component_args["type"],
                            component_args["knowledge_path"])

                    elif component == "CategoryRequirementsComponent":
                        component_dict[
                            "CategoryRequirementsComponent"] = CategoryRequirementsComponent(
                                component_args["information_path"])

                    # "short_memory_extract_words"  "long_memory_extract_words" "system_prompt" "last_prompt"
                    elif component == "ExtractComponent":
                        component_dict["ExtractComponent"] = ExtractComponent(
                            component_args["long_memory_extract_words"],
                            component_args["short_memory_extract_words"],
                            component_args["system_prompt"],
                            component_args["last_prompt"])
                    elif component == "WebSearchComponent":
                        component_dict[
                            "WebSearchComponent"] = WebSearchComponent(
                                component_args["engine_name"],
                                component_args["api"], component_args["name"])
                    elif component == "WebCrawlComponent":
                        component_dict[
                            "WebCrawlComponent"] = WebCrawlComponent(
                                component_args["name"])

                    # ====================================================
                    elif component == "config":
                        self.config[role] = component_args

            agent_states[role] = component_dict

        return agent_states

    def init_relation(self, sop):
        relation = sop["relation"]
        for key, value in relation.items():
            for keyword, next_node in value.items():
                self.nodes[key].next_nodes[keyword] = self.nodes[next_node]

    def summary(self):
        system_prompt = self.environment_prompt + "\n你的任务是根据当前的场景对历史的对话记录进行概括，总结出最重要的信息"
        last_prompt = "请你根据历史的聊天记录进行概括，输出格式为 历史摘要：\{你总结的内容\}"
        response = get_gpt_response_rule(self.shared_memory["chat_history"],
                                         system_prompt,
                                         last_prompt,
                                         log_path=self.log_path,
                                         summary=self.shared_memory["summary"])
        return response

    def update_memory(self, memory):
        self.shared_memory["chat_history"].append(memory)
        summary = None
        if len(self.shared_memory["chat_history"]) > MAX_CHAT_HISTORY:
            summary = self.summary()
            self.shared_memory["chat_history"] = self.shared_memory["chat_history"][-2:]
            self.shared_memory["summary"] = summary

        for agent in self.agents.values():
            agent.agent_dict["long_memory"]["chat_history"] = self.shared_memory["chat_history"]
            agent.agent_dict["long_memory"]["summary"] = summary

    def load_date(self, task: TaskConfig):
        self.current_node_name = task.current_node_name
        self.shared_memory["chat_history"] = task.memory["chat_history"]


class Node():

    def __init__(self,
                 name: str = None,
                 agent_states: dict = None,
                 is_interactive=False,
                 environment_prompt=None,
                 config: list = None):

        self.next_nodes = {}
        self.agent_states = agent_states
        self.is_interactive = is_interactive
        self.name = name
        self.environment_prompt = environment_prompt
        self.config = config

    def get_state(self, role, agent_dict):
        system_prompt, last_prompt = self.compile(role, agent_dict)
        current_role_state = f"目前的角色为：{role}，它的system_prompt为{system_prompt},last_prompt为{last_prompt}"
        return current_role_state

    def compile(self, role, agent_dict: dict):
        components = self.agent_states[role]
        system_prompt = self.environment_prompt if self.environment_prompt else ""
        last_prompt = ""
        res_dict = {}
        for component_name in self.config[role]:
            if component_name not in components:
                continue
            component = components[component_name]
            if isinstance(component, (OutputComponent, LastComponent)):
                last_prompt = last_prompt + "\n" + component.get_prompt(
                    agent_dict)
            elif isinstance(component, PromptComponent):
                system_prompt = system_prompt + "\n" + component.get_prompt(
                    agent_dict)
            elif isinstance(component, ToolComponent):
                response = component.func(agent_dict)
                # print(response)
                if "prompt" in response and response["prompt"]:
                    last_prompt = last_prompt + "\n" + response["prompt"]
                agent_dict.update(response)
                res_dict.update(response)
        return system_prompt, last_prompt, res_dict


class controller:

    def __init__(self, controller_dict) -> None:
        # {judge_system_prompt:,judge_last_prompt: ,judge_extract_words:,call_system_prompt: , call_last_prompt: ,call_extract_words:}
        self.controller_dict = controller_dict

    def transit(self, node: Node, chat_history, **kwargs):
        controller_dict = self.controller_dict[node.name]
        system_prompt = kwargs["environment_prompt"] + "\n"+controller_dict["judge_system_prompt"]
        last_prompt = controller_dict["judge_last_prompt"]
        extract_words = controller_dict["judge_extract_words"]
        response = get_gpt_response_rule(chat_history, system_prompt,
                                         last_prompt, **kwargs)
        next_node = extract(response, extract_words)
        return next_node

    def route(self, node: Node, chat_history, **kwargs):
        controller_dict = self.controller_dict[node.name]
        system_prompt = kwargs["environment_prompt"] + "\n"+controller_dict["call_system_prompt"]
        
        index = chat_history[-1]["content"].find("：")
        last_name = chat_history[-1]["content"][:index] if index != -1 else ""
        last_prompt = f"上一个发言的人为{last_name}\n"
        last_prompt += controller_dict["call_last_prompt"] 
        extract_words = controller_dict["call_extract_words"]
        response = get_gpt_response_rule(chat_history, system_prompt,
                                         last_prompt, **kwargs)
        next_role = extract(response, extract_words)
        return next_role
    
    
    def next(self,sop: SOP):
        current_node:Node
        current_node = sop.current_node
        if len(current_node.next_nodes) == 1:
            next_node = "0"
        else:
           next_node = self.transit(node=current_node, chat_history=sop.shared_memory["chat_history"],summary = sop.shared_memory["summary"],environment_prompt = sop.environment_prompt)
        
        if not next_node.isdigit():
            next_node = "0"
        next_node = current_node.next_nodes[next_node]
        if len(sop.agents.keys()) == 1:
            next_role = list(sop.agents.keys())[0]
        else:
            next_role = self.route(
            node=next_node, chat_history=sop.shared_memory["chat_history"],summary = sop.shared_memory["summary"],environment_prompt = sop.environment_prompt
        )
        if next_role not in sop.agents:
            next_role = random.choice(list(sop.agents.keys()))
        return next_node, next_role
