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
import time
import os
import jieba
from utils import get_gpt_response_rule_stream, get_gpt_response_rule, extract
from sop import Node, SOP, controller
from datebase import *

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
        self.content = {"messages": []}
        self.role = role
        self.name = name
        self.current_node_name = None
        self.sop = None

        self.args_dict = {
            "short_memory": {},
            "long_memory": {"chat_history": []},
        }

    def step(
        self, user_query, user_role, user_name, current_node: Node, temperature=0.3
    ):
        """
        reply api ,The interface set for backend calls
        """
        if self.judge_sensitive(user_query):
            response = "<回复>对不起，您的问题涉及禁忌话题或违规内容，我无法作答，请注意您的言辞！</回复>"
            for res in response:
                time.sleep(0.02)
                yield res
            return

        current_memory = {
            "role": "user",
            "content": f"{user_name}({user_role}):{user_query}",
        }
        self.update_memory(current_memory)

        self.args_dict["query"] = user_query
        self.args_dict["temperature"] = temperature
        response, res_dict = self.act(current_node)

        all = ""
        for res in response:
            all += res if res else ""
            yield res
        current_memory = {
            "role": "assistant",
            "content": f"{self.name}({self.role}):{all}",
        }
        self.update_memory(current_memory)

        # ====================================================#
        if "response" in res_dict and res_dict["response"]:
            all = ""
            for res in res_dict["response"]:
                all += res
                yield res
            current_memory = {
                "role": "assistant",
                "content": f"{self.name}({self.role}):{all}",
            }
            self.update_memory(current_memory)
            del res_dict["response"]

        # ====================================================#

    def load_date(self, task: TaskConfig):
        self.current_node_name = task.current_node_name
        self.args_dict["long_memory"] = {
            key: value for key, value in task.memory.items()
        }

    def act(self, node: Node):
        system_prompt, last_prompt, res_dict = node.compile(self.role, self.args_dict)
        chat_history = self.args_dict["long_memory"]["chat_history"]
        temperature = self.args_dict["temperature"]
        response = get_gpt_response_rule_stream(
            chat_history,
            system_prompt,
            last_prompt,
            temperature=temperature,
            args_dict=self.args_dict,
        )

        return response, res_dict

    def generate_sop(self):
        pass

    def reflection(self):
        pass

    def judge_sensitive(self, query):
        current_path = os.path.abspath(__file__)
        current_path = os.path.dirname(current_path)
        with open(os.path.join(current_path, "sensitive.txt")) as file_01:
            lines = file_01.readlines()
            lines = [i.rstrip() for i in lines]
            seg_list = jieba.cut(query, cut_all=True)
            for seg in seg_list:
                if seg in lines:
                    return True
        return False

    def update_memory(self, memory):
        self.args_dict["long_memory"]["chat_history"].append(memory)

    def run(self, sop):
        while True:
            self.chat(sop)
