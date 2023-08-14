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
"""
Components (modularized prompts) of a Node in an LLM Autonomous agent
"""

from abc import abstractmethod
from text2vec import SentenceModel, semantic_search
from utils import *


class Component():

    def __init__(self):
        pass

class PromptComponent():

    def __init__(self):
        pass

    @abstractmethod
    def get_prompt(self,args_dict):
        pass

class ToolComponent():

    def __init__(self):
        pass

    @abstractmethod
    def func(self):
        pass
    
    
class TaskComponent(PromptComponent):

    def __init__(self, args_dict):
        super().__init__()
        self.task = args_dict["task"]

    def get_prompt(self,args_dict):
        return f"""你需要执行的任务是:{self.task}。"""


class OutputComponent(PromptComponent):

    def __init__(self, args_dict):
        super().__init__()
        self.output = args_dict["output"]

    def get_prompt(self,args_dict):
        return f"""请联系上文，进行<{self.output}>和</{self.output}>的提取，不要进行额外的输出，请严格按照上述格式输出！"""


class StyleComponent(PromptComponent):
    """
    角色、风格组件
    """

    def __init__(self, args_adic):
        super().__init__()
        self.role = args_adic["role"]
        self.name = args_adic["name"]
        self.style = args_adic["style"]

    def get_prompt(self,args_dict):
        return f"""现在你的身份为：{self.role}，你的名字是:{self.name}。你需要遵循以下的输出风格：{self.style}。"""


class RuleComponent(PromptComponent):

    def __init__(self, args_adic):
        super().__init__()
        self.rule = args_adic["rule"]

    def get_prompt(self,args_dict):
        return f"""你需要遵循的规则是:{self.rule}。"""


class DemonstrationComponent(PromptComponent):
    """
    input a list,the example of answer.
    """

    def __init__(self, args_adic):
        super().__init__()
        self.demonstrations = args_adic["demonstrations"]

    def add_demonstration(self, demonstration):
        self.demonstrations.append(demonstration)

    def get_prompt(self,args_dict):
        prompt = "以下是你可以参考的例子：\n"
        for demonstration in self.demonstrations:
            prompt += "\n" + demonstration
        return prompt


class CoTComponent(PromptComponent):
    """
    input a list,the example of answer.
    """

    def __init__(self, args_adic):
        super().__init__()
        self.demonstrations = args_adic["demonstrations"]

    def add_demonstration(self, demonstration):
        self.demonstrations.append(demonstration)

    def get_prompt(self,args_dict):
        prompt = "你在输出前需要以下是你可以参考的例子：\n"
        for demonstration in self.demonstrations:
            prompt += "\n" + demonstration
        return prompt



class IputComponent(PromptComponent):
    def __init__(self):
        super().__init__()

    def get_prompt(self,args_dict):
        information=args_dict["information"]
        return f"你需要知道的是：{information}"



class KnowledgeBaseComponent(ToolComponent):
    def __init__(self,args_dict):
        super().__init__()
        self.top_k = args_dict["top_k"]
        self.type = args_dict["type"]
        self.knowledge_base = args_dict["knowledge_base"]
        
        
        self.embedding_model =  SentenceTransformer('BAAI/bge-large-zh',
                             device=torch.device("cpu"))
        if self.type == "QA":
            self.kb_embeddings, self.kb_questions, self.kb_answers, self.kb_chunks = load_knowledge_base_qa(
                self.knowledge_base)
        else:
            self.kb_embeddings, self.kb_chunks = load_knowledge_base_UnstructuredFile(
                self.knowledge_base)

    def func(self, args_dict):
        query = args_dict["query"]
        knowledge = ""
        query = "为这个句子生成表示以用于检索相关文章：" + query
        query_embedding = self.embedding_model.encode(query, normalize_embeddings=True)
        hits = semantic_search(query_embedding, self.kb_embeddings, top_k=50)
        hits = hits[0]
        temp = []
        if self.type == "QA":
            for hit in hits:
                matching_idx = hit['corpus_id']
                if self.kb_chunks[matching_idx] in temp:
                    pass
                else:
                    knowledge = knowledge + f'问题：{self.kb_questions[matching_idx]}，答案：{self.kb_chunks[matching_idx]}\n\n'
                    temp.append(self.kb_chunks[matching_idx])
                    if len(temp) == 1:
                        break
            print(hits[0]["score"])
            score = hits[0]["score"]
            if score < 0.5:
                return "没有匹配到相关的知识库"
            else:
                print(knowledge)
                return "提供的相关内容是： “" + knowledge + "”如果能完全匹配对应的问题，你就完全输出对应的答案，如果只是有参考的内容，你可以根据以上内容进行回答。"
        else:
            for hit in hits:
                matching_idx = hit['corpus_id']
                if self.kb_chunks[matching_idx] in temp:
                    pass
                else:
                    knowledge = knowledge + f'{self.kb_chunks[matching_idx]}\n\n'
                    temp.append(self.kb_chunks[matching_idx])
                    if len(temp) == self.top_k:
                        break
            print(hits[0]["score"])
            score = hits[0]["score"]
            if score < 0.5:
                return {"prompt":"没有匹配到相关的知识库"}
            else:
                print(knowledge)
                return {"prompt":"相关的内容是： “" + knowledge + "”"}



class StaticComponent(ToolComponent):

    def __init__(self,args_dict):
        super().__init__()
        self.output = args_dict["output"]

    def func(self, args_dict):
        memory = {}
        memory.update(args_dict["long_memory"])
        memory.update(args_dict["short_memory"])

        outputdict = {"response": self.output}
        return outputdict
        
        
class RecomComponent(ToolComponent):

    def __init__(self):
        super().__init__()

    def func(self, args_dict):
        """
        return the recommend of the search shop
        """
        memory = {}
        memory.update(args_dict["long_memory"])
        memory.update(args_dict["short_memory"])

        outputdict = {"response": ""}
        top_category = memory["category"]
        request_items = memory["request_items"]
        chat_history = memory["chat_history"]

        if top_category:
            import sys
            import os
            current_path = os.path.abspath(__file__)
            current_path = os.path.dirname(current_path)
            sys.path.append(
                os.path.join(current_path,
                             '../../examples/shopping_assistant'))
            from tool_prompt import prompt_cat_recom_top
            prompt = prompt_cat_recom_top(top_category)
            chat_answer_generator = get_gpt_response_rule_stream(
                chat_history,
                prompt,
                None,
                args_dict=args_dict,
                temperature=args_dict["temperature"])
            
            outputdict["response"] = chat_answer_generator

        elif not request_items:
            chat_answer = "\\n抱歉呢，亲亲，我们目前没有搜索到您需要的商品，您可以继续提出需求方便我们进行搜寻。"
            outputdict["response"] = chat_answer
        return outputdict


class ExtractComponent(ToolComponent):
    def __init__(self,args_dict):
        super().__init__()
        self.long_memory_extract_words = args_dict["long_memory_extract_words"]
        self.short_memory_extract_words = args_dict["short_memory_extract_words"]
        self.system_prompt = args_dict["system_prompt"]
        self.last_prompt = args_dict["last_prompt"] if args_dict["last_prompt"] else None
        
    def func(self,args_dict):
        response = get_gpt_response_rule(args_dict["long_memory"]["chat_history"],self.system_prompt,self.last_prompt,args_dict=args_dict)
        for extract_word in self.long_memory_extract_words:
            key = extract(response,extract_word)
            args_dict["long_memory"][extract_word] = key
        for extract_word in self.short_memory_extract_words:
            key = extract(response,extract_word)
            args_dict["short_memory"][extract_word] = key
        return {}
    
        
class  CategoryRequirementsComponent(ToolComponent):
    def __init__(self,args_dict):
        super().__init__()
        self.information_dataset = []
        self.leaf_name = []
        for toy_path in args_dict["information_path"]:
            with open(toy_path, encoding='utf-8') as json_file:
                data = json.load(json_file)
            for d in data:
                if "/" in d["cat_leaf_name"]:
                    leaf_names = d["cat_leaf_name"].split("/") + [
                        d["cat_leaf_name"]
                    ]
                else:
                    leaf_names = [d["cat_leaf_name"]]
                for name in leaf_names:
                    self.leaf_name.append(name)
                    new_d = d.copy()
                    new_d["cat_leaf_name"] = name
                    new_d["information"] = flatten_dict(new_d["information"])
                    self.information_dataset.append(new_d)
        self.embedder = SentenceTransformer('BAAI/bge-large-zh',
                             device=torch.device("cpu"))
        self.target_embbeding = self.embedder.encode(self.leaf_name,
                                                     convert_to_tensor=True)
        
    def search_information(self, category, information_dataset):
        knowledge = {}
        for d in information_dataset:
            if category == d["cat_leaf_name"]:
                knowledge = d["information"]
                knowledge = {
                    key: value
                    for key, value in knowledge.items()
                    if (value and key != "相关分类")
                }
                break
        return knowledge
    
    def func(self,args_dict):
        prompt = ""
        messages = args_dict["long_memory"]["chat_history"]
        outputdict = {}
        functions = [
        {
            "name": "search_information",
            "description": "根据用户所需要购买商品的种类跟用户的需求去寻找用户所需要的商品",
           "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "用户现在所需要的商品类别，比如纸尿布，笔记本电脑等，注意，只能有一个",
                    },
                    "requirements": {
                        "type": "string",
                        "description": "用户现在的需求，比如说便宜，安踏品牌等等，可以有多个需求，中间以“ ”分隔",
                    },
                },
                "required": ["category","requirements"],
            },
        }
    ]   
        response = get_gpt_response_function(messages,None,None,functions = functions,function_call={"name":"search_information"})
        response_message = json.loads(response["function_call"]["arguments"])
        category = response_message["category"] if response_message["category"] else None
        requirements = response_message["requirements"] if response_message["requirements"] else category
        if not (category or requirements):
            return {}
        
        topk_result = matching_category(category,
                                        self.leaf_name,
                                        None,
                                        self.target_embbeding,
                                        top_k=3)
        
        top1_score = topk_result[1][0]
        request_items, top_category = search_with_api(requirements, category)
        if top1_score > MIN_CATEGORY_SIM:
            args_dict["long_memory"]['category'] = topk_result[0][0]
            category = topk_result[0][0]
            information = self.search_information(topk_result[0][0],
                                                  self.information_dataset)
            information = limit_keys(information, 3)
            information = limit_values(information, 2)
            prompt += f"""你需要知道的是：用户目前选择的商品是{category}，该商品信息为{information}。你需要根据这些商品信息来询问用户是否有更多的需求"""
            if category in top_category:
                top_category.remove(category)
            
            recommend = ""
            for i,request_item in enumerate(request_items):
                itemTitle = request_item["itemTitle"]
                itemPrice = request_item["itemPrice"]
                recommend += f"{i}.商品名称：{itemTitle},商品价格为:{itemPrice}\n"
            recommend += "你需要对每个商品进行介绍，引导用户购买"
            outputdict["recommend"] = recommend
        else:
            prompt += f"""你需要知道的是：用户目前选择的商品是{category}，而我们店里没有这类商品，但是我们店里有一些近似商品，如{top_category},{topk_result[0][0]}，你需要对这些近似商品进行介绍，并引导用户购买"""
        outputdict["prompt"] = prompt
        return outputdict
        