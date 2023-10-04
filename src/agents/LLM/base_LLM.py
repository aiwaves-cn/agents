from abc import abstractclassmethod
import litellm
import os
import time
from Memory import Memory
from utils import save_logs

class LLM:
    def __init__(self) -> None:
        pass

    @abstractclassmethod 
    def get_response():
        pass


class OpenAILLM(LLM):
    def __init__(self,**kwargs) -> None:
        super().__init__()
        self.MAX_CHAT_HISTORY = eval(
            os.environ["MAX_CHAT_HISTORY"]) if "MAX_CHAT_HISTORY" in os.environ else 10
        
        self.model = kwargs["model"] if "model" in kwargs else "gpt-3.5-turbo-16k-0613"
        self.temperature = kwargs["temperature"] if "temperature" in  kwargs else 0.3
        self.log_path = kwargs["log_path"].replace("/",os.sep) if "log_path" in kwargs else "logs"
    

    def get_stream(self,response, log_path, messages):
        ans = ""
        for res in response:
            if res:
                r = (res.choices[0]["delta"].get("content")
                    if res.choices[0]["delta"].get("content") else "")
                ans += r
                yield r
        
        save_logs(log_path, messages, ans)
        
        
        
    def get_response(self,
                    chat_history,
                    system_prompt,
                    last_prompt=None,
                    stream=False,
                    functions=None,
                    function_call="auto",
                    WAIT_TIME=20,
                    **kwargs):
        """
        return LLM's response 
        """
        litellm.api_key = os.environ["API_KEY"]
        if "PROXY" in os.environ:
            assert "http:" in os.environ["PROXY"] or "socks" in os.environ["PROXY"],"PROXY error,PROXY must be http or socks"
            litellm.proxy = os.environ["PROXY"]
        if "API_BASE" in os.environ:
            litellm.api_base = os.environ["API_BASE"]
        active_mode = True if ("ACTIVE_MODE" in os.environ and os.environ["ACTIVE_MODE"] == "0") else False
        model = self.model
        temperature = self.temperature
        
        
        if active_mode:
            system_prompt = system_prompt + "Please keep your reply as concise as possible,Within three sentences, the total word count should not exceed 30"

        messages = [{
            "role": "system",
            "content": system_prompt
        }] if system_prompt else []
        
        if chat_history:
            if len(chat_history) >  self.MAX_CHAT_HISTORY:
                chat_history = chat_history[- self.MAX_CHAT_HISTORY:]
            if isinstance(chat_history[0],dict):
                messages += chat_history
            elif isinstance(chat_history[0],Memory):
                messages += [memory.get_gpt_message("user") for memory in chat_history]
        
        

        if last_prompt:
            if active_mode:
                last_prompt = last_prompt + "Please keep your reply as concise as possible,Within three sentences, the total word count should not exceed 30"
            # messages += [{"role": "system", "content": f"{last_prompt}"}]
            messages[-1]["content"] += last_prompt
        

        while True:
            try:
                if functions:
                    response = litellm.completion(
                        model=model,
                        messages=messages,
                        functions=functions,
                        function_call=function_call,
                        temperature=temperature,
                    )
                else:
                    response = litellm.completion(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        stream=stream)
                break
            except Exception as e:
                print(e)
                if "maximum context length is" in str(e):
                    if len(messages)>1:
                        del messages[1]
                    else:
                        assert False, "exceed max length"
                else:
                    print(f"Please wait {WAIT_TIME} seconds and resend later ...")
                    time.sleep(WAIT_TIME)

        if functions:
            save_logs(self.log_path, messages, response)
            return response.choices[0].message
        elif stream:
            return self.get_stream(response, self.log_path, messages)
        else:
            save_logs(self.log_path, messages, response)
            return response.choices[0].message["content"]


def init_LLM(default_log_path,**kwargs):
    LLM_type = kwargs["LLM_type"] if "LLM_type" in kwargs else "OpenAI"
    log_path = kwargs["log_path"].replace("/",os.sep) if "log_path" in kwargs else default_log_path
    if LLM_type == "OpenAI":
        LLM = (
            OpenAILLM(**kwargs["LLM"])
            if "LLM" in kwargs
            else OpenAILLM(model = "gpt-3.5-turbo-16k-0613",temperature=0.3,log_path=log_path)
        )
        return LLM
    