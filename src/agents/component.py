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
    
    def get_prompt(self):
        return self.prompt
    
class TaskComponent(Component):
    
    def __init__(self,task):
        super().__init__()
        self.task = task

    def get_prompt(self):
        return f"""你需要执行的任务是:{self.task}。"""
    
class InputComponent(Component):
    
    def __init__(self):
        super().__init__()
        self.input = ""
        
    def get_prompt(self):
        if self.input == "":
            return ""
        return  f"用户的输入是:{self.input}。"

class OutputComponent(Component):

    def __init__(self, output):
        super().__init__()
        self.output = output
    
    def get_prompt(self):
        return  f"""你的输出包在<{self.output}>和</{self.output}>中。
切记，输出格式为： 
```
<{self.output}>
...
</{self.output}>
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

    def get_prompt(self):
        return  f"""现在你来模拟一个{self.agent}。你需要遵循以下的输出风格：
f{self.style}。
"""

class RuleComponent(Component):

    def __init__(self, rule):
        super().__init__()
        self.rule = rule

    def get_prompt(self):
        return  f"""你需要遵循的规则是:{self.rule}。"""

class DemonstrationComponent(Component):
    """
    例子是列表，里面是input和output的元祖
    """

    def __init__(self, demonstrations):
        super().__init__()
        self.demonstrations = demonstrations
        self.prompt = "以下是你可以参考的例子：\n"

    def add_demonstration(self, demonstration):
        for input, output in demonstration:
            self.prompt += input + "\n" + output

    def get_prompt(self):
        for input, output in self.demonstrations:
            self.prompt += input + "\n" + output
        return self.prompt