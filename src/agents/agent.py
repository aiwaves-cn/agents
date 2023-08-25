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
"""LLM autonoumous agent"""
from utils import get_key_history
from datebase import *
from State import State
import torch
from LLM import *
from component import *
from extra_component import *

headers = {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}


class Agent:
    """
    Auto agent, input the JSON of SOP.
    """


    def __init__(self, name,agent_state_roles,**kwargs) -> None:
        self.state_roles = agent_state_roles
        self.name = name
        self.LLMs = kwargs["LLMs"]
        self.agent_dict = {
            "name" :name,
            "current_roles":"",
            "chat_history":[],
            "summary":""
        }

    @classmethod
    def from_config(cls,config):
        roles_to_names = {}
        names_to_roles = {}
        agents = {}
        for agent_name,agent_dict in config["agents"].items():
            agent_state_roles = {}
            agent_LLMs = {}
            for state_name,agent_role in agent_dict.items():
                if state_name not in roles_to_names:
                    roles_to_names[state_name] = {}
                if state_name not in names_to_roles:
                    names_to_roles[state_name] = {}                
                roles_to_names[state_name][agent_role] = agent_name
                names_to_roles[state_name][agent_name] = agent_role
                agent_state_roles[state_name] = agent_role
                current_state = config["states"][state_name]
                LLM_type = current_state["agent_states"][agent_role]['LLM_type'] if "LLM_type" in current_state["agent_states"][agent_role] else "OpenAI"
                if LLM_type == "OpenAI":
                    agent_LLMs[state_name] = OpenAILLM(**current_state["agent_states"][agent_role]['LLM'])
            agents[agent_name] = cls(agent_name,agent_state_roles,LLMs = agent_LLMs)
        return agents,roles_to_names,names_to_roles
    
    
    def step(self, current_state: State, is_user = False):
        if is_user:
            response = input(f"{self.name}:")
            response = f"{self.name}:{response}"
        else:
            return self.act(current_state)
    
    def act(self, current_state: State):

        system_prompt, last_prompt, res_dict = self.compile(current_state)
        chat_history = self.agent_dict["chat_history"]
        current_LLM = self.LLMs[current_state.name]

        query = (
            self.agent_dict["chat_history"][-1]
            if len(self.agent_dict["chat_history"]) > 0
            else " "
        )
        key_history = get_key_history(
            query,
            self.agent_dict["chat_history"][:-1],
            self.agent_dict["chat_embeddings"][:-1],
        )

        response = current_LLM.get_response(
            chat_history,
            system_prompt,
            last_prompt,
            stream=True,
            summary=self.agent_dict["summary"],
            key_history=key_history,
        )
        return {"response":response,"res_dict":res_dict}
        

    def update_memory(self, memory, summary, current_embedding):
        self.agent_dict["chat_history"].append(memory)
        
        if "chat_embeddings" not in self.agent_dict:
            self.agent_dict["chat_embeddings"] = current_embedding
        else:
            self.agent_dict["chat_embeddings"] = torch.cat(
                [self.agent_dict["chat_embeddings"], current_embedding],
                dim=0,
            )
        self.agent_dict["summary"] = summary
        
            
    def compile(self, current_state):
        self.agent_dict["current_roles"] = self.state_roles[current_state.name]
        current_state_name = current_state.name
        self.agent_dict["LLM"] = self.LLMs[current_state_name]
        components = current_state.components[self.state_roles[current_state_name]]
        
        system_prompt = current_state.environment_prompt if current_state.environment_prompt else ""
        last_prompt = ""
        
        res_dict = {}
        for component in components.values():
            if isinstance(component, (OutputComponent, LastComponent)):
                last_prompt = last_prompt + "\n" + component.get_prompt(self.agent_dict)
            elif isinstance(component, PromptComponent):
                system_prompt = system_prompt + "\n" + component.get_prompt(self.agent_dict)
            elif isinstance(component, ToolComponent):
                response = component.func(self.agent_dict)
                if "prompt" in response and response["prompt"]:
                    last_prompt = last_prompt + "\n" + response["prompt"]
                self.agent_dict.update(response)
                res_dict.update(response)
        return system_prompt, last_prompt, res_dict
    

    def generate_sop(self):
        pass

    def reflection(self):
        pass
