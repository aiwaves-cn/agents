import json
import uuid
import requests
from typing import Dict

from .tool import Tool


class TranslateTool(Tool):
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

    def __init__(self, api_key, location, default_target_language="zh-cn"):
        description = "Translate the content to the target language"
        name = "translate"
        parameters = {
            "content": {
                "type": "string",
                "description": "The content to be translated",
            },
            "target_language": {
                "type": "string",
                "description": "The target language of the content",
            },
        }
        super(TranslateTool, self).__init__(description, name, parameters)
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
