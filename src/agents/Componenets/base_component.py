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
from text2vec import semantic_search
from utils import (
    get_key_history,
    load_knowledge_base_qa,
    load_knowledge_base_UnstructuredFile,
    get_embedding,
    extract,
)
import json
from typing import Dict, List
from googleapiclient.discovery import build
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
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
        return f"""The task you need to execute is: <task>{self.task}</task>.\n"""


class OutputComponent(PromptComponent):
    def __init__(self, output):
        super().__init__()
        self.output = output

    def get_prompt(self, agent_dict):
        return f"""Please contact the above to extract <{self.output}> and </{self.output}>, \
            do not perform additional output, please output in strict accordance with the above format!\n"""


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

    def __init__(self, role, style):
        super().__init__()
        self.style = style
        self.role = role

    def get_prompt(self, agent_dict):
        name = agent_dict["name"]
        return f"""Now your role is:\n<role>{self.role}</role>, your name is:\n<name>{name}</name>. \
            You need to follow the output style:\n<style>{self.style}</style>.\n"""


class RuleComponent(PromptComponent):
    def __init__(self, rule):
        super().__init__()
        self.rule = rule

    def get_prompt(self, agent_dict):
        return f"""The rule you need to follow is:\n<rule>{self.rule}</rule>.\n"""


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
        prompt = "Here are demonstrations you can refer to:\n<demonstrations>"
        for demonstration in self.demonstrations:
            prompt += "\n" + demonstration
        prompt += "</demonstrations>\n"
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
        prompt = "You need to think in detail before outputting, the thinking case is as follows:\n<demonstrations>"
        for demonstration in self.demonstrations:
            prompt += "\n" + demonstration
        prompt += "</demonstrations>\n"
        return prompt


class IputComponent(PromptComponent):
    def __init__(self):
        super().__init__()

    def get_prompt(self, agent_dict):
        information = agent_dict["information"]
        return f"The information you need to know:\n<information>{information}</information>\n"


class CustomizeComponent(PromptComponent):
    def __init__(self, template, keywords) -> None:
        super().__init__()
        self.template = template
        self.keywords = keywords

    def get_prompt(self, agent_dict):
        template_keyword = []
        for keyword in self.keywords:
            current_keyword = agent_dict[keyword]
            template_keyword.append(current_keyword)

        return self.template.format(*template_keyword)


class KnowledgeBaseComponent(ToolComponent):
    def __init__(self, top_k, type, knowledge_base):
        super().__init__()
        self.top_k = top_k
        self.type = type
        self.knowledge_base = knowledge_base

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
        query = (
            agent_dict["long_term_memory"][-1]
            if len(agent_dict["long_term_memory"]) > 0
            else ""
        )
        knowledge = ""
        query = (
            "Generate a representation for this sentence for retrieving related articles:"
            + query
        )
        query_embedding = get_embedding(query)
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
                        + f"question:{self.kb_questions[matching_idx]},answer:{self.kb_answers[matching_idx]}\n\n"
                    )
                    temp.append(self.kb_answers[matching_idx])
                    if len(temp) == 1:
                        break
            print(hits[0]["score"])
            score = hits[0]["score"]
            if score < 0.5:
                return {"prompt": "No matching knowledge base"}
            else:
                return {"prompt": "The relevant content is: " + knowledge + "\n"}
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
                return {"prompt": "No matching knowledge base"}
            else:
                print(knowledge)
                return {"prompt": "The relevant content is: " + knowledge + "\n"}


class StaticComponent(ToolComponent):
    def __init__(self, output):
        super().__init__()
        self.output = output

    def func(self, agent_dict):
        outputdict = {"response": self.output}
        return outputdict


class ExtractComponent(ToolComponent):
    def __init__(
        self,
        extract_words,
        system_prompt,
        last_prompt=None,
    ):
        super().__init__()
        self.extract_words = extract_words
        self.system_prompt = system_prompt
        self.last_prompt = last_prompt if last_prompt else None

    def func(self, agent_dict):
        query = (
            agent_dict["long_term_memory"][-1]
            if len(agent_dict["long_term_memory"]) > 0
            else " "
        )
        key_history = get_key_history(
            query,
            agent_dict["long_term_memory"][:-1],
            agent_dict["chat_embeddings"][:-1],
        )
        response = agent_dict["LLM"].get_response(
            agent_dict["long_term_memory"],
            self.system_prompt,
            self.last_prompt,
            agent_dict=agent_dict,
            stream=False,
            key_history=key_history,
        )
        for extract_word in self.extract_words:
            key = extract(response, extract_word)
            agent_dict[extract_word] = key

        return {}


"""Search sources: chatgpt/search engines/specific search sources/can even be multimodal (if it comes to clothing)"""


class WebSearchComponent(ToolComponent):
    """search engines"""

    __ENGINE_NAME__: List = ["google", "bing"]

    def __init__(self, engine_name: str, api: Dict):
        """
        :param engine_name: The name of the search engine used
        :param api: Pass in a dictionary, such as {"bing":"key1", "google":"key2", ...}, of course each value can also be a list, or more complicated
        """
        super(WebSearchComponent, self).__init__()
        """Determine whether the key and engine_name of the api are legal"""

        assert engine_name in WebSearchComponent.__ENGINE_NAME__
        for api_name in api:
            assert api_name in WebSearchComponent.__ENGINE_NAME__

        self.api = api
        self.engine_name = engine_name

        self.search: Dict = {"bing": self._bing_search, "google": self._google_search}

    def _bing_search(self, query: str, **kwargs):
        """Initialize search hyperparameters"""
        subscription_key = self.api["bing"]
        search_url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        params = {
            "q": query,
            "textDecorations": True,
            "textFormat": "HTML",
            "count": 10,
        }
        """start searching"""
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        results = response.json()["webPages"]["value"]
        """excute"""
        metadata_results = []
        for result in results:
            metadata_result = {
                "snippet": result["snippet"],
                "title": result["name"],
                "link": result["url"],
            }
            metadata_results.append(metadata_result)
        return {"meta data": metadata_results}

    def _google_search(self, query: str, **kwargs):
        """Initialize search hyperparameters"""
        api_key = self.api[self.engine_name]["api_key"]
        cse_id = self.api[self.engine_name]["cse_id"]
        service = build("customsearch", "v1", developerKey=api_key)
        """start searching"""
        results = (
            service.cse().list(q=query, cx=cse_id, num=10, **kwargs).execute()["items"]
        )
        """excute"""
        metadata_results = []
        for result in results:
            metadata_result = {
                "snippet": result["snippet"],
                "title": result["title"],
                "link": result["link"],
            }
            metadata_results.append(metadata_result)
        return {"meta data": metadata_results}

    def func(self, agent_dict: Dict, **kwargs) -> Dict:
        query = (
            agent_dict["long_term_memory"][-2]["content"]
            if len(agent_dict["long_term_memory"]) > 0
            else " "
        )
        search_results = self.search[self.engine_name](query=query, **kwargs)
        information = ""
        for i in search_results["meta data"][:2]:
            information += i["snippet"]
        return {
            "prompt": "You can refer to the following information to reply:\n"
            + information
        }

    def convert_search_engine_to(self, engine_name):
        assert engine_name in WebSearchComponent.__ENGINE_NAME__
        self.engine_name = engine_name


class WebCrawlComponent(ToolComponent):
    """Open a single web page for crawling"""

    def __init__(self):
        super(WebCrawlComponent, self).__init__()

    def func(self, agent_dict: Dict) -> Dict:
        url = agent_dict["url"]
        print(f"crawling {url} ......")
        content = ""
        """Crawling content from url may need to be carried out according to different websites, such as wiki, baidu, zhihu, etc."""
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
    def __init__(self):
        super(APIComponent, self).__init__()

    def func(self, agent_dict: Dict) -> Dict:
        pass


class FunctionComponent(ToolComponent):
    def __init__(
        self,
        functions,
        function_call="auto",
        response_type="response",
        your_function=None,
    ):
        super().__init__()
        self.functions = functions
        self.function_call = function_call
        self.parameters = {}
        self.available_functions = {}
        self.response_type = response_type
        if your_function:
            function_name = your_function["name"]
            function_content = your_function["content"]
            exec(function_content)
            self.available_functions[function_name] = eval(function_name)

        for function in self.functions:
            self.parameters[function["name"]] = list(
                function["parameters"]["properties"].keys()
            )
            self.available_functions[function["name"]] = eval(function["name"])

    def func(self, agent_dict):
        messages = agent_dict["long_term_memory"]
        outputdict = {}
        query = (
            agent_dict["long_term_memory"][-1]
            if len(agent_dict["long_term_memory"]) > 0
            else " "
        )
        key_history = get_key_history(
            query,
            agent_dict["long_term_memory"][:-1],
            agent_dict["chat_embeddings"][:-1],
        )
        response = agent_dict["LLM"].get_response(
            messages,
            None,
            functions=self.functions,
            stream=False,
            function_call=self.function_call,
            key_history=key_history,
        )
        response_message = response
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            fuction_to_call = self.available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            input_args = {}
            for args_name in self.parameters[function_name]:
                input_args[args_name] = function_args.get(args_name)
            function_response = fuction_to_call(**input_args)
            if self.response_type == "response":
                outputdict["response"] = function_response
            elif self.response_type == "prompt":
                outputdict["prompt"] = function_response

        return outputdict
