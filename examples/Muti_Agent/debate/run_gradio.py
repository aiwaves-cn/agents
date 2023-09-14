import sys
sys.path.append("../../Gradio_Config")

from gradio_base import UIHelper, WebUI
import os
from gradio_base import WebUI, UIHelper, PORT, HOST, Client
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr

class DebateUI(WebUI):
    """
    正是启动之前需要匹配参数，也就是
    """
    FORMAT = "{}\n<debate topic>\n{}\nAffirmative viewpoint:{}\nNegative viewpoint:{}\n<debate topic>{}"
    AUDIENCE = "Audience"  # 路人的名字
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
        agent_name.sort()
        return agent_name, only_name

    def render_and_register_ui(self):
        gc.add_agent(self.cache["only_name"])
    
    def __init__(
        self,
        client_cmd: list,
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024,
        ui_name: str = "DebateUI"
    ):
        super(DebateUI, self).__init__(client_cmd, socket_host, socket_port, bufsize, ui_name)
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
        render_data = self.render_bubble(history, self.data_history, node_name, render_node_name= True or state % 10 == 2)
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
                            gr.Button.update(value="Restarting...", interactive=False, visible=True),\
                                gr.Button.update(value="Restarting...", interactive=False, visible=True),\
                                    gr.Button.update(value="Restarting...", interactive=False, visible=True)
                            
    def reset_button_after_click(self, history, text_positive, text_negative, text_theme, text_user, btn_send, btn_start, btn_reset):
        self.reset()
        """接受来自client的值"""
        self.first_recieve_from_client(reset_mode=True)
        return gr.Chatbot.update(value=None, visible=False),\
            gr.Textbox.update(value=f"{self.cache['positive']}", interactive=True, visible=True),\
                gr.Textbox.update(value=f"{self.cache['negative']}", interactive=True, visible=True),\
                    gr.Textbox.update(value=f"{self.cache['theme']}", interactive=True, visible=True),\
                        gr.Textbox.update(value=f"", interactive=True, visible=False),\
                            gr.Button.update(interactive=True, visible=False, value="Send"),\
                                gr.Button.update(interactive=True, visible=True, value="Start"),\
                                    gr.Button.update(interactive=False, visible=False, value="Restart")
        
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
                        label="Debate Topic:",
                        value=theme,
                        placeholder="Please input the Debate Topic"
                    )
                    self.text_positive = gr.Textbox(
                        label="Affirmative viewpoint:",
                        value=positive,
                        placeholder="Please input the Affirmative viewpoint"
                    )
                    self.text_negative = gr.Textbox(
                        label="Negative viewpoint:",
                        value=negative,
                        placeholder="Please input the Negative viewpoint"
                    )
                    self.radio_choose = gr.Radio(
                        agents_name,
                        value=agents_name[default_cos_play_id],
                        label="User'agent",
                        interactive=True
                    )
                    self.btn_start = gr.Button(
                        value="run"
                    )
                VISIBLE = False
                with gr.Column():
                    self.chatbot = gr.Chatbot(
                        height= 850,
                        elem_id="chatbot1",
                        label="Dialog",
                        visible=VISIBLE
                    )
                    self.text_user = gr.Textbox(
                        label="Input",
                        placeholder="Input here",
                        visible=VISIBLE
                    )
                    self.btn_send = gr.Button(
                        value="Send",
                        visible=VISIBLE
                    )
                    self.btn_reset = gr.Button(
                        value="Restart",
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


if __name__ == '__main__':
    # 启动client_server_file并自动传递消息
    ui = DebateUI(client_cmd=["python","run.py"])
    # 构建映射关系
    # GradioConfig.add_agent(agents_name=ui.all_agents_name)
    # 搭建前端并建立监听事件
    ui.construct_ui()
    # 启动运行
    ui.run(share=True)
