import sys
sys.path.append("../../Gradio_Config")

import os
from gradio_base import WebUI, UIHelper, PORT, HOST, Client
from gradio_config import GradioConfig as gc
from typing import List, Tuple, Any
import gradio as gr

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
        bufsize: int = 1024,
        ui_name: str = "CodeUI"
    ):
        super(CodeUI, self).__init__(client_cmd, socket_host, socket_port, bufsize, ui_name)
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
 

if __name__ == '__main__':
    # 启动client_server_file并自动传递消息
    ui = CodeUI(client_cmd=["python","run.py"])
    # 构建映射关系
    # GradioConfig.add_agent(agents_name=ui.all_agents_name)
    # 搭建前端并建立监听事件
    ui.construct_ui()
    # 启动运行
    ui.run(share=True)
