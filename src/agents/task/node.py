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
"""The Node class is a base class for all nodes in the SOP graph."""
import copy
import json
import re

from bidict import bidict
from typing import Dict, List, Union

from ..agents.llm import OpenAILLM, LLMConfig
from ..knowledge_bases import KnowledgeBaseConfig, KnowledgeBase
from ..utils.prompts import *
from ..utils.config import Config


class NodeConfig(Config):
    required_fields = [
        "node_name",
        "node_description",
        "begin_role",
        "controller"
    ]

    class ControllerConfig(Config):

        required_fields = []

        def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
            super().__init__(config_path_or_dict)
            self._validate_config()

            self.max_chat_nums = self.config_dict.get("max_chat_nums", 10)

            self.transit_type = self.config_dict.get("transit_type", "llm")
            self.transit_system_prompt = self.config_dict.get("transit_system_prompt")
            self.transit_last_prompt = self.config_dict.get("transit_last_prompt")
            self.transit_extract_word = self.config_dict.get(
                "transit_extract_word", "node"
            )

            self.route_type = self.config_dict.get("route_type", "order")
            self.route_system_prompt = self.config_dict.get("route_system_prompt")
            self.route_last_prompt = self.config_dict.get("route_last_prompt")
            self.route_extract_word = self.config_dict.get("route_extract_word", "role")

        @classmethod
        def generate_config(
                cls,
                task_description: str,
                node_name: str,
                node_description: str,
                next_nodes: List[str],
                node_roles_description: Dict[str, str],
        ):
            max_chat_nums = 10

            llm_config = {
                "LLM_type": "OpenAI",
                "model": "gpt-4-turbo-2024-04-09",
                "temperature": 0.3,
                "log_path": "logs/generate_config/node/controller/transit",
                "ACTIVE_MODE": True,
                "SAVE_LOGS": True,
            }
            llm = OpenAILLM(LLMConfig(llm_config))
            system_prompt = "You are a helpful assistant."
            last_prompt = TRANSIT_CONTROLLER_CONFIG_GENERATION_PROMPT_TEMPLATE.format(
                task_description=task_description,
                node_description=node_description,
                node_roles_description=node_roles_description,
            )

            response, content = llm.get_response(
                chat_messages=None,
                system_prompt=system_prompt,
                last_prompt=last_prompt,
            )

            transit_type = "llm"
            transit_system_prompt = (
                    content
                    + " If all the rules above are met, the task is complete, please consider to transit to the next node. Otherwise, the task is not complete, stay at the current node."
            )
            transit_extract_word = "node"
            transit_last_prompt = TRANSIT_LAST_PROMPT_TEMPLATE.format(
                next_nodes=next_nodes, extract_word=transit_extract_word
            )

            llm_config = {
                "LLM_type": "OpenAI",
                "model": "gpt-4-turbo-2024-04-09",
                "temperature": 0.3,
                "log_path": "logs/generate_config/node/controller/route",
                "ACTIVE_MODE": True,
            }
            llm = OpenAILLM(LLMConfig(llm_config))
            system_prompt = "You are a helpful assistant designed to output JSON."
            last_prompt = ROUTE_CONTROLLER_CONFIG_GENERATION_PROMPT_TEMPLATE.format(
                task_description=task_description,
                node_description=node_description,
                node_roles_description=node_roles_description,
            )

            response, content = llm.get_response(
                chat_messages=None,
                system_prompt=system_prompt,
                last_prompt=last_prompt,
            )

            # Converting the JSON format string to a JSON object
            json_config = json.loads(content.strip("`").strip("json").strip())

            route_type = json_config["route_type"]
            route_system_prompt = json_config["route_system_prompt"]
            route_last_prompt = None
            route_extract_word = "role"

            return cls(
                config_path_or_dict={
                    "max_chat_nums": max_chat_nums,
                    "transit_type": transit_type,
                    "transit_system_prompt": transit_system_prompt,
                    "transit_last_prompt": transit_last_prompt,
                    "transit_extract_word": transit_extract_word,
                    "route_type": route_type,
                    "route_system_prompt": route_system_prompt,
                    "route_last_prompt": route_last_prompt,
                    "route_extract_word": route_extract_word,
                }
            )

        def update(self, config: dict):
            self.max_chat_nums = (
                config["max_chat_nums"]
                if "max_chat_nums" in config
                else self.max_chat_nums
            )

            self.transit_type = (
                config["transit_type"]
                if "transit_type" in config
                else self.transit_type
            )
            self.transit_system_prompt = (
                config["transit_system"]
                if "transit_system" in config
                else self.transit_system_prompt
            )
            self.transit_last_prompt = (
                config["transit_last_prompt"]
                if "transit_last_prompt" in config
                else self.transit_last_prompt
            )
            self.transit_extract_word = (
                config["transit_extract_word"]
                if "transit_extract_word" in config
                else self.transit_extract_word
            )

            self.route_type = (
                config["route_type"] if "route_type" in config else self.route_type
            )
            self.route_system_prompt = (
                config["route_system_prompt"]
                if "route_system_prompt" in config
                else self.route_system_prompt
            )
            self.route_last_prompt = (
                config["route_last_prompt"]
                if "route_last_prompt" in config
                else self.route_last_prompt
            )
            self.route_extract_word = (
                config["route_extract_word"]
                if "route_extract_word" in config
                else self.route_extract_word
            )

    def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
        super().__init__(config_path_or_dict)
        self._validate_config()

        self.node_name: str = self.config_dict["node_name"]
        self.node_description: str = self.config_dict.get("node_description", None)
        self.node_roles_description: dict = self.config_dict.get(
            "node_roles_description", {}
        )
        self.begin_role: str = self.config_dict["begin_role"]
        self.begin_query: str = self.config_dict.get("begin_query", None)
        self.controller: Dict[str, str] = self.ControllerConfig(
            self.config_dict["controller"]
        ).to_dict()
        self.node_primary_prompts: Dict[str, dict] = self.config_dict.get(
            "node_primary_prompts", {}
        )
        self.node_prompt_templates: Dict[str, str] = self.config_dict.get(
            "node_prompt_templates", {}
        )
        for prompt_type in DEFAULT_NODE_PROMPT_TEMPLATES:
            if prompt_type not in self.node_prompt_templates:
                self.node_prompt_templates[prompt_type] = DEFAULT_NODE_PROMPT_TEMPLATES[prompt_type]
        self.node_prompt_paddings: Dict[str, dict] = self.config_dict.get(
            "node_prompt_paddings", {}
        )
        self.kb: dict = self.config_dict.get("kb", None)
        # self.tools: dict = self.config_dict.get("tools", None)

    @classmethod
    def generate_config(
            cls,
            task_description: str,
            node_name: str,
            node_description: str,
            next_nodes: List[str],
    ):
        llm_config = {
            "LLM_type": "OpenAI",
            "model": "gpt-4-turbo-2024-04-09",
            "temperature": 0,
            "log_path": "logs/generate_config/node",
            "ACTIVE_MODE": True,
            "SAVE_LOGS": True,
        }
        llm = OpenAILLM(LLMConfig(llm_config))
        system_prompt = "You are a helpful assistant designed to output JSON."
        last_prompt = NODE_ROLES_CONFIG_GENERATION_PROMPT_TEMPLATE.format(
            task_description=task_description, node_description=node_description
        )

        response, content = llm.get_response(
            chat_messages=None,
            system_prompt=system_prompt,
            last_prompt=last_prompt,
            response_format={"type": "json_object"},
        )

        # Converting the JSON format string to a JSON object
        json_config = json.loads(content.strip("`").strip("json").strip())
        node_roles_description = json_config["roles"]
        begin_role = json_config["begin_role"]

        controller_config = cls.ControllerConfig.generate_config(
            task_description,
            node_name,
            node_description,
            next_nodes,
            node_roles_description,
        )

        node_prompt_templates = {}
        node_prompt_paddings = {}

        for role, role_description in node_roles_description.items():
            system_prompt = "You are a helpful assistant designed to output JSON."
            last_prompt = NODE_PROMPTS_CONFIG_GENERATION_PROMPT_TEMPLATE.format(
                task_description=task_description,
                node_description=node_description,
                node_roles_description=node_roles_description,
                role=role,
                node_prompt_templates=node_prompt_templates,
            )

            response, content = llm.get_response(
                chat_messages=None,
                system_prompt=system_prompt,
                last_prompt=last_prompt,
                response_format={"type": "json_object"},
            )

            # Converting the JSON format string to a JSON object
            json_config = json.loads(content.strip("`").strip("json").strip())

            if (
                    "prompt_templates" not in json_config
                    or "prompt_paddings" not in json_config
            ):
                raise ValueError(
                    f"The prompt_templates and prompt_paddings are required in the generate node prompts config. Currently, the generated config is {json_config}."
                )

            for prompt_type, prompt_template in json_config["prompt_templates"].items():
                node_prompt_templates[prompt_type] = prompt_template

            node_prompt_paddings[role] = {}
            for prompt_type, padding in json_config["prompt_paddings"].items():
                node_prompt_paddings[role][prompt_type] = {
                    "value_source": "config",
                    "value": padding,
                }

        for prompt_type, prompt_template in node_prompt_templates.items():
            # 使用正则表达式替换
            # 正则表达式 `__(\w+)__` 匹配被双下划线包围的单词
            # \w+ 匹配一个或多个字母或数字（即一个单词）
            # 括号 () 用于捕获匹配的部分
            # 在替换字符串中，可以用 \1 引用第一个捕获组
            node_prompt_templates[prompt_type] = re.sub(
                r"__(\w+)__", r"{\1}", prompt_template
            )

        return cls(
            config_path_or_dict={
                "node_name": node_name,
                "node_description": node_description,
                "node_roles_description": node_roles_description,
                "begin_role": begin_role,
                "controller": controller_config.to_dict(),
                "node_prompt_templates": node_prompt_templates,
                "node_prompt_paddings": node_prompt_paddings,
            }
        )


class Node:
    def __init__(self, config: NodeConfig):
        self.config = config
        self.node_name = self.config.node_name
        self.controller = NodeConfig.ControllerConfig(self.config.controller)
        self.begin_role = self.config.begin_role
        self.begin_query = self.config.begin_query
        self.node_description = self.config.node_description
        self.node_primary_prompts = self.config.node_primary_prompts
        self.node_prompt_templates = self.config.node_prompt_templates
        self.node_prompt_paddings = self.config.node_prompt_paddings
        self.kb: KnowledgeBase = (
            KnowledgeBase(config=KnowledgeBaseConfig(self.config.kb))
            if self.config.kb
            else None
        )
        # self.tools = self.config.tools

        # Begin status of the node
        self.current_role: str = self.begin_role
        self.is_begin: bool = True

        # Will be initailized in SOP
        self.next_nodes: Dict[str, Node] = {}
        self.node_agents: List[str] = []
        self.node_roles: List[str] = []

        # In the same node, agent names and roles are mapped one-to-one, so we use a bidict to store the mapping relationships
        # Initialized by SOP
        self.name_role_hash: bidict = bidict()

        # Get the node prompts from the padding (here we don't hava case information, some prompts may be empty)
        self.node_prompts: Dict[str, dict] = {}

        self.node_roles_description: dict = self.config.node_roles_description

        if not self.node_primary_prompts:
            for role in self.node_prompt_paddings.keys():
                self.node_primary_prompts[role] = {}
                for prompt_type in ["TASK", "RULE", "STYLE", "EXAMPLE", "COT"]:
                    self.node_primary_prompts[role][prompt_type] = ""

    def load_node_prompts(self, case_padding: dict = None) -> dict:
        """Load the node prompts from the padding in the config or the case."""
        node_prompts = {}
        for agent_role, primary_prompts_dicts in self.node_primary_prompts.items():
            if agent_role not in self.name_role_hash.inverse:
                raise ValueError(
                    f"Invalid agent role '{agent_role}', the supported agent roles are {self.name_role_hash.inverse.keys()}."
                )
            else:
                agent_name = self.name_role_hash.inverse[agent_role]
            if agent_name not in node_prompts:
                node_prompts[agent_name] = {}
            for prompt_type, prompt in primary_prompts_dicts.items():
                node_prompts[agent_name][prompt_type] = prompt

        for agent_role, agent_padding_dicts in self.node_prompt_paddings.items():
            agent_name = self.name_role_hash.inverse[agent_role]
            if agent_name not in node_prompts:
                node_prompts[agent_name] = {}
            # deal with the padding for each agent
            for prompt_type, var_description in agent_padding_dicts.items():
                if var_description["value_source"] == "config":
                    # the padding comes from the config, directly apply the padding to the prompt
                    node_prompts[agent_name][prompt_type] = Node.apply_var_to_prompt(
                        self.node_prompt_templates,
                        prompt_type,
                        var_description["value"],
                    )

                elif var_description["value_source"] == "case":
                    # the padding comes from the case, apply the padding to the prompt with the case information
                    if case_padding is None:
                        # if the case_padding is None, the padding is not available
                        # add it because when initializing the node, we don't have the case information
                        node_prompts[agent_name][prompt_type] = None
                    else:
                        node_prompts[agent_name][prompt_type] = (
                            Node.apply_var_to_prompt(
                                self.node_prompt_templates,
                                prompt_type,
                                case_padding[var_description["value"]],
                            )
                        )
                else:
                    raise ValueError(
                        f"Invalid value_source'{var_description['value_source']}', the supported value_source are ['config', 'case']"
                    )

        return node_prompts

    @staticmethod
    def apply_var_to_prompt(
            prompt_templates: Dict[str, str], prompt_type: str, padding: dict
    ):
        """Apply the padding to the prompt template."""
        if prompt_type not in prompt_templates:
            raise ValueError(
                f"Invalid prompt type '{prompt_type}', the supported prompt types are {prompt_templates.keys()}."
            )
        prompt = prompt_templates[prompt_type].format(**padding)
        return prompt

    def to_dict(self):
        """trans to a dict, it will cover all the information of the node. the dict can be used to initialize a node."""
        ret_config: NodeConfig = copy.deepcopy(self.config)

        # 根据当前node的具体信息更新config
        # prompt
        # 这种保存的写法是因为目前框架那边把DEFAULT_NODE_PROMPT_TEMPLATES 整合进了self.node_prompt_templates里，彻底弃用之后可以采用下面一行的写法
        ret_config.node_prompt_templates = {
            key: self.node_prompt_templates[key]
            for key in self.node_prompt_templates
            if key not in DEFAULT_NODE_PROMPT_TEMPLATES
        }
        # ret_config.node_prompt_templates = self.node_prompt_templates
        ret_config.node_primary_prompts = self.node_primary_prompts

        # controller
        ret_controller_config = ret_config.controller
        ret_controller_config["max_chat_nums"] = self.controller.max_chat_nums

        ret_controller_config["transit_type"] = self.controller.transit_type
        ret_controller_config["transit_system_prompt"] = self.controller.transit_system_prompt
        ret_controller_config["transit_last_prompt"] = self.controller.transit_last_prompt

        ret_controller_config["route_type"] = self.controller.route_type
        ret_controller_config["route_system_prompt"] = self.controller.route_system_prompt
        ret_controller_config["route_last_prompt"] = self.controller.route_last_prompt

        # node description
        ret_config.node_description = self.node_description

        # roles description
        ret_config.node_roles_description = self.node_roles_description

        # todo 还没修改的：kb, tools,这部分还有一些问题
        return ret_config.to_dict()

    def get_dict_for_node_optimizer(self):
        """Get the dict for the optimizer. only get the info needed for the optimizer."""
        # mode对应了3中优化Node的方式，分别是优化role，优化controller，同时优化role和controller

        # todo role 和 controller还没做
        ret_dict = self.to_dict()
        ret_dict.pop("kb", None)
        ret_dict.pop("tools", None)
        ret_dict.pop("begin_query", None)

        # delete the controller info
        ret_dict["controller"].pop("max_chat_nums", None)
        ret_dict["controller"].pop("transit_type", None)
        ret_dict["controller"].pop("transit_system_prompt", None)
        ret_dict["controller"].pop("transit_last_prompt", None)

        # delete node_primary_prompts
        ret_dict.pop("node_primary_prompts", None)
        ret_dict.pop("node_prompt_templates", None)
        ret_dict.pop("node_prompt_paddings", None)
        return ret_dict
