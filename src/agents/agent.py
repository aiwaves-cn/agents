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
from utils import get_response,extract,get_key_history
from sop import Node
from datebase import *
import torch
import os

headers = {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}


class Agent:
    """
    Auto agent, input the JSON of SOP.
    """

    def __init__(self, role, name) -> None:
        self.role = role
        self.name = name
        self.current_node_name = None
        self.sop = None

        self.agent_dict = {
            "short_memory": {"chat_history":[]},
            "long_memory": {"chat_history": [], "summary": ""},
        }

    def step(self, current_node: Node, is_user,temperature=0.3):
        """
        reply api ,The interface set for backend calls
        """
        self.agent_dict["temperature"] = temperature
        if is_user:
            response = input(f"{self.name}:")
            response = f"{self.name}:{response}"
            res_dict = {}
        else:
            response, res_dict = self.act(current_node)
        # ====================================================#
        if "response" in res_dict and res_dict["response"]:
            for res in res_dict["response"]:
                yield res
            del res_dict["response"]
            
        for res in response:
            yield res
        # ====================================================#

    def load_date(self, task: TaskConfig):
        self.current_node_name = task.current_node_name
        self.agent_dict["long_memory"] = {
            key: value for key, value in task.memory.items()
        }

    def act(self, node: Node):
        """
        Output the output of the agent at this node
        Returns:
            response: gpt generator
            res_dict: other response
        """
        system_prompt, last_prompt, res_dict = node.compile(self.role, self.agent_dict)
        chat_history = self.agent_dict["short_memory"]["chat_history"]
        temperature = self.agent_dict["temperature"]
        
        query = self.agent_dict["long_memory"]["chat_history"][-1] if len(self.agent_dict["long_memory"]["chat_history"])>0 else " "
        key_history = get_key_history(query,self.agent_dict["long_memory"]["chat_history"][:-1],self.agent_dict["long_memory"]["chat_embeddings"][:-1])
        
        response = get_response(
            chat_history,
            system_prompt,
            last_prompt,
            temperature=temperature,
            stream= True,
            summary=self.agent_dict["short_memory"]["summary"],
            key_history = key_history
        )

        return response, res_dict
    
    def update_memory(self,memory,summary,current_embedding):
        MAX_CHAT_HISTORY = eval(os.environ["MAX_CHAT_HISTORY"]) if "MAX_CHAT_HISTORY" in os.environ else 10
        
        self.agent_dict["long_memory"]["chat_history"].append(memory)
        self.agent_dict["short_memory"]["chat_history"].append(memory)
        if "chat_embeddings" not in  self.agent_dict["long_memory"]:
            self.agent_dict["long_memory"]["chat_embeddings"] = current_embedding
        else:
            self.agent_dict["long_memory"]["chat_embeddings"] = torch.cat([self.agent_dict["long_memory"]["chat_embeddings"],current_embedding],dim = 0)
        self.agent_dict["short_memory"]["summary"] = summary
        if len(self.agent_dict["short_memory"]["chat_history"]) > MAX_CHAT_HISTORY:
            self.agent_dict["short_memory"]["chat_history"] = self.agent_dict["short_memory"]["chat_history"][-MAX_CHAT_HISTORY//2:]
            

    def generate_sop(self):
        pass

    def reflection(self):
        pass

