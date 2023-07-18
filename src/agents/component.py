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

"""Component of an LLM Autonomous agent"""
class Component():
    def __init__(self):
        self.prompt = ""
    
    @staticmethod
    def set_prompt():
        pass
    
    def get_prompt(self):
        return self.prompt
    
class TaskComponent(Component):
    
    def __init__(self,task):
        super().__init__()
        self.task = task
        self.prompt = self.set_prompt(task)
        
    def set_prompt(self, task):
        self.task = task
        self.prompt = f"""你需要执行的任务是{self.task}。"""

class InputComponent(Component):
    
    def __init__(self,input):
        super().__init__()
        self.input = input
        self.prompt = self.set_prompt(input)
        
    def set_prompt(self, input):
        self.judgement = input
        self.prompt = f"用户的输入是{input}。"

class OutoutComponent(Component):

    def __init__(self, output):
        super().__init__()
        self.output = output
        self.prompt = ""
        self.set_prompt(output)

    def set_prompt(self, output):
        self.output = output
        self.prompt = f"""你的输出包在<{output}>和</{output}>中。
可以开始输出了，输出格式为： 
```
{output}
...
/{output}
```
"""

class StyleComponent(Component):
    """
    角色、风格组件
    """

    def __init__(self, agent, style):
        super().__init__()
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


class RuleComponent(Component):

    def __init__(self, rule):
        super().__init__()
        self.rule = rule
        self.prompt = ""
        self.set_prompt(rule)

    def set_prompt(self, rule):
        self.rule = rule
        self.prompt = f"""你需要遵循的规则是{self.rule}。"""


class DemonstrationComponent(Component):
    """
    例子是列表，里面是input和output的元祖
    """

    def __init__(self, demonstrations):
        super().__init__()
        self.demonstrations = demonstrations
        self.prompt = ""
        self.set_prompt(demonstrations)

    def set_prompt(self, demonstrations):
        self.demonstrations = demonstrations
        self.prompt = f"""以下是一些你可以学习的案例。"""
        for input, output in demonstrations:
            self.prompt += input + "\n" + output

    def add_demonstration(self, demonstration):
        for input, output in demonstration:
            self.prompt += input + "\n" + output


def get_extract_prompt(extract_word):
    prompt = f"""
    根据上下文，帮我进行<{extract_word}></{extract_word}>的提取
    """
    return prompt