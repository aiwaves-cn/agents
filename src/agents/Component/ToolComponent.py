from abc import abstractmethod
import uuid
from text2vec import semantic_search
from ..utils import (
    get_relevant_history,
    load_knowledge_base_qa,
    load_knowledge_base_UnstructuredFile,
    get_embedding,
    extract,
)
import json
from typing import Dict, List
import os
from googleapiclient.discovery import build
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import base64
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
from serpapi import GoogleSearch
import time

class ToolComponent:
    def __init__(self):
        pass

    @abstractmethod
    def func(self):
        pass
    
class KnowledgeBaseComponent(ToolComponent):
    """
    Inject knowledge base
    top_k : Top_k with the highest matching degree
    type : "QA" or others
    knowledge_base(json_path) : knowledge_base_path
    """
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

    def func(self, agent):
        query = (
            agent.long_term_memory[-1]["content"]
            if len(agent.long_term_memory) > 0
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
            if score < 0.75:
                return {"prompt": "No matching knowledge base"}
            else:
                return {"prompt": "The relevant content is: " + knowledge + "\n"}
        else:
            for hit in hits:
                matching_idx = hit["corpus_id"]
                if self.kb_chunks[matching_idx] in temp:
                    pass
                else:
                    knowledge = knowledge + f"{self.kb_chunks[matching_idx]}\n\n"
                    temp.append(self.kb_chunks[matching_idx])
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
    "Return static response"
    def __init__(self, output):
        super().__init__()
        self.output = output

    def func(self, agent):
        outputdict = {"response": self.output}
        return outputdict


class ExtractComponent(ToolComponent):
    """
    Extract keywords based on the current scene and store them in the environment
    extract_words(list) : Keywords to be extracted
    system_prompt & last_prompt : Prompt to extract keywords
    """
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

    def func(self, agent):
        response = agent.LLM.get_response(
            agent.long_term_memory,
            self.system_prompt,
            self.last_prompt,
            stream=False,
        )
        for extract_word in self.extract_words:
            key = extract(response, extract_word)
            key = key if key else response
            agent.environment.shared_memory[extract_word] = key

        return {}


"""Search sources: chatgpt/search engines/specific search sources/can even be multimodal (if it comes to clothing)"""


class WebSearchComponent(ToolComponent):
    """search engines"""

    __ENGINE_NAME__: List = ["google", "bing", "serpapi"]

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

        self.search: Dict = {
            "bing": self._bing_search, 
            "google": self._google_search,
            "serpapi": self._serpapi_request,
        }

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
        """execute"""
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
        """execute"""
        metadata_results = []
        for result in results:
            metadata_result = {
                "snippet": result["snippet"],
                "title": result["title"],
                "link": result["link"],
            }
            metadata_results.append(metadata_result)
        return {"meta data": metadata_results}

    # Get SerpApi's API key from https://serpapi.com/manage-api-key
    def _serpapi_request(self, query: str, **kwargs):
        """Initialize search hyperparameters"""
        api_key = self.api[self.engine_name]
        """start searching"""
        results = GoogleSearch({
            "q": query,
            "api_key": api_key,
        }).get_dict()
        if "error" in results.keys():
           raise Exception(results["error"])
        """execute"""
        snippets = []
        if "answer_box_list" in results.keys():
            results["answer_box"] = results["answer_box_list"]
        if "answer_box" in results.keys():
            answer_box = results["answer_box"]
            if isinstance(answer_box, list):
                answer_box = answer_box[0]
            if "result" in answer_box.keys():
                snippets.append(answer_box["result"])
            elif "answer" in answer_box.keys():
                snippets.append(answer_box["answer"])
            elif "snippet" in answer_box.keys():
                snippets.append(answer_box["snippet"])
            elif "snippet_highlighted_words" in answer_box.keys():
                snippets.append(answer_box["snippet_highlighted_words"])
            else:
                answer = {}
                for key, value in answer_box.items():
                    if not isinstance(value, (list, dict)) and not (
                        isinstance(value, str) and value.startswith("http")
                    ):
                        answer[key] = value
                snippets.append(str(answer))
        elif "events_results" in results.keys():
            snippets.append(results["events_results"][:10])
        elif "sports_results" in results.keys():
            snippets.append(results["sports_results"])
        elif "top_stories" in results.keys():
            snippets.append(results["top_stories"])
        elif "news_results" in results.keys():
            snippets.append(results["news_results"])
        elif "jobs_results" in results.keys() and "jobs" in results["jobs_results"].keys():
            snippets.append(results["jobs_results"]["jobs"])
        elif (
            "shopping_results" in results.keys()
            and "title" in results["shopping_results"][0].keys()
        ):
            snippets.append(results["shopping_results"][:3])
        elif "questions_and_answers" in results.keys():
            snippets.append(results["questions_and_answers"])
        elif (
            "popular_destinations" in results.keys()
            and "destinations" in results["popular_destinations"].keys()
        ):
            snippets.append(results["popular_destinations"]["destinations"])
        elif "top_sights" in results.keys() and "sights" in results["top_sights"].keys():
            snippets.append(results["top_sights"]["sights"])
        elif (
            "images_results" in results.keys()
            and "thumbnail" in results["images_results"][0].keys()
        ):
            snippets.append(str([item["thumbnail"] for item in results["images_results"][:10]]))
        else:
            if "knowledge_graph" in results.keys():
                knowledge_graph = results["knowledge_graph"]
                title = knowledge_graph["title"] if "title" in knowledge_graph else ""
                if "description" in knowledge_graph.keys():
                    snippets.append(knowledge_graph["description"])
                for key, value in knowledge_graph.items():
                    if (
                        isinstance(key, str)
                        and isinstance(value, str)
                        and key not in ["title", "description"]
                        and not key.endswith("_stick")
                        and not key.endswith("_link")
                        and not value.startswith("http")
                    ):
                        snippets.append(f"{title} {key}: {value}.")
            if "organic_results" in results.keys():
                first_organic_result = results["organic_results"][0]
                if "snippet" in first_organic_result.keys():
                    snippets.append(first_organic_result["snippet"])
                elif "snippet_highlighted_words" in first_organic_result.keys():
                    snippets.append(first_organic_result["snippet_highlighted_words"])
                elif "rich_snippet" in first_organic_result.keys():
                    snippets.append(first_organic_result["rich_snippet"])
                elif "rich_snippet_table" in first_organic_result.keys():
                    snippets.append(first_organic_result["rich_snippet_table"])
                elif "link" in first_organic_result.keys():
                    snippets.append(first_organic_result["link"])
            if "buying_guide" in results.keys():
                snippets.append(results["buying_guide"])
            if "local_results" in results.keys() and "places" in results["local_results"].keys():
                snippets.append(results["local_results"]["places"])

        metadata_results = list(map(lambda snippet: { "snippet": str(snippet) }, snippets))
        return {"meta data": metadata_results}

    def func(self, agent, **kwargs) -> Dict:
        query = (
            agent.long_term_memory[-1]["content"]
            if len(agent.long_term_memory) > 0
            else " "
        )
        response = agent.LLM.get_response(
            None,
            system_prompt=f"Please analyze the provided conversation and identify keywords that can be used for a search engine query. Format the output as <keywords>extracted keywords</keywords>:\nConversation:\n{query}",
            stream=False,
        )
        response = extract(response, "keywords")
        query = response if response else query

        search_results = self.search[self.engine_name](query=query, **kwargs)
        information = ""
        for i in search_results["meta data"][:5]:
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

    def func(self, agent_dict) -> Dict:
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
        """'../config/google_mail.json'"""
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

    def func(self, agent) -> Dict:
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

    def func(self, agent):
        messages = agent.long_term_memory
        outputdict = {}
        query = agent.long_term_memory[-1].content if len(agent.long_term_memory) > 0 else " "
        relevant_history = get_relevant_history(
            query,
            agent.long_term_memory[:-1],
            agent.chat_embeddings[:-1],
        )
        response = agent.LLM.get_response(
            messages,
            None,
            functions=self.functions,
            stream=False,
            function_call=self.function_call,
            relevant_history=relevant_history,
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


class CodeComponent(ToolComponent):
    def __init__(self, file_name, keyword) -> None:
        super().__init__()
        self.file_name = file_name
        self.keyword = keyword
        self.system_prompt = (
            "you need to extract the modified code as completely as possible."
        )
        self.last_prompt = (
            f"Please strictly adhere to the following format for outputting: \n"
        )
        self.last_prompt += (
            f"<{self.keyword}> the content you need to extract </{self.keyword}>"
        )

    def func(self, agent):
        response = agent.LLM.get_response(
            agent.long_term_memory,
            self.system_prompt,
            self.last_prompt,
            stream=False,
        )
        code = extract(response, self.keyword)
        code = code if code else response
        os.makedirs("output_code", exist_ok=True)
        file_name = "output_code/" + self.file_name
        codes = code.split("\n")
        if codes[0] == "```python":
            codes.remove(codes[0])
        if codes[-1] == "```":
            codes.remove(codes[-1])
        code = "\n".join(codes)
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(code)
        return {}

class FlightComponent(ToolComponent):
    def __init__(self, client_id, client_secret, name="flight"):
        super().__init__()
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self._get_access_token()

    def _get_access_token(self):
        """
        Retrieve access token from Amadeus API for authentication.
        """
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            self.token_expiration = time.time() + response.json()['expires_in']
            return response.json()['access_token']
        else:
            raise Exception("Failed to get access token from Amadeus API")

    def _is_token_expired(self):
        return time.time() > self.token_expiration

    def _refresh_token(self):
        self.token = self._get_access_token()

    def _query_flight_data(self, search_params: Dict) -> Dict:
        """
        Fetches flight price information based on search parameters.

        :param search_params: Dictionary containing search parameters like departure and arrival airports, dates, etc.
        :return: Flight price information or an error message.
        """
        headers = {'Authorization': f'Bearer {self.token}'}
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers" 
        response = requests.get(url, headers=headers, params=search_params)
        if response.status_code == 200:
            return response.json()
        else:
            try:
                return {"error": "Unable to fetch flight data", "detail": response.json()["detail"]}
            except:
                return {"error": "Invalid inputs"}

    def _parse_flight_data(self, flight_data):
        information = f"There are {len(flight_data['data'])} flights available. Here are their information. "
        for i, flight in enumerate(flight_data['data']):
            flight_information = f"Flight ({i+1}): "

            flight_information += f"The duration of departing trip {i+1} is {flight['itineraries'][0]['duration']}."

            flight_information += f"Departing trip {i+1} has {len(flight['itineraries'][0]['segments'])} segments."

            for j, segment in enumerate(flight['itineraries'][0]['segments']):
                flight_information += f"Segment {j+1} goes from airport {segment['departure']['iataCode']} at {segment['departure']['at']} to {segment['arrival']['iataCode']} at {segment['arrival']['at']}. "
            
            if len(flight['itineraries']) > 1:

                flight_information += f"The duration of returning trip {i+1} is {flight['itineraries'][1]['duration']}."

                flight_information += f"Returning trip {i+1} has {len(flight['itineraries'][1]['segments'])} segments."
                for j, segment in enumerate(flight['itineraries'][1]['segments']):
                    flight_information += f"Segment {j+1} goes from airport {segment['departure']['iataCode']} at {segment['departure']['at']}  to {segment['arrival']['iataCode']} at {segment['arrival']['at']} . "
            
            flight_information += f"Trip {i+1} has a total price of of {flight['price']['total']} {flight['price']['currency']}.\n"

            information += flight_information
        return information

    def func(self, agent) -> Dict:
        """
        Function to gather flights and their prices based on provided parameters.

        See parameters at: https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search/api-reference

        :param flight_search_dict: Dictionary containing search parameters.
        :return: Dictionary with flight price data or error message.
        """

        query = ""
        for i in range(3, 0, -1): # get last 3 queries
            if len(agent.long_term_memory) >= i:
                query += agent.long_term_memory[len(agent.long_term_memory) - i]["content"]

        response = agent.LLM.get_response(
            None,
            system_prompt=f'''Please analyze the provided conversation and identify keywords that could be used to make a flight booking using the Amadeus API.
             You must identify whether the conversation is related to searching flight information.
             You must identify the origin location for the flight and convert it into an 3-character IATA code for the closest airport. 
             You must identify the destination location for the flight and convert it into an 3-character IATA code for the closest airport.
             You must identity the departure date for the flight in the YYYY-MM-DD format. If there is no year, make the full date the next possible one chronologically from the current date. If the date is not specified, leave this empty
             You must identify the number of passengers on the flight. 
             If they exist, you may identify the return date of the trip in the YYYY-MM-DD format, the currency code desired, and the max price of the trip. 
             Format the output as: 
             <isRelevant>False if this conversation is not about flight information, otherwise empty</isRelevant>
             <originIATALocationCode>extracted origin airport in the format of an airport IATA code</originIATALocationCode>
             <destinationIATALocationCode>extracted destination airport in the format of an airport IATA code</destinationIATALocationCode>
             <departureDate>extracted departure date in the YYYY-MM-DD format</departureDate>
             <adults>extracted number of passengers</adults>
             <returnDate>extracted return date in in the YYYY-MM-DD format</returnDate>
             <currencyCode>extracted preferred currency for the flight offers. Currency is specified in the ISO 4217 format, e.g. EUR for Euro</currencyCode>
             <maxPrice>extracted maximum price per passenger for the trip</maxPrice>\n 
             Make sure to leave each field empty if that information is not present. Do NOT include any text between the tags if the information is not provided.\nConversation:\n{query}''',
            stream=False,
        )

        if extract(response, "isRelevant") == "False":
            return {"prompt": ""}

        search_params = {
            "originLocationCode": extract(response, "originIATALocationCode"),
            "destinationLocationCode": extract(response, "destinationIATALocationCode"),
            "departureDate": extract(response, "departureDate"),
            "adults": extract(response, "adults"),
            "returnDate": extract(response, "returnDate"),
            "currencyCode": extract(response, "currencyCode"),
            "maxPrice": extract(response, "maxPrice"),
            "max": 3
        }

        error = False

        error_information = ""

        if search_params["originLocationCode"] == "":
            error = True
            error_information += "You need the origin location in order to search up available flights."
        if search_params["destinationLocationCode"] == "":
            error = True
            error_information += "You need the destination location in order to search up available flights."
        if search_params["departureDate"] == "":
            error = True
            error_information += "You need the departure date in order to search up available flights."
        if search_params["adults"] == "":
            search_params["adults"] = 1
        if search_params["returnDate"] == "":
            search_params.pop("returnDate", None)
        if search_params["currencyCode"] == "":
            search_params["currencyCode"] = "USD"
        if search_params["maxPrice"] == "":
            search_params.pop("maxPrice", None)
        if error:
            return {
            "prompt": "You can refer to the following information to reply:\n"
            + error_information
        }

        if self._is_token_expired():
            self._refresh_token()

        flight_data = self._query_flight_data(search_params)

        if "error" in flight_data:
            try:
                return_dict = {"prompt": "You can refer to the following information to reply:\n There is an error with the query, you should clarify about " + flight_data["detail"]}
                return return_dict
            except:
                return {"prompt": flight_data["error"]}

        return {
            "prompt": "You can refer to the following information to reply:\n"
            + self._parse_flight_data(flight_data)
        }