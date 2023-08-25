from abc import abstractclassmethod
import openai
import os
import json
import datetime
import time

API_KEY = os.environ["API_KEY"]
PROXY = os.environ["PROXY"]
MAX_CHAT_HISTORY = eval(
    os.environ["MAX_CHAT_HISTORY"]) if "MAX_CHAT_HISTORY" in os.environ else 10

class LLM:
    def __init__(self) -> None:
        pass

    @abstractclassmethod 
    def get_response():
        pass


class OpenAILLM(LLM):
    def __init__(self,**kwargs) -> None:
        super().__init__()
        self.model = kwargs["model"] if "model" in kwargs else "gpt-3.5-turbo-16k-0613"
        self.temperature = kwargs["temperature"] if "temperature" in  kwargs else 0.3
        self.log_path = kwargs["log_path"] if "log_path" in kwargs else "logs"
    
    
    def save_logs(self,log_path, messages, response):
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        log_path = log_path if log_path else "logs"
        log = {}
        log["input"] = messages
        log["output"] = response
        os.makedirs(log_path, exist_ok=True)
        log_file = os.path.join(
            log_path,
            datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S") + ".json")
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)


    def get_stream(self,response, log_path, messages):
        ans = ""
        for res in response:
            if res:
                r = (res.choices[0]["delta"].get("content")
                    if res.choices[0]["delta"].get("content") else "")
                ans += r
                yield r
        self.save_logs(log_path, messages, ans)
        


    def get_response(self,
                    chat_history,
                    system_prompt,
                    last_prompt=None,
                    stream=False,
                    functions=None,
                    function_call="auto",
                    WAIT_TIME=20,
                    **kwargs):
        openai.api_key = API_KEY
        openai.proxy = PROXY
        model = self.model
        temperature = self.temperature
        
        
        active_mode = kwargs["active_mode"] if "active_mode" in kwargs else False
        summary = kwargs["summary"] if "summary" in kwargs else None
        key_history = kwargs["key_history"] if "key_history" in kwargs else None
        key_his = "Relevant historical chat records are as follows <history>\n{\n"
        if key_history:
            for his in key_history:
                key_his += his["content"] + "\n"
            key_his +="}\n</history>\n"
        

        if active_mode:
            system_prompt = system_prompt + "Please keep your reply as concise as possible"

        messages = [{
            "role": "system",
            "content": system_prompt
        }] if system_prompt else []
        
        if chat_history:
            if len(chat_history) >  MAX_CHAT_HISTORY:
                chat_history = chat_history[- MAX_CHAT_HISTORY:]
            messages += chat_history

        if last_prompt or summary or key_history:
            last_prompt = last_prompt if last_prompt else ""
            last_prompt = f"The information you know is:\n<summary>\n{summary}\n</summary>" + last_prompt if summary else last_prompt
            last_prompt = key_his + last_prompt if key_his else last_prompt
            if active_mode:
                last_prompt = last_prompt + "Please keep your reply as concise as possible"
            # messages += [{"role": "system", "content": f"{last_prompt}"}]
            messages += [{"role": "user", "content": f"{last_prompt}"}]
        

        while True:
            try:
                if functions:
                    response = openai.ChatCompletion.create(
                        model=model,
                        messages=messages,
                        functions=functions,
                        function_call=function_call,
                        temperature=temperature,
                    )
                else:
                    response = openai.ChatCompletion.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        stream=stream)
                break
            except Exception as e:
                print(e)
                if "maximum context length is" in str(e):
                    assert False, "exceed max length"
                    break
                else:
                    print("Please wait {WAIT_TIME} seconds and resend later ...")
                    time.sleep(WAIT_TIME)

        if functions:
            self.save_logs(self.log_path, messages, response)
            return response.choices[0].message
        elif stream:
            return self.get_stream(response, self.log_path, messages)
        else:
            self.save_logs(self.log_path, messages, response)
            return response.choices[0].message["content"]