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

"""standard operation procedure of an LLM Autonomous agent"""
from abc import abstractmethod
import json
from utils import *
from component import *
class SOP():

    def __init__(self,file_path):
        self.nodes = self.load_json(file_path)

    def load_json(file_path):
        json.loads(file_path)

class Tool():

    def __init__(self, type, **args):
        if type == "kb":
            database = database


class Node():

    def __init__(self,
                 tool: Tool = None,
                 node_type: str = None,
                 last_prompt: str = None,
                 need_response: bool = None,
                 extract_words: str = None,
                 next_nodes: dict = None,
                 done=False,
                 user_input:str= None,
                 **components):
        self.prompt = ""
        if tool != None:
            tool = Tool(type)
            tool_prompt = tool.get_prompt()
        self.node_type = node_type
        self.next_nodes = next_nodes
        self.components = components
        self.system_prompt = self.get_prompt()
        self.last_prompt = last_prompt
        self.extract_words = extract_words
        self.need_response = need_response
        self.done = done
        self.user_input = user_input
        
    def set_user_input(self,user_input):
        self.user_input = user_input

    # merge component
    def get_component(self):
        components = []
        for i in self.args:
            if i in ["input", "output", "style", "rule", "demonstration","task"]:
                if i == "input":
                    self.args[i].input = self.user_input
                components.append(self.args[i])
        return components

    def get_system_prompt(self):
        components = []
        for component in self.components:
            if component == "input":
                self.components[component].input = self.user_input

        components = self.get_component()
        prompt = ""
        for i in components:
            if not isinstance(i,OutputComponent):
                prompt += i.get_prompt()
        return prompt
    
    ##return complete
    def get_last_prompt(self):
        components = self.get_component()
        prompt = ""
        for i in components:
            if isinstance(i,OutputComponent):
                prompt += i.get_prompt()
        return prompt

    def add_component_system(self, component):
        self.system_prompt += component.get_prompt()

    def add_component_last(self, component):
        self.last_prompt += component.get_prompt()
        

task_component = StyleComponent("你是一个客服。服务的公司是保未来公司。保未来公司主要帮助用户申请香港优秀人才入境计划。",
                                 "专业")

# judge_idle node
rule_component_judge_idle = RuleComponent("""你现在需要判断用户说的内容是否只是闲聊，与公司的业务是否相关。
    例如用户说“你好”，“再见”，“帮我写个python代码”，“帮我写小说”这样用公司业务无关的话，就是闲聊。
    如果用户问你的信息，比如你是谁，你擅长做什么也算是闲聊，因为这与公司的业务无关，只是问你关于你的信息。
    并且你应该充分结合上下文，如果用户说了“没有”，“是的”，“大学本科毕业”等信息，你要判断他是不是在问答你的问题，而不是在闲聊。
    """)


last_prompt_judge_idle = OutputComponent("闲聊")
input_prompt = InputComponent()

args_judge_idle = {
    "task":task_component,
    "role":rule_component_judge_idle,
    "input":input_prompt
}
root = Node(node_type="judge",
                  last_prompt=last_prompt_judge_idle,
                  extract_words="闲聊",
                  done = False,
                  **args_judge_idle)