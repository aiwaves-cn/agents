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
"""The solution module contains the Solution class, which is the main class for the solution of a task."""
import copy
import os
from typing import Union

from .task import TaskConfig, Task
from .sop import SOPConfig, SOP
from ..agents.agent_team import AgentTeamConfig, AgentTeam
from ..evaluation.trajectory import Trajectory
from ..evaluation.state import State
from ..utils.config import Config


class SolutionConfig(Config):

    required_fields = ["agent_team", "sop"]

    def __init__(self, config_path_or_dict: Union[str, dict] = None) -> None:
        super().__init__(config_path_or_dict)
        self._validate_config()

        self.task = self.config_dict.get("task", None)
        self.agent_team = self.config_dict["agent_team"]
        self.sop = self.config_dict["sop"]

    @classmethod
    def generate_config(cls, query):
        task_config = TaskConfig.generate_config(query)
        sop_config = SOPConfig.generate_config(query, task_config.task_description)

        all_node_roles_description = {}
        for node_name, node_config in sop_config.nodes.items():
            all_node_roles_description[node_name] = node_config[
                "node_roles_description"
            ]
        agent_team_config = AgentTeamConfig.generate_config(
            task_config.task_description, all_node_roles_description
        )

        return cls(
            config_path_or_dict={
                "task": task_config.to_dict(),
                "agent_team": agent_team_config.to_dict(),
                "sop": sop_config.to_dict(),
            }
        )


class Solution:
    def __init__(self, config: SolutionConfig):
        self.config = config
        self.task: Task = (
            Task(config=TaskConfig(self.config.task)) if self.config.task else None
        )
        self.agent_team: AgentTeam = AgentTeam(
            config=AgentTeamConfig(self.config.agent_team)
        )
        self.sop = SOP(config=SOPConfig(self.config.sop))
        self.sop.init_name_role_hash_for_nodes(agent_team=self.agent_team)
        self.sop.init_node_prompts()

    def run(self, mode="test"):
        if mode == "train":
            trajectory = Trajectory([])

        while not self.sop.finished:
            current_node, current_agent_name = self.sop.next(
                environment=self.agent_team.environment
            )
            if current_node and current_agent_name:
                action = self.agent_team.step(current_agent_name, current_node)
                self.agent_team.execute(action)
                if mode == "train":
                    trajectory.add_state(
                        State(
                            current_node,
                            self.agent_team.agents[current_agent_name],
                            action,
                            self.agent_team.environment,
                        )
                    )
            else:
                assert self.sop.finished == True
                # TODO: Save environment shared short term memory

        if mode == "train":
            return trajectory
        else:
            return None

    def update_prompt_template(self, node_name, agent_name, prompt_template):
        """更新node中agent的prompt_template"""
        pass

    def dump(self, base_path):
        """Save the solution configuration to a file."""
        # get the base path, create the directory if it does not exist
        base_path = str(base_path)
        if base_path.endswith("solution.json"):
            base_path = base_path[:-13]
        os.makedirs(base_path, exist_ok=True)

        # get the path of the configuration files
        solution_path = f"{base_path}/solution.json"
        sop_path = f"{base_path}/sop.json"
        task_path = f"{base_path}/task.json"
        agent_team_path = f"{base_path}/agent_team.json"

        # save solution configuration
        solution_config = copy.deepcopy(self.config)
        solution_config.task = task_path
        solution_config.agent_team = agent_team_path
        solution_config.sop = sop_path
        solution_config.dump(solution_path)

        # save task, agent_team, and sop configurations
        self.task.dump(task_path)
        self.agent_team.dump(agent_team_path)
        self.sop.dump(sop_path)
