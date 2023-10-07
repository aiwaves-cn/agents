import sys
sys.path.append('../../../../src/agents')
from agents.Agent import Agent
from agents.State import State
import os
import copy
import time
from typing import List, Dict, Any
import openai
import litellm
from myutils import print_log, simulation
import abc
import json
import socket

PROXY = os.environ["PROXY"]
litellm.proxy = PROXY

class Client:

    server = None
    current_node = None
    cache = {}

    def __init__(self, host='127.0.0.1', port=9999, bufsize=1024):
        self.bufsize = bufsize
        assert bufsize > 0
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.send("hello agent".encode('utf-8'))
        print_log("client: Connected successfully......")

    def start_server(self):
        while True:
            message = yield
            if message == 'exit':
                break
            self.client_socket.send(message.encode('utf-8'))

    def listening_for_start(self):

        remaining = ""
        while True:

            dataset = self.client_socket.recv(self.bufsize)
            try:
                # if isinstance(remaining, bytes):
                #     raise UnicodeDecodeError
                dataset = dataset.decode('utf-8')
            except UnicodeDecodeError:

                if not isinstance(remaining, bytes):

                    remaining = remaining.encode('utf-8')
                assert isinstance(dataset, bytes)
                remaining += dataset
                try:
                    response = remaining.decode('utf-8')
                    remaining = ""
                except:
                    continue
            assert isinstance(remaining, str)

            dataset = remaining + dataset
            if dataset == "<START>":
                break
            list_dataset = dataset.split("<SELFDEFINESEP>")
            if len(list_dataset) == 1:

                remaining = list_dataset[0]

                continue
            else:

                remaining = list_dataset[-1]

            list_dataset = list_dataset[:-1]
            print(list_dataset)
            for data in list_dataset:
                data = eval(data)
                if isinstance(data, dict):
                    Client.cache.update(data)
                else:
                    assert False

class MyAgent(Agent):
    API_KEY: str = os.environ["API_KEY"]
    WAIT_TIME: int = 20
    DEFAULT_MODEL: int = "gpt-3.5-turbo-16k-0613"
    TEMPERATURE: int = 0.3
    SIMULATION: bool = False
    __REDUCE_MODE__: list = ["cut", "summary"]

    def __init__(
            self,
            name: str,
            SYSTEM_PROMPT: str,
            query: str
    ):
        self.name = name
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        self.messages: list = list()
        self.messages.append(
            {"role": "system", "content": self.SYSTEM_PROMPT}
        )
        self.messages_copy: list = copy.deepcopy(self.messages)
        self.query = query

        self.summary_pointer = 1
        litellm.api_key = MyAgent.API_KEY



    def send_message(self, recorder=None, mode="cut", stream=True):
        # print("sending...")
        assert self.messages[-1]["role"] in ["user", "system"], \
            "please make sure the last role is user or system!"
        while True:
            try:
                # copy_message = copy.deepcopy(self.messages)
                # print(self.messages)
                if not MyAgent.SIMULATION:
                    completion = litellm.completion(
                        model=MyAgent.DEFAULT_MODEL,
                        messages=self.messages,
                        temperature=MyAgent.TEMPERATURE,
                        stream=stream
                    )
                else:
                    completion = simulation()
                if not stream:
                    if completion["choices"][0]["finish_reason"] == "length":

                        print("Length exceeded, deleted")
                        self.reduce_message(mode=mode, N=2)
                        continue
                    self.messages.append(
                        self._parse_response(completion)
                    )
                    self.messages_copy.append(
                        copy.deepcopy(self.messages[-1])
                    )
                else:

                    complete_response = ""
                    for chunk in completion:
                        # print(chunk)
                        if "content" in chunk["choices"][0]["delta"]:
                            complete_response = f"""{complete_response}{chunk["choices"][0]["delta"]["content"]}"""
                            yield chunk["choices"][0]["delta"]["content"]
                    yield None
                    self.messages.append(
                        self._parse_response(complete_response)
                    )
                    self.messages_copy.append(
                        copy.deepcopy(self.messages[-1])
                    )
                if recorder is not None:
                    recorder.add(
                        agent_name=self.name,
                        new_message_index=len(self.messages) - 1
                    )
                break
            except Exception as e:
                raise e
                print_log(e)
                if "maximum context length is" in str(e):
                    print_log("maximum length exceeded! skip!")
                    self.reduce_message(mode=mode, N=2)
                else:
                    print_log(f"Please wait {MyAgent.WAIT_TIME} seconds and resend later ...")
                    time.sleep(MyAgent.WAIT_TIME)



    def prepare_message(self, message):
        if isinstance(message, str):
            self.messages.append(
                {"role": "user", "content": message}
            )
            self.messages_copy.append(
                {"role": "user", "content": message}
            )
        elif isinstance(message, list):
            self.messages.extend(message)
            self.messages_copy.extend(message)
        else:
            assert False

    def _parse_response(self, completion, check_name: bool = True) -> dict:
        if isinstance(completion, dict):
            js = completion["choices"][0]["message"]
        elif isinstance(completion, str):
            js = {"content": completion, "role": "assistant"}
        else:
            assert False, \
                "invalid completion."
        if check_name:
            js["content"] = js["content"].replace(f"<{self.name}>", "").replace(f"</{self.name}>", "")
        return {"role": js["role"], "content": js["content"]}



    def get_message(self, index: int, function=None, source: str = "copy", **kwargs) -> str:
        assert source in ["copy", "origin"]
        assert len(self.messages) > index
        if function:
            if source == "copy":
                return function(self.messages_copy[index]["content"], kwargs)
            elif source == "origin":
                return function(self.messages[index]["content"], kwargs)
        else:
            if source == "copy":
                return self.messages_copy[index]["content"]
            elif source == "origin":
                return self.messages[index]["content"]



    def reduce_message(self, mode: str = "cut", N: int = 1, summary_agent=None):
        assert mode in MyAgent.__REDUCE_MODE__, \
            f"mode `{mode}` is invalid."
        if mode == "cut":

            """system | user | assistant | user | assistant"""
            for i in range(N):
                self.messages.pop(1)
            assert self.messages[-1]["role"] in ["user", "system"], \
                "please make sure the last role is user or system!"
        elif mode == "summary":
            assert isinstance(summary_agent, MyAgent), \
                "the summary agent is not class MyAgent."

            # summary_agent.prepare_message()



    def output_message(self, recorder=None, mode="cut", stream=True, output_func=None, node_name:str=None):
        if stream:
            print(f"【{self.name}】 ", end="")
            complete_response = ""
            FIRST = True
            for chunk in self.send_message(recorder=recorder, stream=stream, mode=mode):
                if chunk is not None:
                    complete_response = f"{complete_response}{chunk}"
                    if output_func is None:
                        print(chunk, end="")
                    else:
                        # print(chunk, end="")
                        if FIRST:
                            output_func(0, self.name, chunk, node_name)
                            FIRST = False
                        else:
                            output_func(1, self.name, chunk, node_name)
                        # yield complete_response, self.name
        else:
            next(self.send_message(recorder=recorder, stream=stream, mode=mode), None)
            if output_func is None:
                print(f"【{self.name}】{self.get_message(index=-1)}")
            else:
                output_func(None, self.name, self.get_message(index=-1), node_name)

class Recorder:
    def __init__(self, agents: Dict[str, MyAgent]):

        self.recorder: List = list()
        self.__AGENTS_NAME__ = []
        # 记录一下每个AGENT上次说话的时间，这样就不用一次一次的遍历了
        self.__AGENTS_SPEAK_TIME__ = {}
        self.agents: Dict[str, MyAgent] = agents
        self._register()



    def _register(self):
        for agent_name in self.agents:
            self.__AGENTS_NAME__.append(agent_name)
            self.__AGENTS_SPEAK_TIME__[agent_name] = 0

    def add(self, agent_name: str, new_message_index: int):
        self.recorder.append(
            [agent_name, new_message_index]
        )
        if agent_name not in self.__AGENTS_NAME__:
            self.__AGENTS_NAME__.append(agent_name)
        self.__AGENTS_SPEAK_TIME__[agent_name] = len(self.recorder)

    def clear(self):
        self.recorder.clear()



    def prepare(self, agent_name: str, agents: Dict[str, MyAgent], return_dict: bool = False):
        if agent_name.lower() != "all":
            assert agent_name in self.__AGENTS_NAME__, \
                f"There is no `MyAgent {agent_name}` in Recorder!"

        history = ""
        history_dict = []
        start_index = self.__AGENTS_SPEAK_TIME__[agent_name] if agent_name.lower() != "all" else 0
        for i in range(
                start_index, len(self.recorder)
        ):
            his_ag_name, his_ag_index = self.recorder[i]
            history_dict.append(
                {"role": "user", "content": agents[his_ag_name].get_message(his_ag_index, source="copy")}
            )
            history = f"{history}\n<{his_ag_name.upper()}>\n{agents[his_ag_name].get_message(his_ag_index, source='copy')}\n</{his_ag_name.upper()}>\n"
            # history = f"{history}\n{agent_name}: {agents[his_ag_name].get_message(his_ag_index, source='copy')}\n"
        if return_dict:
            return history_dict
        else:
            return history.strip()

class Node(State):

    def __init__(
            self,
            agents: List[MyAgent],
            summary_agent: MyAgent = None,
            save: bool = False
    ):
        self.agents = {}
        for agent in agents:
            self.agents[agent.name] = agent

        self.summary_agent: MyAgent = summary_agent
        self.recorder = Recorder(agents=self.agents)
        self.save = save

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def communicate(self):
        raise NotImplementedError

    @abc.abstractmethod
    def end(self):
        raise NotImplementedError()

    def run(self):
        self.start()
        self.communicate()
        response = self.end()
        if self.save:
            self.save_history()
        return response

    def save_history(self, save_path=None):
        if save_path is None:
            save_path = f"./Node2.json"
        results = []
        for agent_name in self.agents:
            results.append(
                self.agents[agent_name].messages_copy
            )
        json.dump(
            results,
            open(save_path, "w")
        )

def ask_gpt(system_prompt="", input="", name="parser"):

    temperature = MyAgent.TEMPERATURE
    MyAgent.TEMPERATURE = 0
    agent = MyAgent(
        name=name, SYSTEM_PROMPT=system_prompt, query=""
    )
    agent.prepare_message(message=input)
    # agent.temp_send_message()
    agent.output_message(stream=False)
    MyAgent.TEMPERATURE = temperature
    return agent.get_message(index=-1)

