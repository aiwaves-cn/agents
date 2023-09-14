import sys
sys.path.append("../../Gradio_Config")

import os
from gradio_base import WebUI, UIHelper, PORT, HOST
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr

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
    
    def construct_ui(self):
        with gr.Blocks(css=gc.CSS) as demo:
            with gr.Row():
                with gr.Column():
                    self.chatbot = gr.Chatbot(
                        elem_id="chatbot1"
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
    
    def btn_send_when_click(self, chatbot, text_requirement):
        """
        inputs=[self.chatbot, self.text_requirement],
        outputs=[self.chatbot, self.btn_start, self.text_requirement, self.btn_reset]
        """
        chatbot = [[UIHelper.wrap_css(content=text_requirement, name="User"), None]]
        yield chatbot,\
            gr.Button.update(visible=True, interactive=False, value="Running"),\
            gr.Textbox.update(visible=True, interactive=False, value=""),\
            gr.Button.update(visible=False, interactive=False) 
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
        self.data_history = list()
        receive_server = self.receive_server
        while True:
            data_list: List = receive_server.send(None)
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = data
                assert isinstance(state, int)
                assert state in [10, 11, 12, 99]
                if state == 99:
                    # finish
                    fs = [self.cache['pwd']+'/output_code/'+_ for _ in os.listdir(self.cache['pwd']+'/output_code')]
                    yield gr.File.update(value=fs, visible=True, interactive=True),\
                        history, \
                        gr.Chatbot.update(visible=True),\
                        gr.Button.update(visible=True, interactive=True, value="Start"),\
                        gr.Button.update(visible=True, interactive=True),\
                        gr.Textbox.update(visible=True, interactive=True, placeholder="Please input your requirement", value="")
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
            None, None, gr.Button.update(value="Restarting...", interactive=False),\
                gr.Button.update(value="Restarting...", interactive=False),\
                    gr.Textbox.update(value="Restarting", interactive=False)
    
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
            gr.Textbox.update(value=self.cache['requirement'], interactive=True, visible=True)
        
    def file_when_select(self, file):
        CODE_PREFIX = "```python\n{}\n```"
        with open(file.name, "r", encoding='utf-8') as f:
            contents = f.readlines()
        codes = "".join(contents)
        return [[CODE_PREFIX.format(codes),None]]
 

if __name__ == '__main__':
    ui = CodeUI(client_cmd=["python","gradio_backend.py"])
    ui.construct_ui()
    ui.run(share=True)
