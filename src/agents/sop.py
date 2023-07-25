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
        """_summary_

        Args:
            tool (Tool, optional): _description_. Defaults to None.
            node_type (str, optional): _description_. Defaults to None.
            extract_words (str, optional): _description_. Defaults to "".
            next_nodes (dict, optional): _description_. Defaults to {}.
            done (bool, optional): _description_. Defaults to False.
            user_input (str, optional): _description_. Defaults to "".
            components(dict) : "style"  *"task"*  "rule" "demonstration"  "input" "tool" *"output"*
        """
        self.prompt = ""
        self.node_type = node_type
        
        self.next_nodes = {}
        
        self.components = components
        self.user_input = user_input
        self.extract_words = extract_words
        self.done = done
        self.name = name
        
    def set_user_input(self,user_input):
        self.user_input = user_input


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
    


class ToolNode:
    def __init__(self,next_nodes = {},name="",done=False):
        self.next_nodes = next_nodes
        self.name = name
        self.done = done
    @abstractmethod
    def func():
        pass

class MatchNode(ToolNode):
    def __init__(self,next_nodes = {},name="",done=False):
        super().__init__(next_nodes,name,done)
        # 建立数据库
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
        #函数：搜索知识库相关的信息
        #入参 attachment 类型：dict 含义：message携带的信息
        #出参 re_info 类型：List 含义：与attachments['category']的知识库相关的三条记录
        #出参 all_knowd 类型：List 含义：与attachments['category']的知识库
        knowledge = {}
        for d in information_dataset:
            if category == d["cat_leaf_name"]:
                knowledge = d["information"]
                knowledge = {key: value for key, value in knowledge.items() if (value and key!="相关分类")}
                break         
        return knowledge
    
    
    def func(self,memory):
        
        outputdict = {"reponse":"","temp_memory":{},"long_memory":{},"next_node_id" : "1"}
        
        topk_result = matching_category(memory["extract_category"],self.leaf_name,None,self.target_embbeding,top_k=3)
        top1_score = topk_result[1][0]
        if top1_score > MIN_CATEGORY_SIM:
            outputdict["long_memory"]['category'] = topk_result[0][0]
            information = self.search_information(topk_result[0][0],self.information_dataset)
            information = limit_keys(information,5)
            information = limit_values(information,3)
            outputdict["next_node_id"] = "0"
            outputdict["temp_memory"]["information"] = information
        
        return  outputdict
        
class SearchNode(ToolNode):
    def __init__(self, next_nodes={}, name="", done=False):
        super().__init__(next_nodes, name, done)
    
    def func(self,memory):
        outputdict = {"reponse":"","temp_memory":{},"long_memory":{},"next_node_id" : "0"}
        requirements = memory["requirements"]
        category = memory["extract_category"]
        information = memory["information"]
        chat_answer = ""
        
        prompt = prompt_cat_markdown(category,information)
        response  = get_gpt_response_rule(memory["ch_dict"],prompt)
        chat_answer+="\n" + response
        
        
        print(requirements,category)
        
        request_items,top_category = search_with_api(requirements,category)
        if request_items:
            if len(request_items):
                chat_answer += f"""客户关键词为{requirements},子类目为{category},给你推荐产品:\n"""
                for i in range(0,len(request_items)):
                    chat_answer += f"""{str(i+1)}:“{request_items[i]['itemTitle']}，推荐理由如下：”\n"""
            if category in top_category:
                    top_category.remove(category)
            if top_category:
                prompt = prompt_cat_recom_top(top_category)
                response = get_gpt_response_rule(memory["ch_dict"],prompt)
                chat_answer += "\n" + response
        else:
            chat_answer +=  "\n" + "抱歉呢，亲亲，我们目前没有搜索到您需要的商品，您可以继续提出需求方便我们进行搜寻。"
            
        
        outputdict["response"] = chat_answer
        return outputdict
        