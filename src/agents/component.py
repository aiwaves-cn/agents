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


class PromptComponent(Component):

    def __init__(self):
        self.prompt = ""

    @abstractmethod
    def get_prompt(self):
        pass

class PromptComponent():

    def __init__(self):
        pass

    @abstractmethod
    def get_prompt(self):
        pass

class ToolComponent():

    def __init__(self):
        pass

    @abstractmethod
    def func(self):
        pass

class TaskComponent(Component):

    def __init__(self, args_dict):
        super().__init__()
        self.task = args_dict["task"]

    def get_prompt(self):
        return f"""你需要执行的任务是:{self.task}。"""


class OutputComponent(Component):

    def __init__(self, args_dict):
        super().__init__()
        self.output = args_dict["output"]

    def get_prompt(self):
        return f"""请联系上文，进行<{self.output}>和</{self.output}>的提取，不要进行额外的输出，请严格按照上述格式输出！"""


class StyleComponent(Component):
    """
    角色、风格组件
    """

    def __init__(self, args_adic):
        super().__init__()
        self.role = args_adic["role"]
        self.style = args_adic["style"]

    def get_prompt(self):
        return f"""现在你来模拟一个{self.role}。你需要遵循以下的输出风格：{self.style}。"""


class RuleComponent(Component):

    def __init__(self, args_adic):
        super().__init__()
        self.rule = args_adic["rule"]

    def get_prompt(self):
        return f"""你需要遵循的规则是:{self.rule}。"""


class DemonstrationComponent(Component):
    """
    input a list,the example of answer.
    """

    def __init__(self, args_adic):
        super().__init__()
        self.demonstrations = args_adic["demonstrations"]

    def add_demonstration(self, demonstration):
        self.demonstrations.append(demonstration)

    def get_prompt(self):
        prompt = "以下是你可以参考的例子：\n"
        for demonstration in self.demonstrations:
            prompt += "\n" + demonstration
        return prompt


class CoTComponent(Component):
    """
    input a list,the example of answer.
    """

    def __init__(self, args_adic):
        super().__init__()
        self.demonstrations = args_adic["demonstrations"]

    def add_demonstration(self, demonstration):
        self.demonstrations.append(demonstration)

    def get_prompt(self):
        prompt = "你在输出前需要以下是你可以参考的例子：\n"
        for demonstration in self.demonstrations:
            prompt += "\n" + demonstration
        return prompt


class Top_Category_ShoppingComponent(Component):

    def __init__(self):
        super().__init__()

    def get_prompt(self, long_memory, temp_memory):
        memory = {"extract_category": "", "top_category": ""}
        memory.update(long_memory)
        memory.update(temp_memory)

        return f"""你需要知道的是：用户目前选择的商品是{memory["extract_category"]}，而我们店里没有这类商品，但是我们店里有一些近似商品，如{memory["possible_category"],memory["top_category"]}"""


class User_Intent_ShoppingComponent(Component):

    def __init__(self) -> None:
        super().__init__()

    def get_prompt(self, long_memory, temp_memory):
        memory = {"information": "", "category": ""}
        memory.update(long_memory)
        memory.update(temp_memory)

        return f"""你需要知道的是：用户目前选择的商品是{memory["category"]}，该商品信息为{memory["information"]}。"""


class KnowledgeBaseComponent(Component):

    def __init__(self,args_adic):
        super().__init__()
        self.top_k = args_adic["top_k"]
        self.embedding_model = SentenceModel(
            'shibing624/text2vec-base-chinese', device="cpu")
        self.type = args_adic["type"]
        self.knowledge_base = args_adic["knowledge_base"]
        if self.type == "QA":
            self.kb_embeddings, self.kb_questions, self.kb_answers, self.kb_chunks = load_knowledge_base_qa(
                self.knowledge_base)
        else:
            self.kb_embeddings, self.kb_chunks = load_knowledge_base_UnstructuredFile(
                self.knowledge_base)

    def get_knowledge(self, query):
        knowledge = ""
        query_embedding = self.embedding_model.encode(query)
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
                return "没有匹配到相关的知识库"
            else:
                print(knowledge)
                return "相关的内容是： “" + knowledge + "”"

    def func(self, args_dict):
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

        chat_history = get_keyword_in_long_temp("chat_history", long_memory,
                                                temp_memory).copy()
        outputdict = {"response": "", "next_node_id": "0"}
        yield outputdict

        function_response = self.get_knowledge(query=chat_history[-1]["content"])
        
        chat_history.append({
            "role": "assistant",
            "content": function_response,
        })

        response = get_gpt_response_rule_stream(
            chat_history,
            system_prompt=self.system_prompt,
            last_prompt=self.last_prompt,
            args_dict=args_dict,
            temperature=args_dict["temperature"])
        all = ""
        for res in response:
            all += res
            yield res
        long_memory["chat_history"].append({
            "role": "assistant",
            "content": all
        })




class StaticComponent(Component):

    def __init__(self,args_adic):
        super().__init__()
        self.output = args_adic["output"]

    def func(self, args_dict):
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

        outputdict = {"response": self.output, "next_node_id": "0"}
        long_memory["chat_history"].append({
            "role": "assistant",
            "content": self.output
        })
        yield outputdict
        
class RecomComponent(Component):

    def __init__(self):
        super().__init__()

    def func(self, args_dict):
        """
        return the recommend of the search shop
        """
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

        outputdict = {"response": "", "next_node_id": "0"}
        top_category = get_keyword_in_long_temp("top_category", long_memory,
                                                temp_memory)
        request_items = get_keyword_in_long_temp("request_items", long_memory,
                                                 temp_memory)
        chat_history = get_keyword_in_long_temp("chat_history", long_memory,
                                                temp_memory)

        if top_category:
            yield outputdict
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
            all = ""
            for chat_answer in chat_answer_generator:
                all += chat_answer
                yield chat_answer
            long_memory["chat_history"].append({
                "role": "assistant",
                "content": all
            })

        elif not request_items:
            chat_answer = "\\n抱歉呢，亲亲，我们目前没有搜索到您需要的商品，您可以继续提出需求方便我们进行搜寻。"
            long_memory["chat_history"].append({
                "role": "assistant",
                "content": chat_answer
            })
            outputdict["response"] = chat_answer
            yield outputdict


class MatchComponent(Component):

    def __init__(self):
        super().__init__()

        # create dateset
        self.information_dataset = []
        self.leaf_name = []
        for toy_path in TOY_INFO_PATH:
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
        self.embedder = SentenceModel('shibing624/text2vec-base-chinese',
                                      device=torch.device("cpu"))
        self.target_embbeding = self.embedder.encode(self.leaf_name,
                                                     convert_to_tensor=True)

    def search_information(self, category, information_dataset):
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
                knowledge = {
                    key: value
                    for key, value in knowledge.items()
                    if (value and key != "相关分类")
                }
                break
        return knowledge

    def func(self, args_dict):
        """
        return the memory of information and determine the next node
        """
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

        extract_category = get_keyword_in_long_temp("extract_category",
                                                    long_memory, temp_memory)

        outputdict = {"response": "", "next_node_id": "0"}

        topk_result = matching_category(extract_category,
                                        self.leaf_name,
                                        None,
                                        self.target_embbeding,
                                        top_k=3)
        top1_score = topk_result[1][0]
        if top1_score > MIN_CATEGORY_SIM:
            long_memory['category'] = topk_result[0][0]
            information = self.search_information(topk_result[0][0],
                                                  self.information_dataset)
            information = limit_keys(information, 3)
            information = limit_values(information, 2)
            outputdict["next_node_id"] = "1"
            temp_memory["information"] = information
        else:
            temp_memory["possible_category"] = topk_result[0][0]

        yield outputdict


class SearchComponent(Component):

    def __init__(self):
        super().__init__()

    def func(self, args_dict):
        """
        return the recommend of the search shop
        """
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

        outputdict = {"response": "", "next_node_id": "0"}
        requirements = get_keyword_in_long_temp("requirements", long_memory,
                                                temp_memory)
        category = get_keyword_in_long_temp("category", long_memory,
                                            temp_memory)
        if category == "":
            category = get_keyword_in_long_temp("extract_category",
                                                long_memory, temp_memory)

        request_items, top_category = search_with_api(requirements, category)
        if category in top_category:
            top_category.remove(category)

        temp_memory["top_category"] = top_category
        long_memory["request_items"] = request_items
        yield outputdict
