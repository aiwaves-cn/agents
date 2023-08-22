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
    sop indispensable attribute: begin_role   begin_query begin_query nodes(agent_states)  relation
    
    output: a sop graph
    """

    def __init__(self, json_path):
        with open(json_path) as f:
            sop = json.load(f)
        self.sop = sop
        self.root = None
        self.agents_role_name = {}
        self.controller_dict = {}
        self.config = {}
        self.agents = {}
        self.shared_memory = {"chat_history": [],"short_history":[],"summary": ""}
        
        self.temperature = sop["temperature"] if "temperature" in sop else 0.3
        self.active_mode = sop["active_mode"] if "active_mode" in sop else False
        self.log_path = sop["log_path"] if "log_path" in sop else "logs"
        self.summary_system_prompt = sop["summary_system_prompt"] if "summary_system_prompt" in sop else None
        self.summary_last_prompt = sop["summary_last_prompt"] if "summary_last_prompt" in sop else None
        self.user_roles = sop["user_roles"] if "user_roles" in sop else []

        self.nodes = self.init_nodes(sop)
        self.init_relation(sop)
        self.current_node = self.root


    def init_nodes(self, sop):
        # node_sop: a list of the node
        node_sop = sop["nodes"]
        nodes_dict = {}
        for node in node_sop.values():
            # str
            name = node["name"]
            self.agents_role_name[name] = {}

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
            agent_states = self.init_states(name, node["agent_states"])

            # config ["style","rule",......]
            config = self.config
            environment_prompt = node["environment_prompt"]
            # contrller  {judge_system_prompt:,judge_last_prompt: ,call_system_prompt: , call_last_prompt}

            if "controller" in node:
                self.controller_dict[name] = node["controller"]
                if "controller_type" in node:
                    self.controller_dict[name]["controller_type"] = node["controller_type"]

            now_node = Node(name=name,
                            is_interactive=is_interactive,
                            config=config,
                            environment_prompt=environment_prompt,
                            agent_states=agent_states)
            
            now_node.begin_role = node["begin_role"] if "begin_role" in node else None
            now_node.begin_query = node["begin_query"] if "begin_query" in node else None
            nodes_dict[name] = now_node

            if "root" in node.keys() and node["root"]:
                self.root = now_node
        return nodes_dict

    def init_states(self, node_name, agent_states_dict: dict):
        agent_states = {}
        for role, components in agent_states_dict.items():
            component_dict = {}
            for component, component_args in components.items():
                if component:

                    # "role" "style"
                    if component == "style":
                        agent_name = component_args["name"]
                        component_dict["style"] = StyleComponent(
                            component_args["role"], component_args["name"],
                            component_args["style"])

                        self.agents_role_name[node_name][agent_name] = role

                        # "task"
                    elif component == "task":
                        component_dict["task"] = TaskComponent(
                            component_args["task"])

                        # "rule"
                    elif component == "rule":
                        component_dict["rule"] = RuleComponent(
                            component_args["rule"])

                        # "demonstration"
                    elif component == "demonstrations":
                        component_dict[
                            "demonstrations"] = DemonstrationComponent(
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
                    elif component == "CustomizeComponent":
                        component["CustomizeComponent"] = CustomizeComponent(
                            component_args["template"],component_args["keywords"]
                        )

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
        summary_system_prompt = self.summary_system_prompt if self.summary_system_prompt else "\n你的任务是根据当前的场景对历史的对话记录进行概括，总结出最重要的信息"
        summary_last_prompt = self.summary_last_prompt if self.summary_last_prompt else "请你根据历史的聊天记录进行概括，输出格式为  历史摘要：\{你总结的内容\} "
        system_prompt = self.current_node.environment_prompt + summary_system_prompt
        last_prompt = summary_last_prompt
        query = self.shared_memory["chat_history"][-1] if len(self.shared_memory["chat_history"])>0 else " "
        key_history = get_key_history(query,self.shared_memory["chat_history"][:-1],self.shared_memory["chat_embeddings"][:-1])
        response = get_response(
            self.shared_memory["short_history"],
            system_prompt,
            last_prompt,
            stream= False,
            log_path=self.log_path,
            summary=self.shared_memory["summary"],
            key_history = key_history
        )
        return response

    def update_memory(self, memory):
        global MAX_CHAT_HISTORY
        self.shared_memory["chat_history"].append(memory)
        self.shared_memory["short_history"].append(memory)
        current_embedding = get_embedding(memory["content"])
        if "chat_embeddings" not in self.shared_memory:
            self.shared_memory["chat_embeddings"]= current_embedding
        else:
            self.shared_memory["chat_embeddings"] = torch.cat([self.shared_memory["chat_embeddings"],current_embedding],dim = 0)
        
        summary = None
        
        if len(self.shared_memory["short_history"]) > MAX_CHAT_HISTORY:
            summary = self.summary()
            self.shared_memory["short_history"] = [self.shared_memory["short_history"][-MAX_CHAT_HISTORY//2:]]
            self.shared_memory["summary"] = summary

        for agent in self.agents[self.current_node.name].values():
            agent.agent_dict["long_memory"][
                "chat_history"].append(memory)
            if "chat_embeddings" not in  agent.agent_dict["long_memory"]:
                agent.agent_dict["long_memory"]["chat_embeddings"] = current_embedding
            else:
                 agent.agent_dict["long_memory"]["chat_embeddings"] = torch.cat([agent.agent_dict["long_memory"]["chat_embeddings"],current_embedding],dim = 0)
            agent.agent_dict["short_memory"]["chat_history"] = self.shared_memory["short_history"]
            agent.agent_dict["short_memory"]["summary"] = summary

    def send_memory(self, next_node):
        summary = self.summary()
        self.shared_memory["summary"] = summary
        self.shared_memory["short_history"] = []
        for agent in self.agents[next_node.name].values():
            agent.agent_dict["short_memory"]["summary"] = summary

    def load_date(self, task: TaskConfig):
        self.current_node_name = task.current_node_name
        self.shared_memory["chat_history"] = task.memory["chat_history"]


class Node:

    def __init__(
        self,
        name: str = None,
        agent_states: dict = None,
        is_interactive=False,
        environment_prompt=None,
        config: list = None,
    ):
        
        self.next_nodes = {}
        self.agent_states = agent_states
        self.is_interactive = is_interactive
        self.name = name
        self.environment_prompt = environment_prompt
        self.config = config
        self.current_role = None
        self.begin_role = None
        self.begin_query = None
        self.roles = []

    def get_state(self, role, agent_dict):
        system_prompt, last_prompt = self.compile(role, agent_dict)
        current_role_state = (
            f"目前的角色为：{role}，它的system_prompt为{system_prompt},last_prompt为{last_prompt}"
        )
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
        system_prompt = "<environment>" + kwargs[
            "environment_prompt"] + "</environment>\n" + controller_dict[
                "judge_system_prompt"]

        last_prompt = controller_dict["judge_last_prompt"]
        extract_words = controller_dict["judge_extract_words"]
        response = get_response(chat_history, system_prompt,
                                        last_prompt, stream = False,**kwargs)
        next_node = extract(response, extract_words)
        return next_node

    def route(self, node: Node, chat_history, **kwargs):
        controller_type = self.controller_dict[node.name]["controller_type"] if "controller_type" in self.controller_dict[node.name] else "0"
        if controller_type == "0":
            controller_dict = self.controller_dict[node.name]
            system_prompt = "<environment>" + kwargs[
                "environment_prompt"] + "</environment>\n" + controller_dict[
                    "call_system_prompt"]
            
            index = -1
            if len(chat_history) > 0:
                if "<output>" in chat_history[-1]["content"]:
                    chat_history[-1]["content"] = extract(
                        chat_history[-1]["content"], "output")

                index = max(chat_history[-1]["content"].find("："),
                            chat_history[-1]["content"].find(":"))

            last_name = chat_history[-1]["content"][:index] if index != -1 else ""
            last_prompt = f"上一个发言的人为:{last_name}\n注意：目前轮到的人不能和上一次发言的人是同一个人，所以不能输出<结束>{last_name}</结束>"

            last_prompt += controller_dict["call_last_prompt"]
            extract_words = controller_dict["call_extract_words"]
            response = get_response(chat_history, system_prompt,
                                    last_prompt, stream=False,**kwargs)
            next_role = extract(response, extract_words)
        elif controller_type == "1":
            if not node.current_role:
                next_role = node.roles[0]
            else:
                index = node.roles.index(node.current_role)
                next_role = node.roles[(index+1)%len(node.roles)]
        
        elif controller_type == "2":
            next_role = random.choice(node.roles)
            
        return next_role

    def next(self, sop: SOP):
        current_node: Node
        current_node = sop.current_node
        if len(current_node.next_nodes) == 1:
            next_node = "0"
        else:
            query = sop.shared_memory["chat_history"][-1] if len(sop.shared_memory["chat_history"])>0 else " "
            key_history = get_key_history(query,sop.shared_memory["chat_history"][:-1],sop.shared_memory["chat_embeddings"][:-1])
            next_node = self.transit(
                node=current_node,
                chat_history=sop.shared_memory["short_history"],
                summary=sop.shared_memory["summary"],
                key_history = key_history,
                environment_prompt=current_node.environment_prompt)

        if not next_node.isdigit():
            next_node = "0"

        next_node = current_node.next_nodes[next_node]
        if len(sop.agents[current_node.name].keys()) == 1:
            next_role = list(sop.agents[current_node.name].keys())[0]
        else:
            query = sop.shared_memory["chat_history"][-1] if len(sop.shared_memory["chat_history"])>0 else " "
            key_history = get_key_history(query,sop.shared_memory["chat_history"][:-1],sop.shared_memory["chat_embeddings"][:-1])
            next_role = self.route(
                node=next_node,
                chat_history=sop.shared_memory["short_history"],
                summary=sop.shared_memory["summary"],
                key_history = key_history, 
                environment_prompt=current_node.environment_prompt,
            )

        if next_role not in next_node.roles:
            next_role = random.choice(next_node.roles)
        next_node.current_role = next_role

        return next_node, next_role
