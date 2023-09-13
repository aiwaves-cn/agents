import argparse
import sys
sys.path.append("Gradio_Config")
import os
from gradio_base import WebUI, UIHelper, PORT, HOST, Client
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr


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
        bufsize: int = 1024,
        ui_name: str = "SingleAgentUI"
    ):
        super(SingleAgentUI, self).__init__(client_cmd, socket_host, socket_port, bufsize, ui_name)
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
                    label="Dialog",
                    height= 600
                )
                with gr.Row():
                    self.text_user = gr.Textbox(
                        label="Input",
                        placeholder="Please enter your content",
                        scale=10
                    )
                    self.btn_send = gr.Button(
                        value="Send",
                        scale=1
                    )
                    self.btn_reset = gr.Button(
                        value="Restart",
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


if __name__ == '__main__':
    # 启动client_server_file并自动传递消息
    parser = argparse.ArgumentParser(description='A demo of chatbot')
    parser.add_argument('--agent', type=str, help='path to SOP json')
    args = parser.parse_args()
    ui = SingleAgentUI(
        # client_server_file="serving.py"
        client_cmd=["python", "Single_Agent/gradio_backend.py","--agent",args.agent]
    )
    # 构建映射关系
    # GradioConfig.add_agent(agents_name=ui.all_agents_name)
    # 搭建前端并建立监听事件
    ui.construct_ui()
    # 启动运行
    ui.run(share=True)
