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
import uuid
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
import base64
import os.path
import re
from datetime import datetime, timedelta
from typing import Tuple, List, Any, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm


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

    def __init__(self, role):
        super().__init__()
        self.role = role

    def get_prompt(self, agent_dict):
        name = agent_dict["name"]
        style = agent_dict["style"]
        return f"""Now your role is:\n<role>{self.role}</role>, your name is:\n<name>{name}</name>. \
            You need to follow the output style:\n<style>{style}</style>.\n"""


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


class CustomizeComponent(PromptComponent):
    def __init__(self, template, keywords) -> None:
        super().__init__()
        self.template = template
        self.keywords = keywords

    def get_prompt(self, agent_dict):
        template_keyword = {}
        for keyword in self.keywords:
            current_keyword = agent_dict["environment"].shared_memory[keyword]
            template_keyword[keyword] = current_keyword
        return self.template.format(**template_keyword)


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
            agent_dict["long_term_memory"][-1]["content"]
            if len(agent_dict["long_term_memory"]) > 0
            else ""
        )
        knowledge = ""
        query = extract(query, "query")
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
        self.default_prompt = (
            "Please strictly adhere to the following format for outputting:\n"
        )
        for extract_word in extract_words:
            self.default_prompt += (
                f"<{extract_word}> the content you need to extract </{extract_word}>"
            )
        self.last_prompt = last_prompt if last_prompt else self.default_prompt

    def func(self, agent_dict):
        response = agent_dict["LLM"].get_response(
            agent_dict["long_term_memory"],
            self.system_prompt,
            self.last_prompt,
            agent_dict=agent_dict,
            stream=False,
        )
        for extract_word in self.extract_words:
            key = extract(response, extract_word)
            key = key if key else response
            agent_dict["environment"].shared_memory[extract_word] = key

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
            agent_dict["long_term_memory"][-1]["content"]
            if len(agent_dict["long_term_memory"]) > 0
            else " "
        )
        query = extract(query, "query")
        response = agent_dict["LLM"].get_response(
            None,
            system_prompt=f"Please analyze the provided conversation and identify keywords that can be used for a search engine query. Format the output as <keywords>extracted keywords</keywords>:\nConversation:\n{query}",
            stream=False,
        )
        response = extract(response, "keywords")
        query = response if response else query

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


class MailComponent(ToolComponent):
    __VALID_ACTION__ = ["read", "send"]

    def __init__(
        self, cfg_file: str, default_action: str = "read", name: str = "e-mail"
    ):
        """'../conifg/google_mail.json'"""
        super(MailComponent, self).__init__(name)
        self.name = name
        assert (
            default_action.lower() in self.__VALID_ACTION__
        ), f"Action `{default_action}` is not allowed! The valid action is in `{self.__VALID_ACTION__}`"
        self.action = default_action.lower()
        self.credential = self._login(cfg_file)

    def _login(self, cfg_file: str):
        SCOPES = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
        ]
        creds = None
        if os.path.exists("token.json"):
            print("Login Successfully!")
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            print("Please authorize in an open browser.")
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cfg_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def _read(self, mail_dict: dict):
        credential = self.credential
        state = mail_dict["state"] if "state" in mail_dict else None
        time_between = (
            mail_dict["time_between"] if "time_between" in mail_dict else None
        )
        sender_mail = mail_dict["sender_mail"] if "sender_mail" in mail_dict else None
        only_both = mail_dict["only_both"] if "only_both" in mail_dict else False
        order_by_time = (
            mail_dict["order_by_time"] if "order_by_time" in mail_dict else "descend"
        )
        include_word = (
            mail_dict["include_word"] if "include_word" in mail_dict else None
        )
        exclude_word = (
            mail_dict["exclude_word"] if "exclude_word" in mail_dict else None
        )
        MAX_SEARCH_CNT = (
            mail_dict["MAX_SEARCH_CNT"] if "MAX_SEARCH_CNT" in mail_dict else 50
        )
        number = mail_dict["number"] if "number" in mail_dict else 10
        if state is None:
            state = "all"
        if time_between is not None:
            assert isinstance(time_between, tuple)
            assert len(time_between) == 2
        assert state in ["all", "unread", "read", "sent"]
        if only_both:
            assert sender_mail is not None
        if sender_mail is not None:
            assert isinstance(sender_mail, str)
        assert credential
        assert order_by_time in ["descend", "ascend"]

        def generate_query():
            query = ""
            if state in ["unread", "read"]:
                query = f"is:{state}"
            if state in ["sent"]:
                query = f"in:{state}"
            if only_both:
                query = f"{query} from:{sender_mail} OR to:{sender_mail}"
            if sender_mail is not None and not only_both:
                query = f"{query} from:({sender_mail})"
            if include_word is not None:
                query = f"{query} {include_word}"
            if exclude_word is not None:
                query = f"{query} -{exclude_word}"
            if time_between is not None:
                TIME_FORMAT = "%Y/%m/%d"
                t1, t2 = time_between
                if t1 == "now":
                    t1 = datetime.now().strftime(TIME_FORMAT)
                if t2 == "now":
                    t2 = datetime.now().strftime(TIME_FORMAT)
                if isinstance(t1, str) and isinstance(t2, str):
                    t1 = datetime.strptime(t1, TIME_FORMAT)
                    t2 = datetime.strptime(t2, TIME_FORMAT)
                elif isinstance(t1, str) and isinstance(t2, int):
                    t1 = datetime.strptime(t1, TIME_FORMAT)
                    t2 = t1 + timedelta(days=t2)
                elif isinstance(t1, int) and isinstance(t2, str):
                    t2 = datetime.strptime(t2, TIME_FORMAT)
                    t1 = t2 + timedelta(days=t1)
                else:
                    assert False, "invalid time"
                if t1 > t2:
                    t1, t2 = t2, t1
                query = f"{query} after:{t1.strftime(TIME_FORMAT)} before:{t2.strftime(TIME_FORMAT)}"
            return query.strip()

        def sort_by_time(data: List[Dict]):
            if order_by_time == "descend":
                reverse = True
            else:
                reverse = False
            sorted_data = sorted(
                data,
                key=lambda x: datetime.strptime(x["time"], "%Y-%m-%d %H:%M:%S"),
                reverse=reverse,
            )
            return sorted_data

        try:
            service = build("gmail", "v1", credentials=credential)
            results = (
                service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX"], q=generate_query())
                .execute()
            )

            messages = results.get("messages", [])
            email_data = list()

            if not messages:
                print("No eligible emails.")
                return None
            else:
                pbar = tqdm(total=min(MAX_SEARCH_CNT, len(messages)))
                for cnt, message in enumerate(messages):
                    pbar.update(1)
                    if cnt >= MAX_SEARCH_CNT:
                        break
                    msg = (
                        service.users()
                        .messages()
                        .get(
                            userId="me",
                            id=message["id"],
                            format="full",
                            metadataHeaders=None,
                        )
                        .execute()
                    )

                    subject = ""
                    for header in msg["payload"]["headers"]:
                        if header["name"] == "Subject":
                            subject = header["value"]
                            break

                    sender = ""
                    for header in msg["payload"]["headers"]:
                        if header["name"] == "From":
                            sender = re.findall(
                                r"\b[\w\.-]+@[\w\.-]+\.\w+\b", header["value"]
                            )[0]
                            break
                    body = ""
                    if "parts" in msg["payload"]:
                        for part in msg["payload"]["parts"]:
                            if part["mimeType"] == "text/plain":
                                data = part["body"]["data"]
                                body = base64.urlsafe_b64decode(data).decode("utf-8")
                                break

                    email_info = {
                        "sender": sender,
                        "time": datetime.fromtimestamp(
                            int(msg["internalDate"]) / 1000
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "subject": subject,
                        "body": body,
                    }
                    email_data.append(email_info)
                pbar.close()
            email_data = sort_by_time(email_data)[0:number]
            return {"results": email_data}
        except Exception as e:
            print(e)
            return None

    def _send(self, mail_dict: dict):
        recipient_mail = mail_dict["recipient_mail"]
        subject = mail_dict["subject"]
        body = mail_dict["body"]
        credential = self.credential
        service = build("gmail", "v1", credentials=credential)

        message = MIMEMultipart()
        message["to"] = recipient_mail
        message["subject"] = subject

        message.attach(MIMEText(body, "plain"))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        try:
            message = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )
            return {"state": True}
        except HttpError as error:
            print(error)
            return {"state": False}

    def func(self, mail_dict: dict):
        if "action" in mail_dict:
            assert mail_dict["action"].lower() in self.__VALID_ACTION__
            self.action = mail_dict["action"]
        functions = {"read": self._read, "send": self._send}
        return functions[self.action](mail_dict)

    def convert_action_to(self, action_name: str):
        assert (
            action_name.lower() in self.__VALID_ACTION__
        ), f"Action `{action_name}` is not allowed! The valid action is in `{self.__VALID_ACTION__}`"
        self.action = action_name.lower()


class WeatherComponet(ToolComponent):
    def __init__(self, api_key, name="weather", TIME_FORMAT="%Y-%m-%d"):
        super(WeatherComponet, self).__init__(name)
        self.name = name
        self.TIME_FORMAT = TIME_FORMAT
        self.api_key = api_key

    def _parse(self, data):
        dict_data: dict = {}
        for item in data["data"]:
            date = item["datetime"]
            dict_data[date] = {}
            if "weather" in item:
                dict_data[date]["description"] = item["weather"]["description"]
            mapping = {
                "temp": "temperature",
                "max_temp": "max_temperature",
                "min_temp": "min_temperature",
                "precip": "accumulated_precipitation",
            }
            for key in ["temp", "max_temp", "min_temp", "precip"]:
                if key in item:
                    dict_data[date][mapping[key]] = item[key]
        return dict_data

    def _query(self, city_name, country_code, start_date, end_date):
        """https://www.weatherbit.io/api/historical-weather-daily"""
        # print(datetime.strftime(start_date, self.TIME_FORMAT), datetime.strftime(datetime.now(), self.TIME_FORMAT), end_date, datetime.strftime(datetime.now()+timedelta(days=1), self.TIME_FORMAT))
        if start_date == datetime.strftime(
            datetime.now(), self.TIME_FORMAT
        ) and end_date == datetime.strftime(
            datetime.now() + timedelta(days=1), self.TIME_FORMAT
        ):
            """today"""
            url = f"https://api.weatherbit.io/v2.0/current?city={city_name}&country={country_code}&key={self.api_key}"
        else:
            url = f"https://api.weatherbit.io/v2.0/history/daily?&city={city_name}&country={country_code}&start_date={start_date}&end_date={end_date}&key={self.api_key}"
        response = requests.get(url)
        data = response.json()
        return self._parse(data)

    def func(self, weather_dict: Dict) -> Dict:
        TIME_FORMAT = self.TIME_FORMAT
        # Beijing, Shanghai
        city_name = weather_dict["city_name"]
        # CN, US
        country_code = weather_dict["country_code"]
        # 2020-02-02
        start_date = datetime.strftime(
            datetime.strptime(weather_dict["start_date"], self.TIME_FORMAT),
            self.TIME_FORMAT,
        )
        end_date = weather_dict["end_date"] if "end_date" in weather_dict else None
        if end_date is None:
            end_date = datetime.strftime(
                datetime.strptime(start_date, TIME_FORMAT) + timedelta(days=-1),
                TIME_FORMAT,
            )
        else:
            end_date = datetime.strftime(
                datetime.strptime(weather_dict["end_date"], self.TIME_FORMAT),
                self.TIME_FORMAT,
            )
        if datetime.strptime(start_date, TIME_FORMAT) > datetime.strptime(
            end_date, TIME_FORMAT
        ):
            start_date, end_date = end_date, start_date
        assert start_date != end_date
        return self._query(city_name, country_code, start_date, end_date)


class TranslateComponent(ToolComponent):
    __SUPPORT_LANGUAGE__ = [
        "af",
        "am",
        "ar",
        "as",
        "az",
        "ba",
        "bg",
        "bn",
        "bo",
        "bs",
        "ca",
        "cs",
        "cy",
        "da",
        "de",
        "dsb",
        "dv",
        "el",
        "en",
        "es",
        "et",
        "eu",
        "fa",
        "fi",
        "fil",
        "fj",
        "fo",
        "fr",
        "fr-CA",
        "ga",
        "gl",
        "gom",
        "gu",
        "ha",
        "he",
        "hi",
        "hr",
        "hsb",
        "ht",
        "hu",
        "hy",
        "id",
        "ig",
        "ikt",
        "is",
        "it",
        "iu",
        "iu-Latn",
        "ja",
        "ka",
        "kk",
        "km",
        "kmr",
        "kn",
        "ko",
        "ku",
        "ky",
        "ln",
        "lo",
        "lt",
        "lug",
        "lv",
        "lzh",
        "mai",
        "mg",
        "mi",
        "mk",
        "ml",
        "mn-Cyrl",
        "mn-Mong",
        "mr",
        "ms",
        "mt",
        "mww",
        "my",
        "nb",
        "ne",
        "nl",
        "nso",
        "nya",
        "or",
        "otq",
        "pa",
        "pl",
        "prs",
        "ps",
        "pt",
        "pt-PT",
        "ro",
        "ru",
        "run",
        "rw",
        "sd",
        "si",
        "sk",
        "sl",
        "sm",
        "sn",
        "so",
        "sq",
        "sr-Cyrl",
        "sr-Latn",
        "st",
        "sv",
        "sw",
        "ta",
        "te",
        "th",
        "ti",
        "tk",
        "tlh-Latn",
        "tlh-Piqd",
        "tn",
        "to",
        "tr",
        "tt",
        "ty",
        "ug",
        "uk",
        "ur",
        "uz",
        "vi",
        "xh",
        "yo",
        "yua",
        "yue",
        "zh-Hans",
        "zh-Hant",
        "zu",
    ]

    def __init__(
        self, api_key, location, default_target_language="zh-cn", name="translate"
    ):
        super(TranslateComponent, self).__init__(name)
        self.name = name
        self.api_key = api_key
        self.location = location
        self.default_target_language = default_target_language

    def func(self, translate_dict: Dict) -> Dict:
        content = translate_dict["content"]
        target_language = self.default_target_language
        if "target_language" in translate_dict:
            target_language = translate_dict["target_language"]
        assert (
            target_language in self.__SUPPORT_LANGUAGE__
        ), f"language `{target_language}` is not supported."

        endpoint = "https://api.cognitive.microsofttranslator.com"

        path = "/translate"
        constructed_url = endpoint + path

        params = {"api-version": "3.0", "to": target_language}

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Ocp-Apim-Subscription-Region": self.location,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        body = [{"text": content}]

        request = requests.post(
            constructed_url, params=params, headers=headers, json=body
        )
        response = request.json()
        response = json.dumps(
            response,
            sort_keys=True,
            ensure_ascii=False,
            indent=4,
            separators=(",", ": "),
        )
        response = eval(response)
        return {"result": response[0]["translations"][0]["text"]}


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
