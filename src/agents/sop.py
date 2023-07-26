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
from prompt import *
MIN_CATEGORY_SIM = 0.7
TOY_INFO_PATH =['/home/aiwaves/longli/fenxiang/toy_info.json',"/home/aiwaves/longli/fenxiang/bb_info.json"] #子类目相关知识库的路径

class SOP:
    """
    input:the json of the sop
    output: a sop graph
    """
    def __init__(self,json_path):
        with open(json_path) as f:
            sop = json.load(f)
        self.root = None
        self.nodes = {}
        if "gpt_nodes" in sop:
            gpt_nodes = self.init_gpt_nodes(sop)
            self.nodes.update(gpt_nodes)
        if "tool_nodes" in sop:
            tool_nodes = self.init_tool_nodes(sop)
            self.nodes.update(tool_nodes)
        if "relation" in sop:
            self.init_relation(sop)
        
    
    def init_gpt_nodes(self,sop):
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
            
            now_node = GPTNode(name=name,node_type=node_type,extract_words=extract_word,done=done,components=components_dict)
            nodes_dict[name] = now_node
            if  "root" in node.keys():
                self.root = now_node
        return nodes_dict
            
    def init_tool_nodes(self,sop):
        # node_sop:a list of the node
        node_sop = sop["tool_nodes"]
        nodes_dict = {}
        for node in node_sop:
            node = node_sop[node]
            name = node["name"]
            done = node["done"]
            tool_name = node["tool_name"]
            if tool_name == "MatchNode":
                now_node = MatchNode(name=name,done=done)
            elif tool_name == "SearchNode":
                now_node = SearchNode(name=name,done=done)
            elif tool_name == "SearchRecomNode":
                now_node = SearchRecomNode(name=name,done=done)
            elif tool_name == "RecomTopNode":
                now_node = RecomTopNode(name=name,done=done)           
            nodes_dict[name] = now_node
            
            if  "root" in node.keys():
                self.root = now_node
        return nodes_dict
            
    def init_components(self,components_dict:dict):
        args_dict = {}
        for key,value in components_dict.items():
            value = components_dict[key]
            if value:
                if key == "style":
                    args_dict["style"] = StyleComponent(value["agent"],value["style"])
                elif key == "task":
                    args_dict["task"] = TaskComponent(value["task"])
                elif key == "rule":
                    args_dict["rule"] = RuleComponent(value["rule"])
                elif key == "demonstration":
                    args_dict["demonstration"] = DemonstrationComponent(value["demonstration"])
                elif key == "input":
                    args_dict["input"] = InputComponent()
                elif key == "tool":
                    args_dict["tool"] = KnowledgeBaseComponent(value["knowledge_base"])
                elif key == "output":
                    args_dict["output"] = OutputComponent(value["output"])
                elif key == "knowledge":
                    if value == "Information_KnowledgeComponent":
                        args_dict["knowledge"] =  Information_KnowledgeComponent()
        return args_dict
                    
    def init_relation(self,sop):
        relation = sop["relation"]
        
        for key,value in relation.items():
            for keyword,next_node in value.items():
                self.nodes[key].next_nodes[keyword] = self.nodes[next_node]
            


class GPTNode():

    def __init__(self,
                 name:str = None,
                 node_type: str = None,
                 extract_words: str = "",
                 done=False,
                 user_input:str= "",
                 components:dict = {}):
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
        self.user_input = user_input
        self.extract_words = extract_words
        self.done = done
        self.name = name
    
    # mainly used for inputcomponent
    def set_user_input(self,user_input):
        self.user_input = user_input

    # get complete prompt
    def get_prompt(self,long_memory={},temp_memory = {}):
        prompt = ""
        last_prompt = ""
        for value in self.components.values():
            if isinstance(value,InputComponent) or isinstance(value,KnowledgeBaseComponent):
                value.user_input = self.user_input
                prompt = prompt +"\n" + value.get_prompt()
            elif isinstance(value,OutputComponent):
                last_prompt += value.get_prompt()
            elif isinstance(value,Information_KnowledgeComponent):
                prompt = prompt +"\n" + value.get_prompt(long_memory,temp_memory)
            else:
                prompt =prompt +"\n" + value.get_prompt()
        return prompt,last_prompt
    

# the base of the toolnode
class ToolNode:
    def __init__(self,name="",done=False):
        self.next_nodes = {}
        self.name = name
        self.done = done
    @abstractmethod
    def func(self,memory):
        pass

class StaticNode(ToolNode):
    def __init__(self, name="",output = "", done=False):
        super().__init__(name, done)
        self.output = output
    def func(self,memory):
        outputdict = {"response":self.output,"temp_memory":{},"long_memory":{},"next_node_id" : "0"}
        return outputdict

class MatchNode(ToolNode):
    def __init__(self,name="",done=False):
        super().__init__(name,done)
        
        # create dateset
        self.information_dataset = []
        self.leaf_name = []
        for toy_path in TOY_INFO_PATH:
            with open (toy_path,encoding='utf-8') as json_file:
                data = json.load(json_file)
            for d in data:
                if "/" in d["cat_leaf_name"]:
                    leaf_names = d["cat_leaf_name"].split("/") + [ d["cat_leaf_name"]]
                else:
                    leaf_names = [ d["cat_leaf_name"]]
                for name in leaf_names:
                    self.leaf_name.append(name)
                    new_d = d.copy()
                    new_d["cat_leaf_name"] = name
                    new_d["information"] = flatten_dict(new_d["information"])
                    self.information_dataset.append(new_d)
        self.embedder  = SentenceModel('shibing624/text2vec-base-chinese',device = torch.device("cpu"))
        self.target_embbeding = self.embedder.encode(self.leaf_name, convert_to_tensor=True)

    
    def search_information(self,category,information_dataset):
        """

        Args:
            category (str): Categories that need to be matched in the database
            information_dataset (list): the dateset

        Returns:
            dict: Information on target categories
        """
        knowledge = {}
        for d in information_dataset:
            if category == d["cat_leaf_name"]:
                knowledge = d["information"]
                knowledge = {key: value for key, value in knowledge.items() if (value and key!="相关分类")}
                break         
        return knowledge
    
    
    def func(self,memory):
        """
        return the memory of information and determine the next node
        """
        outputdict = {"response":"","temp_memory":{},"long_memory":{},"next_node_id" : "1"}
        
        topk_result = matching_category(memory["extract_category"],self.leaf_name,None,self.target_embbeding,top_k=3)
        top1_score = topk_result[1][0]
        if top1_score > MIN_CATEGORY_SIM:
            outputdict["long_memory"]['category'] = topk_result[0][0]
            information = self.search_information(topk_result[0][0],self.information_dataset)
            information = limit_keys(information,5)
            information = limit_values(information,3)
            outputdict["next_node_id"] = "0"
            outputdict["temp_memory"]["information"] = information
        else:
            outputdict["temp_memory"]["possible_category"] = topk_result[0][0]
        
        yield  outputdict
        
        
class SearchNode(ToolNode):
    def __init__(self, name="", done=False):
        super().__init__(name, done)
    
    def func(self,memory):
        """
        return the recommend of the search shop
        """
        outputdict = {"response":"","temp_memory":{},"long_memory":{},"next_node_id" : "0"}
        requirements = memory["requirements"]
        category = memory["category"]
        
        request_items,top_category = search_with_api(requirements,category)
        if category in top_category:
            top_category.remove(category)
        
        outputdict["temp_memory"]["top_category"] = top_category
        outputdict["temp_memory"]["request_items"] = request_items
        yield outputdict
        
        

class SearchRecomNode(ToolNode):
    def __init__(self, name="", done=False):
        super().__init__(name, done)
    
    def func(self,memory):
        """
        return the recommend of the search shop
        """
        outputdict = {"response":"","temp_memory":{},"long_memory":{},"next_node_id" : "0"}
        request_items = memory["request_items"]
        chat_answer = "<response>"
        if request_items:
            if len(request_items):
                chat_answer += f"""经过搜索后,给你推荐产品:\n"""
                for i in range(0,len(request_items)):
                    chat_answer += f"""{str(i+1)}:“{request_items[i]['itemTitle']}，推荐理由如下：”\n"""
        chat_answer +="</response>"
        outputdict["response"] = chat_answer
        yield outputdict

class RecomTopNode(ToolNode):
    def __init__(self, name="", done=False):
        super().__init__(name, done)
    
    def func(self, memory):
        """
        return the recommend of the search shop
        """
        outputdict = {"response": "", "temp_memory": {}, "long_memory": {}, "next_node_id": "0"}
        top_category = memory["top_category"]
        request_items = memory["request_items"]
        if top_category:
            yield outputdict
            prompt = prompt_cat_recom_top(top_category)
            chat_answer_generator = get_gpt_response_rule_stream(memory["ch_dict"], prompt, "请联系上文进行回答，并按格式输出，即输出格式为：<response>（你的回复内容）</response>，请严格按照上述格式输出！")
            for chat_answer in chat_answer_generator:
                yield chat_answer
        elif not request_items:
            chat_answer = "<response>抱歉呢，亲亲，我们目前没有搜索到您需要的商品，您可以继续提出需求方便我们进行搜寻。</response>"
            outputdict["response"] = chat_answer
            yield outputdict