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
"""The AgentTeam class is a class that represents a team of agents."""
import os
import copy
import json
from typing import Dict, Union

from .agent import AgentConfig, Agent
from .llm import OpenAILLM, LLMConfig
from .memory import ShortTermMemory, LongTermMemory
from .environment import EnvironmentConfig, Environment
from .action import Action
from ..utils.config import Config
from ..utils.prompts import AGENT_TEAM_CONFIG_GENERATION_PROMPT_TEMPLATE


class AgentTeamConfig(Config):

    required_fields = ["agents", "environment"]

    def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
        super().__init__(config_path_or_dict)
        self._validate_config()

        self.agents: dict = self.config_dict["agents"]
        self.environment: dict = self.config_dict["environment"]

    @classmethod
    def generate_config(
        cls, task_description: str, all_node_roles_description: Dict[str, dict]
    ):
        llm_config = {
            "LLM_type": "OpenAI",
            "model": "gpt-4-turbo-2024-04-09",
            "temperature": 0.3,
            "log_path": "logs/generate_config/agent_team",
            "ACTIVE_MODE": True,
            "SAVE_LOGS": True,
        }

        all_roles_description = ""
        for node_name, node_roles_description in all_node_roles_description.items():
            all_roles_description += f"Node '{node_name}' contains the roles '{list(node_roles_description.keys())}', they cannot be allocated to the same people. "
            for role_name, role_description in node_roles_description.items():
                all_roles_description += (
                    "At node '{node_name}', {role_name} {role_description}. ".format(
                        node_name=node_name,
                        role_name=role_name,
                        role_description=role_description[0].lower()
                        + role_description[1:].strip("."),
                    )
                )

        llm = OpenAILLM(LLMConfig(llm_config))
        system_prompt = "You are a helpful assistant designed to output JSON."
        last_prompt = AGENT_TEAM_CONFIG_GENERATION_PROMPT_TEMPLATE.format(
            task_description=task_description,
            all_roles_description=all_roles_description.strip(),
        )

        response, content = llm.get_response(
            chat_messages=None,
            system_prompt=system_prompt,
            last_prompt=last_prompt,
        )

        # Converting the JSON format string to a JSON object
        json_config = json.loads(content.strip("`").strip("json").strip())

        agents_dict = {}
        for agent_name, agent_roles in json_config.items():
            agent_config = AgentConfig.generate_config(agent_name, agent_roles)
            agents_dict[agent_name] = agent_config.to_dict()

        environment_config = EnvironmentConfig()

        return cls(
            config_path_or_dict={
                "agents": agents_dict,
                "environment": environment_config.to_dict(),
            }
        )


class AgentTeam:
    """Agent has a team of agents, and the team has an environment.
    The team is responsible for the interaction between agents and the environment."""

    def __init__(self, config: AgentTeamConfig):
        self.config = config
        self.agents: Dict[str, Agent] = {}
        if self.config.agents:
            for agent_config in self.config.agents.values():
                agent = Agent(config=AgentConfig(agent_config))
                self.agents[agent.agent_name] = agent
        self.environment: Environment = (
            Environment(config=EnvironmentConfig(self.config.environment))
            if self.config.environment
            else None
        )

    def step(self, agent_name, current_node, user_input=None):
        return self.agents[agent_name].step(
            current_node=current_node,
            environment=self.environment,
            user_input=user_input,
        )

    def execute(self, action: Action):
        content = ""
        for res in action.content:
            content += res

        # Delete the third person from the dialogue
        parse = "{action.agent_name}:"
        content = content.replace(parse, "")

        # Update short-term memory in shared memory of the environment
        shared_short_term_memory: ShortTermMemory = self.environment.shared_memory[
            "short_term_memory"
        ]
        shared_short_term_memory.append_memory(
            {
                "name": action.agent_name,
                "role": action.agent_role,
                "content": content,
            }
        )

        # Update summary in shared memory of the environment
        ENVIRONMENT_SUMMARY_STEP = eval(
            os.environ.get("ENVIRONMENT_SUMMARY_STEP", "10")
        )
        if len(shared_short_term_memory) % ENVIRONMENT_SUMMARY_STEP == 0:
            summary = shared_short_term_memory.get_memory_summary()
            self.environment.shared_memory["summary"] = summary

        # Update long-term memory in shared memory of the environment
        shared_long_term_memory: LongTermMemory = self.environment.shared_memory[
            "long_term_memory"
        ]
        shared_long_term_memory.append_memory_from_short_term_memory(
            shared_short_term_memory
        )

        # Update short-term memory and long-term memory of the act agent if it is not acted by the user
        if not self.agents[action.agent_name].is_user:
            self.agents[action.agent_name].short_term_memory.append_memory(
                {
                    "name": action.agent_name,
                    "role": "assistant",
                    "content": content,
                }
            )
            self.agents[
                action.agent_name
            ].long_term_memory.append_memory_from_short_term_memory(
                self.agents[action.agent_name].short_term_memory
            )

    def dump(self, path):
        save_config = copy.deepcopy(self.config)

        # todo 优化agent和environment时再修改，此时不涉及对agent的更新

        save_config.dump(path)
