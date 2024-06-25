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
"""The Agent class is a class that represents an agent."""
import json
import logging
import litellm
from datetime import datetime
from typing import Dict, Union

from .llm import LLMConfig, OpenAILLM
from .memory import Memory, ShortTermMemory, LongTermMemory
from .toolkit import Toolkit
from .environment import Environment
from .action import ActionConfig, Action
from ..tools import Tool
from ..utils.prompts import *
from ..utils.config import Config
from ..utils.files import save_logs

logger = logging.getLogger(__name__)


class AgentConfig(Config):

    required_fields = ["agent_name", "agent_roles"]

    def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
        super().__init__(config_path_or_dict)
        self._validate_config()

        self.agent_name: str = self.config_dict["agent_name"]
        self.agent_roles: Dict[str, str] = self.config_dict["agent_roles"]
        self.agent_style: str = self.config_dict.get("agent_style")
        self.agent_description: str = self.config_dict.get("agent_description")
        self.LLM_config: dict = self.config_dict.get("LLM_config")
        self.toolkit: dict = self.config_dict.get("toolkit")
        self.memory: dict = self.config_dict.get("memory")
        self.is_user: bool = self.config_dict.get("is_user", False)

    @classmethod
    def generate_config(cls, agent_name: str, agent_roles: Dict[str, str]):
        llm_config = LLMConfig()
        llm_config.log_path = f"logs/{agent_name}"

        return cls(
            config_path_or_dict={
                "agent_name": agent_name,
                "agent_roles": agent_roles,
                "LLM_config": llm_config.to_dict(),
            }
        )


class Agent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_name = self.config.agent_name
        self.agent_roles = self.config.agent_roles
        self.agent_style = self.config.agent_style
        self.agent_description = self.config.agent_description
        llm_config = (
            LLMConfig(self.config.LLM_config) if self.config.LLM_config else None
        )
        self.LLM = OpenAILLM(llm_config) if llm_config else None
        if self.config.memory:
            self.short_term_memory = (
                ShortTermMemory(
                    config=self.config.memory["short_term_memory"], messages=[]
                )
                if "short_term_memory" in self.config.memory
                else ShortTermMemory(config={}, messages=[])
            )
            self.long_term_memory = (
                LongTermMemory(
                    config=self.config.memory["long_term_memory"],
                    json_path=self.config.memory["long_term_memory"].get(
                        "json_path", f"memory/{self.agent_name}.jsonl"
                    ),
                    chunk_list=[],
                )
                if "long_term_memory" in self.config.memory
                else LongTermMemory(
                    config={},
                    json_path=f"memory/{self.agent_name}.jsonl",
                    chunk_list=[],
                )
            )
        else:
            self.short_term_memory = ShortTermMemory(config={}, messages=[])
            self.long_term_memory = LongTermMemory(
                config={},
                json_path=f"memory/{self.agent_name}.jsonl",
                chunk_list=[],
            )
        self.toolkit = (
            Toolkit.from_config(self.config.toolkit) if self.config.toolkit else None
        )
        self.is_user = self.config.is_user

    def observe(self, environment: Environment):
        """
        observe the environment and return the observation
        Return: observation(dict)
        """
        # If the environment type is cooperative, the agent will share the information with other agents
        if environment.environment_type == "cooperative":
            short_term_memory_messages = environment.shared_memory[
                "short_term_memory"
            ].get_memory()
            environment_relevant_memory = Memory.encode_memory(
                short_term_memory_messages, self.agent_name
            )
        # Otherwise, the agent will not use the shared memory
        else:
            environment_relevant_memory = "None."

        agent_relevant_memory = self.short_term_memory.get_memory_string(
            self.agent_name
        )

        observation = OBSERVATION_TEMPLATE.format(
            environment_relevant_memory=environment_relevant_memory,
            agent_relevant_memory=agent_relevant_memory,
        )
        observation = {
            "role": "user",
            "content": observation,
        }
        return observation

    def step(self, current_node, environment: Environment, user_input=None):
        """
        return actions by current state and environment
        Return: action(Action)
        """

        is_node_begin = current_node.is_begin
        current_node.is_begin = False
        is_agent_begin = (
            True
            if is_node_begin
            and current_node.begin_role
            and current_node.begin_role == current_node.name_role_hash[self.agent_name]
            else False
        )

        used_prompt_templates = {}
        prompts_order = []
        response = {}
        content = ""
        tools_results_dict = {}
        system_prompt = ""
        last_prompt = ""
        history_messages = []

        # If the agent is acted by the user, then the agent will use the user input as the content
        start_time = None
        end_time = None
        if self.is_user:
            user_input = user_input if user_input else input(f"{self.agent_name}: ")
            content = user_input
        # Otherwise the agent will use LLM to generate the response
        else:
            # First update the information according to the current environment
            if len(environment.shared_memory["short_term_memory"].get_memory()) > 0:
                observation = self.observe(environment)
                if observation:
                    self.short_term_memory.append_memory(observation)

            # If the agent is the first to speak in the node, then the agent will use the predefined begin_query
            if is_agent_begin and current_node.begin_query:
                content = current_node.begin_query
            # Otherwise, the agent will use the LLM to generate the response
            else:
                start_time = datetime.now().timestamp()
                history_messages = self.short_term_memory.get_memory()
                system_prompt, last_prompt = self.compile(current_node)

                agent_role = current_node.name_role_hash[self.agent_name]
                if agent_role in current_node.node_primary_prompts:
                    prompts_order.extend(
                        list(current_node.node_primary_prompts[agent_role].keys())
                    )
                
                if agent_role in current_node.node_prompt_paddings:
                    for prompt_type in current_node.node_prompt_paddings[agent_role].keys():
                        if prompt_type not in DEFAULT_NODE_PROMPT_TEMPLATES:
                            prompts_order.append(prompt_type)
                            used_prompt_templates[prompt_type] = (
                                current_node.node_prompt_templates[prompt_type]
                            )

                available_tools = []
                if self.toolkit and self.toolkit.tool_specifications:
                    available_tools.extend(self.toolkit.tool_specifications)
                if (
                    environment.shared_toolkit
                    and environment.shared_toolkit.tool_specifications
                ):
                    available_tools.extend(
                        environment.shared_toolkit.tool_specifications
                    )
                if current_node.kb and current_node.kb.kb_specification:
                    available_tools.append(current_node.kb.kb_specification)
                if len(available_tools) == 0:
                    available_tools = None

                response, content = self.LLM.get_response(
                    chat_messages=history_messages,
                    system_prompt=system_prompt,
                    last_prompt=last_prompt,
                    stream=False,
                    tools=available_tools,
                )
                end_time = datetime.now().timestamp()

            if isinstance(content, litellm.Message) and content.get("tool_calls"):
                tool_calls = content.tool_calls
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_arguments = json.loads(tool_call.function.arguments)
                    # If the tool is the knowledge_base_retriever, then the agent will retrieve the information from the knowledge base
                    if tool_name == "knowledge_base_retriever":
                        print("\nRetrieving from knowledge base...\n")
                        retrieved_context = current_node.kb.retrieve(**tool_arguments)
                        content = retrieved_context
                    # If the tool is in the toolkit, then the agent will call the tool to generate the content
                    else:
                        if self.toolkit and tool_name in self.toolkit.tools:
                            tool: Tool = self.toolkit.tools[tool_name]
                        elif (
                            environment.shared_toolkit
                            and tool_name in environment.shared_toolkit.tools
                        ):
                            tool: Tool = environment.shared_toolkit.tools[tool_name]
                        else:
                            raise ValueError(
                                f"Tool {tool_name} is not found in the toolkit."
                            )
                        tool_result = tool.func(**tool_arguments)
                        tools_results_dict[tool_call.id] = tool_result
                        content = tool_result["content"]
                save_logs(self.LLM.log_path, history_messages, content)
            else:
                content = content.strip(f"Speak content:").strip()

            print(f"\n{self.agent_name}: {content}\n")

        action_dict = {
            "used_prompt_templates": used_prompt_templates,
            "prompts_order": prompts_order,
            "response": response,
            "content": content,
            "tools_results_dict": tools_results_dict,
            "agent_role": current_node.name_role_hash[self.agent_name],
            "agent_name": self.agent_name,
            "is_user": self.is_user,
            "is_node_begin": is_node_begin,
            "is_agent_begin": is_agent_begin,
            "system_prompt": system_prompt,
            "last_prompt": last_prompt,
            "history_messages": history_messages,
            "latency": end_time - start_time if start_time is not None else 0,
            "start_time_ms": round(start_time * 1000) if start_time is not None else 0,
            "end_time_ms": round(end_time * 1000) if end_time is not None else 0,
        }
        action = Action(config=ActionConfig(action_dict))
        return action

    def compile(self, current_node):
        """
        get prompt from state depend on your role
        Return:
        system_prompt:system_prompt for agents's LLM
        last_prompt:last_prompt for agents's LLM
        """
        system_prompt: str = current_node.node_description
        last_prompt: str = ""
        if self.agent_name in current_node.node_prompts:
            for prompt_type, prompt in current_node.node_prompts[
                self.agent_name
            ].items():
                if prompt:
                    last_prompt = last_prompt + "\n" + prompt
        last_prompt = AGENT_LAST_PROMPT_TEMPLATE.format(
            last_prompt=last_prompt,
            name=self.agent_name,
        )

        return system_prompt, last_prompt

    def to_dict(self, node_name: str):
        """used for serialization in state"""
        # attention: the agent_role should be the role of the agent in the current node,
        # not the role of the agent in the whole task."""

        return {
            "agent_name": self.agent_name,
            "agent_roles": self.agent_roles,
            "agent_role": self.agent_roles.get(node_name, None),
            "agent_style": self.agent_style,
            "agent_description": self.agent_description,
            "is_user": self.is_user,
            "toolkit": self.config.toolkit,
            "LLM": self.config.LLM_config if self.LLM else None,
            "long_term_memory": self.long_term_memory.get_memory(),
            "short_term_memory": self.short_term_memory.get_memory(),
        }
