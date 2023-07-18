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

"""standard operation procedure of an LLM autonoumous agent"""
class Tool():

    def __init__(self, type, **args):
        if type == "database":
            database = database


class PromptNode():

    def __init__(self,
                 tool: Tool = None,
                 node_type: str = None,
                 last_prompt: str = None,
                 need_response: bool = None,
                 extract_words: str = None,
                 next_nodes: dict = None,
                 done=False,
                 **args):
        self.prompt = ""
        if tool != None:
            tool = Tool(type)
            tool_prompt = tool.get_prompt()
        self.node_type = node_type
        self.next_nodes = next_nodes
        self.args = args
        self.system_prompt = self.get_prompt()
        self.last_prompt = last_prompt
        self.extract_words = extract_words
        self.need_response = need_response
        self.done = done

    def get_component(self):
        components = []
        for i in self.args:
            if i in ["judge", "extract", "style", "rule", "demonstration"]:
                components.append(self.args[i])
        return components

    def get_prompt(self):
        components = self.get_component()
        prompt = ""
        for i in components:
            prompt += i.prompt
        return prompt

    def add_component_system(self, component):
        self.system_prompt += component.get_prompt()

    def add_component_last(self, component):
        self.last_prompt += component.get_prompt()


class JudgeComponent():

    def __init__(self, judgement):
        self.judgement = judgement
        self.prompt = ""
        self.set_prompt(judgement)

    def set_prompt(self, judgement):
        self.judgement = judgement
        self.prompt = f"请你判断以上内容是否是{judgement}。"

    def get_prompt(self):
        return self.prompt


class ExtractComponent():

    def __init__(self, extract_words):
        self.extract_words = extract_words
        self.prompt = ""
        self.set_prompt(extract_words)

    def set_prompt(self, extract_words):
        self.extract_words = extract_words
        self.prompt = f"""你的输出包在<{extract_words}>和</{extract_words}>中。如果是闲聊返回<{extract_words}>0</{extract_words}>,如果不是闲聊返回<{extract_words}>1</{extract_words}>。
可以开始输出了，输出格式为： 
```
{extract_words}
...
/{extract_words}
```
"""

    def get_prompt(self):
        return self.prompt


class StyleComponent():
    """
    角色、风格组件
    """

    def __init__(self, agent, style):
        self.agent = agent
        self.style = style
        self.prompt = ""
        self.set_prompt(agent, style)

    def set_prompt(self, agent, style):
        self.agent = agent
        self.style = style
        self.prompt = f"""现在你来模拟一个{agent}。你需要遵循以下的输出风格：
f{style}。
"""

    def get_prompt(self):
        return self.prompt


class RuleComponent():

    def __init__(self, rule):
        self.rule = rule
        self.prompt = ""
        self.set_prompt(rule)

    def set_prompt(self, rule):
        self.rule = rule
        self.prompt = f"""你需要执行的任务是{self.rule}。"""

    def get_prompt(self):
        return self.prompt


class DemonstrationComponent():
    """
    例子是列表，里面是input和output的元祖
    """

    def __init__(self, demonstrations):
        self.demonstrations = demonstrations
        self.prompt = ""
        self.set_prompt(demonstrations)

    def set_prompt(self, demonstrations):
        self.demonstrations = demonstrations
        self.prompt = f"""以下是一些你可以学习的案例。"""
        for input, output in demonstrations:
            self.prompt += input + "\n" + output

    def get_prompt(self):
        return self.prompt

    def add_demonstration(self, demonstration):
        for input, output in demonstration:
            self.prompt += input + "\n" + output


def get_extract_prompt(extract_word):
    prompt = f"""
    根据上下文，帮我进行<{extract_word}></{extract_word}>的提取
    """
    return prompt