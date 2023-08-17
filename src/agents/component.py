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
import abc
from typing import Dict, List
from googleapiclient.discovery import build
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class Component:
    def __init__(self):
        pass


class PromptComponent:
    def __init__(self):
        pass

    @abstractmethod
    def get_prompt(self, agent_dict):
        pass


class ToolComponent:
    def __init__(self):
        pass

    @abstractmethod
    def func(self):
        pass


class TaskComponent(PromptComponent):
    def __init__(self, task):
        super().__init__()
        self.task = task

    def get_prompt(self, agent_dict):
        return f"""你需要执行的任务是:{self.task}。"""


class OutputComponent(PromptComponent):
    def __init__(self, output):
        super().__init__()
        self.output = output

    def get_prompt(self, agent_dict):
        return f"""请联系上文，进行<{self.output}>和</{self.output}>的提取，不要进行额外的输出，请严格按照上述格式输出！"""


class LastComponent(PromptComponent):
    def __init__(self, last_prompt):
        super().__init__()
        self.last_prompt = last_prompt

    def get_prompt(self, agent_dict):
        return self.last_prompt


class StyleComponent(PromptComponent):
    """
    角色、风格组件
    """

    def __init__(self, role, name, style):
        super().__init__()
        self.role = role
        self.name = name
        self.style = style

    def get_prompt(self, agent_dict):
        return f"""现在你的身份为：{self.role}，你的名字是:{self.name}。你需要遵循以下的输出风格：{self.style}。"""


class RuleComponent(PromptComponent):
    def __init__(self, rule):
        super().__init__()
        self.rule = rule

    def get_prompt(self, agent_dict):
        return f"""你需要遵循的规则是:{self.rule}。"""


class DemonstrationComponent(PromptComponent):
    """
    input a list,the example of answer.
    """

    def __init__(self, demonstrations):
        super().__init__()
        self.demonstrations = demonstrations

    def add_demonstration(self, demonstration):
        self.demonstrations.append(demonstration)

    def get_prompt(self, agent_dict):
        prompt = "以下是你可以参考的例子：\n"
        for demonstration in self.demonstrations:
            prompt += "\n" + demonstration
        return prompt


class CoTComponent(PromptComponent):
    """
    input a list,the example of answer.
    """

    def __init__(self, demonstrations):
        super().__init__()
        self.demonstrations = demonstrations

    def add_demonstration(self, demonstration):
        self.demonstrations.append(demonstration)

    def get_prompt(self, agent_dict):
        prompt = "你在输出前需要进行详细思考，思考案例如下：\n"
        for demonstration in self.demonstrations:
            prompt += "\n" + demonstration
        return prompt


class IputComponent(PromptComponent):
    def __init__(self):
        super().__init__()

    def get_prompt(self, agent_dict):
        information = agent_dict["information"]
        return f"你需要知道的是：{information}"


class KnowledgeBaseComponent(ToolComponent):
    def __init__(self, top_k, type, knowledge_base):
        super().__init__()
        self.top_k = top_k
        self.type = type
        self.knowledge_base = knowledge_base

        self.embedding_model = SentenceTransformer(
            "BAAI/bge-large-zh", device=torch.device("cpu")
        )
        if self.type == "QA":
            (
                self.kb_embeddings,
                self.kb_questions,
                self.kb_answers,
                self.kb_chunks,
            ) = load_knowledge_base_qa(self.knowledge_base)
        else:
            self.kb_embeddings, self.kb_chunks = load_knowledge_base_UnstructuredFile(
                self.knowledge_base
            )

    def func(self, agent_dict):
        query = agent_dict["query"]
        knowledge = ""
        query = "为这个句子生成表示以用于检索相关文章：" + query
        query_embedding = self.embedding_model.encode(query, normalize_embeddings=True)
        hits = semantic_search(query_embedding, self.kb_embeddings, top_k=50)
        hits = hits[0]
        temp = []
        if self.type == "QA":
            for hit in hits:
                matching_idx = hit["corpus_id"]
                if self.kb_chunks[matching_idx] in temp:
                    pass
                else:
                    knowledge = (
                        knowledge
                        + f"问题：{self.kb_questions[matching_idx]}，答案：{self.kb_answers[matching_idx]}\n\n"
                    )
                    temp.append(self.kb_answers[matching_idx])
                    if len(temp) == 1:
                        break
            print(hits[0]["score"])
            score = hits[0]["score"]
            if score < 0.5:
                return {"prompt": "没有匹配到相关的知识库"}
            else:
                return {"prompt": "相关的内容是： “" + knowledge + "”"}
        else:
            for hit in hits:
                matching_idx = hit["corpus_id"]
                if self.kb_chunks[matching_idx] in temp:
                    pass
                else:
                    knowledge = knowledge + f"{self.kb_answers[matching_idx]}\n\n"
                    temp.append(self.kb_answers[matching_idx])
                    if len(temp) == self.top_k:
                        break
            print(hits[0]["score"])
            score = hits[0]["score"]
            if score < 0.5:
                return {"prompt": "没有匹配到相关的知识库"}
            else:
                print(knowledge)
                return {"prompt": "相关的内容是： “" + knowledge + "”"}


class StaticComponent(ToolComponent):
    def __init__(self, output):
        super().__init__()
        self.output = output

    def func(self, agent_dict):
        memory = {}
        memory.update(agent_dict["long_memory"])
        memory.update(agent_dict["short_memory"])

        outputdict = {"response": self.output}
        return outputdict


class ExtractComponent(ToolComponent):
    def __init__(
        self,
        long_memory_extract_words,
        short_memory_extract_words,
        system_prompt,
        last_prompt=None,
    ):
        super().__init__()
        self.long_memory_extract_words = long_memory_extract_words
        self.short_memory_extract_words = short_memory_extract_words
        self.system_prompt = system_prompt
        self.last_prompt = last_prompt if last_prompt else None

    def func(self, agent_dict):
        response = get_gpt_response_rule(
            agent_dict["long_memory"]["chat_history"],
            self.system_prompt,
            self.last_prompt,
            agent_dict=agent_dict,
        )
        for extract_word in self.long_memory_extract_words:
            key = extract(response, extract_word)
            agent_dict["long_memory"][extract_word] = key
        for extract_word in self.short_memory_extract_words:
            key = extract(response, extract_word)
            agent_dict["short_memory"][extract_word] = key
        return {}


class CategoryRequirementsComponent(ToolComponent):
    def __init__(self, information_path):
        super().__init__()
        self.information_dataset = []
        self.leaf_name = []
        for toy_path in information_path:
            with open(toy_path, encoding="utf-8") as json_file:
                data = json.load(json_file)
            for d in data:
                if "/" in d["cat_leaf_name"]:
                    leaf_names = d["cat_leaf_name"].split("/") + [d["cat_leaf_name"]]
                else:
                    leaf_names = [d["cat_leaf_name"]]
                for name in leaf_names:
                    self.leaf_name.append(name)
                    new_d = d.copy()
                    new_d["cat_leaf_name"] = name
                    new_d["information"] = flatten_dict(new_d["information"])
                    self.information_dataset.append(new_d)
        self.embedder = SentenceTransformer(
            "BAAI/bge-large-zh", device=torch.device("cpu")
        )
        self.target_embbeding = self.embedder.encode(
            self.leaf_name, convert_to_tensor=True
        )

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

    def func(self, agent_dict):
        prompt = ""
        messages = agent_dict["long_memory"]["chat_history"]
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
                    "required": ["category", "requirements"],
                },
            }
        ]
        response = get_gpt_response_function(
            messages,
            None,
            None,
            functions=functions,
            function_call={"name": "search_information"},
        )
        response_message = json.loads(response["function_call"]["arguments"])
        category = (
            response_message["category"] if response_message["category"] else None
        )
        requirements = (
            response_message["requirements"]
            if response_message["requirements"]
            else category
        )
        if not (category or requirements):
            return {}

        topk_result = matching_category(
            category, self.leaf_name, None, self.target_embbeding, top_k=3
        )

        top1_score = topk_result[1][0]
        request_items, top_category = search_with_api(requirements, category)
        if top1_score > MIN_CATEGORY_SIM:
            agent_dict["long_memory"]["category"] = topk_result[0][0]
            category = topk_result[0][0]
            information = self.search_information(
                topk_result[0][0], self.information_dataset
            )
            information = limit_keys(information, 3)
            information = limit_values(information, 2)
            prompt += f"""你需要知道的是：用户目前选择的商品是{category}，该商品信息为{information}。你需要根据这些商品信息来询问用户是否有更多的需求。例如： "商品信息为：{{乒乓球拍海绵类型\": [\n        \"薄海绵(击球快)\",\n        \"硬海绵(快攻型)\",\n        \"厚海绵(后劲足)\",\n        \"软海绵(控球型)\"\n      ],\n      \"大小描述\": [\n        \"中号\",\n        \"大号\",\n        \"小号\",\n        \"均码\",\n      ]}}\n输出：\n<回复>非常高兴您选择了我们的乒乓球拍产品！关于您的选择，我有以下详细的推荐：\n\n乒乓球拍海绵类型:\n\n**薄海绵(击球快)**: 如果您的打法以速度为主，希望球拍反应迅速，那么薄海绵可能是一个很好的选择。\n**硬海绵(快攻型)**: 如果您是一名快攻型选手，硬海绵将有助于您提高攻击力和击球速度。\n**厚海绵(后劲足)**: 对于更注重控制和旋转的选手，厚海绵可以提供更好的弹性和后劲。\n**软海绵(控球型)**: 如果您更看重对球的控制，那么软海绵可能是您的首选。它可以帮助您更好地控制球的方向和速度。\n大小描述:\n**中号**: 中号的球拍适合大多数人，它提供了良好的控制感和合适的打击面积。\n**大号**: 如果您希望有更大的击球面积，可以考虑选择大号球拍，它能帮助您更容易击中球。\n**小号**: 小号球拍更适合孩子或是手较小的人使用，它更易于控制。\n**均码**: 均码的球拍适合大部分人群，如果您不确定自己适合哪种尺寸，可以考虑选择均码球拍。\n希望这些建议能帮助您更好地理解每个选项，并为您的购买决策提供帮助。当然，您的个人喜好和需求是最重要的，这些都只是建议供您参考。</回复>\n  \n2.\n输入商品信息为：{{ \"品牌\": [\n        \"DIY\",\n        \"钓鱼\",\n      ],\n      \"发饰分类\": [\n        \"发箍\",\n        \"对夹\",\n        \"边夹\"\n      ],\n      \"风格\": [\n        \"甜美\",\n        \"复古/宫廷\",\n        \"日韩\",\n      ],\n      \"材质\": [\n        \"缎\",\n        \"布\",\n      ]}}\n输出：\n<回复>非常高兴您选择了我们的产品！关于您的选择，我有以下详细的推荐：\n品牌:\n**DIY**: DIY品牌的产品以其独特的个性化设计和高品质材料赢得了消费者的喜爱。如果你是手工艺品的热爱者，那么这个品牌绝对不容错过。\n**钓鱼**: 钓鱼品牌因其专注于创新和用户体验，受到了广大消费者的一致好评。\n发饰分类:\n**发箍**: 发箍非常适合运动或者是需要保持发型整洁的场合，它能有效地帮助你固定头发，避免头发散落影响视线。\n**对夹**: 对夹适合任何场合，尤其是需要快速简单地改变发型的时候，它是你的最佳选择。\n**边夹**: 边夹可以作为你日常打扮的点睛之笔，为你的发型增加一抹色彩。\n风格:\n**甜美**: 甜美风格的发饰通常以其温柔的色彩和繁复的设计受到年轻女孩的喜爱。\n**复古/宫廷**: 复古/宫廷风格则给人一种高贵而神秘的感觉，非常适合正式的场合。\n**日韩**: 日韩风格的发饰以其简约而精致的设计，给人留下深刻印象。\n材质:\n**缎**: 缎是一种光滑柔软的织物，常常被用于高档的头饰制作，其质地舒适，触感良好。\n**布**: 布材质的发饰以其轻便耐用，保养简单等特点，赢得了消费者的喜爱。\n希望这些建议能帮助您更好地理解每个选项，并为您的购买决策提供帮助。当然，您的个人喜好和需求是最重要的，这些都只是建议供您参考。</回复>"""
            if category in top_category:
                top_category.remove(category)

            recommend = ""
            for i, request_item in enumerate(request_items):
                itemTitle = request_item["itemTitle"]
                itemPrice = request_item["itemPrice"]
                recommend += f"{i}.商品名称：{itemTitle},商品价格为:{itemPrice}\n"
            recommend += "你需要对每个商品进行介绍，引导用户购买"
            outputdict["recommend"] = recommend
        else:
            prompt += f"""你需要知道的是：用户目前选择的商品是{category}，而我们店里没有这类商品，但是我们店里有一些近似商品，如{top_category},{topk_result[0][0]}，你需要对这些近似商品进行介绍，并引导用户购买"""
        outputdict["prompt"] = prompt
        return outputdict


"""搜索源: chatgpt/搜索引擎/特定的搜索源/甚至可以多模态（如果涉及到服装）"""


class WebSearchComponent(ToolComponent):
    """搜索引擎"""

    __ENGINE_NAME__: List = ["google", "bing"]

    def __init__(self, engine_name: str, api: Dict):
        """
        :param engine_name: 使用的搜索引擎的名称
        :param api: 传入一个字典, 比如{"bing":"key1", "google":"key2", ...}，当然每个value也可以是list，或者更加复杂的
        """
        super(WebSearchComponent, self).__init__()
        """判断api的key和engine_name是否合法"""

        assert engine_name in WebSearchComponent.__ENGINE_NAME__
        for api_name in api:
            assert api_name in WebSearchComponent.__ENGINE_NAME__

        self.api = api
        self.engine_name = engine_name

        self.search: Dict = {"bing": self._bing_search, "google": self._google_search}

    def _bing_search(self, query: str, **kwargs):
        """初始化搜索超参数"""
        subscription_key = self.api["bing"]
        search_url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        params = {
            "q": query,
            "textDecorations": True,
            "textFormat": "HTML",
            "count": 10,
        }
        """开始搜索"""
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        results = response.json()["webPages"]["value"]
        """处理"""
        metadata_results = []
        for result in results:
            metadata_result = {
                "snippet": result["snippet"],
                "title": result["name"],
                "link": result["url"],
            }
            metadata_results.append(metadata_result)
        print(metadata_results)
        return {"meta data": metadata_results}

    def _google_search(self, query: str, **kwargs):
        """初始化搜索超参数"""
        api_key = self.api[self.engine_name]["api_key"]
        cse_id = self.api[self.engine_name]["cse_id"]
        service = build("customsearch", "v1", developerKey=api_key)
        """开始搜索"""
        results = (
            service.cse().list(q=query, cx=cse_id, num=10, **kwargs).execute()["items"]
        )
        """处理"""
        metadata_results = []
        for result in results:
            metadata_result = {
                "snippet": result["snippet"],
                "title": result["title"],
                "link": result["link"],
            }
            metadata_results.append(metadata_result)
        print(metadata_results)
        return {"meta data": metadata_results}

    def func(self, agent_dict: Dict, **kwargs) -> Dict:
        search_results = self.search[self.engine_name](
            query=agent_dict["query"], **kwargs
        )

        return {"search_result": search_results}

    def convert_search_engine_to(self, engine_name):
        assert engine_name in WebSearchComponent.__ENGINE_NAME__
        self.engine_name = engine_name


class WebCrawlComponent(ToolComponent):
    """打开一个single的网页进行爬取"""

    def __init__(self):
        super(WebCrawlComponent, self).__init__()

    def func(self, agent_dict: Dict) -> Dict:
        url = agent_dict["url"]
        print(f"crawling {url} ......")
        content = ""
        """从url中爬取内容，感觉可能需要根据不同的网站进行，比如wiki、baidu、zhihu, etc."""
        driver = webdriver.Chrome()
        try:
            """open url"""
            driver.get(url)

            """wait 20 second"""
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            """crawl code"""
            page_source = driver.page_source

            """parse"""
            soup = BeautifulSoup(page_source, "html.parser")

            """concatenate"""
            for paragraph in soup.find_all("p"):
                content = f"{content}\n{paragraph.get_text()}"
        except Exception as e:
            print("Error:", e)
        finally:
            """quit"""
            driver.quit()
        return {"content": content.strip()}


class APIComponent(ToolComponent):
    def __init__(self, name):
        super(APIComponent, self).__init__(name)

    def func(self, agent_dict: Dict) -> Dict:
        pass
