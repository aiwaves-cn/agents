import sys
sys.path.append("Gradio_Config")
import os
import argparse
from gradio_base import WebUI, UIHelper, PORT, HOST, Client
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr

class GeneralUI(WebUI):
    def render_and_register_ui(self):
        # bind the agent with avatar
        self.agent_name:list = [self.cache["agents_name"]] if isinstance(self.cache["agents_name"], str) else self.cache['agents_name']
        gc.add_agent(self.agent_name)
    
    def handle_message(self, history, state, agent_name, token, node_name):
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
        render_data = self.render_bubble(history, self.data_history, node_name, render_node_name= True)
        return render_data
    
    def __init__(
        self,
        client_cmd: list,
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024,
        ui_name: str = "GeneralUI"
    ):
        super(GeneralUI, self).__init__(client_cmd, socket_host, socket_port, bufsize, ui_name)
        self.first_recieve_from_client()
        self.current_node_name = ""
        self.data_history = None
        for _ in ['agents_name']:
            assert _ in self.cache
    
    def construct_ui(self):
        with gr.Blocks(css=gc.CSS) as demo:
            
            with gr.Column():
                self.btn_start = gr.Button(
                    value="Start😁(Click here to start!)"
                )
                self.chatbot = gr.Chatbot(
                    elem_id="chatbot1",
                    label="Dialog",
                    visible=False,
                    height=700
                )
                with gr.Row():
                    self.text_input = gr.Textbox(
                        placeholder="Please enter your content.",
                        label="Input",
                        scale=9,
                        visible=False
                    )
                    self.btn_send = gr.Button(
                        value="Send",
                        visible=False
                    )
                self.btn_reset = gr.Button(
                    value="Restart",
                    visible=False
                )

            all_components = [self.btn_start, self.btn_send, self.btn_reset, self.chatbot, self.text_input]
            
            self.btn_start.click(
                fn = self.btn_start_when_click,
                inputs=[],
                outputs=all_components
            ).then(
                fn = self.btn_start_after_click,
                inputs=[self.chatbot],
                outputs=all_components
            )
            
            self.btn_send.click(
                fn=self.btn_send_when_click,
                inputs=[self.text_input, self.chatbot],
                outputs=all_components
            ).then(
                fn=self.btn_send_after_click,
                inputs=[self.text_input, self.chatbot],
                outputs=all_components
            )
            
            self.text_input.submit(
                fn=self.btn_send_when_click,
                inputs=[self.text_input, self.chatbot],
                outputs=all_components
            ).then(
                fn=self.btn_send_after_click,
                inputs=[self.text_input, self.chatbot],
                outputs=all_components
            )
            
            self.btn_reset.click(
                fn=self.btn_reset_when_click,
                inputs=[],
                outputs=all_components
            ).then(
                fn=self.btn_reset_after_click,
                inputs=[],
                outputs=all_components
            )
            
            self.demo = demo
    
    def btn_start_when_click(self):
        """
        inputs=[]
        outputs=[self.btn_start, self.btn_send, self.btn_reset, self.chatbot, self.text_input]
        """
        self.send_start_cmd()
        return gr.Button.update(visible=False), \
            gr.Button.update(visible=False),\
            gr.Button.update(visible=False),\
            gr.Chatbot.update(visible=True),\
            gr.Textbox.update(visible=False)
    
    def btn_start_after_click(self, history):
        """
        inputs=[self.chatbot]
        outputs=[self.btn_start, self.btn_send, self.btn_reset, self.chatbot, self.text_input]
        """
        if self.data_history is None:
            self.data_history = list()
        receive_server = self.receive_server
        while True:
            data_list: List = receive_server.send(None)
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name = data
                self.current_node_name = node_name
                assert isinstance(state, int)
                assert state in [10, 11, 12, 30, 99]
                if state == 99:
                    # finish
                    yield gr.Button.update(visible=False),\
                        gr.Button.update(visible=True, interactive=False),\
                        gr.Button.update(visible=True, interactive=True),\
                        history,\
                        gr.Textbox.update(visible=True, interactive=False)
                    return
                elif state == 30:
                    # user input
                    yield gr.Button.update(visible=False), \
                            gr.Button.update(visible=True),\
                            gr.Button.update(visible=True),\
                            history,\
                            gr.Textbox.update(visible=True, value="")
                    return 
                history = self.handle_message(history, state, agent_name, token, node_name)
                yield gr.Button.update(visible=False), \
                    gr.Button.update(visible=False),\
                    gr.Button.update(visible=False),\
                    history,\
                    gr.Textbox.update(visible=False)
    
    def btn_send_when_click(self, text_input, history):
        '''
        inputs=[self.text_input, self.chatbot]
        outputs=[self.btn_start, self.btn_send, self.btn_reset, self.chatbot, self.text_input]
        '''
        history = self.handle_message(history, 10, 'User', text_input, self.current_node_name)
        self.send_message("<USER>"+text_input+self.SIGN["SPLIT"])
        return gr.Button.update(visible=False), \
            gr.Button.update(visible=False),\
            gr.Button.update(visible=False),\
            history,\
            gr.Textbox.update(visible=False)
    
    def btn_send_after_click(self, text_input, history):
        '''
        inputs=[self.text_input, self.chatbot]
        outputs=[self.btn_start, self.btn_send, self.btn_reset, self.chatbot, self.text_input]
        '''
        yield from self.btn_start_after_click(history=history)
        return 
    
    def btn_reset_when_click(self):
        """
        outputs=[self.btn_start, self.btn_send, self.btn_reset, self.chatbot, self.text_input]
        """
        return gr.Button.update(interactive=False), gr.Button.update(interactive=False), gr.Button.update(interactive=False, value="Restarting....."), gr.Chatbot.update(label="Dialog"), \
            gr.Textbox.update(interactive=False)
    
    def btn_reset_after_click(self):
        self.reset()
        self.first_recieve_from_client(reset_mode=True)
        return gr.Button.update(interactive=True, visible=True), \
            gr.Button.update(interactive=True, visible=False), \
            gr.Button.update(interactive=True, value="Restart", visible=False), \
            gr.Chatbot.update(label="Dialog", visible=False), \
            gr.Textbox.update(interactive=True, visible=False)
  
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A demo of chatbot')
    parser.add_argument('--agent', type=str, help='path to SOP json')
    args = parser.parse_args()
    
    ui = GeneralUI(client_cmd=["python","gradio_backend.py","--agent", args.agent])
    ui.construct_ui()
    ui.run(share=True)
