from gradio_base import WebUI, UIHelper
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr

class DebateUI(WebUI):
    """
    正是启动之前需要匹配参数，也就是
    """
    def __init__(
        self,
        client_server_file: str,
        socket_host: str = '127.0.0.1',
        socket_port: int = 9999,
        bufsize: int = 1024
    ):
        super(DebateUI, self).__init__(client_server_file, socket_host, socket_port, bufsize)

    """处理发送来的数据"""
    def handle_message(self, history:list,
            state, agent_name, token, node_name):
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
        render_data = self.render_bubble(history, self.data_history, node_name)
        return render_data

    def start_button_when_click(self, theme, positive, negative, choose):
        """
        inputs=[self.text_theme, self.text_positive, self.text_negative, self.radio_choose],
        只要把chatbot显示出来就行
        outputs=[self.chatbot]
        """
        # 1. 向前端发送数据消息
        message = [theme, positive, negative, choose]
        self.send_message(str(message))
        # 2. 向前端发送开始运行的消息
        self.send_message(self.SIGN["START"])
        return gr.Chatbot.update(
            visible=True
        )

    def start_button_after_click(self, history):
        """
        inputs=[self.chatbot],
        outputs=[self.chatbot, self.text_user, self.btn_send]
        """
        # 这个是用于存放历史数据的，
        self.data_history = list()
        # 主要是开始渲染后端发来的消息
        receive_server = self.receive_message()
        while True:
            data_list: List = next(receive_server)
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = item
                assert isinstance(state, int)
                if state == 30:
                    """选择权交给用户，就是让用户进行交互"""
                    # 1. 设置interactive和visible
                    yield history,\
                        gr.Textbox.update(visible=True, interactive=True), \
                        gr.Button.update(visible=True, interactive=True)
                    # 2. 监听动作（一般来说，这个item应该就是data_list就是最后一个）
                    #    所以可以直接break，来监听下一个，让程序阻塞在这里
                    break
                else:
                    history = self.handle_message(history, state, agent_name, token, node_name)
                    yield history, \
                          gr.Textbox.update(visible=False, interactive=False), \
                          gr.Button.update(visible=False, interactive=False)

    def send_button_when_click(self, text_user, history:list):
        """点击这个按钮的目的是将内容渲染到前端"""
        """
        inputs=[self.text_user, self.chatbot],
        outputs=[self.text_user, self.btn_send, self.chatbot]
        """
        history.append(
            [UIHelper.wrap_css(text_user, "User"), None]
        )
        return gr.Textbox.update(value="", visible=False),\
            gr.Button.update(visible=False), \
            history

    def send_button_after_click(self, text_user):
        """将文本的内容发送到后端"""
        self.send_message("<USER>"+text_user+self.SIGN["SPLIT"])

    def construct_ui(
        self,
        theme:str,
        positive:str,
        negative:str,
        agents_name:List,
        default_cos_play_id:int=None
    ):
        """
        用户输入。正方，反方，辩论主题
        四个文本框，一个按钮，一个radio
        """
        if default_cos_play_id is None:
            default_cos_play_id = 0
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
        # =================设置监听器=====================
        """向后端发送选择的信息和启动命令"""
        self.btn_start.click(
            # 向后端发送选择的信息并启动进程
            fn=self.start_button_when_click,
            inputs=[self.text_theme, self.text_positive, self.text_negative, self.radio_choose],
            # 只要把chatbot显示出来就行
            outputs=[self.chatbot]
        ).then(
            # 接收后端的信息并渲染
            fn=self.start_button_after_click,
            inputs=[self.chatbot],
            outputs=[self.chatbot, self.text_user, self.btn_send]
        )
        """接收后端的暂停信息，然后向后端发送"""
        self.btn_send.click(
            # 这个是渲染到前端
            fn=self.send_button_when_click,
            inputs=[self.text_user, self.chatbot],
            outputs=[self.text_user, self.btn_send, self.chatbot]
        ).then(
            # 这个是发送到后端
            fn=self.send_button_after_click,
            inputs=[],
            outputs=[]
        )
        # ==============================================
        self.demo = demo

class SingleAgentUI(WebUI):
    def __init__(
        self,
        client_server_file: str,
        socket_host: str = '127.0.0.1',
        socket_port: int = 9999,
        bufsize: int = 1024
    ):
        super(SingleAgentUI, self).__init__(client_server_file, socket_host, socket_port, bufsize)

class NovelUI(WebUI):
    def __init__(
            self,
            client_server_file: str,
            socket_host: str = '127.0.0.1',
            socket_port: int = 9999,
            bufsize: int = 1024
    ):
        super(NovelUI, self).__init__(client_server_file, socket_host, socket_port, bufsize)

def test_ui():
    with gr.Blocks(css=gc.CSS) as demo:
        with gr.Row():
            with gr.Column():
                theme = gr.Textbox(
                    label="辩论主题:",
                    placeholder="请输入辩论主题"
                )
                positive = gr.Textbox(
                    label="正方观点:",
                    placeholder="请输入正方观点"
                )
                negative = gr.Textbox(
                    label="反方观点:",
                    placeholder="请输入反方观点"
                )
                choose = gr.Radio(
                    [str(i) for i in range(10)],
                    value="2",
                    label="用户扮演的角色"
                )
                btn_start = gr.Button(
                    value="开始"
                )
            with gr.Column():
                chatbot = gr.Chatbot(
                    elem_id="chatbot1",
                    label="对话"
                )
                text_user = gr.Textbox(
                    label="你的输入:",
                    placeholder="请输入"
                )
                btn_send = gr.Button(
                    value="发送"
                )
    demo.queue()
    demo.launch(share=True)

if __name__ == '__main__':
    test_ui()
    # ui = DebateUI(
    #     client_server_file=""
    # )
    # ui.run()