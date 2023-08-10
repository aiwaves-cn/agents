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
from utils import get_gpt_response_rule_stream,get_gpt_response_rule,extract
from sop import Node,SOP
from datebase import *

headers = {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'X-Accel-Buffering': 'no',
}


class Agent():
    """
    Auto agent, input the JSON of SOP.
    """

    def __init__(self, role, name) -> None:
        self.content = {"messages": []}
        self.role = role
        self.name = name
        self.current_node_name = None

        self.args_dict = {
            "short_memory": {},
            "long_memory": {},
        }

    def step(self, user_query, user_role, user_name, sop: SOP):
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
            "content": f"{user_name}({user_role}):{user_query}"
        }
        self.update_memory(current_memory)
        self.args_dict["query"] = user_query
        self.args_dict["temperature"] = sop.temperature

        # print(f"chat_history:{chat_history}")
        flag = 0
        current_node = sop.nodes[self.current_node_name]
        current_node:Node
        "Continuous recursion"
        while True:
            flag = current_node.is_interactive
            print(current_node.name)
            response, res_dict = self.act(current_node)
            if len(current_node.next_nodes) == 1:
                current_node = current_node.next_nodes["0"]
            else:
                next_node = self.plan(current_node)
                current_node = current_node.next_nodes[next_node]

            all = ""
            for res in response:
                all += res if res else ''
                yield res
            current_memory = {
                "role": self.role,
                "content": f"{self.name}({self.role}):{all}"
            }
            self.update_memory(current_memory)

            #====================================================#
            if "response" in res_dict and res_dict["response"]:
                for res in res_dict["response"]:
                    yield res
                del res_dict["response"]

            #====================================================#

            if flag or current_node == sop.root:
                self.args_dict["temp_memory"] = {}
                yield {
                    "memory": self.args_dict,
                    "current_node_name": current_node.name
                }
                break

    def load_date(self, task:TaskConfig):
        self.current_node_name = task.current_node_name
        self.args_dict["long_memory"] = {
            key: value
            for key, value in task.memory.items()
        }

    def act(self, node: Node):
        system_prompt, last_prompt, res_dict = node.compile(
            self.role, self.args_dict)
        chat_history = self.args_dict["long_history"]["chat_history"]
        temperature = self.args_dict["temperature"]
        response = get_gpt_response_rule_stream(chat_history,
                                                system_prompt,
                                                last_prompt,
                                                temperature=temperature,
                                                args_dict=self.args_dict)

        return response, res_dict

    def plan(self, node: Node):
        system_prompt = node.transition_rule["system_prompt"]
        last_prompt = node.transition_rule["last_prompt"]
        keyword = node.transition_rule[:keyword]
        response = get_gpt_response_rule(
            self.args_dict["long_memory"]["chat_history"],
            system_prompt,
            last_prompt,
            args_dict=self.args_dict)
        next_node = extract(response, keyword)
        return next_node

    def generate_sop(self):
        pass

    def reflection(self):
        pass

    def judge_sensitive(self, query):
        current_path = os.path.abspath(__file__)
        current_path = os.path.dirname(current_path)
        with open(os.path.join(current_path, 'sensitive.txt')) as file_01:
            lines = file_01.readlines()
            lines = [i.rstrip() for i in lines]
            seg_list = jieba.cut(query, cut_all=True)
            for seg in seg_list:
                if seg in lines:
                    return True
        return False

    def update_memory(self, memory):
        if "long_memory" in self.args_dict:
            self.args_dict["long_memory"].append(memory)
        else:
            self.args_dict["long_memory"] = memory

    def chat(self, sop: SOP, user_role="user", user_name="A神"):
        """
            reply api ,The interface set for backend calls 
            """
        user_query = input("user:")
        if self.judge_sensitive(user_query):
            response = "<回复>对不起，您的问题涉及禁忌话题或违规内容，我无法作答，请注意您的言辞！</回复>"
            print(f"AI:{response}")
            return

        current_memory = {
            "role": "user",
            "content": f"{user_name}({user_role}):{user_query}"
        }
        self.update_memory(current_memory)
        self.args_dict["query"] = user_query
        self.args_dict["temperature"] = sop.temperature

        flag = 0
        current_node = sop.nodes[self.current_node_name]

        while True:
            flag = current_node.is_interactive
            print(current_node.name)
            response, res_dict = self.act(current_node)
            if len(current_node.next_nodes) == 1:
                current_node = current_node.next_nodes["0"]
            else:
                current_node = current_node.next_nodes[res_dict["next_node"]]

            all = ""
            for res in response:
                all += res if res else ''
            print(f"{self.name}({self.role}):{all}")
            current_memory = {
                "role": self.role,
                "content": f"{self.name}({self.role}):{all}"
            }
            self.update_memory(current_memory)

            #====================================================#
            all = ""
            if "response" in res_dict and res_dict["response"]:
                for res in res_dict["response"]:
                    all += res
                del res_dict["response"]
            print(f"{self.name}({self.role}):{all}")
            #====================================================#

            if flag or current_node == sop.root:
                self.current_node_name = current_node.name
                self.args_dict["temp_memory"] = {}
                break

    def run(self,sop):
        while True:
            self.chat(sop)


my_sop = SOP("/home/aiwaves/longli/agents/examples/eye/eye_new.json")
agent = Agent("眼科客服","吴嘉隆")
agent.run(my_sop)
