import requests
from typing import Dict, List
from serpapi import GoogleSearch
from googleapiclient.discovery import build
from .tool import Tool


class WebSearchTool(Tool):
    """web search engines"""

    __ENGINE__: List = ["google", "bing", "serpapi"]

    def __init__(self, engine: str, api: Dict):
        """
        :param engine: The name of the search engine used
        :param api: Pass in a dictionary, such as {"bing":"key1", "google":"key2", ...}, of course each value can also be a list, or more complicated
        """
        description = "Search the web for information"
        name = "web_search"
        parameters = {
            "query": {
                "type": "string",
                "description": "The query to be searched",
            }
        }
        super(WebSearchTool, self).__init__(description, name, parameters)

        """Determine whether the key and engine of the api are legal"""
        assert engine in WebSearchTool.__ENGINE__
        for api_name in api:
            assert api_name in WebSearchTool.__ENGINE__

        self.api = api
        self.engine = engine

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
        api_key = self.api[self.engine]["api_key"]
        cse_id = self.api[self.engine]["cse_id"]
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
        api_key = self.api[self.engine]
        """start searching"""
        results = GoogleSearch(
            {
                "q": query,
                "api_key": api_key,
            }
        ).get_dict()
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
        elif (
            "jobs_results" in results.keys()
            and "jobs" in results["jobs_results"].keys()
        ):
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
        elif (
            "top_sights" in results.keys() and "sights" in results["top_sights"].keys()
        ):
            snippets.append(results["top_sights"]["sights"])
        elif (
            "images_results" in results.keys()
            and "thumbnail" in results["images_results"][0].keys()
        ):
            snippets.append(
                str([item["thumbnail"] for item in results["images_results"][:10]])
            )
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
            if (
                "local_results" in results.keys()
                and "places" in results["local_results"].keys()
            ):
                snippets.append(results["local_results"]["places"])

        metadata_results = list(
            map(lambda snippet: {"snippet": str(snippet)}, snippets)
        )
        return {"meta data": metadata_results}

    def convert_search_engine_to(self, engine):
        assert engine in WebSearchTool.__ENGINE__
        self.engine = engine

    def func(self, query, **kwargs) -> Dict:
        search_results = self.search[self.engine](query=query, **kwargs)
        information = ""
        for i in search_results["meta data"][:5]:
            information += i["snippet"]
        return {
            "prompt": "You can refer to the following information to reply:\n"
            + information
        }
