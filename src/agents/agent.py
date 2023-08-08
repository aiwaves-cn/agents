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
from utils import *
from sop import *
from flask import Response
from datebase import *
import time
from config import *
import jieba

headers = {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'X-Accel-Buffering': 'no',
}


class Agent():
    """
    Auto agent, input the JSON of SOP.
    """

    def __init__(self, sop) -> None:
        self.content = {"messages": []}
        self.SOP = SOP(sop)  
        self.temperature = self.SOP.temperature if hasattr(self.SOP,"temperature") else 0.3

        self.root = self.SOP.root
        self.now_node = self.root

        self.temp_memory = {}
        self.long_memory = {"chat_history": []}
        

        
        self.args_dict = {
            "temp_memory": self.temp_memory,
            "long_memory": self.long_memory,
            "log_path": self.SOP.log_path,
            "temperature": self.temperature,
            "answer_simplify":self.SOP.answer_simplify
        }

    def reply(self, userName, query):
        """
        reply api ,The interface set for backend calls 
        """
        print(query)
        if type(userName) != int:
            userName = 0
        assert type(userName) == int, "username type is not int!"
        self.load_date(userName)

        if self.judge_sensitive(query):
            response = "<回复>对不起，您的问题涉及禁忌话题或违规内容，我无法作答，请注意您的言辞！</回复>"
            for res in response:
                time.sleep(0.02)
                yield res
            return

        now_memory = {"role": "user", "content": query}
        self.update_memory(now_memory)
        self.args_dict["query"] = query

        chat_history = self.long_memory["chat_history"]
        # print(f"chat_history:{chat_history}")
        flag = 0
        now_node = self.now_node
        
        print(self.long_memory)
        "Continuous recursion"
        while True:
            if now_node.done:
                flag = 1
            else:
                flag = 0
            print(now_node.name)
            if isinstance(now_node, GPTNode):
                # If the current node is a node that requires user feedback or a leaf node, recursion will jump out after the node ends running

                # Extract key information to determine which node branch to enter
                if now_node.node_type == "judge":
                    system_prompt, last_prompt = now_node.get_prompt(
                        self.args_dict)
                    response = get_gpt_response_rule(chat_history,
                                                     system_prompt,
                                                     last_prompt,
                                                     args_dict=self.args_dict)
                    keywords = extract(response, now_node.extract_words)
                    next_nodes_nums = len(now_node.next_nodes.keys())

                    for i, key in enumerate(now_node.next_nodes):
                        if i == next_nodes_nums - 1:
                            now_node = now_node.next_nodes[key]
                        elif key == keywords:
                            now_node = now_node.next_nodes[key]
                            break

                # Extract keywords to proceed to the next node
                elif now_node.node_type == "extract":

                    system_prompt, last_prompt = now_node.get_prompt(
                        self.args_dict)
                    response = get_gpt_response_rule(chat_history,
                                                     system_prompt,
                                                     last_prompt,
                                                     args_dict=self.args_dict)
                    if type(now_node.extract_words) == list:
                        for extract_word in now_node.extract_words:
                            keywords = extract(response, extract_word)
                            self.long_memory[extract_word] = keywords
                    else:
                        keywords = extract(response, now_node.extract_words)
                        self.long_memory[now_node.extract_words] = keywords
                    now_node = now_node.next_nodes["0"]

                elif now_node.node_type == "response":

                    system_prompt, last_prompt = now_node.get_prompt(
                        self.args_dict)

                    response = get_gpt_response_rule_stream(
                        chat_history,
                        system_prompt,
                        None,
                        temperature=self.temperature,
                        args_dict=self.args_dict)
                    now_node = now_node.next_nodes["0"]
                    self.now_node = now_node
                    all = ""
                    for res in response:
                        all += res if res else ''
                        yield res
                    now_memory = {"role": "assistant", "content": all}
                    self.update_memory(now_memory)

                elif now_node.node_type == "response_and_extract":
                    now_node.set_user_input(chat_history[-1]["content"])
                    system_prompt, last_prompt = now_node.get_prompt(
                        self.args_dict)
                    response = get_gpt_response_rule_stream(
                        chat_history,
                        system_prompt,
                        last_prompt,
                        temperature=self.temperature,
                        args_dict=self.args_dict)
                    all = ""
                    for res in response:
                        all += res if res else ''
                        yield res

                    if type(now_node.extract_words) == list:
                        for extract_word in now_node.extract_words:
                            keywords = extract(all, extract_word)
                            self.long_memory[extract_word] = keywords
                    else:
                        keywords = extract(all, now_node.extract_words)
                        self.long_memory[now_node.extract_words] = keywords

            elif isinstance(now_node, ToolNode):
                now_output = now_node.func(self.args_dict)
                next_node_id = "0"
                for output in now_output:
                    if isinstance(output, dict):
                        response = output["response"]
                        next_node_id = output["next_node_id"]
                        for res in response:
                            time.sleep(0.02)
                            yield res
                    else:
                        yield output
                now_node = now_node.next_nodes[next_node_id]
                self.now_node = now_node

            if flag or now_node == self.root:
                self.temp_memory = {}
                task = find_data(userName)
                task.memory = self.long_memory
                task.now_node_name = self.now_node.name
                task.save()
                break

    def step(self):
        """
        run on your terminal
        """
        query = input("客户:")
        if self.judge_idle(query):
            chat = self.chat(query, 0, True)
            all = ""
            for res in chat:
                all += res
            print("AI:" + all)
            return

        now_memory = {"role": "user", "content": query}
        self.update_memory(now_memory)

        chat_history = self.long_memory["chat_history"]
        flag = 0
        now_node = self.now_node
        "Continuous recursion"
        while True:
            # If the current node is a node that requires user feedback or a leaf node, recursion will jump out after the node ends running
            if now_node.done:
                flag = 1
            if isinstance(now_node, GPTNode):
                # Extract key information to determine which node branch to enter
                if now_node.node_type == "judge":
                    system_prompt, last_prompt = now_node.get_prompt(
                        self.args_dict)
                    response = get_gpt_response_rule(chat_history,
                                                     system_prompt,
                                                     last_prompt,
                                                     args_dict=self.args_dict)
                    keywords = extract(response, now_node.extract_words)
                    next_nodes_nums = len(now_node.next_nodes.keys())
                    for i, key in enumerate(now_node.next_nodes):
                        if i == next_nodes_nums - 1:
                            now_node = now_node.next_nodes[key]
                        elif key == keywords:
                            now_node = now_node.next_nodes[key]
                            break

                # Extract keywords to proceed to the next node
                elif now_node.node_type == "extract":

                    system_prompt, last_prompt = now_node.get_prompt(
                        self.args_dict)
                    response = get_gpt_response_rule(chat_history,
                                                     system_prompt,
                                                     last_prompt,
                                                     args_dict=self.args_dict)
                    if type(now_node.extract_words) == list:
                        for extract_word in now_node.extract_words:
                            keywords = extract(response, extract_word)
                            self.long_memory[extract_word] = keywords
                    else:
                        keywords = extract(response, now_node.extract_words)
                        self.long_memory[now_node.extract_words] = keywords
                    now_node = now_node.next_nodes["0"]

                elif now_node.node_type == "response":

                    system_prompt, last_prompt = now_node.get_prompt(
                        self.args_dict)
                    response = get_gpt_response_rule_stream(
                        chat_history,
                        system_prompt,
                        None,
                        args_dict=self.args_dict)
                    now_node = now_node.next_nodes["0"]
                    self.now_node = now_node
                    all = ""
                    for res in response:
                        all += res if res else ''

                    now_memory = {"role": "assistant", "content": all}
                    self.update_memory(now_memory)
                    print("AI:" + all)

                elif now_node.node_type == "response_and_extract":
                    now_node.set_user_input(chat_history[-1]["content"])
                    system_prompt, last_prompt = now_node.get_prompt(
                        self.args_dict)
                    response = get_gpt_response_rule_stream(
                        chat_history,
                        system_prompt,
                        last_prompt,
                        args_dict=self.args_dict)
                    all = ""
                    for res in response:
                        all += res if res else ''
                        print("AI:" + all)

                    if type(now_node.extract_words) == list:
                        for extract_word in now_node.extract_words:
                            keywords = extract(all, extract_word)
                            self.long_memory[extract_word] = keywords
                    else:
                        keywords = extract(all, now_node.extract_words)
                        self.long_memory[now_node.extract_words] = keywords

            elif isinstance(now_node, ToolNode):
                now_output = now_node.func(self.args_dict)
                next_node_id = "0"
                all = ""
                for output in now_output:
                    if isinstance(output, dict):
                        response = output["response"]
                        next_node_id = output["next_node_id"]
                        print("AI:" + response)
                    else:
                        all += output
                if all:
                    print("AI:" + all)

                now_node = now_node.next_nodes[next_node_id]
                self.now_node = now_node

            if flag or now_node == self.root:
                self.temp_memory = {}
                break

    def load_date(self, username):
        task = find_data(username)
        if task:
            now_node_name = task.now_node_name
            self.now_node = self.SOP.nodes[now_node_name]
            self.long_memory = {
                key: value
                for key, value in task.memory.items()
            }
            chat_history = [item for item in task.memory["chat_history"]]
            self.long_memory["chat_history"] = chat_history

        else:
            self.now_node = self.root
            self.long_memory = {"chat_history": []}
            add_date(username, self.long_memory, self.root.name)

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
        self.long_memory["chat_history"].append(memory)
        self.args_dict["long_memory"] = self.long_memory

    def run(self):
        while True:
            self.step()