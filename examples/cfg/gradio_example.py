import copy
import os
from gradio_base import WebUI, UIHelper, PORT, HOST, Client
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr
import re
import time

class DebateUI(WebUI):
    """
    正是启动之前需要匹配参数，也就是
    """
    FORMAT = "{}\n<debate topic>\n{}\nAffirmative viewpoint:{}\nNegative viewpoint:{}\n<debate topic>{}"
    AUDIENCE = "不扮演(作为观众)"  # 路人的名字
    cache = {}
    all_agents_name = []
    receive_server = None

    @classmethod
    def extract(cls, content):
        # pattern = re.compile(
        #     cls.FORMAT.format("(.+?)", "(.+?)", "(.+?)", "(.+?)", "(.+)")
        # )
        # match = pattern.search(content)
        # return match.group(2), match.group(3), match.group(4)
        topic = content.split("<debate topic>")[1].split("Affirmative viewpoint:")[0]
        positive = content.split("<debate topic>")[1].split("Affirmative viewpoint:")[1].split("negative viewpoint:")[0]
        negative = content.split("<debate topic>")[1].split("Affirmative viewpoint:")[1].split("negative viewpoint:")[1]
        return topic.strip(), positive.strip(), negative.strip()

    @classmethod
    def merge(cls, theme, positive, negative, origin_content) -> str:
        # pattern = re.compile(cls.FORMAT.format("(.+?)", "(.+?)", "(.+?)", "(.+?)", "(.+)"))
        # match = pattern.search(origin_content)
        # return cls.FORMAT.format(
        #     match.group(1), theme, positive, negative, match.group(5)
        # )
        return cls.FORMAT.format(
            origin_content.split("<debate topic>")[0],
            theme, positive, negative,
            origin_content.split("<debate topic>")[-1]
        )

    @classmethod
    def convert2list4agentname(cls, sop):
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
        agent_name.append(cls.AUDIENCE)
        agent_name = list(set(agent_name))
        return agent_name, only_name

    def render_and_register_ui(self):
        gc.add_agent(self.cache["only_name"])
    
    def __init__(
        self,
        client_cmd: list,
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024
    ):
        super(DebateUI, self).__init__(client_cmd, socket_host, socket_port, bufsize)
        # """初始化一下"""
        # self.receive_server = self.receive_message()
        # next(self.receive_server)
        # """接受一下sop的信息"""
        # data:List = self.receive_server.send(None)
        # print(data)
        # assert len(data) == 1
        # data = eval(data[0])
        # assert isinstance(data, dict)
        # self.cache.update(data)
        # """注册agent name"""
        # gc.add_agent(self.cache["only_name"])
        # self.data_history = None
        # self.FIRST = True
        self.first_recieve_from_client()
        self.data_history = list()

    """处理发送来的数据"""
    def handle_message(self, history:list,
            state, agent_name, token, node_name):
        # print("MIKE-history:",history)
        if state % 10 == 0:
            """这个还是在当前气泡里面的"""
            self.data_history.append({agent_name: token})
        elif state % 10 == 1:
            self.data_history[-1][agent_name] += token
        elif state % 10 == 2:
            """表示不是同一个气泡了"""
            history.append([None, ""])
            self.data_history.clear()
            self.data_history.append({agent_name: token})
        else:
            assert False
        # print("MIKE-data_history", self.data_history)
        render_data = self.render_bubble(history, self.data_history, node_name, render_node_name= state % 10 == 2)
        return render_data

    def start_button_when_click(self, theme, positive, negative, choose):
        """
        inputs=[self.text_theme, self.text_positive, self.text_negative, self.radio_choose],
        只要把chatbot显示出来就行
        outputs=[self.chatbot]
        """
        # 1. 向前端发送数据消息
        cosplay = None if choose == self.AUDIENCE else choose.split("(")[0]
        message = dict(theme=theme, positive=positive, negative=negative, cosplay=cosplay)
        # self.send_message(str(message)) # 自动加结束符
        # time.sleep(2)
        # # 2. 向前端发送开始运行的消息
        # self.send_message(self.SIGN["START"])   # 自动加结束符
        self.send_start_cmd(message=message)
        return gr.Chatbot.update(
            visible=True
        ), gr.Button.update(visible=False)

    def start_button_after_click(self, history):
        """
        inputs=[self.chatbot],
        outputs=[self.chatbot, self.text_user, self.btn_send]
        """
        # 这个是用于存放历史数据的，
        # if self.data_history is None:
        self.data_history = list()
        # 主要是开始渲染后端发来的消息
        # receive_server = self.receive_message()
        receive_server = self.receive_server
        while True:
            data_list: List = receive_server.send(None)
            print("收到:", data_list)
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = data
                assert isinstance(state, int)
                if state == 30:
                    """选择权交给用户，就是让用户进行交互"""
                    # 1. 设置interactive和visible
                    print("server:显示1")
                    yield history,\
                        gr.Textbox.update(visible=True, interactive=True), \
                        gr.Button.update(visible=True, interactive=True),\
                            gr.Button.update(visible=True, interactive=True)
                    return
                    # 2. 监听动作（一般来说，这个item应该就是data_list就是最后一个）
                    #    所以可以直接break，来监听下一个，让程序阻塞在这里
                    # print("server:显示2")
                    # break
                else:
                    history = self.handle_message(history, state, agent_name, token, node_name)
                    yield history, \
                          gr.Textbox.update(visible=False, interactive=False), \
                          gr.Button.update(visible=False, interactive=False),\
                              gr.Button.update(visible=False, interactive=False)

    def send_button_when_click(self, text_user, history:list):
        """点击这个按钮的目的是将内容渲染到前端"""
        """
        inputs=[self.text_user, self.chatbot],
        outputs=[self.text_user, self.btn_send, self.chatbot]
        """
        print(f"server1: {text_user}")
        history.append(
            [UIHelper.wrap_css(text_user, "User"), None]
        )
        """将文本的内容发送到后端"""
        print(f"server: 准备发送输入{text_user}")
        self.send_message("<USER>"+text_user+self.SIGN["SPLIT"])
        return gr.Textbox.update(value="", visible=False),\
              gr.Button.update(visible=False), \
                history,\
                    gr.Button.update(visible=False)

    def reset_button_when_click(self, history, text_positive, text_negative, text_theme, text_user, btn_send, btn_start, btn_reset):
        """当点击的时候"""
        """
        self.chatbot, 
        self.text_positive, 
        self.text_negative, 
        self.text_theme, 
        self.text_user,
        self.btn_send,
        self.btn_start,
        self.btn_reset"""
        return None, \
            "", \
                "", \
                    "", \
                        "", \
                            gr.Button.update(value="重启中...", interactive=False, visible=True),\
                                gr.Button.update(value="重启中...", interactive=False, visible=True),\
                                    gr.Button.update(value="重启中...", interactive=False, visible=True)
                            
    def reset_button_after_click(self, history, text_positive, text_negative, text_theme, text_user, btn_send, btn_start, btn_reset):
        self.reset()
        """接受来自client的值"""
        self.first_recieve_from_client(reset_mode=True)
        return gr.Chatbot.update(value=None, visible=False),\
            gr.Textbox.update(value=f"{self.cache['positive']}", interactive=True, visible=True),\
                gr.Textbox.update(value=f"{self.cache['negative']}", interactive=True, visible=True),\
                    gr.Textbox.update(value=f"{self.cache['theme']}", interactive=True, visible=True),\
                        gr.Textbox.update(value=f"", interactive=True, visible=False),\
                            gr.Button.update(interactive=True, visible=False, value="发送"),\
                                gr.Button.update(interactive=True, visible=True, value="开始"),\
                                    gr.Button.update(interactive=False, visible=False, value="重启")
        
    def construct_ui(
        self,
        theme:str=None,
        positive:str=None,
        negative:str=None,
        agents_name:List=None,
        default_cos_play_id:int=None
    ):
        """
        用户输入。正方，反方，辩论主题
        四个文本框，一个按钮，一个radio
        """
        theme = self.cache["theme"] if theme is None else theme
        positive = self.cache["positive"] if positive is None else positive
        negative = self.cache["negative"] if negative is None else negative
        agents_name = self.cache["agents_name"] if agents_name is None else agents_name
        default_cos_play_id = self.cache["default_cos_play_id"] if default_cos_play_id is None else default_cos_play_id
        # =================初始化界面=====================
        with gr.Blocks(css=gc.CSS) as demo:
            with gr.Row():
                with gr.Column():
                    self.text_theme = gr.Textbox(
                        label="辩论主题:",
                        value=theme,
                        placeholder="请输入辩论主题"
                    )
                    self.text_positive = gr.Textbox(
                        label="正方观点:",
                        value=positive,
                        placeholder="请输入正方观点"
                    )
                    self.text_negative = gr.Textbox(
                        label="反方观点:",
                        value=negative,
                        placeholder="请输入反方观点"
                    )
                    self.radio_choose = gr.Radio(
                        agents_name,
                        value=agents_name[default_cos_play_id],
                        label="用户扮演的角色",
                        interactive=True
                    )
                    self.btn_start = gr.Button(
                        value="开始"
                    )
                VISIBLE = False
                with gr.Column():
                    self.chatbot = gr.Chatbot(
                        elem_id="chatbot1",
                        label="对话",
                        visible=VISIBLE
                    )
                    self.text_user = gr.Textbox(
                        label="你的输入:",
                        placeholder="请输入",
                        visible=VISIBLE
                    )
                    self.btn_send = gr.Button(
                        value="发送",
                        visible=VISIBLE
                    )
                    self.btn_reset = gr.Button(
                        value="重启",
                        visible=VISIBLE
                    )
            # =================设置监听器=====================
            """向后端发送选择的信息和启动命令"""
            self.btn_start.click(
                # 向后端发送选择的信息并启动进程
                fn=self.start_button_when_click,
                inputs=[self.text_theme, self.text_positive, self.text_negative, self.radio_choose],
                # 只要把chatbot显示出来就行
                outputs=[self.chatbot, self.btn_send]
            ).then(
                # 接收后端的信息并渲染
                fn=self.start_button_after_click,
                inputs=[self.chatbot],
                outputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset]
            )
            """接收后端的暂停信息，然后向后端发送"""
            self.btn_send.click(
                # 渲染到前端+发送后端
                fn=self.send_button_when_click,
                inputs=[self.text_user, self.chatbot],
                outputs=[self.text_user, self.btn_send, self.chatbot, self.btn_reset]
            ).then(
                # 监听后端更新
                fn=self.start_button_after_click,
                inputs=[self.chatbot],
                outputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset]
            )
            """重启"""
            self.btn_reset.click(
                fn=self.reset_button_when_click,
                inputs=[
                    self.chatbot, 
                    self.text_positive, 
                    self.text_negative, 
                    self.text_theme, 
                    self.text_user,
                    self.btn_send,
                    self.btn_start,
                    self.btn_reset
                ],
                outputs=[
                    self.chatbot, 
                    self.text_positive, 
                    self.text_negative, 
                    self.text_theme, 
                    self.text_user,
                    self.btn_send,
                    self.btn_start,
                    self.btn_reset
                ]
            ).then(
                fn=self.reset_button_after_click,
                inputs=[
                    self.chatbot, 
                    self.text_positive, 
                    self.text_negative, 
                    self.text_theme, 
                    self.text_user,
                    self.btn_send,
                    self.btn_start,
                    self.btn_reset
                ],
                outputs=[
                    self.chatbot, 
                    self.text_positive, 
                    self.text_negative, 
                    self.text_theme, 
                    self.text_user,
                    self.btn_send,
                    self.btn_start,
                    self.btn_reset
                ]
            )
            # ==============================================
        self.demo = demo

class SingleAgentUI(WebUI):
    """
    1. 建立双向链接
    2. 同步信息
    3. 准备开始启动(发送启动的命令)
    """
    
    def render_and_register_ui(self):
        self.agent_name = self.cache["agent_name"] if isinstance(self.cache["agent_name"], str) else self.cache['agent_name'][0]
        gc.add_agent([self.agent_name])
    
    """和DebateUI基本相同，唯一的区别在于不需要设置信息"""
    def __init__(
        self,
        client_cmd: list,
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024
    ):
        super(SingleAgentUI, self).__init__(client_cmd, socket_host, socket_port, bufsize)
        # self.FIRST = True
        # self.receive_server = self.receive_message()
        # assert next(self.receive_server) == "hello"
        # """接收一下开场白，这里一般都是传个字典过来"""
        # data:List = self.receive_server.send(None)
        # print(data)
        # assert len(data) == 1
        # data = eval(data[0])
        # assert isinstance(data, dict)
        # self.cache.update(data)
        # """注册一下agent_name"""
        self.FIRST = True
        self.first_recieve_from_client()
        self.data_history = list()

    def btn_send_when_click(self, history, btn_send, text):
        # 主要作用是渲染气泡，然后将按钮禁用
        """
        inputs=[self.chatbot, self.btn_send, self.text_user]
        outputs=[self.chatbot, self.btn_send, self.text_user]

        输入的内容在text中
        """
        history.append(
            [UIHelper.wrap_css(content=text, name="User"), None]
        )
        if self.FIRST:
            # # 2. 向前端发送开始运行的消息
            # self.send_message(str({'hello':'hello'}))   # 没有用，只是空发一下
            # time.sleep(2)
            # self.send_message(self.SIGN["START"])   # 自动加结束符
            # time.sleep(2)
            self.send_start_cmd()
            self.FIRST = False
        return history, gr.Button.update(interactive=False, value="生成中"), gr.Text.update(interactive=False)

    def handle_message(self, history:list,
            state, agent_name, token, node_name):
        # print("MIKE-history:",history)
        if state % 10 in [0, 2]:
            """这个还是在当前气泡里面的"""
            self.data_history.clear()
            self.data_history.append({agent_name: token})
        elif state % 10 == 1:
            self.data_history[-1][agent_name] += token
        # elif state % 10 == 2:
        #     """表示不是同一个气泡了"""
        #     history.append([None, ""])
        #     self.data_history.clear()
        #     self.data_history.append({agent_name: token})
        else:
            assert False
        # print("MIKE-data_history", self.data_history)
        # 如果state%10==2，说明到了新节点
        print("123:", history)
        render_data = self.render_bubble(history, self.data_history, node_name, render_node_name= state % 10 == 2)
        return render_data

    def btn_send_after_click(self, history, btn_send, text):
        # 主要作用是接收前端的信息
        """
        inputs=[self.chatbot, self.btn_send, self.text_user]
        outputs=[self.chatbot, self.btn_send, self.text_user]
        """
        self.send_message("<USER>"+text)
        while True:
            """接受一个"""
            data_list: List = self.receive_server.send(None)
            print("收到:", data_list)
            
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = data
                assert isinstance(state, int)
                if state == 30:
                    """选择权交给用户，就是让用户进行交互"""
                    # 1. 设置interactive和visible
                    print("server:显示1")
                    yield history,\
                        gr.Button.update(visible=True, interactive=True, value="发送"), \
                        gr.Textbox.update(visible=True, interactive=True)
                    return
                else:
                    print("1234:", history)
                    history = self.handle_message(history, state, agent_name, token, node_name)
                    yield history, \
                          gr.Button.update(visible=False, interactive=False), \
                          gr.Textbox.update(visible=False, interactive=False, value="")

    """重新启动"""
    def btn_reset_when_click(self, history, text, btn_send, btn_reset):
        yield history.append([None, UIHelper.wrap_css("正在重启", name="System")]), \
            gr.Textbox.update(value="", visible=True, interactive=True), \
                gr.Button.update(visible=True, interactive=False),\
                    gr.Button.update(visible=True, interactive=False, value="正在重启")
        return
    
    def btn_reset_after_click(self, history, text, btn_send, btn_reset):
        self.reset()
        self.first_recieve_from_client(reset_mode=True)
        self.FIRST = True
        content = None
        if not self.cache["user_first"]:
            content = self.prepare()
        return None if content is None else [[None, UIHelper.wrap_css(content, name=self.agent_name)]], \
            gr.Textbox.update(value="", visible=True, interactive=True), \
                gr.Button.update(visible=True, interactive=True),\
                    gr.Button.update(visible=True, interactive=True, value="重启")
           
    def prepare(self):
        if self.FIRST:
            self.send_start_cmd()
            self.FIRST = False
        # if self.FIRST:
        #     # 2. 向前端发送开始运行的消息
        #     self.send_message(str({'hello':'hello'}))   # 没有用，只是空发一下
        #     time.sleep(2)
        #     self.send_message(self.SIGN["START"])   # 自动加结束符
        #     # time.sleep(2)
        #     self.FIRST = False
        content = ""
        """agent在一开始就会输出"""
        while True:
            """那就是那边会传来消息"""
            data_list: List = self.receive_server.send(None)
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = data
                print(state)
                if state == 30:
                    return content
                content += token
        
    def construct_ui(
        self
    ):
        """从cache中判断一下是否是用户输入第一句话"""
        content = None
        print("hi::",self.cache["user_first"])
        if not self.cache["user_first"]:
            content = self.prepare()
        print("hi:",content is None)
        with gr.Blocks(css=gc.CSS) as demo:
            with gr.Column():
                self.chatbot = gr.Chatbot(
                    value=None if content is None else [[None, UIHelper.wrap_css(content=content, name=self.agent_name)]],
                    elem_id="chatbot1",
                    label="对话"
                )
                with gr.Row():
                    self.text_user = gr.Textbox(
                        label="你的输入:",
                        placeholder="请输入",
                        scale=10
                    )
                    self.btn_send = gr.Button(
                        value="发送",
                        scale=1
                    )
                    self.btn_reset = gr.Button(
                        value="重启",
                        scale=1
                    )

            # =============注册监听事件===============
            self.btn_send.click(
                fn=self.btn_send_when_click,
                inputs=[self.chatbot, self.btn_send, self.text_user],
                outputs=[self.chatbot, self.btn_send, self.text_user]
            ).then(
                fn=self.btn_send_after_click,
                inputs=[self.chatbot, self.btn_send, self.text_user],
                outputs=[self.chatbot, self.btn_send, self.text_user]
            )

            self.text_user.submit(
                fn=self.btn_send_when_click,
                inputs=[self.chatbot, self.btn_send, self.text_user],
                outputs=[self.chatbot, self.btn_send, self.text_user]
            ).then(
                fn=self.btn_send_after_click,
                inputs=[self.chatbot, self.btn_send, self.text_user],
                outputs=[self.chatbot, self.btn_send, self.text_user]
            )
            
            self.btn_reset.click(
                fn=self.btn_reset_when_click,
                inputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset],
                outputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset]
            ).then(
                fn=self.btn_reset_after_click,
                inputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset],
                outputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset]
            )
            # ========================================
        self.demo = demo

class NovelUI(WebUI):
    def __init__(
        self,
        client_cmd: list,
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024
    ):
        super(NovelUI, self).__init__(client_cmd, socket_host, socket_port, bufsize)

class CodeUI(WebUI):
    """传给我，我传给他，然后启动"""
    
    def render_and_register_ui(self):
        self.agent_name:list = [self.cache["agents_name"]] if isinstance(self.cache["agents_name"], str) else self.cache['agents_name']
        gc.add_agent(self.agent_name)
    
    def __init__(
        self,
        client_cmd: list,
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024 
    ):
        super(CodeUI, self).__init__(client_cmd, socket_host, socket_port, bufsize)
        self.first_recieve_from_client()
        self.data_history = list()
    
    def construct_ui(self):
        with gr.Blocks(css=gc.CSS) as demo:
            with gr.Row():
                # 第一列
                with gr.Column():
                    self.chatbot = gr.Chatbot(
                        elem_id="chatbot1"
                    )
                    with gr.Row():
                        self.text_requirement = gr.Textbox(
                            value=self.cache['requirement'],
                            placeholder="请输入你的要求",
                            scale=9,
                        )
                        self.btn_start = gr.Button(
                            value="开始",
                            scale=1
                        )
                    self.btn_reset = gr.Button(
                        value="重启",
                        visible=False
                    )
                
                # 第二列
                with gr.Column():
                    self.file = gr.File(visible=False)
                    self.chat_code_show = gr.Chatbot(
                        elem_id="chatbot1",
                        visible=False
                    )   
                # =========创建监听事件==========
                self.btn_start.click(
                    fn=self.btn_send_when_click,
                    inputs=[self.chatbot, self.text_requirement],
                    outputs=[self.chatbot, self.btn_start, self.text_requirement, self.btn_reset]
                ).then(
                    fn=self.btn_send_after_click,
                    inputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement],
                    outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement]
                )
                self.text_requirement.submit(
                    fn=self.btn_send_when_click,
                    inputs=[self.chatbot, self.text_requirement],
                    outputs=[self.chatbot, self.btn_start, self.text_requirement, self.btn_reset]
                ).then(
                    fn=self.btn_send_after_click,
                    inputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement],
                    outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement]
                )
                self.btn_reset.click(
                    fn=self.btn_reset_when_click,
                    inputs=[],
                    outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement]
                ).then(
                    fn=self.btn_reset_after_click,
                    inputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement],
                    outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement]
                )
                self.file.select(
                    fn=self.file_when_select,
                    inputs=[self.file],
                    outputs=[self.chat_code_show]
                )
                # ==============================
            self.demo = demo
    
    """处理发送来的数据"""
    def handle_message(self, history:list,
            state, agent_name, token, node_name):
        # print("MIKE-history:",history)
        if state % 10 == 0:
            """这个还是在当前气泡里面的"""
            self.data_history.append({agent_name: token})
        elif state % 10 == 1:
            self.data_history[-1][agent_name] += token
        elif state % 10 == 2:
            """表示不是同一个气泡了"""
            history.append([None, ""])
            self.data_history.clear()
            self.data_history.append({agent_name: token})
        else:
            assert False
        # print("MIKE-data_history", self.data_history)
        render_data = self.render_bubble(history, self.data_history, node_name, render_node_name=True)
        return render_data
    
    # 监听
    def btn_send_when_click(self, chatbot, text_requirement):
        """
        inputs=[self.chatbot, self.text_requirement],
        outputs=[self.chatbot, self.btn_start, self.text_requirement, self.btn_reset]
        """
        """渲染气泡，然后隐藏按钮"""
        chatbot = [[UIHelper.wrap_css(content=text_requirement, name="User"), None]]
        yield chatbot,\
            gr.Button.update(visible=True, interactive=False, value="运行中"),\
            gr.Textbox.update(visible=True, interactive=False, value=""),\
            gr.Button.update(visible=False, interactive=False)                  # 重启
        """发送启动命令"""
        self.send_start_cmd({'requirement': text_requirement})
    
    def btn_send_after_click(
        self, 
        file,
        history,
        show_code,
        btn_send,
        btn_reset,
        text_requirement
    ):
        """这个应该就自动运行到结束"""
        """更新chatbot"""
        """结束的state为99"""
        self.data_history = list()
        receive_server = self.receive_server
        while True:
            data_list: List = receive_server.send(None)
            print("收到:", data_list)
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = data
                assert isinstance(state, int)
                """非人机"""
                assert state in [10, 11, 12, 99]
                if state == 99:
                    """结束渲染"""
                    """拿到路径"""
                    fs = [self.cache['pwd']+'/output_code/'+_ for _ in os.listdir(self.cache['pwd']+'/output_code')]
                    yield gr.File.update(value=fs, visible=True, interactive=True),\
                        history, \
                        gr.Chatbot.update(visible=True),\
                        gr.Button.update(visible=True, interactive=True, value="开始"),\
                        gr.Button.update(visible=True, interactive=True),\
                        gr.Textbox.update(visible=True, interactive=True, placeholder="请输入你的要求", value="")
                    return
                history = self.handle_message(history, state, agent_name, token, node_name)
                yield gr.File.update(visible=False),\
                    history, \
                    gr.Chatbot.update(visible=False),\
                    gr.Button.update(visible=True, interactive=False),\
                    gr.Button.update(visible=False, interactive=False),\
                    gr.Textbox.update(visible=True, interactive=False)
    
    def btn_reset_when_click(self):
        """
        inputs = []
        outputs = [self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement]
        """
        return gr.File.update(visible=False),\
            None, None, gr.Button.update(value="重启中", interactive=False),\
                gr.Button.update(value="重启中", interactive=False),\
                    gr.Textbox.update(value="重启中", interactive=False)
    
    def btn_reset_after_click(
        self,
        file,
        chatbot,
        show_code,
        btn_send,
        btn_reset,
        text_requirement
    ):
        print("mmmmmmm:...")
        self.reset()
        """接受来自client的值"""
        self.first_recieve_from_client(reset_mode=True)
        return gr.File.update(value=None, visible=False),\
            gr.Chatbot.update(value=None, visible=True),\
            gr.Chatbot.update(value=None, visible=False),\
            gr.Button.update(value="开始", visible=True, interactive=True),\
            gr.Button.update(value="重启", interactive=False, visible=False),\
            gr.Textbox.update(value=self.cache['requirement'], interactive=True, visible=True)
        
    """监听文件点击"""
    def file_when_select(self, file):
        """点击文件放到前端去渲染"""
        CODE_PREFIX = "```python\n{}\n```"
        with open(file.name, "r", encoding='utf-8') as f:
            contents = f.readlines()
        codes = "".join(contents)
        return [[CODE_PREFIX.format(codes),None]]
        
        
def test_ui():
    # with gr.Blocks(css=gc.CSS) as demo:
    #     with gr.Row():
    #         with gr.Column():
    #             # 实时对话
    #             chatbot1 = gr.Chatbot(
    #                 elem_id="chatbot1",
    #                 label="对话",
    #             )
    #             # 输入的要求
    #             text_requirement = gr.Textbox(
    #                 placeholder="剧本的要求",
    #                 value=""
    #             )
    #             with gr.Row():
    #                 radio_start_agent = gr.Radio(
    #                     label="开始的agent",
    #                     choices=[str(i) for i in range(5)]
    #                 )
    #                 text_start_query = gr.Textbox(
    #                     value="开始的query",
    #                     placeholder=""
    #                 )
    code = """```python
import torch
class A:
    def __init__(self):
        print("class A is instanced")
        
if __name__ == '__main__':
    a = A()
    print("done")  
```  
"""
    with gr.Blocks(css=gc.CSS) as demo:
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot(
                    elem_id="chatbot1"
                )
                with gr.Row():
                    text_requirement = gr.Textbox(
                        value="",
                        placeholder="请输入你的要求",
                        scale=9
                    )
                    btn_start = gr.Button(
                        value="开始",
                        scale=1
                    )
                btn_reset = gr.Button(
                    value="重启"
                )
                
            with gr.Column():
                file = gr.File()
                chat_code_show = gr.Chatbot(
                    elem_id="chatbot1",
                    value=[[code, None]]
                )            
            
            
    demo.queue()
    demo.launch(share=True)

if __name__ == '__main__':
    # test_ui()
    import os

    # 指定要遍历的文件夹路径
    folder_path = '../Muti_Agent/software_company/output_code/'
    print(os.listdir(folder_path))
    
    print(os.getcwd())
    # # 使用os.walk()遍历文件夹
    # for root, directories, files in os.walk(folder_path):
    #     for file in files:
    #         # 输出文件的完整路径
    #         file_path = os.path.join(root, file)
    #         print(file_path)
    # # ui = DebateUI(
    #     client_server_file=""
    # )
    # ui.run()
