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
        self.Question()
    
        chat_history_orig = self.content["messages"][0]
        ch_dict = self.process_history(chat_history_orig)
        now_node = self.now_node
        
        while now_node.done:
            if now_node.node_type =="judge":
                response = get_gpt_response_rule(ch_dict,now_node.system_prompt,now_node.last_prompt)
                keywords = extract(response,now_node.extract_words)
                print(response)
                if self.is_done(now_node):
                    break
                next_nodes_nums = len(now_node.next_nodes)
                for i,key in enumerate(now_node.next_nodes):
                    if i == next_nodes_nums-1:
                        now_node = now_node.next_nodes[key]
                    if key == keywords:
                        now_node = now_node.next_nodes[key]
                        break
                
            elif now_node.node_type == "extract":
                response = get_gpt_response_rule(ch_dict,now_node.system_prompt,now_node.last_prompt)
                keywords = extract(response,now_node.extract_words)
                if self.is_done(now_node):
                    break
                now_node = now_node.next_nodes[0]
            
            elif now_node.node_type == "response":
                response = get_gpt_response_rule(ch_dict,now_node.system_prompt,now_node.last_prompt)
                self.answer(response)
                if now_node.need_response:
                    self.question()
                chat_history_orig = self.content["messages"]
                ch_dict = self.process_history(chat_history_orig)
                if self.is_done(now_node):
                    break
                now_node = now_node.next_nodes[0]
                self.now_node = now_node
                
    def chat(self):
        while True:
            self.step()  
        
        
    def answer(self,return_message):
        for rem in return_message:
            if rem["type"]=="chat":
                answer = rem["content"]
                self.content["messages"].append([{"role":"bot","content":answer}])
        
    def question(self):
        """
        append the question of user
        """
        question = input("用户：")
        self.content["messages"].append([{"role":"user","content":question}])

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
    
    def is_done(self,node):
        return node.done
    

style_component = StyleComponent("你是一个客服。服务的公司是保未来公司。保未来公司主要帮助用户申请香港优秀人才入境计划。",
                                 "专业")
rule_component = RuleComponent("""你现在需要判断用户说的内容是否只是闲聊，与公司的业务是否相关。
    例如用户说“你好”，“再见”，“帮我写个python代码”，“帮我写小说”这样用公司业务无关的话，就是闲聊。
    如果用户问你的信息，比如你是谁，你擅长做什么也算是闲聊，因为这与公司的业务无关，只是问你关于你的信息。
    并且你应该充分结合上下文，如果用户说了“没有”，“是的”，“大学本科毕业”等信息，你要判断他是不是在问答你的问题，而不是在闲聊。
    """)
extract_component = ExtractComponent("闲聊")
last_prompt_1 = get_extract_prompt("闲聊")
args1 = {
     "style" : style_component,
    "rule" :rule_component,
    "extract" : extract_component
}
root = Node(node_type="judge",
                  last_prompt=last_prompt_1,
                  extract_words="闲聊",
                  done=True,
                  need_response=True,
                  **args1)

bot = Agent(root)
bot.chat()