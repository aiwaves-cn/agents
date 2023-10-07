import sys
sys.path.append("../../Gradio_Config")
import os
from gradio_base import WebUI, UIHelper, PORT, HOST
from gradio_config import GradioConfig as gc
from gradio_config import StateConfig as sc
from typing import List
import gradio as gr


class NovelUI(WebUI):
    
    node2show = {
        "Node 1": "Write Character Settings and Script Outlines🖊️",
        "Node 2": "Expand the first chapter<br>✍️",
        "Node 3": "Expand the second chapter<br>✍️",
        "Node 4": "Expand the third chapter<br>✍️",
        "state1": "Perform the first plot<br>🎭",
        "state2": "Perform the second plot<br>🎭",
        "state3": "Perform the third plot<br>🎭",
        "state4": "Perform the forth plot<br>🎭"
    }
    show2node = {}
    
    def render_and_register_ui(self):
        self.agent_name:list = [self.cache["agents_name"]] if isinstance(self.cache["agents_name"], str) else self.cache['agents_name']
        gc.add_agent(self.agent_name)
    
    def handle_message(self, history:list, record:list, state, agent_name, token, node_name):
        RECORDER = True if state//10 ==2 else False
        render_data:list = record if RECORDER else history
        data:list = self.data_recorder if RECORDER else self.data_history
        if state % 10 == 0:
            data.append({agent_name: token})
        elif state % 10 == 1:
            # Same state. Need to add new bubble in same bubble.
            data[-1][agent_name] += token
        elif state % 10 == 2:
            # New state. Need to add new bubble.
            render_data.append([None, ""])
            data.clear()
            data.append({agent_name: token})
        else:
            assert False, "Invalid state."
        render_data = self.render_bubble(render_data, data, node_name, render_node_name=True)
        if RECORDER:
            record = render_data
        else:
            history = render_data
        return history, record
    
    def update_progress(self, node_name, node_schedule):
        DONE = True
        node_name = self.node2show[node_name]
        for idx, name in enumerate(self.cache['nodes_name']):
            name = self.node2show[name]
            self.progress_manage['show_type'][idx] = "active-show-up"
            self.progress_manage['show_content'][idx] = ("" if name != node_name else "💬",)
            if name == node_name:
                DONE = False
                self.progress_manage['schedule'][idx] = node_schedule
            elif DONE:
                self.progress_manage['schedule'][idx] = 100
            elif DONE == False:
                self.progress_manage['schedule'][idx] = 0
        if self.cache['nodes_name'].index(self.show2node[node_name]) ==  len(self.cache['nodes_name']) - 2 and node_schedule == 100:
            self.progress_manage['schedule'][-1] = 100
        return sc.FORMAT.format(
            sc.CSS,
            sc.update_states(
                current_states=self.progress_manage["schedule"],
                current_templates=self.progress_manage["show_type"],
                show_content=self.progress_manage["show_content"]
            )
        )
    
    def __init__(
        self,
        client_cmd: list,
        socket_host: str = HOST,
        socket_port: int = PORT,
        bufsize: int = 1024,
        ui_name: str = "NovelUI"
    ):
        super(NovelUI, self).__init__(client_cmd, socket_host, socket_port, bufsize, ui_name)
        self.first_recieve_from_client()
        for item in ['agents_name', 'nodes_name', 'output_file_path', 'requirement', "api_key"]:
            assert item in self.cache
        self.progress_manage = {
            "schedule": [None for _ in range(len(self.cache['nodes_name']))],
            "show_type": [None for _ in range(len(self.cache['nodes_name']))],
            "show_content": [None for _ in range(len(self.cache['nodes_name']))]
        }
        NovelUI.show2node = {NovelUI.node2show[_]:_ for _ in NovelUI.node2show.keys()}
        
    def construct_ui(self):
        with gr.Blocks(css=gc.CSS) as demo:
            with gr.Column():
                self.progress = gr.HTML(
                    value=sc.FORMAT.format(
                        sc.CSS,
                        sc.create_states([NovelUI.node2show[name] for name in self.cache['nodes_name']], False)
                    )
                )
                with gr.Row():
                    with gr.Column(scale=6):
                        self.chatbot = gr.Chatbot(
                            elem_id="chatbot1",
                            label="Dialog",
                            height=500
                        )
                        self.text_api = gr.Textbox(
                            value = self.cache["api_key"],
                            placeholder="openai key",
                            label="Please input valid openai key for gpt-3.5-turbo-16k."
                        )
                        with gr.Row():
                            self.text_requirement = gr.Textbox(
                                placeholder="Requirement of the novel",
                                value=self.cache['requirement'],
                                scale=9
                            )
                            self.btn_start = gr.Button(
                                value="Start",
                                scale=1
                            )
                        self.btn_reset = gr.Button(
                            value="Restart",
                            visible=False
                        )
                    with gr.Column(scale=5):
                        self.chat_record = gr.Chatbot(
                            elem_id="chatbot1",
                            label="Record",
                            visible=False
                        )
                        self.file_show = gr.File(
                            value=[],
                            label="FileList",
                            visible=False
                        )
                        self.chat_show = gr.Chatbot(
                            elem_id="chatbot1",
                            label="FileRead",
                            visible=False
                        )
            
                # ===============Event Listener===============
                self.btn_start.click(
                    fn=self.btn_start_when_click,
                    inputs=[self.text_requirement, self.text_api],
                    outputs=[self.chatbot, self.chat_record, self.btn_start, self.text_requirement]
                ).then(
                    fn=self.btn_start_after_click,
                    inputs=[self.chatbot, self.chat_record],
                    outputs=[self.progress, self.chatbot, self.chat_record, self.chat_show, self.btn_start, self.btn_reset, self.text_requirement, self.file_show]
                )
                self.btn_reset.click(
                    fn=self.btn_reset_when_click,
                    inputs=[],
                    outputs=[self.progress, self.chatbot, self.chat_record, self.chat_show, self.btn_start, self.btn_reset, self.text_requirement, self.file_show]
                ).then(
                    fn=self.btn_reset_after_click,
                    inputs=[],
                    outputs=[self.progress, self.chatbot, self.chat_record, self.chat_show, self.btn_start, self.btn_reset, self.text_requirement, self.file_show]
                )
                self.file_show.select(
                    fn=self.file_when_select,
                    inputs=[self.file_show],
                    outputs=[self.chat_show]
                )
                # ===========================================
            self.demo = demo
            
    def btn_start_when_click(self, text_requirement:str, api_key:str):
        """
        inputs=[self.text_requirement],
        outputs=[self.chatbot, self.chat_record, self.btn_start, self.text_requirement]
        """
        history = [[UIHelper.wrap_css(content=text_requirement, name="User"), None]]
        yield history,\
            gr.Chatbot.update(visible=True),\
            gr.Button.update(interactive=False, value="Running"),\
            gr.Textbox.update(value="", interactive=False)
        self.send_start_cmd({'requirement': text_requirement, "api_key": api_key})
        return 
        
    def btn_start_after_click(self, history:List, record):
        def walk_file():
            print("file:", self.cache['output_file_path'])
            files = []
            for _ in os.listdir(self.cache['output_file_path']):
                if os.path.isfile(self.cache['output_file_path']+'/'+_):
                    files.append(self.cache['output_file_path']+'/'+_)
            
            return files
        """
        inputs=[self.chatbot, self.chat_record],
        outputs=[self.progress, self.chatbot, self.chat_record, self.chat_show, self.btn_start, self.btn_reset, self.text_requirement, self.file_show]
        """
        self.data_recorder = list()
        self.data_history = list()
        receive_server = self.receive_server
        while True:
            data_list: List = receive_server.send(None)
            for item in data_list:
                data = eval(item)
                assert isinstance(data, list)
                state, agent_name, token, node_name, node_schedule = data
                assert isinstance(state, int)
                fs:List = walk_file()
                # 10/11/12 -> history
                # 20/21/22 -> recorder
                # 99 -> finish
                # 30 -> register new agent
                assert state in [10, 11, 12, 20, 21, 22, 99, 30]
                if state == 30:
                    # register new agent.
                    gc.add_agent(eval(agent_name))
                    continue
                if state == 99:
                    # finish
                    yield gr.HTML.update(value=self.update_progress(node_name, node_schedule)),\
                        history,\
                        gr.Chatbot.update(visible=True, value=record),\
                        gr.Chatbot.update(visible=True),\
                        gr.Button.update(visible=True, interactive=False, value="Done"),\
                        gr.Button.update(visible=True, interactive=True),\
                        gr.Textbox.update(visible=True, interactive=False),\
                        gr.File.update(value=fs, visible=True, interactive=True)
                    return
                
                history, record = self.handle_message(history, record, state, agent_name, token, node_name)
                # [self.progress, self.chatbot, self.chat_record, self.chat_show, self.btn_start, self.btn_reset, self.text_requirement, self.file_show]
                yield gr.HTML.update(value=self.update_progress(node_name, node_schedule)),\
                        history,\
                        gr.Chatbot.update(visible=True, value=record),\
                        gr.Chatbot.update(visible=False),\
                        gr.Button.update(visible=True, interactive=False),\
                        gr.Button.update(visible=False, interactive=True),\
                        gr.Textbox.update(visible=True, interactive=False),\
                        gr.File.update(value=fs, visible=True, interactive=True)
    
    def btn_reset_when_click(self):
        """
        inputs=[],
        outputs=[self.progress, self.chatbot, self.chat_record, self.chat_show, self.btn_start, self.btn_reset, self.text_requirement, self.file_show]
        """
        return gr.HTML.update(value=sc.create_states(states_name=self.cache['nodes_name'])),\
            gr.Chatbot.update(value=None),\
            gr.Chatbot.update(value=None, visible=False),\
            gr.Chatbot.update(value=None, visible=False),\
            gr.Button.update(value="Restarting...", visible=True, interactive=False),\
            gr.Button.update(value="Restarting...", visible=True, interactive=False),\
            gr.Textbox.update(value="Restarting...", interactive=False, visible=True),\
            gr.File.update(visible=False)
    
    def btn_reset_after_click(self):
        """
        inputs=[],
        outputs=[self.progress, self.chatbot, self.chat_record, self.chat_show, self.btn_start, self.btn_reset, self.text_requirement, self.file_show]
        """
        self.reset()
        self.first_recieve_from_client(reset_mode=True)
        return gr.HTML.update(value=sc.create_states(states_name=self.cache['nodes_name'])),\
            gr.Chatbot.update(value=None),\
            gr.Chatbot.update(value=None, visible=False),\
            gr.Chatbot.update(value=None, visible=False),\
            gr.Button.update(value="Start", visible=True, interactive=True),\
            gr.Button.update(value="Restart", visible=False, interactive=False),\
            gr.Textbox.update(value="", interactive=True, visible=True),\
            gr.File.update(visible=False)
    
    def file_when_select(self, file_obj):
        """
        inputs=[self.file_show],
        outputs=[self.chat_show]
        """
        CODE_PREFIX = "```json\n{}\n```"
        with open(file_obj.name, "r", encoding='utf-8') as f:
            contents = f.readlines()
        codes = "".join(contents)
        return [[CODE_PREFIX.format(codes),None]]
      
   
if __name__ == '__main__':
    ui = NovelUI(client_cmd=["python","gradio_backend.py"])
    ui.construct_ui()
    ui.run(share=True)