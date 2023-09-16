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

# Emoji comes from this website:
# https://emojipedia.org/
import subprocess
from gradio_config import GradioConfig as gc
import gradio as gr
from typing import List, Tuple, Any
import time
import socket
import psutil
import os
from abc import abstractmethod

def convert2list4agentname(sop):
    """
    Extract the agent names of all states
    return:
        only name: [name1, name2, ...]
        agent_name: [name1(role1), name2(role2), ...]
    """
    only_name = []  
    agent_name = [] 
    roles_to_names = sop.roles_to_names
    for state_name,roles_names in roles_to_names.items():
        for role,name in roles_names.items():
            agent_name.append(f"{name}({role})")
            only_name.append(name)
    agent_name = list(set(agent_name))
    agent_name.sort()
    return agent_name, only_name

def is_port_in_use(port):
    """Check if the port is available"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True
    return False

def check_port(port):
    """Determine available ports"""
    if os.path.isfile("PORT.txt"):
        port = int(open("PORT.txt","r",encoding='utf-8').readlines()[0])
    else:
        for i in range(10):
            if is_port_in_use(port+i) == False:
                port += i
                break
        with open("PORT.txt", "w") as f:
            f.writelines(str(port))
    return port

# Determine some heads
SPECIAL_SIGN = {
    "START": "<START>",
    "SPLIT": "<SELFDEFINESEP>",
    "END": "<ENDSEP>"
}
HOST = "127.0.0.1"
# The starting port number for the search.
PORT = 15000                
PORT = check_port(PORT)
    
def print_log(message:str):
    print(f"[{time.ctime()}]{message}")

global_dialog = {
    "user": [],
    "agent": {},
    "system": []
}

class UIHelper:
    """Static Class"""

    @classmethod
    def wrap_css(cls, content, name) -> str:
        """
        Description:
            Wrap CSS around each output, and return it in HTML format for rendering with Markdown.
        Input:
            content: Output content 
            name: Whose output is it
        Output:
            HTML
        """
        assert name in gc.OBJECT_INFO, \
            f"The current name `{name}` is not registered with an image. The names of the currently registered agents are in `{gc.OBJECT_INFO.keys()}`. Please use `GradioConfig.add_agent()` from `Gradio_Config/gradio_config.py` to bind the name of the new agent."
        output = ""
        info = gc.OBJECT_INFO[name]
        if info["id"] == "USER":
            output = gc.BUBBLE_CSS["USER"].format(
                info["bubble_color"],                   # Background-color
                info["text_color"],                     # Color of the agent's name 
                name,                                   # Agent name
                info["text_color"],                     # Font color
                info["font_size"],                      # Font size
                content,                                # Content
                info["head_url"]                        # URL of the avatar
            )
        elif info["id"] == "SYSTEM":
            output = gc.BUBBLE_CSS["SYSTEM"].format(
                info["bubble_color"],                   # Background-color
                info["font_size"],                      # Font size
                info["text_color"],                     # Font color
                name,                                   # Agent name
                content                                 # Content
            )
        elif info["id"] == "AGENT":
            output = gc.BUBBLE_CSS["AGENT"].format(
                info["head_url"],                       # URL of the avatar
                info["bubble_color"],                   # Background-color
                info["text_color"],                     # Font color
                name,                                   # Agent name
                info["text_color"],                     # Font color
                info["font_size"],                      # Font size
                content,                                # Content
            )
        else:
            assert False, f"Id `{info['id']}` is invalid. The valid id is in ['SYSTEM', 'AGENT', 'USER']"
        return output

    @classmethod
    def novel_filter(cls, content, agent_name):
        
        """比如<CONTENT>...</CONTENT>，就应该输出CONTENT:..."""
        IS_RECORDER = agent_name.lower() in ["recorder", "summary"]
        if IS_RECORDER:
            BOLD_FORMAT = """<div style="color: #000000; display:inline">
    <b>{}</b>
</div>
<span style="color: black;">
"""
        else:
            BOLD_FORMAT = "<b>{}</b>"
        CENTER_FORMAT = """<div style="background-color: #F0F0F0; text-align: center; padding: 5px; color: #000000">
    <b>{}</b>
</div>
"""
        START_FORMAT = "<{}>"
        END_FORMAT = "</{}>"
        mapping = {
            "TARGET": "🎯 Current Target: ",
            "NUMBER": "🍖 Required Number: ",
            "THOUGHT": "🤔 Overall Thought: ",
            "FIRST NAME": "⚪ First Name: ",
            "LAST NAME": "⚪ Last Name: ",
            "ROLE": "🤠 Character Properties: ",
            "RATIONALES": "🤔 Design Rationale: ",
            "BACKGROUND": "🚊 Character Background: ",
            "ID": "🔴 ID: ",
            "TITLE": "🧩 Chapter Title: ",
            "ABSTRACT": "🎬 Abstract: ",
            "CHARACTER INVOLVED": "☃️ Character Involved: ",
            "ADVICE": "💬 Advice:",
            "NAME": "📛 Name: ",
            "GENDER": "👩‍👩‍👦‍👦 Gender: ",
            "AGE": "⏲️ Age: ",
            "WORK": "👨‍🔧 Work: ",
            "PERSONALITY": "🧲 Character Personality: ",
            "SPEECH STYLE": "🗣️ Speaking Style: ",
            "RELATION": "🏠 Relation with Others: ",
            "WORD COUNT": "🎰 Word Count: ",
            "CHARACTER DESIGN": "📈 Character Design: ",
            "CHARACTER REQUIRE": "📈 Character Require: ",
            "CHARACTER NAME": "📈 Character Naming Analysis: ",
            "CHARACTER NOW": "📈 Character Now: ",
            "OUTLINE DESIGN": "📈 Outline Design: ",
            "OUTLINE REQUIRE": "📈 Outline Require: ",
            "OUTLINE NOW": "📈 Outline Now: ",
            "SUB TASK": "🎯 Current Sub Task: ",
            "CHARACTER ADVICE": "💬 Character Design Advice: ",
            "OUTLINE ADVANTAGE": "📈 Outline Advantage: ",
            "OUTLINE DISADVANTAGE": "📈 Outline Disadvantage: ",
            "OUTLINE ADVICE": "💬 Outline Advice: ",
            "NEXT": "➡️ Next Advice: ",
            "TOTAL NUMBER": "🔢 Total Number: "
        }
        for i in range(1, 10):
            mapping[f"CHARACTER {i}"] = f"🦄 Character {i}"
            mapping[f"SECTION {i}"] = f"🏷️ Chapter {i}"
        for key in mapping:
            if key in [f"CHARACTER {i}" for i in range(1, 10)] \
                    or key in [f"SECTION {i}" for i in range(1, 10)] \
                    :
                content = content.replace(
                    START_FORMAT.format(key), CENTER_FORMAT.format(mapping[key])
                )
            elif key in ["TOTAL NUMBER"]:
                content = content.replace(
                    START_FORMAT.format(key), CENTER_FORMAT.format(mapping[key]) + """<span style="color: black;">"""
                )
                content = content.replace(
                    END_FORMAT.format(key), "</span>"
                )
            else:
                content = content.replace(
                    START_FORMAT.format(key), BOLD_FORMAT.format(mapping[key])
                )

            content = content.replace(
                END_FORMAT.format(key), "</span>" if IS_RECORDER else ""
            )
        return content
    
    @classmethod
    def singleagent_filter(cls, content, agent_name):
        return content
    
    @classmethod
    def debate_filter(cls, content, agent_name):
        return content
    
    @classmethod
    def code_filter(cls, content, agent_name):
        # return content.replace("```python", "<pre><code>").replace("```","</pre></code>")
        return content
    
    @classmethod
    def general_filter(cls, content, agent_name):
        return content
    
    @classmethod
    def filter(cls, content: str, agent_name: str, ui_name: str):
        """
        Description:
            Make certain modifications to the output content to enhance its aesthetics when content is showed in gradio.
        Input:
            content: output content
            agent_name: Whose output is it
            ui_name: What UI is currently launching
        Output:
            Modified content
        """
        mapping = {
            "SingleAgentUI": cls.singleagent_filter,
            "DebateUI": cls.debate_filter,
            "NovelUI": cls.novel_filter,
            "CodeUI": cls.code_filter,
            "GeneralUI": cls.general_filter
        }
        if ui_name in mapping:
            return mapping[ui_name](content, agent_name)
        else:
            return content

class Client:
    """
    For inter-process communication, this is the client. 
    `gradio_backend.PY` serves as the backend, while `run_gradio` is the frontend. 
    Communication between the frontend and backend is accomplished using Sockets.
    """
    # =======================Radio Const String======================
    SINGLE_MODE = "Single Mode"
    AUTO_MODE = "Auto Mode"
    MODE_LABEL = "Select the execution mode"
    MODE_INFO = "Single mode refers to when the current agent output ends, it will stop running until you click to continue. Auto mode refers to when you complete the input, all agents will continue to output until the task ends."
    # ===============================================================
    mode = AUTO_MODE
    FIRST_RUN:bool = True
    # if last agent is user, then next agent will be executed automatically rather than click button 
    LAST_USER:bool = False
    
    receive_server = None
    send_server = None
    current_node = None
    cache = {}

    def __init__(self, host=HOST, port=PORT, bufsize=1024):
        assert Client.mode in [Client.SINGLE_MODE, Client.AUTO_MODE]
        self.SIGN = SPECIAL_SIGN
        self.bufsize = bufsize
        assert bufsize > 0
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        while True:
            data = self.client_socket.recv(self.bufsize).decode('utf-8')
            if data == "hi":
                self.client_socket.send("hello agent".encode('utf-8'))
                time.sleep(1)
            elif data == "check":
                break
        print_log("Client: connecting successfully......")

    def start_server(self):
        while True:
            message = yield
            if message == 'exit':
                break
            self.send_message(message=message)

    def send_message(self, message):
        """Send the messaget to the server."""
        if isinstance(message, list) or isinstance(message, dict):
            message = str(message)
        assert isinstance(message, str)
        message = message + self.SIGN["SPLIT"]
        self.client_socket.send(message.encode('utf-8'))

    def receive_message(self, end_identifier: str = None, split_identifier: str = SPECIAL_SIGN["SPLIT"]) -> List:
        """Receive messages from the server, and it will block the process. Supports receiving long text."""
        remaining = ""
        while True:
            # receive message
            dataset = self.client_socket.recv(self.bufsize)
            try:
                # If decoding fails, it indicates that the current transmission is a long text.
                dataset = dataset.decode('utf-8')
            except UnicodeDecodeError:
                if not isinstance(remaining, bytes):
                    remaining = remaining.encode('utf-8')
                assert isinstance(dataset, bytes)
                remaining += dataset
                try:
                    dataset = remaining.decode('utf-8')
                    remaining = ""
                except UnicodeDecodeError:
                    continue
            assert isinstance(remaining, str)
            dataset = remaining + dataset
            list_dataset = dataset.split(split_identifier)
            if len(list_dataset) == 1:
                # If there is only one result from the split, it indicates that the current sequence itself has not yet ended.
                remaining = list_dataset[0]
                continue
            else:
                remaining = list_dataset[-1]
            # Recieve successfully
            list_dataset = list_dataset[:-1]
            return_value = []
            for item in list_dataset:
                if end_identifier is not None and item == end_identifier:
                    break
                return_value.append(item)
            identifier = yield return_value
            if identifier is not None:
                end_identifier, split_identifier = identifier

    def listening_for_start_(self):
        """
        When the server starts, the client is automatically launched. 
        At this point, process synchronization is required, 
        such as sending client data to the server for rendering, 
        then the server sending the modified data back to the client, 
        and simultaneously sending a startup command. 
        Once the client receives the data, it will start running.
        """
        Client.receive_server = self.receive_message()
        # Waiting for information from the server.
        data: list = next(Client.receive_server)
        assert len(data) == 1
        data = eval(data[0])
        assert isinstance(data, dict)
        Client.cache.update(data)
        # Waiting for start command from the server.
        data:list = Client.receive_server.send(None)
        assert len(data) == 1
        assert data[0] == "<START>"

class WebUI:
    """
    The base class for the frontend, which encapsulates some functions for process information synchronization. 
    When a new frontend needs to be created, you should inherit from this class, 
    then implement the `construct_ui()` method and set up event listeners. 
    Finally, execute `run()` to load it.
    """
    
    def receive_message(
        self,
        end_identifier:str=None,
        split_identifier:str=SPECIAL_SIGN["SPLIT"]
    )->List:
        """This is the same as in Client class."""
        yield "hello"
        remaining = ""
        while True:
            dataset = self.client_socket.recv(self.bufsize)
            try:
                dataset = dataset.decode('utf-8')
            except UnicodeDecodeError:
                if not isinstance(remaining, bytes):
                    remaining = remaining.encode('utf-8')
                assert isinstance(dataset, bytes)
                remaining += dataset
                try:
                    dataset = remaining.decode('utf-8')
                    remaining = ""
                except UnicodeDecodeError:
                    continue
            assert isinstance(remaining, str)
            dataset = remaining + dataset
            list_dataset = dataset.split(split_identifier)
            if len(list_dataset) == 1:
                remaining = list_dataset[0]
                continue
            else:
                remaining = list_dataset[-1]
            list_dataset = list_dataset[:-1]
            return_value = []
            for item in list_dataset:
                if end_identifier is not None and item == end_identifier:
                    break
                return_value.append(item)
            identifier = yield return_value
            if identifier is not None:
                end_identifier, split_identifier = identifier

    def send_message(self, message:str):
        """Send message to client."""
        SEP = self.SIGN["SPLIT"]
        self.client_socket.send(
            (message+SEP).encode("utf-8")
        )
    
    def _connect(self):
        # check 
        if self.server_socket:
            self.server_socket.close()
            assert not os.path.isfile("PORT.txt")
            self.socket_port = check_port(PORT)
        # Step1. initialize
        self.server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        # Step2. binding ip and port
        self.server_socket.bind((self.socket_host, self.socket_port))
        # Step3. run client
        self._start_client()

        # Step4. listening for connect
        self.server_socket.listen(1)

        # Step5. test connection
        client_socket, client_address = self.server_socket.accept()
        print_log("server: establishing connection......")
        self.client_socket = client_socket
        while True:
            client_socket.send("hi".encode('utf-8'))
            time.sleep(1)
            data = client_socket.recv(self.bufsize).decode('utf-8')
            if data == "hello agent":
                client_socket.send("check".encode('utf-8'))
                print_log("server: connect successfully")
                break
        assert os.path.isfile("PORT.txt")
        os.remove("PORT.txt")
        if self.receive_server:
            del self.receive_server
        self.receive_server = self.receive_message()
        assert next(self.receive_server) == "hello"
    
    @abstractmethod
    def render_and_register_ui(self):
        # You need to implement this function. 
        # The function's purpose is to bind the name of the agent with an image. 
        # The name of the agent is stored in `self.cache[]`, 
        # and the function for binding is in the method `add_agents` of the class `GradioConfig` in `Gradio_Config/gradio_config.py``.
        # This function will be executed in `self.first_recieve_from_client()`
        pass
    
    def first_recieve_from_client(self, reset_mode:bool=False):
        """
        This function is used to receive information from the client and is typically executed during the initialization of the class.
        If `reset_mode` is False, it will bind the name of the agent with an image.
        """
        self.FIRST_RECIEVE_FROM_CLIENT = True
        data_list:List = self.receive_server.send(None)
        assert len(data_list) == 1
        data = eval(data_list[0])
        assert isinstance(data, dict)
        self.cache.update(data)
        if not reset_mode:
            self.render_and_register_ui()
    
    def _second_send(self, message:dict):
        # Send the modified message.
        # It will be executed in `self.send_start_cmd()` automtically.
        self.send_message(str(message))
    
    def _third_send(self):
        # Send start command.
        # It will be executed in `self.send_start_cmd()` automtically.
        self.send_message(self.SIGN['START'])
    
    def send_start_cmd(self, message:dict={"hello":"hello"}):
        # If you have no message to send, you can ignore the args `message`.
        assert self.FIRST_RECIEVE_FROM_CLIENT, "Please make sure you have executed `self.first_recieve_from_client()` manually."
        self._second_send(message=message)
        time.sleep(1)
        self._third_send()
        self.FIRST_RECIEVE_FROM_CLIENT = False
    
    def __init__(
        self,
        client_cmd: list,           # ['python','test.py','--a','b','--c','d']
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024,
        ui_name: str = ""
    ):
        self.ui_name = ui_name
        self.server_socket = None
        self.SIGN = SPECIAL_SIGN
        self.socket_host = socket_host
        self.socket_port = socket_port
        self.bufsize = bufsize
        self.client_cmd = client_cmd
        
        self.receive_server = None
        self.cache = {}
        assert self.bufsize > 0
        self._connect()

    def _start_client(self):
        print(f"server: excuting `{' '.join(self.client_cmd)}` ...")
        self.backend = subprocess.Popen(self.client_cmd)
        
    def _close_client(self):
        print(f"server: killing `{' '.join(self.client_cmd)}` ...")
        self.backend.terminate()
    
    def reset(self):
        print("server: restarting ...")
        self._close_client()
        time.sleep(1)
        self._connect()

    def render_bubble(self, rendered_data, agent_response, node_name, render_node_name:bool=True):
        # Rendered bubbles (HTML format) are used for gradio output.
        output = f"**{node_name}**<br>" if render_node_name else ""
        for item in agent_response:
            for agent_name in item:
                content = item[agent_name].replace("\n", "<br>")
                content = UIHelper.filter(content, agent_name, self.ui_name)
                output = f"{output}<br>{UIHelper.wrap_css(content, agent_name)}"
        rendered_data[-1] = [rendered_data[-1][0], output]
        return rendered_data

    def run(self,share: bool = True):
        self.demo.queue()
        self.demo.launch(share=share)


if __name__ == '__main__':
    pass
