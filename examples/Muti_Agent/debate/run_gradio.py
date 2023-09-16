import sys
sys.path.append("../../Gradio_Config")

from gradio_base import UIHelper, WebUI
import os
from gradio_base import WebUI, UIHelper, PORT, HOST, Client
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr
import time

class DebateUI(WebUI):
    FORMAT = "{}\n<debate topic>\n{}\nAffirmative viewpoint:{}\nNegative viewpoint:{}\n<debate topic>{}"
    AUDIENCE = "Audience" 
    cache = {}
    all_agents_name = []
    receive_server = None

    @classmethod
    def extract(cls, content):
        topic = content.split("<debate topic>")[1].split("Affirmative viewpoint:")[0]
        positive = content.split("<debate topic>")[1].split("Affirmative viewpoint:")[1].split("negative viewpoint:")[0]
        negative = content.split("<debate topic>")[1].split("Affirmative viewpoint:")[1].split("negative viewpoint:")[1]
        return topic.strip(), positive.strip(), negative.strip()

    @classmethod
    def merge(cls, theme, positive, negative, origin_content) -> str:
        return cls.FORMAT.format(
            origin_content.split("<debate topic>")[0],
            theme, positive, negative,
            origin_content.split("<debate topic>")[-1]
        )

    @classmethod
    def convert2list4agentname(cls, sop):
        only_name = [] 
        agent_name = []     
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
        self.first_recieve_from_client()
        self.data_history = list()
        self.caller = 0

    def handle_message(self, history:list,
            state, agent_name, token, node_name):
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
        render_data = self.render_bubble(history, self.data_history, node_name, render_node_name= True or state % 10 == 2)
        return render_data

    def start_button_when_click(self, theme, positive, negative, choose, mode):
        """
        inputs=[self.text_theme, self.text_positive, self.text_negative, self.radio_choose],
        outputs=[self.chatbot, self.btn_send]
        """
        cosplay = None if choose == self.AUDIENCE else choose.split("(")[0]
        message = dict(theme=theme, positive=positive, negative=negative, cosplay=cosplay, mode=mode)
        self.send_start_cmd(message=message)
        return gr.Chatbot.update(
            visible=True
        ), gr.Button.update(visible=False)

    def start_button_after_click(self, history):
        """
        inputs=[self.chatbot],
        outputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset, self.btn_next]
        """
        if self.caller == 0:
            # not single mode
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
                if state == 30:
                    # user input
                    yield history,\
                        gr.Textbox.update(visible=True, interactive=True), \
                        gr.Button.update(visible=True, interactive=True),\
                        gr.Button.update(visible=True, interactive=True),\
                        gr.Button.update(visible=False)
                    return
                elif state == 99:
                    # finish
                    yield history, gr.Textbox.update(visible=True, interactive=False, value="finish!"), \
                        gr.Button.update(visible=True, interactive=False, value="finish!"), gr.Button.update(visible=True, interactive=True),\
                            gr.Button.update(visible=False)
                elif state == 98:
                    yield history, \
                          gr.Textbox.update(visible=False, interactive=False), \
                          gr.Button.update(visible=False, interactive=False),\
                            gr.Button.update(visible=False, interactive=False),\
                            gr.Button.update(visible=True, value=f"Next Agent: 🤖{agent_name} | Next Node: ⭕{node_name}")
                    return
                else:
                    history = self.handle_message(history, state, agent_name, token, node_name)
                    yield history, \
                          gr.Textbox.update(visible=False, interactive=False), \
                          gr.Button.update(visible=False, interactive=False),\
                            gr.Button.update(visible=False, interactive=False),\
                                gr.Button.update(visible=False)

    def send_button_when_click(self, text_user, history:list):
        """
        inputs=[self.text_user, self.chatbot],
        outputs=[self.text_user, self.btn_send, self.chatbot]
        """
        history.append(
            [UIHelper.wrap_css(text_user, "User"), None]
        )
        # print(f"server: send {text_user} to client")
        self.send_message("<USER>"+text_user+self.SIGN["SPLIT"])
        return gr.Textbox.update(value="", visible=False),\
              gr.Button.update(visible=False), \
                history,\
                    gr.Button.update(visible=False)

    def reset_button_when_click(self, history, text_positive, text_negative, text_theme, text_user, btn_send, btn_start, btn_reset):
        """
        self.chatbot, 
        self.text_positive, 
        self.text_negative, 
        self.text_theme, 
        self.text_user,
        self.btn_send,
        self.btn_start,
        self.btn_reset
        self.btn_next
        """
        self.caller = 0
        return None, \
            "", \
                "", \
                    "", \
                        "", \
                            gr.Button.update(value="Restarting...", interactive=False, visible=True),\
                                gr.Button.update(value="Restarting...", interactive=False, visible=True),\
                                    gr.Button.update(value="Restarting...", interactive=False, visible=True),\
                                        gr.Button.update(value="Restarting...", interactive=False, visible=False)
                            
    def reset_button_after_click(self, history, text_positive, text_negative, text_theme, text_user, btn_send, btn_start, btn_reset):
        self.reset()
        self.first_recieve_from_client(reset_mode=True)
        return gr.Chatbot.update(value=None, visible=False),\
            gr.Textbox.update(value=f"{self.cache['positive']}", interactive=True, visible=True),\
                gr.Textbox.update(value=f"{self.cache['negative']}", interactive=True, visible=True),\
                    gr.Textbox.update(value=f"{self.cache['theme']}", interactive=True, visible=True),\
                        gr.Textbox.update(value=f"", interactive=True, visible=False),\
                            gr.Button.update(interactive=True, visible=False, value="Send"),\
                                gr.Button.update(interactive=True, visible=True, value="Start"),\
                                    gr.Button.update(interactive=False, visible=False, value="Restart"),\
                                        gr.Button.update(interactive=True, visible=False, value="Next Agent")
    
    def btn_next_when_click(self):
        yield gr.Button.update(visible=False)
        self.send_message("nothing")
        self.caller = 1         # will note clear the self.data_history
        time.sleep(0.5)
        return
    
    def construct_ui(
        self,
        theme:str=None,
        positive:str=None,
        negative:str=None,
        agents_name:List=None,
        default_cos_play_id:int=None
    ):
        theme = self.cache["theme"] if theme is None else theme
        positive = self.cache["positive"] if positive is None else positive
        negative = self.cache["negative"] if negative is None else negative
        agents_name = self.cache["agents_name"] if agents_name is None else agents_name
        default_cos_play_id = self.cache["default_cos_play_id"] if default_cos_play_id is None else default_cos_play_id
        
        with gr.Blocks(css=gc.CSS) as demo:
            with gr.Row():
                with gr.Column():
                    self.radio_mode = gr.Radio(
                        [Client.AUTO_MODE, Client.SINGLE_MODE],
                        value=Client.AUTO_MODE,
                        interactive=True,
                        label = Client.MODE_LABEL,
                        info = Client.MODE_INFO
                    )
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
                        height= 650,
                        elem_id="chatbot1",
                        label="Dialog",
                        visible=VISIBLE
                    )
                    self.btn_next = gr.Button(
                        value="Next Agent Start",
                        visible=False
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
                    
            self.btn_start.click(
                fn=self.start_button_when_click,
                inputs=[self.text_theme, self.text_positive, self.text_negative, self.radio_choose, self.radio_mode],
                outputs=[self.chatbot, self.btn_start]
            ).then(
                fn=self.start_button_after_click,
                inputs=[self.chatbot],
                outputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset, self.btn_next]
            )
            
            self.btn_send.click(
                fn=self.send_button_when_click,
                inputs=[self.text_user, self.chatbot],
                outputs=[self.text_user, self.btn_send, self.chatbot, self.btn_reset]
            ).then(
                fn=self.start_button_after_click,
                inputs=[self.chatbot],
                outputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset, self.btn_next]
            )
            
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
                    self.btn_reset,
                    self.btn_next
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
                    self.btn_reset,
                    self.btn_next
                ]
            )
            
            self.btn_next.click(
                fn=self.btn_next_when_click,
                inputs=[],
                outputs=[self.btn_next]
            ).then(
                fn=self.start_button_after_click,
                inputs=[self.chatbot],
                outputs=[self.chatbot, self.text_user, self.btn_send, self.btn_reset, self.btn_next]
            )
            
        self.demo = demo


if __name__ == '__main__':
    ui = DebateUI(client_cmd=["python","gradio_backend.py"])
    ui.construct_ui()
    ui.run(share=True)
