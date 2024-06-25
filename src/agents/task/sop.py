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
"""The SOP module provides the SOP class. """
import copy
import json
import random
from typing import Dict, List, Union, Any
from bidict import bidict

from ..agents.llm import OpenAILLM, LLMConfig
from ..agents.agent_team import AgentTeam
from ..agents.environment import Environment
from ..agents.memory import Memory, ShortTermMemory, LongTermMemory
from .node import NodeConfig, Node
from ..knowledge_bases import KnowledgeBaseConfig, KnowledgeBase
from ..utils.prompts import *
from ..utils.config import Config
from ..utils.text import extract


class SOPConfig(Config):
    required_fields = ["nodes", "edges", "root"]

    def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
        super().__init__(config_path_or_dict)
        self._validate_config()

        self.nodes: Dict[str, dict] = self.config_dict["nodes"]
        self.edges: Dict[str, List[str]] = self.config_dict["edges"]
        self.root: str = self.config_dict["root"]
        self.end: str = self.config_dict.get("end", "end_node")
        self.global_kb: Dict[str, Any[list, str]] = self.config_dict.get("kb", None)

    @classmethod
    def generate_config(cls, query, task_description):
        llm_config = {
            "LLM_type": "OpenAI",
            "model": "gpt-4-turbo-2024-04-09",
            "temperature": 0.3,
            "log_path": "logs/generate_config/sop",
            "ACTIVE_MODE": True,
            "SAVE_LOGS": True,
        }
        llm = OpenAILLM(LLMConfig(llm_config))
        system_prompt = "You are a helpful assistant designed to output JSON."
        last_prompt = SOP_CONFIG_GENERATION_PROMPT_TEMPLATE.format(
            query=query, task_description=task_description
        )

        response, content = llm.get_response(
            chat_messages=None,
            system_prompt=system_prompt,
            last_prompt=last_prompt,
            response_format={"type": "json_object"},
        )

        # Converting the JSON format string to a JSON object
        json_config = json.loads(content.strip("`").strip("json").strip())
        checked_config = cls.check_config(json_config)

        nodes_dict = {}
        for node_name, node_description in checked_config["nodes"].items():
            if node_name == checked_config["end"]:
                continue
            node_config = NodeConfig.generate_config(
                task_description,
                node_name,
                node_description,
                checked_config["edges"][node_name],
            )
            nodes_dict[node_name] = node_config.to_dict()

        return cls(
            config_path_or_dict={
                "nodes": nodes_dict,
                "edges": checked_config["edges"],
                "root": checked_config["root"],
                "end": checked_config["end"],
            }
        )

    @staticmethod
    def check_config(config: dict):
        if "nodes" not in config:
            raise ValueError("The 'nodes' field is required in the SOP config.")
        if "edges" not in config:
            raise ValueError("The 'edges' field is required in the SOP config.")
        if "root" not in config:
            raise ValueError("The 'root' field is required in the SOP config.")
        if "end" not in config:
            raise ValueError("The 'end' field is required in the SOP config.")

        validate_nodes_name_set = set(config["nodes"].keys())
        visited_nodes_name_set = set()
        for node_name, next_nodes in config["edges"].items():
            if node_name not in validate_nodes_name_set:
                raise ValueError(
                    f"The node name '{node_name}' in the edges is not a validate"
                )
            else:
                visited_nodes_name_set.add(node_name)

            for next_node in next_nodes:
                if next_node not in validate_nodes_name_set:
                    raise ValueError(
                        f"The next node name '{next_node}' of '{node_name} in the edges is not in the nodes."
                    )

            # If the node is not in the list of next_nodes, insert it into the first position of the list
            if node_name not in next_nodes:
                next_nodes.insert(0, node_name)

        if config["root"] not in validate_nodes_name_set:
            raise ValueError(f"The root node '{config['root']}' is not in the nodes.")
        if config["end"] not in validate_nodes_name_set:
            raise ValueError(f"The end node '{config['end']}' is not in the nodes.")

        visited_nodes_name_set.add(config["end"])
        if visited_nodes_name_set != validate_nodes_name_set:
            raise ValueError(
                f"The nodes in the edges are not the same as the nodes.\n Validate nodes: {validate_nodes_name_set}\n Visited nodes: {visited_nodes_name_set}"
            )

        return config


class SOP:
    def __init__(self, config: SOPConfig):
        self.config = config

        # Initialize the nodes
        self.nodes: Dict[str, Node] = {}
        for node_config in self.config.nodes.values():
            if node_config["node_name"] == "end_node":
                continue
            node = Node(config=NodeConfig(node_config))
            self.nodes[node.node_name] = node

        self.root: Node = self.nodes[self.config.root]
        self.end: str = self.config.end
        if self.config.global_kb:
            self.global_kb: KnowledgeBase = KnowledgeBase(
                config=KnowledgeBaseConfig(self.config.global_kb)
            )
        else:
            self.global_kb = None

        # Initialize the edges
        for node_name, node_edges in self.config.edges.items():
            node: Node = self.nodes[node_name]
            for to_node in node_edges:
                node.next_nodes[to_node] = (
                    self.nodes[to_node] if to_node in self.nodes else None
                )

        # Begin status of the SOP
        self.current_node: Node = self.root
        self.finished: bool = False

        llm_config = {
            "LLM_type": "OpenAI",
            "model": "gpt-4-turbo-2024-04-09",
            "temperature": 0.3,
            "log_path": "logs/sop",
            "ACTIVE_MODE": True,
            "SAVE_LOGS": True,
        }
        self.llm = OpenAILLM(LLMConfig(llm_config))

    def init_name_role_hash_for_nodes(self, agent_team: AgentTeam):
        for agent_name, agent in agent_team.agents.items():
            for node_name, role in agent.agent_roles.items():
                if not self.nodes[node_name].name_role_hash:
                    self.nodes[node_name].name_role_hash = bidict()
                self.nodes[node_name].name_role_hash[agent_name] = role

        for node_name, node in self.nodes.items():
            node.node_agents = list(node.name_role_hash.keys())
            node.node_roles = list(node.name_role_hash.values())

    def init_node_prompts(self):
        for node_name, node in self.nodes.items():
            node.node_prompts = node.load_node_prompts()

    def update_nodes_from_case(self, case_padding: dict):
        # Update the node prompts from the case padding, specifically, input the case padding into the node prompts
        for _, node in self.nodes.items():
            if node.node_name == "end_node":
                continue
            node.node_prompts = node.load_node_prompts(case_padding)

    def transit(
            self, history_messages: list, relevant_memory: str, environment_summary: str
    ):
        """
        Determine the next node based on the current situation
        Return :
        next_node(node) : the next node
        """

        # If the current node is a single loop node, the loop continues
        if len(self.current_node.next_nodes) == 1:
            next_node = self.current_node
        # Otherwise, the controller determines the next node
        else:
            # If the number of chats at the current node has reached the upper limit, transit to the next node
            if len(history_messages) > self.current_node.controller.max_chat_nums:
                idx = list(self.current_node.next_nodes.keys()).index(
                    self.current_node.node_name
                )
                idx = (idx + 1) % len(self.current_node.next_nodes)
                next_node = list(self.current_node.next_nodes.values())[idx]
            # Otherwise, the controller determines whether to transit to the next node
            if self.current_node.controller.transit_type == "llm":
                node_description = (
                    NODE_DESCRIPTION_TEMPLATE.format(
                        node_description=self.current_node.node_description
                    )
                    if self.current_node.node_description
                    else ""
                )

                transit_system_prompt = (
                    self.current_node.controller.transit_system_prompt
                )
                transit_system_prompt = (
                    f"{node_description}\n{transit_system_prompt}\n"
                    if transit_system_prompt
                    else f"{node_description}\n"
                )

                transit_last_prompt = self.current_node.controller.transit_last_prompt
                if not transit_last_prompt:
                    transit_last_prompt = TRANSIT_LAST_PROMPT_TEMPLATE.format(
                        next_nodes=list(self.current_node.next_nodes.keys()),
                        extract_word=self.current_node.controller.transit_extract_word,
                    )

                transit_message = TRASNSIT_MESSAGE_TEMPLATE.format(
                    environment_summary=environment_summary,
                    chat_history_message=Memory.encode_memory(history_messages),
                    query=Memory.encode_memory(history_messages[-1:]),
                )
                if relevant_memory:
                    transit_message += RELEVANT_HISTORY_TEMPLATE.format(
                        relevant_history=relevant_memory
                    )

                transit_last_prompt = transit_message + transit_last_prompt

                response, content = self.llm.get_response(
                    chat_messages=None,
                    system_prompt=transit_system_prompt,
                    last_prompt=transit_last_prompt,
                )

                node = extract(
                    content, self.current_node.controller.transit_extract_word
                )
                if node in self.current_node.next_nodes:
                    next_node = self.current_node.next_nodes[node]
                # If no parsing result, the loop continues
                else:
                    next_node = self.current_node
            elif self.current_node.controller.transit_type == "order":
                idx = list(self.current_node.next_nodes.keys()).index(
                    self.current_node.node_name
                )
                idx = (idx + 1) % len(self.current_node.next_nodes)
                next_node = list(self.current_node.next_nodes.values())[idx]
            # Otherwise, raise an error
            else:
                raise ValueError(
                    f"Controller type '{self.current_node.controller.transit_type}' is not supported! Please choose from 'order' and 'llm'."
                )

        return next_node

    def route(self, history_messages: list, relevant_memory: str):
        """
        Determine the role that needs action based on the current situation
        Return :
        next_agent_name(str) : the name of the next act agent
        """

        # Start assigning role after knowing the next node to enter
        # If there is only one role in the node, assign it directly
        if len(self.current_node.node_roles) == 1:
            next_role = self.current_node.node_roles[0]
        # Otherwise, the controller determines the next role
        else:
            # If the controller type is "order", the roles are assigned in order
            if self.current_node.controller.route_type == "order":
                if not self.current_node.current_role:
                    next_role = self.current_node.node_roles[0]
                else:
                    idx = self.current_node.node_roles.index(
                        self.current_node.current_role
                    )
                    idx = (idx + 1) % len(self.current_node.node_roles)
                    next_role = self.current_node.node_roles[idx]
            # If the controller type is "random", the roles are assigned randomly
            elif self.current_node.controller.route_type == "random":
                next_role = random.choice(self.current_node.node_roles)
            # If the controller type is "llm", the roles are assigned by the LLM
            elif self.current_node.controller.route_type == "llm":
                node_description = (
                    NODE_DESCRIPTION_TEMPLATE.format(
                        node_description=self.current_node.node_description
                    )
                    if self.current_node.node_description
                    else ""
                )

                assign_role_prompt = ""
                for role in self.current_node.node_roles:
                    assign_role_prompt += ASSIGN_ROLE_PROMPT_TEMPLATE.format(
                        role=role,
                        extract_word=self.current_node.controller.route_extract_word,
                    )

                route_system_prompt = self.current_node.controller.route_system_prompt
                route_system_prompt = (
                    f"{node_description}\n{route_system_prompt}\n{assign_role_prompt}"
                    if route_system_prompt
                    else f"{node_description}\n{assign_role_prompt}"
                )

                route_last_prompt = self.current_node.controller.route_last_prompt
                if not route_last_prompt:
                    if len(history_messages) > 0:
                        last_name = (
                            history_messages[-1]["name"]
                            if "name" in history_messages[-1]
                            else ""
                        )
                    else:
                        last_name = ""
                    last_name = history_messages[-1]["name"] if history_messages else ""

                    route_last_prompt = ROUTE_LAST_PROMPT_TEMPLATE.format(
                        query=Memory.encode_memory(history_messages[-1:]),
                        relevant_history=relevant_memory,
                        assign_role_prompt=assign_role_prompt,
                        last_name=last_name,
                    )

                route_message = ROUTE_MESSAGE_TEMPLATE.format(
                    chat_history_message=Memory.encode_memory(history_messages),
                    last_name=last_name,
                )

                response, content = self.llm.get_response(
                    chat_messages=[
                        {
                            "role": "user",
                            "content": route_message,
                        }
                    ],
                    system_prompt=route_system_prompt,
                    last_prompt=route_last_prompt,
                )

                next_role = extract(
                    content, self.current_node.controller.route_extract_word
                )
                # If the next role is not available in the node roles, choose one randomly
                if next_role not in self.current_node.node_roles:
                    next_role = random.choice(self.current_node.node_roles)
            # Otherwise, raise an error
            else:
                raise ValueError(
                    f"Controller type '{self.current_node.controller.route_type}' is not supported! Please choose from 'order', 'random' and 'llm'."
                )

        self.current_node.current_role = next_role
        next_agent_name = self.current_node.name_role_hash.inverse[next_role]

        return next_agent_name

    def next(self, environment: Environment):
        """
        Determine the next node and the agent that needs action based on the current situation
        Return :
        next_node(node) : the next node
        next_agent_name(str) : the name of the next act agent
        """

        # Check if it is the first time to enter the current node
        if self.current_node.is_begin:
            # Get the agent according to the beginning node
            agent_name = self.current_node.name_role_hash.inverse[
                self.current_node.begin_role
            ]
            return self.current_node, agent_name

        # Get relevant memory
        shared_short_term_memory: ShortTermMemory = environment.shared_memory[
            "short_term_memory"
        ]
        shared_long_term_memory: LongTermMemory = environment.shared_memory[
            "long_term_memory"
        ]
        if len(shared_short_term_memory) > 0 and self.global_kb:
            relevant_memory = self.global_kb.retrieve_from_file(
                query=shared_short_term_memory.get_memory()[-1]["content"],
                file_path=shared_long_term_memory.json_path,
            )
            if "no suitable information retrieved" in relevant_memory.lower():
                relevant_memory = ""
        else:
            relevant_memory = ""

        if shared_short_term_memory:
            history_messages = shared_short_term_memory.get_memory()
        else:
            history_messages = []

        # Transit to the next node
        next_node: Node = self.transit(
            history_messages=history_messages,
            relevant_memory=relevant_memory,
            environment_summary=environment.shared_memory["summary"],
        )
        self.current_node = next_node
        # If the next node is the end node, finish the process directly
        if not next_node or next_node.node_name == self.end:
            self.finished = True
            return None, None

        # Route to get the next agent name
        next_agent_name = self.route(
            history_messages=history_messages,
            relevant_memory=relevant_memory,
        )

        return next_node, next_agent_name

    def dump(self, save_path):
        # 旧代码，深拷贝以下config类之后，修改这个类，然后用这个类的dumps保存
        # save_config: SOPConfig = copy.deepcopy(self.config)
        # for node in self.nodes.values():
        #     save_config.nodes[node.node_name] = node.to_dict()
        # save_config.dump(save_path)

        # 新代码，直接调用to_dict得到字典之后保存
        save_dict = self.to_dict()
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(save_dict, f, indent=4, ensure_ascii=False)

    def to_dict(self):
        """
        get the whole SOP configuration in dict format

        Returns: dict
        """
        ret_dict = self.config.to_dict()
        ret_dict["nodes"] = {
            node.node_name: node.to_dict() for node in self.nodes.values()
        }
        ret_dict["root"] = self.root.node_name
        ret_dict["end"] = self.end
        ret_dict["edges"] = {}
        for node in self.nodes.values():
            ret_dict["edges"][node.node_name] = list(node.next_nodes.keys())
        return ret_dict

    def get_dict_for_sop_optimizer(self):
        """
        get the SOP configuration in dict format for SOP optimizer.
        会删除掉一些与SOP优化无关的字段

        Returns:

        """
        ret_dict = self.to_dict()

        # delete some unnecessary fields for sop_optimizer
        for node_config in ret_dict["nodes"].values():
            node_config.pop("tools", None)
            node_config.pop("node_prompt_templates", None)
            node_config.pop("node_roles_description", None)
            node_config.pop("node_prompt_paddings", None)
            node_config.pop("node_primary_prompts", None)
            node_config.pop("begin_query", None)
            node_config.pop("begin_role", None)
            node_config.pop("kb", None)

            # controller
            node_config.pop("controller", None)
            # node_config["controller"].pop("route_type", None)
            # node_config["controller"].pop("route_system_prompt", None)
            # node_config["controller"].pop("route_last_prompt", None)
            # node_config["controller"].pop("route_extract_word", None)
            # node_config["controller"].pop("max_chat_nums", None)
            # node_config["controller"].pop("transit_extract_word", None)

        ret_dict.pop("global_kb", None)
        return ret_dict
