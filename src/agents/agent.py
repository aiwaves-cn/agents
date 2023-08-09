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
    def __init__(self, role,name) -> None:
        self.content = {"messages": []}
        self.role = role
        self.name = name  
        self.current_node_name = None
          
        self.args_dict = {
            "short_memory": {},
            "long_memory": {},
        }

    def step(self, user_query,user_role,user_name, sop:SOP):
        """
        reply api ,The interface set for backend calls 
        """
        if self.judge_sensitive(user_query):
            response = "<回复>对不起，您的问题涉及禁忌话题或违规内容，我无法作答，请注意您的言辞！</回复>"
            for res in response:
                time.sleep(0.02)
                yield res
            return

        current_memory = {"role": "user", "content": f"{user_name}({user_role}):{user_query}"}
        self.update_memory(current_memory)
        self.args_dict["query"] = user_query
        self.args_dict["temperature"] = sop.temperature

        chat_history = self.args_dict["long_memory"]["chat_history"]
        # print(f"chat_history:{chat_history}")
        flag = 0
        current_node = sop.nodes[self.current_node_name]

        "Continuous recursion"
        while True:
            flag = current_node.is_interactive
            print(current_node.name)
            response,res_dict = self.get_action(current_node)
            
            if len(current_node.next_nodes) == 1:
                current_node = current_node.next_nodes["0"]
            else:
                current_node = current_node.next_nodes[res_dict["next_node"]]
                
            all = ""
            for res in response:
                all += res if res else ''
                yield res
            current_memory = {"role": self.role, "content": f"{self.name}({self.role}):{all}"}
            self.update_memory(current_memory)

            if flag or current_node == sop.root:
                self.args_dict["temp_memory"] = {}
                yield {"memory":self.args_dict,"current_node_name":current_node.name}
                break

    def load_date(self, task):
        self.current_node_name = task.current_node_name
        self.args_dict["long_memory"] = {
            key: value
            for key, value in task.memory.items()
        }
            

    def get_action(self,node:Node):
        system_prompt,last_prompt,res_dict = node.compile(self.role,self.args_dict)
        chat_history = self.args_dict["long_history"]["chat_history"]
        temperature = self.args_dict["temperature"]
        response = get_gpt_response_rule_stream(chat_history,system_prompt,last_prompt,temperature=temperature,args_dict=self.args_dict)
        return response,res_dict
        
    
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

    def run(self):
        while True:
            self.step()
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def step2(self):
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
            if isinstance(now_node, Node):
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
