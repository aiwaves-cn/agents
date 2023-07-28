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

MAX_CHAT_HISTORY = 5
headers = {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
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
        self.temp_memory = {}
        self.long_memory = {}
    
    def reply(self,userName,history):
        """
        reply api ,The interface set for backend calls 
        """
        self.load_date(userName)
        
        flag = 0
        now_node = self.now_node
        chat_history = self.process_history(history)
        self.temp_memory["chat_history"] = chat_history
        "Continuous recursion"
        while True:
            print(now_node.name)
            if isinstance(now_node,GPTNode):
                # If the current node is a node that requires user feedback or a leaf node, recursion will jump out after the node ends running
                if now_node.done:
                    flag =1
                
                # Extract key information to determine which node branch to enter
                if now_node.node_type =="judge":
                    now_node.set_user_input(chat_history[-1]["content"])
                    
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
                    now_node.set_user_input(chat_history[-1]["content"])
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
                    now_node.set_user_input(chat_history[-1]["content"])
                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule_stream(chat_history,system_prompt,"""请严格按照下面的回复格式进行输出：
                                                                                        <response>
                                                                                        （你的回复内容）
                                                                                        </response>""")
                    now_node = now_node.next_nodes["0"]
                    self.now_node = now_node
                    for res in response:
                        yield  res  
                
                elif now_node.node_type =="response_and_extract":
                    now_node.set_user_input(chat_history[-1]["content"])
                    system_prompt,last_prompt = now_node.get_prompt(self.long_memory,self.temp_memory)
                    response = get_gpt_response_rule_stream(chat_history,system_prompt,last_prompt)
                    all = ""
                    for res in response:
                        all += res.choices[0]['delta'].get('content') if res.choices[0]['delta'].get('content') else ''
                        yield  res  
                        
                    if type(now_node.extract_words) == list:
                        for extract_word in now_node.extract_words:
                            keywords = extract(all,extract_word)
                            self.long_memory[extract_word] = keywords
                    else:
                        keywords = extract(all,now_node.extract_words)
                        self.long_memory[now_node.extract_words] = keywords
                    
                    
                    
            elif isinstance(now_node,ToolNode):
                memory = {}
                memory.update(self.long_memory)
                memory.update(self.temp_memory)
                now_output = now_node.func(memory)
                next_node_id = "0"
                for output in now_output:
                    if isinstance(output,dict):
                        response = output["response"]
                        for k,v in output["temp_memory"].items():
                            self.temp_memory[k] = v
                            memory[k] = v
                        for k,v in output["long_memory"].items():
                            self.long_memory[k] = v
                            memory[k] = v
                        next_node_id = output["next_node_id"]
                        yield response
                    else:
                        yield output
                    
                now_node = now_node.next_nodes[next_node_id]
                self.now_node = now_node       
                  
            if flag or now_node == self.root:
                self.temp_memory = {}
                task = find_data(userName)
                task.memory = self.long_memory
                task.now_node = self.now_node
                task.save()
                break



    def load_date(self,username):
        task = find_data(username)
        if username=="":
            username = 0
        if task:
            now_node_name = task.now_node_name
            self.now_node = self.SOP.nodes[now_node_name]
            self.long_memory = task.memory
        else:
            self.now_node = self.root
            self.long_memory = {}
            add_date(username,self.long_memory,self.root.name)
            
            
            
    def process_history(self,history):
        """Dealing with incoming data in different situations

        Args:
            chat_history (list): input chat history

        Returns:
            list: history of gpt usage
        """
        chat_history = []
        for ch in history:
            if ch["message"]:
                if ch["type"]== 0:
                    chat_history.append(  {"role": "user", "content": ch["message"]})
                else:
                    chat_history.append(  {"role": "assistant", "content": ch["message"]})
        
        if len(chat_history)>2*MAX_CHAT_HISTORY:
            chat_history = chat_history[-(2*MAX_CHAT_HISTORY+1):]
        return chat_history
    

    