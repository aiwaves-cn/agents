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


class SOP:
    """
    input:the json of the sop
    output: a sop graph
    """

    def __init__(self, json_path):
        with open(json_path) as f:
            sop = json.load(f)
        self.root = None
        self.nodes = {}

        self.temperature = sop["temperature"] if "temperature" in sop else 0.3
        self.active_mode = sop["active_mode"] if "active_mode" in sop else False
        self.log_path = sop["log_path"] if "log_path" in sop else "logs"
        self.answer_simplify = sop["answer_simplify"] if "answer_simplify" in sop else False

        if "gpt_nodes" in sop:
            gpt_nodes = self.init_gpt_nodes(sop)
            self.nodes.update(gpt_nodes)
        if "tool_nodes" in sop:
            tool_nodes = self.init_tool_nodes(sop)
            self.nodes.update(tool_nodes)
        if "relation" in sop:
            self.init_relation(sop)

    def init_gpt_nodes(self, sop):
        # node_sop: a list of the node
        node_sop = sop["gpt_nodes"]
        nodes_dict = {}
        for node in node_sop:
            node = node_sop[node]
            name = node["name"]
            node_type = node["node_type"]
            extract_word = node["extract_word"]
            done = node["done"]
            components_dict = self.init_components(node["components"])

            now_node = GPTNode(name=name,
                               node_type=node_type,
                               extract_words=extract_word,
                               done=done,
                               components=components_dict)
            nodes_dict[name] = now_node
            if "root" in node.keys() and node["root"]:
                self.root = now_node
        return nodes_dict

    def init_tool_nodes(self, sop):
        # node_sop:a list of the node
        node_sop = sop["tool_nodes"]
        nodes_dict = {}
        for node in node_sop:
            node = node_sop[node]
            name = node["name"]
            done = node["done"]
            tool_name = node["tool_name"]

            if tool_name == "MatchNode":
                now_node = MatchNode(name=name, done=done)
            elif tool_name == "SearchNode":
                now_node = SearchNode(name=name, done=done)
            elif tool_name == "SearchRecomNode":
                now_node = SearchRecomNode(name=name, done=done)
            elif tool_name == "RecomTopNode":
                now_node = RecomTopNode(name=name, done=done)
            elif tool_name == "StaticNode":
                now_node = StaticNode(name=name,
                                      done=done,
                                      output=node["output"])
            elif tool_name == "KnowledgeResponseNode":
                last_prompt = node[
                    "last_prompt"] if "last_prompt" in node else None
                system_prompt = node[
                    "system_prompt"] if "system_prompt" in node else None

                active_prompt = (
                    node["active_prompt"] if "active_prompt" in node else
                    """如果你需要用户提供更多信息才能完整回答问题，你需要先输出能回答的内容，然后根据已知的内容和用户的问题进行追问。例如：用户的问题是：“度数500度能做手术吗？”提供的内容为："问题：我度数500度，散光200度可以做全飞秒手术吗？，答案：全飞秒手术可以做1000度以内的近视和散光500度内的"。所以你应该结合这个内容做出回复。但是你不知道用户的散光度数，也不知道用户要做什么手术，所以你应该追问“请问您散光多少度呀？”或者“你要做全飞秒手术还是半飞秒手术呢？”这样的问题来补充用户的相关信息。请你把可以追问的问题输出在回复的最后。"""
                ) if self.active_mode else None

                knowledge_base = node[
                    "knowledge_base"] if "knowledge_base" in node else None
                type = node["type"] if "type" in node else None
                now_node = KnowledgeResponseNode(knowledge_base=knowledge_base,
                                                 system_prompt=system_prompt,
                                                 last_prompt=last_prompt,
                                                 active_prompt = active_prompt,
                                                 name=name,
                                                 type=type,
                                                 done=done)
            else:
                assert 1 == False, "wrong tool node name"
            nodes_dict[name] = now_node

            if "root" in node.keys() and node["root"]:
                self.root = now_node
            if "judge_idle_node" in node.keys() and node["judge_idle_node"]:
                self.judge_idle_node = now_node
            if "idle_response_node" in node.keys(
            ) and node["idle_response_node"]:
                self.idle_response_node = now_node

        return nodes_dict

    def init_components(self, components_dict: dict):
        args_dict = {}
        for key, value in components_dict.items():
            value = components_dict[key]
            if value:
                if key == "style":
                    args_dict["style"] = StyleComponent(
                        value["agent"], value["style"])
                elif key == "task":
                    args_dict["task"] = TaskComponent(value["task"])
                elif key == "rule":
                    args_dict["rule"] = RuleComponent(value["rule"])
                elif key == "demonstration":
                    args_dict["demonstration"] = DemonstrationComponent(
                        value["demonstration"])
                elif key == "tool":
                    args_dict["tool"] = KnowledgeBaseComponent(
                        value["knowledge_base"])
                elif key == "output":
                    args_dict["output"] = OutputComponent(value["output"])
                elif key == "knowledge":
                    if value == "Information_KnowledgeComponent":
                        args_dict[
                            "knowledge"] = Information_KnowledgeComponent()
        return args_dict

    def init_relation(self, sop):
        relation = sop["relation"]

        for key, value in relation.items():
            for keyword, next_node in value.items():
                self.nodes[key].next_nodes[keyword] = self.nodes[next_node]


class GPTNode():

    def __init__(self,
                 name: str = None,
                 node_type: str = None,
                 extract_words=None,
                 done=False,
                 user_input: str = "",
                 components: dict = {}):
        """the simplist node mainly based on gpt:
            input the prompt,output the response.Afterwards, use response for different operations

        Args:
            tool (Tool, optional): _description_. Defaults to None.
            node_type (str, optional): three type (response, extract,judge)  
                                        ---response:return a response
                                        ---extract:return a keyword for memory
                                        ---judge:return the keyword to determine which node for next
            extract_words (str, optional): _description_. Defaults to "".
            next_nodes (dict, optional): _description_. Defaults to {}.
            done (bool, optional):   True:When the program runs to this node, it will be interrupted, allowing the user to input.
            user_input (str, optional): The content you want to agent know. Defaults to "".
            
            components(dict) : Contains the definition of various components
           { 
           "style":{"agent":"" , "style": "" } ,
            *"task"*:{"task":""} , 
            "rule":{"rule":""}, 
            "knowledge" (str): ""
            "demonstration":{"demonstration":[]} , 
            "input":true or false,
            "tool":{tool_name:"",**args} ,
            *"output"*:{"output":""} 
            }
           --style(agent,style) : agent(str):the role of the agent.   style(str):the style of the agent
           --task(task) : task(str):the task of the agent
           --rule(rule) : rule(str):the rule of the agent
           --knowledge(str) : the name of knowledge component
           --demonstration: demenstration(list):the example of answer
           --input : yet have external inputs , always be last input
           --tool(tool_name,**args) : tool_name(str):the name of tool,**args(Dict):the parameters of tool
           --output(output) : output(str):the html wrap of response
        """
        self.prompt = ""
        self.node_type = node_type

        self.next_nodes = {}

        self.components = components
        self.extract_words = extract_words
        self.done = done
        self.name = name

    # get complete prompt
    def get_prompt(self, args_dict):
        prompt = ""
        last_prompt = ""
        query = args_dict["query"] if args_dict["query"] else ""
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

        for value in self.components.values():
            if isinstance(value, KnowledgeBaseComponent):
                value.user_input = query
                prompt = prompt + "\n" + value.get_prompt()
            elif isinstance(value, OutputComponent):
                last_prompt += value.get_prompt()
            elif isinstance(value, Information_KnowledgeComponent):
                prompt = prompt + "\n" + value.get_prompt(
                    long_memory, temp_memory)
            else:
                prompt = prompt + "\n" + value.get_prompt()

        return prompt, last_prompt
