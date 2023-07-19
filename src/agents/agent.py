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
import time 

MAX_CHAT_HISTORY = 5

class Agent():
    def __init__(self,root:Node) -> None:
        self.content = {
            "messages":[]
            }
        self.root = root
        self.now_node = root
        self.done = False
        

    def step(self):
        """
        One interaction
        """
        self.question()
    def step(self):
        self.question()
        now_node = self.now_node
        flag = 0
        while True:
            chat_history_orig = self.content["messages"]
            ch_dict = self.process_history(chat_history_orig)
            if now_node.done:
                flag =1
                
            if now_node.node_type =="judge":
                now_node.set_user_input(ch_dict[-1]["content"])
                system_prompt,last_prompt = now_node.get_prompt()
                response = get_gpt_response_rule(ch_dict,system_prompt,last_prompt)
                keywords = extract(response,now_node.extract_words)
                print("AI:" + response)
                next_nodes_nums = len(now_node.next_nodes.keys())
                for i,key in enumerate(now_node.next_nodes):
                    if i == next_nodes_nums-1:
                        now_node = now_node.next_nodes[key]
                    if key == keywords:
                        now_node = now_node.next_nodes[key]
                        break
                
            elif now_node.node_type == "extract":
                now_node.set_user_input(ch_dict)
                system_prompt,last_prompt = now_node.get_prompt()
                response = get_gpt_response_rule(ch_dict,system_prompt,last_prompt)
                print("AI:" + response)
                keywords = extract(response,now_node.extract_words)
                now_node = now_node.next_nodes[0]
            
            elif now_node.node_type == "response":
                now_node.set_user_input(ch_dict)
                system_prompt,last_prompt = now_node.get_prompt()
                response = get_gpt_response_rule(ch_dict,system_prompt,last_prompt)
                response = extract(response,now_node.extract_words)
                print("AI:" + response)
                self.answer(response)
                chat_history_orig = self.content["messages"]
                ch_dict = self.process_history(chat_history_orig)
                now_node = now_node.next_nodes[0]
                self.now_node = now_node
                
            if flag or now_node == self.root:
                break
            
    def chat(self):
        while True:
            self.step()  
        
        
    def answer(self,return_message):
        self.content["messages"].append({"role":"bot","content":return_message})
        
    def question(self):
        """
        append the question of user
        """
        question = input("用户：")
        self.content["messages"].append({"role":"user","content":question})

    def process_history(self,chat_history):
        """Dealing with incoming data in different situations

        Args:
            chat_history (_type_): input chat history

        Returns:
            list: history of gpt usage
        """
        ch_dict = []
        for ch in chat_history:
            if ch["role"]=="user":
                ch_dict.append(  {"role": "user", "content": ch["content"]})
            else:
                ch_dict.append(  {"role": "assistant", "content": ch["content"]})
        
        if len(ch_dict)>2*MAX_CHAT_HISTORY:
            ch_dict = ch_dict[-(2*MAX_CHAT_HISTORY+1):]
        return ch_dict
    
    def is_done(self,node:Node):
        return node.done
    

style_component = StyleComponent("一个客服。服务的公司是保未来公司。保未来公司主要帮助用户申请香港优秀人才入境计划。",
                                 "专业")
task_component_judge_idle = TaskComponent("需要判断用户说的内容是否只是闲聊，与公司的业务是否相关")
# judge_idle node
rule_component_judge_idle = RuleComponent("""
    例如用户说“你好”，“再见”，“帮我写个python代码”，“帮我写小说”这样用公司业务无关的话，就是闲聊。
    如果用户问你的信息，比如你是谁，你擅长做什么也算是闲聊，因为这与公司的业务无关，只是问你关于你的信息。
    并且你应该充分结合上下文，如果用户说了“没有”，“是的”，“大学本科毕业”等信息，你要判断他是不是在问答你的问题，而不是在闲聊。
    如果是闲聊的话，输出<闲聊>是</闲聊>,不是的话输出输出<闲聊>否</闲聊>
    """)


last_prompt_judge_idle = OutputComponent("闲聊")
input_prompt_judge_idle = InputComponent()

args_judge_idle = {
    "style":style_component,
    "task":task_component_judge_idle,
    "rule":rule_component_judge_idle,
    "input":input_prompt_judge_idle,
    "output":last_prompt_judge_idle
}
root = Node(node_type="judge",
            extract_words="闲聊",
            done = False,
            **args_judge_idle)

# idle node
task_component_idle = TaskComponent("需要与用户进行正常的聊天")
rule_component_idle = RuleComponent("""你有客户在和你闲聊。如果他是在打招呼的话，让他问你问题咨询，诱导他提问，如果他说的是结束或者再见的话，你要礼貌得说再见，并且询问他的联系方式。
    如果他是在骂你的话，你应该道歉并且说你之后会做好。
    """)
last_prompt_idle = OutputComponent("回复")
input_prompt_idle = InputComponent()

args_idle = {
    "style":style_component,
    "task":task_component_idle,
    "rule":rule_component_idle,
    "input":input_prompt_idle,
    "output":last_prompt_idle
}
idle_node = Node(node_type="response",
            extract_words="回复",
            done = True,
            next_nodes= {0:root},
            **args_idle)

# tool node
task_component_idle = TaskComponent("需要与用户进行正常的聊天")
rule_component_idle = RuleComponent("""你有客户在和你闲聊。如果他是在打招呼的话，让他问你问题咨询，诱导他提问，如果他说的是结束或者再见的话，你要礼貌得说再见，并且询问他的联系方式。
    如果他是在骂你的话，你应该道歉并且说你之后会做好。
    """)
last_prompt_idle = OutputComponent("回复")
input_prompt_idle = InputComponent()

args_idle = {
    "style":style_component,
    "task":task_component_idle,
    "rule":rule_component_idle,
    "input":input_prompt_idle,
    "output":last_prompt_idle
}
idle_node = Node(node_type="response",
            extract_words="回复",
            done = True,
            next_nodes= {0:root},
            **args_idle)


root.next_nodes = {"是":idle_node,"否":root}


agent = Agent(root)
agent.chat()