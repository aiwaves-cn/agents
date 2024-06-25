import os
from interpreter import OpenInterpreter

from .tool import Tool


class CodeInterpreterTool(Tool):

    def __init__(self, model: str = "gpt-4", api_key: str = None, api_base: str = None):
        description = "Order a programmer to write and run code based on the description of a problem."
        name = "code_interpreter"
        parameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The description of the problem.",
                }
            },
            "required": ["query"],
        }
        super().__init__(description, name, parameters)
        self.interpreter = OpenInterpreter()
        self.interpreter.llm.model = model
        self.interpreter.llm.api_key = (
            api_key if api_key else os.environ["OPENAI_API_KEY"]
        )
        if api_base:
            self.interpreter.llm.api_base = api_base
        elif "OPENAI_BASE_URL" in os.environ:
            self.interpreter.llm.api_base = os.environ["OPENAI_BASE_URL"]

    def func(self, query: str):
        messages = self.interpreter.chat(query, display=False)

        code = []
        console = []
        content = ""
        for message in messages:
            if message["type"] == "code":
                code.append(message["content"])
            elif message["type"] == "console":
                console.append(message["content"])
            elif message["type"] == "message":
                content += message["content"] + "\n"

        return {
            "messages": messages,
            "code": code,
            "console": console,
            "content": content,
        }
