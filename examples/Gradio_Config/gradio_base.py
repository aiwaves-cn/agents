"""https://emojipedia.org/zh/%E6%83%B3%E4%B8%80%E6%83%B3"""
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
    """把agentname搞成list ['1', '2']"""
    """每个元素是名字+扮演的角色，比如是一辩二辩"""
    """就遍历一下就行"""
    only_name = []      # 只有name
    agent_name = []     # 前端渲染
    roles_to_names = sop.roles_to_names
    for state_name,roles_names in roles_to_names.items():
        for role,name in roles_names.items():
            agent_name.append(f"{name}({role})")
            only_name.append(name)
    agent_name = list(set(agent_name))
    agent_name.sort()
    return agent_name, only_name

def is_port_in_use(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True
    return False

def check_port(port):
    if os.path.isfile("PORT.txt"):
        port = int(open("PORT.txt","r",encoding='utf-8').readlines()[0])
        print(port)
    else:
        for i in range(10):
            if is_port_in_use(port+i) == False:
                port += i
                break
        with open("PORT.txt", "w") as f:
            f.writelines(str(port))
        print(port)
    return port

SPECIAL_SIGN = {
    # 双方约定正式开始运行的符号
    "START": "<START>",
    # 双方约定每个消息的分隔符，这个主要是对渲染气泡的时候来说的
    "SPLIT": "<SELFDEFINESEP>",
    # 双方约定每种类型消息的结束符，也可以为空吧
    "END": "<ENDSEP>"
}
HOST = "127.0.0.1"

PORT = 6289
PORT = check_port(PORT)
    
def print_log(message:str):
    print(f"[{time.ctime()}]{message}")

"""全局的对话，只用于回答"""
global_dialog = {
    "user": [],
    "agent": {

    },
    "system": []
}

class UIHelper:
    """静态类"""

    @classmethod
    def init(cls):
        first_node_agents_name, cnt = gc.init_zjt(gc.NOVEL_PROMPT, cnt=0)
        return first_node_agents_name

    """为每个输出弄一个css，返回的是HTML格式，目的是交给markdown渲染"""
    @classmethod
    def wrap_css(cls, content, name) -> str:
        """content: 输出的内容 name: 谁的输出"""
        """确保name这个人是存在的"""
        assert name in gc.OBJECT_INFO, f"'{name}' not in {gc.OBJECT_INFO.keys()}"
        """取出这个人的全部信息"""
        output = ""
        info = gc.OBJECT_INFO[name]
        if info["id"] == "USER":
            # 背景颜色 名字颜色 名字 字体颜色 字体大小 内容 图片地址
            output = gc.BUBBLE_CSS["USER"].format(
                info["bubble_color"],
                info["text_color"],
                name,
                info["text_color"],
                info["font_size"],
                content,
                info["head_url"]
            )
        elif info["id"] == "SYSTEM":
            # 背景颜色 字体大小 字体颜色 名字 内容
            output = gc.BUBBLE_CSS["SYSTEM"].format(
                info["bubble_color"],
                info["font_size"],
                info["text_color"],
                name,
                content
            )
        elif info["id"] == "AGENT":
            # 图片地址 背景颜色 名字颜色 名字 字体颜色 字体大小 内容
            output = gc.BUBBLE_CSS["AGENT"].format(
                info["head_url"],
                info["bubble_color"],
                info["text_color"],
                name,
                info["text_color"],
                info["font_size"],
                content,
            )
        else:
            assert False
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
            "TARGET": "🎯 当前的目标: ",
            "NUMBER": "🍖 要求的数量: ",
            "THOUGHT": "🤔 总体构思: ",
            "FIRST NAME": "⚪ 姓: ",
            "LAST NAME": "⚪ 名: ",
            "ROLE": "角色属性: ",
            "RATIONALES": "🤔 设计理由: ",
            "BACKGROUND": "🚊 人物背景: ",
            "ID": "🔴 编号: ",
            "TITLE": "🧩 章节标题: ",
            "ABSTRACT": "🎬 摘要: ",
            "CHARACTER INVOLVED": "☃️ 参与的角色: ",
            "ADVICE": "💬 建议:",
            "NAME": "📛 姓名: ",
            "GENDER": "👩‍👩‍👦‍👦 性别: ",
            "AGE": "⏲️ 年龄: ",
            "WORK": "👨‍🔧 工作: ",
            "CHARACTER": "🧲 人物性格: ",
            "SPEECH STYLE": "🗣️ 讲话风格: ",
            "RELATION": "🏠 与其他角色的关系: ",
            "WORD COUNT": "🎰 字数: ",
            "CHARACTER DESIGN": "📈 角色设计情况: ",
            "CHARACTER REQUIRE": "📈 角色设计要求: ",
            "CHARACTER NAME": "📈 角色命名分析: ",
            "CHARACTER NOW": "📈 目前角色现状: ",
            "OUTLINE DESIGN": "📈 大纲设计情况: ",
            "OUTLINE REQUIRE": "📈 大纲设计要求: ",
            "OUTLINE NOW": "📈 大纲设计现状: ",
            "SUB TASK": "🎯 当前任务: ",
            "CHARACTER ADVICE": "💬 角色设计建议: ",
            "OUTLINE ADVANTAGE": "📈 大纲优点: ",
            "OUTLINE DISADVANTAGE": "📈 大纲缺点: ",
            "OUTLINE ADVICE": "💬 大纲建议: ",
            "NEXT": "➡️下一步建议: ",
            "TOTAL NUMBER": "🔢 总数: "
        }
        for i in range(1, 10):
            mapping[f"CHARACTER {i}"] = f"🦄 角色{i}"
            mapping[f"SECTION {i}"] = f"🏷️ 章节{i}"
        for key in mapping:
            if key in [f"CHARACTER {i}" for i in range(1, 10)] \
                    or key in [f"SECTION {i}" for i in range(1, 10)] \
                    :
                content = content.replace(
                    START_FORMAT.format(key), CENTER_FORMAT.format(mapping[key])
                )
            elif key in ["TOTAL NUMBER"]:
                # 颜色问题，所以得用这种强制转换成黑色
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
        # pass
        return content
    
    @classmethod
    def code_filter(cls, content, agent_name):
        # return content.replace("```python", "<pre><code>").replace("```","</pre></code>")
        return content
    
    @classmethod
    def filter(cls, content: str, agent_name: str, ui_name: str):
        mapping = {
            "SingleAgentUI": cls.singleagent_filter,
            "DebateUI": cls.debate_filter,
            "NovelUI": cls.novel_filter,
            "CodeUI": cls.code_filter
        }
        return mapping[ui_name](content, agent_name)

class Client:

    receive_server = None
    send_server = None
    current_node = None
    cache = {}

    def __init__(self, host=HOST, port=PORT, bufsize=1024):
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
        print_log("client: 连接成功......")

    def start_server(self):
        while True:
            message = yield
            if message == 'exit':
                break
            # self.client_socket.send(message.encode('utf-8'))
            self.send_message(message=message)

    def send_message(self, message):
        if isinstance(message, list) or isinstance(message, dict):
            message = str(message)
        assert isinstance(message, str)
        message = message + self.SIGN["SPLIT"]
        self.client_socket.send(message.encode('utf-8'))

    def receive_message(self, end_identifier: str = None, split_identifier: str = SPECIAL_SIGN["SPLIT"]) -> List:
        """接收消息，直到收到了结束符，会阻塞"""
        remaining = ""
        while True:
            """接收消息"""
            dataset = self.client_socket.recv(self.bufsize)
            try:
                """每次如果解码成功，则进行split，否则直接读下一个"""
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
            """按照分隔符进行分割"""
            list_dataset = dataset.split(split_identifier)
            if len(list_dataset) == 1:
                """只分了一个，说明当前这个序列本身就还是没有结束"""
                remaining = list_dataset[0]
                continue
            else:
                """如果分了多个，则最后一个设为remaining"""
                remaining = list_dataset[-1]
            """成功分割，则不取最后一个，对于正常的来说，为空，不正常的在remain中"""
            list_dataset = list_dataset[:-1]
            """接收到的消息都在list_dataset里面"""
            return_value = []
            for item in list_dataset:
                if end_identifier is not None and item == end_identifier:
                    break
                return_value.append(item)
            identifier = yield return_value
            if identifier is not None:
                end_identifier, split_identifier = identifier

    def listening_for_start_(self):
        """接受两次消息，一次是前端渲染好的，另外一次是启动命令"""
        print("client:", self.client_socket)
        Client.receive_server = self.receive_message()
        """第一次消息"""
        data: list = next(Client.receive_server)
        print("listen-1:", data)
        assert len(data) == 1
        data = eval(data[0])
        assert isinstance(data, dict)
        Client.cache.update(data)
        """第二次消息"""
        data:list = Client.receive_server.send(None)
        assert len(data) == 1
        assert data[0] == "<START>"

class WebUI:
    
    def receive_message(
        self,
        end_identifier:str=None,
        split_identifier:str=SPECIAL_SIGN["SPLIT"]
    )->List:
        """接收消息，直到收到了结束符，会阻塞"""
        yield "hello"
        remaining = ""
        while True:
            """接收消息"""
            dataset = self.client_socket.recv(self.bufsize)
            try:
                """每次如果解码成功，则进行split，否则直接读下一个"""
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
            # print("mike-org:", dataset)
            """按照分隔符进行分割"""
            # print("mike-split:", split_identifier)
            list_dataset = dataset.split(split_identifier)
            # print("mike:", list_dataset, len(list_dataset))
            if len(list_dataset) == 1:
                """只分了一个，说明当前这个序列本身就还是没有结束"""
                remaining = list_dataset[0]
                continue
            else:
                """如果分了多个，则最后一个设为remaining"""
                remaining = list_dataset[-1]
            """成功分割，则不取最后一个，对于正常的来说，为空，不正常的在remain中"""
            list_dataset = list_dataset[:-1]
            # print("mike-return:", list_dataset)
            """接收到的消息都在list_dataset里面"""
            return_value = []
            for item in list_dataset:
                if end_identifier is not None and item == end_identifier:
                    break
                return_value.append(item)
            identifier = yield return_value
            if identifier is not None:
                end_identifier, split_identifier = identifier

    def send_message(self, message:str):
        """将数据发送到后端"""
        """需要实现约定好格式"""
        print(f"server:发送`{message}`")
        SEP = self.SIGN["SPLIT"]
        self.client_socket.send(
            (message+SEP).encode("utf-8")
        )
    
    """
    建立连接后：
        1. 先client发送数据到server
        2. server接受数据进行展示
        3. server发送数据到client
        4. client接受数据并覆盖 
        5. server发送开始运行的命令
        6. client正式开始
        
            client  server
        1.   send    rec
        2.   rec     send
        3.   rec     send
    """ 
    def _connect(self):
        """socket启动"""
        # Step0. 先判断一下是否已经有了
        if self.server_socket:
            """如果有了，那就说明是重启的，可能需要重新商议一下通信的端口号"""
            self.server_socket.close()
            assert not os.path.isfile("PORT.txt")
            self.socket_port = check_port(PORT)
        # Step1. 初始化
        self.server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        # Step2. 绑定IP和端口
        print((self.socket_host, self.socket_port))
        self.server_socket.bind((self.socket_host, self.socket_port))
        # Step3. 启动客户端
        print_log("server: 正在启动客户端......")
        # 记录一下后端的进程用于重启
        # self.backend = subprocess.Popen(["python", client_server_file])
        self._start_client()

        # Step4. 监听并阻塞当前进程
        print_log("server: 等待客户端连接......")
        self.server_socket.listen(1)

        # Step5. 测试连接
        client_socket, client_address = self.server_socket.accept()
        print_log("server: 正在建立连接......")
        self.client_socket = client_socket
        while True:
            client_socket.send("hi".encode('utf-8'))
            time.sleep(1)
            data = client_socket.recv(self.bufsize).decode('utf-8')
            if data == "hello agent":
                client_socket.send("check".encode('utf-8'))
                print_log("server:连接成功")
                break
        assert os.path.isfile("PORT.txt")
        os.remove("PORT.txt")
        if self.receive_server:
            del self.receive_server
        self.receive_server = self.receive_message()
        assert next(self.receive_server) == "hello"
    
    @abstractmethod
    def render_and_register_ui(self):
        """渲染ui并注册"""
        pass
    
    def first_recieve_from_client(self, reset_mode:bool=False):
        """1. 接受client发送的消息，进行渲染，同时需要注册"""
        """一般放在构造的时候"""
        self.FIRST_RECIEVE_FROM_CLIENT = True
        data_list:List = self.receive_server.send(None)
        assert len(data_list) == 1
        data = eval(data_list[0])
        assert isinstance(data, dict)
        self.cache.update(data)
        if not reset_mode:
            self.render_and_register_ui()
    
    def _second_send(self, message:dict):
        """2. 发送消息，主要是将值覆盖"""
        self.send_message(str(message))
    
    def _third_send(self):
        """3. 发送开始消息，主要是驱动"""
        self.send_message(self.SIGN['START'])
    
    def send_start_cmd(self, message:dict={"hello":"hello"}):
        """运行之前请确保first_receive_from_client已经运行"""
        """将上面的全部串起来"""
        """此处的message就是前端搜集的，通过dict的方式进行发送"""
        assert self.FIRST_RECIEVE_FROM_CLIENT, "请先保证从client接受消息"
        self._second_send(message=message)
        time.sleep(1)
        self._third_send()
        self.FIRST_RECIEVE_FROM_CLIENT = False
    
    def __init__(
        self,
        # client_server_file: str,
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
        print("启动进程......")
        self.backend = subprocess.Popen(self.client_cmd)
        
    def _close_client(self):
        print("关闭进程......")
        self.backend.terminate()
    
    def reset(self):
        # Step 1. 关闭后端进程并重新启动
        self._close_client()
        time.sleep(1)
        self._connect()

    def render_bubble(self, rendered_data, agent_response, node_name, render_node_name:bool=True):
        # print("mike:", agent_response)
        print("mike-5")
        output = f"**{node_name}**<br>" if render_node_name else ""
        for item in agent_response:
            for agent_name in item:
                content = item[agent_name].replace("\n", "<br>")
                content = UIHelper.filter(content, agent_name, self.ui_name)
                output = f"{output}<br>{UIHelper.wrap_css(content, agent_name)}"
        rendered_data[-1] = [rendered_data[-1][0], output]
        return rendered_data

    """启动gradio"""
    def run(self,share: bool = True):
        self.demo.queue()
        self.demo.launch(share=share)


if __name__ == '__main__':
    """初始化"""
    # MyAgent.SIMULATION = False
    # MyAgent.TEMPERATURE = 0.3
    # agents_name_of_start_node = UIHelper.init()
    # # ui = WebUI(client_server_file="run_cmd.py")
    # ui = WebUI(client_server_file="simulate_cmd.py", bufsize=18)
    # ui.construct_ui(
    #     task_prompt="task_prompt",
    #     agents_name_of_start_node=agents_name_of_start_node,
    #     default_agent=agents_name_of_start_node[0],
    #     default_agent_question="default_agent_question"
    # )
    # ui.run(share=True)
    pass

    """
    todo:
        1. 结束、暂停、重新开始
        2. 对<>进行替换，也就是格式化
        3. 加入system
        4. gradio主题色更改
        5. 是否要加入文件读取
    """
