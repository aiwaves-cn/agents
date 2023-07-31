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
from prompt import *
from flask import Response
from datebase import *
import time
import json

headers = {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
with open("")
args = json.loads("")
class Agent():
    """
    Auto agent, input the JSON of SOP.
    """
    def __init__(self,sop) -> None:
        self.content = {
            "messages":[]
            }
        self.SOP = SOP(sop)
        self.root = self.SOP.root       
        self.now_node = self.root
        self.judge_idle_node = self.SOP.judge_idle_node
        self.idle_response_node = self.SOP.idle_response_node
        
        
        self.temp_memory = {}
        self.long_memory = {"chat_history":[],"idle_history":[]}
    
    def reply(self,userName,query):
        """
        reply api ,The interface set for backend calls 
        """
        if type(userName)!=int:
            userName = 0
        assert type(userName) == int,"username type is not int!"
        self.load_date(userName)
        if self.judge_idle(query):
            chat =  self.chat(query,userName)
            for res in chat:
                yield res
            return       
            
        self.long_memory["chat_history"].append({"role": "user", "content": query})
        self.long_memory["idle_history"].append({"role": "user", "content": query})
        
        chat_history = self.long_memory["chat_history"]
        # print(f"chat_history:{chat_history}")
        flag = 0
        now_node = self.now_node
        "Continuous recursion"
        while True:
            if now_node.done:
                flag = 1
            else:
                flag = 0
            print(now_node.name)
            if isinstance(now_node,GPTNode):
                # If the current node is a node that requires user feedback or a leaf node, recursion will jump out after the node ends running
                
                # Extract key information to determine which node branch to enter
                if now_node.node_type =="judge":
                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule(chat_history,system_prompt,last_prompt)
                    keywords = extract(response,now_node.extract_words)
                    next_nodes_nums = len(now_node.next_nodes.keys())
                    for i,key in enumerate(now_node.next_nodes):
                        if i == next_nodes_nums-1:
                            now_node = now_node.next_nodes[key]
                        elif key == keywords:
                            now_node = now_node.next_nodes[key]
                            break
                    
                    
                # Extract keywords to proceed to the next node
                elif now_node.node_type == "extract":

                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule(chat_history,system_prompt,last_prompt)
                    if type(now_node.extract_words) == list:
                        for extract_word in now_node.extract_words:
                            keywords = extract(response,extract_word)
                            self.long_memory[extract_word] = keywords
                    else:
                        keywords = extract(response,now_node.extract_words)
                        self.long_memory[now_node.extract_words] = keywords
                    now_node = now_node.next_nodes["0"]
                
                elif now_node.node_type == "response":
                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule_stream(chat_history,system_prompt,None)
                    now_node = now_node.next_nodes["0"]
                    self.now_node = now_node
                    all = ""
                    for res in response:
                        all += res if res else ''
                        yield  res  
                    self.long_memory["chat_history"].append({"role": "assistant", "content": all})
                    self.long_memory["idle_history"].append({"role": "assistant", "content": all})
                
                elif now_node.node_type =="response_and_extract":
                    now_node.set_user_input(chat_history[-1]["content"])
                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule_stream(chat_history,system_prompt,last_prompt)
                    all = ""
                    for res in response:
                        all += res if res else ''
                        yield  res
                        
                    if type(now_node.extract_words) == list:
                        for extract_word in now_node.extract_words:
                            keywords = extract(all,extract_word)
                            self.long_memory[extract_word] = keywords
                    else:
                        keywords = extract(all,now_node.extract_words)
                        self.long_memory[now_node.extract_words] = keywords
                    
                    
                    
            elif isinstance(now_node,ToolNode):
                now_output = now_node.func(self.long_memory,self.temp_memory)
                next_node_id = "0"
                for output in now_output:
                    if isinstance(output,dict):
                        response = output["response"]
                        next_node_id = output["next_node_id"]
                        for res in response:
                            time.sleep(0.05)
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
            chat =  self.chat(query,0,True)
            all = ""
            for res in chat:
                all +=res
            print("AI:" + all)
            return 
            
        self.long_memory["chat_history"].append({"role": "user", "content": query})
        self.long_memory["idle_history"].append({"role": "user", "content": query})
        
        chat_history = self.long_memory["chat_history"]
        flag = 0
        now_node = self.now_node
        "Continuous recursion"
        while True:
            # If the current node is a node that requires user feedback or a leaf node, recursion will jump out after the node ends running
            if now_node.done:
                flag =1
            if isinstance(now_node,GPTNode):               
                # Extract key information to determine which node branch to enter
                if now_node.node_type =="judge":
                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule(chat_history,system_prompt,last_prompt)
                    keywords = extract(response,now_node.extract_words)
                    next_nodes_nums = len(now_node.next_nodes.keys())
                    for i,key in enumerate(now_node.next_nodes):
                        if i == next_nodes_nums-1:
                            now_node = now_node.next_nodes[key]
                        elif key == keywords:
                            now_node = now_node.next_nodes[key]
                            break
                    
                    
                # Extract keywords to proceed to the next node
                elif now_node.node_type == "extract":

                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule(chat_history,system_prompt,last_prompt)
                    if type(now_node.extract_words) == list:
                        for extract_word in now_node.extract_words:
                            keywords = extract(response,extract_word)
                            self.long_memory[extract_word] = keywords
                    else:
                        keywords = extract(response,now_node.extract_words)
                        self.long_memory[now_node.extract_words] = keywords
                    now_node = now_node.next_nodes["0"]
                
                
                
                elif now_node.node_type == "response":

                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule_stream(chat_history,system_prompt,None)
                    now_node = now_node.next_nodes["0"]
                    self.now_node = now_node
                    all = ""
                    for res in response:
                        all += res if res else '' 
                    self.long_memory["chat_history"].append({"role": "assistant", "content": all})
                    self.long_memory["idle_history"].append({"role": "assistant", "content": all})
                    print("AI:" + all)
                
                elif now_node.node_type =="response_and_extract":
                    now_node.set_user_input(chat_history[-1]["content"])
                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule_stream(chat_history,system_prompt,last_prompt)
                    all = ""
                    for res in response:
                        all += res if res else ''
                        print("AI:" + all)  
                        
                    if type(now_node.extract_words) == list:
                        for extract_word in now_node.extract_words:
                            keywords = extract(all,extract_word)
                            self.long_memory[extract_word] = keywords
                    else:
                        keywords = extract(all,now_node.extract_words)
                        self.long_memory[now_node.extract_words] = keywords
                    
                    
                    
            elif isinstance(now_node,ToolNode):
                now_output = now_node.func(self.long_memory,self.temp_memory)
                next_node_id = "0"
                all = ""
                for output in now_output:
                    if isinstance(output,dict):
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


    def load_date(self,username):
        task = find_data(username)
        print(task)
        if task:
            now_node_name = task.now_node_name
            print(f"now_node_name:{now_node_name}")
            self.now_node = self.SOP.nodes[now_node_name]
            self.long_memory = {key: value for key, value in task.memory.items()}
            chat_history = [item for item in task.memory["chat_history"]]
            idle_history = [item for item in task.memory["idle_history"]]
            self.long_memory["chat_history"] = chat_history
            self.long_memory["idle_history"] = idle_history
            
        else:
            self.now_node = self.root
            self.long_memory = {"chat_history":[],"idle_history":[]}
            add_date(username,self.long_memory,self.root.name)
            
            
            
    def process_history(self,chat_history):
        """Dealing with incoming data in different situations

        Args:
            chat_history (list): input chat history

        Returns:
            list: history of gpt usage
        """       
        if len(chat_history)>2*MAX_CHAT_HISTORY:
            chat_history = chat_history[-(2*MAX_CHAT_HISTORY+1):]
        return chat_history
    
    def judge_idle(self,query):
        system_prompt,last_prompt = self.judge_idle_node.get_prompt(self.long_memory,self.temp_memory)
        chat_history = self.long_memory["idle_history"]
        chat_history.append({"role": "user", "content": query})
        response = get_gpt_response_rule(chat_history,system_prompt,last_prompt)
        keywords = extract(response,self.judge_idle_node.extract_words)
        if keywords == "是":
            return True
        else:
            return False

    def chat(self,query,userName,is_cmd = False):
        system_prompt,last_prompt = self.idle_response_node.get_prompt(self.long_memory,self.temp_memory)
        idle_history = self.long_memory["idle_history"]
        idle_history.append({"role": "user", "content": query})
        response = get_gpt_response_rule_stream(idle_history,system_prompt,None)
        all = ""
        for res in response:
            all += res if res else ''
            yield  res  
        self.long_memory["idle_history"].append({"role": "assistant", "content": all}) 
        if not is_cmd:
            task = find_data(userName)
            task.memory = self.long_memory
            task.save()
        
        
    def run(self):
        while True:
            self.step()