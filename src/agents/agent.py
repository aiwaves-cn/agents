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
from sop import Node,SOP,controller
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
        self.sop = None
        
        self.args_dict = {
            "short_memory": {},
            "long_memory": {"chat_history":[]},
        }

    def step(self, user_query, user_role, user_name, current_node:Node,temperature = 0.3):
        """
        reply api ,The interface set for backend calls 
        """
        if self.judge_sensitive(user_query):
            response = "<回复>对不起，您的问题涉及禁忌话题或违规内容，我无法作答，请注意您的言辞！</回复>"
            for res in response:
                time.sleep(0.02)
                yield res
            return

        self.args_dict["query"] = user_query
        self.args_dict["temperature"] = temperature
        response, res_dict = self.act(current_node)

        all = ""
        for res in response:
            all += res if res else ''
            yield res

        #====================================================#
        if "response" in res_dict and res_dict["response"]:
            all = ""
            for res in res_dict["response"]:
                all +=res
                yield res
            del res_dict["response"]

        #====================================================#


    def load_date(self, task:TaskConfig):
        self.current_node_name = task.current_node_name
        self.args_dict["long_memory"] = {
            key: value
            for key, value in task.memory.items()
        }
        

    def act(self, node: Node):
        system_prompt, last_prompt, res_dict = node.compile(
            self.role, self.args_dict)
        chat_history = self.args_dict["long_memory"]["chat_history"]
        temperature = self.args_dict["temperature"]
        response = get_gpt_response_rule_stream(chat_history,
                                                system_prompt,
                                                last_prompt,
                                                temperature=temperature,
                                                args_dict=self.args_dict)

        return response, res_dict
    

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

    def updatememory(self,memory):
        self.args_dict["long_memory"]["chat_history"].append(memory)




def run(sop:SOP,controller:controller,name = "A神",role = "客户"):
    while True:
        current_node = sop.current_node
        print(current_node.name)
        query = input(f"{name}({role}):")
        current_memory = {"role":"user","content":f"{name}({role}):{query}"}
        sop.shared_memory["chat_history"].append(current_memory)
        while True:
            
            next_node,next_role = step(sop,controller)
            
            flag =  next_node.is_interactive
            current_node = next_node
            sop.current_node = current_node
            
            if next_role == role:
                break
            current_agent = sop.agents[next_role]
            current_agent = sop.agents[next_role]
            response = current_agent.step(query,role,name,current_node,sop.temperature)
            print(f"{current_agent.name}({current_agent.role}):",end="")
            all = f"{current_agent.name}({current_agent.role}):"
            for res in response:
                all+=res
                print(res,end="")
                time.sleep(0.02)
            print()
            sop.shared_memory["chat_history"].append({"role":"assistant","content":all})
            
            if flag:
                break
    
def step(sop:SOP,controller:controller):
    current_node = sop.current_node
    if len(current_node.next_nodes) == 1:
        next_node = "0"
    else:
        next_node = controller.judge(current_node,sop.shared_memory["chat_history"])
    next_node = current_node.next_nodes[next_node]
    if len(sop.agents.keys())==1:
        next_role = list(sop.agents.keys())[0]
    else:
        next_role = controller.allocate_task(next_node,sop.shared_memory["chat_history"])   
    return next_node,next_role



# agent = Agent("眼科客服","吴家隆")
# my_sop = SOP("/home/aiwaves/longli/agents/examples/eye/eye_newnew.json")
# my_controller = controller(my_sop.controller_dict)
# my_sop.agents = {"眼科客服":agent}
# agent.sop = my_sop

# run(my_sop,my_controller)
