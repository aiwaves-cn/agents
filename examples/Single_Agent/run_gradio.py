import argparse
import sys
sys.path.append("Gradio_Config")
import os
from gradio_base import WebUI, UIHelper, PORT, HOST, Client
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr


class SingleAgentUI(WebUI):
    
    def render_and_register_ui(self):
        self.agent_name = self.cache["agent_name"] if isinstance(self.cache["agent_name"], str) else self.cache['agent_name'][0]
        gc.add_agent([self.agent_name])
    
    def __init__(
        self,
        client_cmd: list,
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024,
        ui_name: str = "SingleAgentUI"
    ):
        super(SingleAgentUI, self).__init__(client_cmd, socket_host, socket_port, bufsize, ui_name)
        self.FIRST = True
        self.first_recieve_from_client()
        self.data_history = list()

    def btn_send_when_click(self, history, btn_send, text):
        """
        inputs=[self.chatbot, self.btn_send, self.text_user]
        outputs=[self.chatbot, self.btn_send, self.text_user]
        """
        history.append(
            [UIHelper.wrap_css(content=text, name="User"), None]
        )
        if self.FIRST:
            self.send_start_cmd()
            self.FIRST = False
        return history, gr.Button.update(interactive=False, value="Waiting"), gr.Text.update(interactive=False)

    def handle_message(self, history:list,
            state, agent_name, token, node_name):
        if state % 10 in [0, 2]:
            self.data_history.clear()
            self.data_history.append({agent_name: token})
        elif state % 10 == 1:
            self.data_history[-1][agent_name] += token
        else:
            assert False, "Invalid state."
        render_data = self.render_bubble(history, self.data_history, node_name, render_node_name= state % 10 == 2)
        return render_data

    def btn_send_after_click(self, history, btn_send, text):
        """
        inputs=[self.chatbot, self.btn_send, self.text_user]
        outputs=[self.chatbot, self.btn_send, self.text_user]
        """
        self.send_message("<USER>"+text)
        while True:
            data_list: List = self.receive_server.send(None)
            
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = data
                assert isinstance(state, int)
                if state == 30:
                    yield history,\
                        gr.Button.update(visible=True, interactive=True, value="Send"), \
                        gr.Textbox.update(visible=True, interactive=True)
                    return
                else:
                    history = self.handle_message(history, state, agent_name, token, node_name)
                    yield history, \
                          gr.Button.update(visible=False, interactive=False), \
                          gr.Textbox.update(visible=False, interactive=False, value="")

    def btn_reset_when_click(self, history, text, btn_send, btn_reset):
        yield history.append([None, UIHelper.wrap_css("Restarting", name="System")]), \
            gr.Textbox.update(value="", visible=True, interactive=True), \
                gr.Button.update(visible=True, interactive=False),\
                    gr.Button.update(visible=True, interactive=False, value="Restarting")
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
                    gr.Button.update(visible=True, interactive=True, value="Restart")
           
    def prepare(self):
        if self.FIRST:
            self.send_start_cmd()
            self.FIRST = False
        content = ""
        while True:
            data_list: List = self.receive_server.send(None)
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = data
                if state == 30:
                    return content
                content += token
        
    def construct_ui(
        self
    ):
        content = None
        if not self.cache["user_first"]:
            content = self.prepare()
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
        self.demo = demo


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A demo of chatbot')
    parser.add_argument('--agent', type=str, help='path to SOP json')
    args = parser.parse_args()
    
    ui = SingleAgentUI(
        client_cmd=["python", "Single_Agent/gradio_backend.py", "--agent", args.agent]
    )
    ui.construct_ui()
    ui.run(share=True)
