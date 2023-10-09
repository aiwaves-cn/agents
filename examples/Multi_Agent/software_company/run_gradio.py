import sys
sys.path.append("../../Gradio_Config")

import os
from gradio_base import WebUI, UIHelper, PORT, HOST, Client
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr
import time

class CodeUI(WebUI):
    
    def render_and_register_ui(self):
        self.agent_name:list = [self.cache["agents_name"]] if isinstance(self.cache["agents_name"], str) else self.cache['agents_name']
        gc.add_agent(self.agent_name)
    
    def __init__(
        self,
        client_cmd: list,
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024,
        ui_name: str = "CodeUI"
    ):
        super(CodeUI, self).__init__(client_cmd, socket_host, socket_port, bufsize, ui_name)
        self.first_recieve_from_client()
        self.data_history = list()
        self.caller = 0
    
    def construct_ui(self):
        with gr.Blocks(css=gc.CSS) as demo:
            with gr.Row():
                with gr.Column():
                    self.text_api = gr.Textbox(
                        value = self.cache["api_key"],
                        placeholder="openai key",
                        label="Please input valid openai key for gpt-3.5-turbo-16k."
                    )
                    self.radio_mode = gr.Radio(
                        [Client.AUTO_MODE, Client.SINGLE_MODE],
                        value=Client.AUTO_MODE,
                        interactive=True,
                        label = Client.MODE_LABEL,
                        info = Client.MODE_INFO
                    )
                    self.chatbot = gr.Chatbot(
                        elem_id="chatbot1"
                    )
                    self.btn_next = gr.Button(
                        value="Next Agent",
                        visible=False, elem_id="btn"
                    )
                    with gr.Row():
                        self.text_requirement = gr.Textbox(
                            value=self.cache['requirement'],
                            placeholder="Please enter your content",
                            scale=9,
                        )
                        self.btn_start = gr.Button(
                            value="Start!",
                            scale=1
                        )
                    self.btn_reset = gr.Button(
                        value="Restart",
                        visible=False
                    )
                
                with gr.Column():
                    self.file = gr.File(visible=False)
                    self.chat_code_show = gr.Chatbot(
                        elem_id="chatbot1",
                        visible=False
                    )   
                
                self.btn_start.click(
                    fn=self.btn_send_when_click,
                    inputs=[self.chatbot, self.text_requirement, self.radio_mode, self.text_api],
                    outputs=[self.chatbot, self.btn_start, self.text_requirement, self.btn_reset]
                ).then(
                    fn=self.btn_send_after_click,
                    inputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement],
                    outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement, self.btn_next]
                )
                self.text_requirement.submit(
                    fn=self.btn_send_when_click,
                    inputs=[self.chatbot, self.text_requirement, self.text_api],
                    outputs=[self.chatbot, self.btn_start, self.text_requirement, self.btn_reset]
                ).then(
                    fn=self.btn_send_after_click,
                    inputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement],
                    outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement, self.btn_next]
                )
                self.btn_reset.click(
                    fn=self.btn_reset_when_click,
                    inputs=[],
                    outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement, self.btn_next]
                ).then(
                    fn=self.btn_reset_after_click,
                    inputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement],
                    outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement, self.btn_next]
                )
                self.file.select(
                    fn=self.file_when_select,
                    inputs=[self.file],
                    outputs=[self.chat_code_show]
                )
                self.btn_next.click(
                    fn = self.btn_next_when_click,
                    inputs=[],
                    outputs=[self.btn_next]
                ).then(
                    fn=self.btn_send_after_click,
                    inputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement],
                    outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement, self.btn_next]
                )
                
            self.demo = demo
    

    def handle_message(self, history:list, state, agent_name, token, node_name):
        if state % 10 == 0:
            self.data_history.append({agent_name: token})
        elif state % 10 == 1:
            # Same state. Need to add new bubble in same bubble.
            self.data_history[-1][agent_name] += token
        elif state % 10 == 2:
            # New state. Need to add new bubble.
            history.append([None, ""])
            self.data_history.clear()
            self.data_history.append({agent_name: token})
        else:
            assert False, "Invalid state."
        render_data = self.render_bubble(history, self.data_history, node_name, render_node_name=True)
        return render_data
    
    def btn_send_when_click(self, chatbot, text_requirement, mode, api):
        """
        inputs=[self.chatbot, self.text_requirement, radio, text_api],
        outputs=[self.chatbot, self.btn_start, self.text_requirement, self.btn_reset]
        """
        chatbot = [[UIHelper.wrap_css(content=text_requirement, name="User"), None]]
        yield chatbot,\
            gr.Button.update(visible=True, interactive=False, value="Running"),\
            gr.Textbox.update(visible=True, interactive=False, value=""),\
            gr.Button.update(visible=False, interactive=False)
        self.send_start_cmd({'requirement': text_requirement, "mode": mode, "api_key": api})
        return
    
    def btn_send_after_click(
        self, 
        file,
        history,
        show_code,
        btn_send,
        btn_reset,
        text_requirement
    ):
        """
        outputs=[self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement, self.btn_next]
        """
        if self.caller == 0:
            self.data_history = list()
        self.caller = 0
        receive_server = self.receive_server
        while True:
            data_list: List = receive_server.send(None)
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = data
                assert isinstance(state, int)
                assert state in [10, 11, 12, 99, 98]
                if state == 99:
                    # finish
                    fs = [self.cache['pwd']+'/output_code/'+_ for _ in os.listdir(self.cache['pwd']+'/output_code')]
                    yield gr.File.update(value=fs, visible=True, interactive=True),\
                        history, \
                        gr.Chatbot.update(visible=True),\
                        gr.Button.update(visible=True, interactive=True, value="Start"),\
                        gr.Button.update(visible=True, interactive=True),\
                        gr.Textbox.update(visible=True, interactive=True, placeholder="Please input your requirement", value=""),\
                        gr.Button.update(visible=False)
                    return
                elif state == 98:
                    yield gr.File.update(visible=False),\
                        history, \
                        gr.Chatbot.update(visible=False),\
                        gr.Button.update(visible=True, interactive=False),\
                        gr.Button.update(visible=True, interactive=True),\
                        gr.Textbox.update(visible=True, interactive=False),\
                        gr.Button.update(visible=True, value=f"Next Agent: 🤖{agent_name} | Next Node: ⭕{node_name}")
                    return
                history = self.handle_message(history, state, agent_name, token, node_name)
                yield gr.File.update(visible=False),\
                    history, \
                    gr.Chatbot.update(visible=False),\
                    gr.Button.update(visible=True, interactive=False),\
                    gr.Button.update(visible=False, interactive=False),\
                    gr.Textbox.update(visible=True, interactive=False),\
                    gr.Button.update(visible=False)
    
    def btn_reset_when_click(self):
        """
        inputs = []
        outputs = [self.file, self.chatbot, self.chat_code_show, self.btn_start, self.btn_reset, self.text_requirement, self.btn_next]
        """
        return gr.File.update(visible=False),\
            None, None, gr.Button.update(value="Restarting...", interactive=False),\
                gr.Button.update(value="Restarting...", interactive=False),\
                    gr.Textbox.update(value="Restarting", interactive=False),\
                        gr.Button.update(visible=False)
    
    def btn_reset_after_click(
        self,
        file,
        chatbot,
        show_code,
        btn_send,
        btn_reset,
        text_requirement
    ):
        self.reset()
        self.first_recieve_from_client(reset_mode=True)
        return gr.File.update(value=None, visible=False),\
            gr.Chatbot.update(value=None, visible=True),\
            gr.Chatbot.update(value=None, visible=False),\
            gr.Button.update(value="Start", visible=True, interactive=True),\
            gr.Button.update(value="Restart", interactive=False, visible=False),\
            gr.Textbox.update(value=self.cache['requirement'], interactive=True, visible=True),\
            gr.Button.update(visible=False)
        
    def file_when_select(self, file):
        CODE_PREFIX = "```python\n{}\n```"
        with open(file.name, "r", encoding='utf-8') as f:
            contents = f.readlines()
        codes = "".join(contents)
        return [[CODE_PREFIX.format(codes),None]]
    
    def btn_next_when_click(self):
        self.caller = 1             # it will remain the value in self.data_history
        self.send_message("nothing")
        time.sleep(0.5)
        yield gr.Button.update(visible=False)
        return
        

if __name__ == '__main__':
    ui = CodeUI(client_cmd=["python","gradio_backend.py"])
    ui.construct_ui()
    ui.run(share=True)
