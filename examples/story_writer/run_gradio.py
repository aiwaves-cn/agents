import sys
from gradio_config import CSS, OBJECT_INFO, BUBBLE_CSS, init, ROLE_2_NAME
import gradio as gr
sys.path.append("../../src/agents")
# from agent import Agent
# from sop import SOP, controller
# from serving import autorun, init_agents
import time
# import sys
import os

# sys.path.append("../../src/agents")
from agent import Agent
from sop import SOP, controller

def run(sop: SOP, controller: controller, name="A神", role="user"):
    while True:
        current_node = sop.current_node
        print(current_node.name)
        query = input(f"{name}({role}):")
        current_memory = {"role": "user", "content": f"{name}({role}):{query}"}
        sop.shared_memory["chat_history"].append(current_memory)
        while True:
            next_node, next_role = controller.next(sop, controller)
            flag = next_node.is_interactive
            current_node = next_node
            sop.current_node = current_node
            if next_role == role:
                break
            current_agent = sop.agents[next_role]
            current_agent = sop.agents[next_role]
            response = current_agent.step(
                query, role, name, current_node, sop.temperature
            )
            all = ""
            for res in response:
                all += res
                print(res, end="")
                time.sleep(0.02)
            print()
            sop.shared_memory["chat_history"].append(
                {"role": "user", "content": all}
            )

            if flag:
                break
            
            
def autorun(sop: SOP, controller: controller,begin_name,begin_role,begin_query):
    current_node = sop.current_node
    print(current_node.name)
    current_memory = {"role": "user", "content": f"{begin_name}({begin_role}):{begin_query}"}
    sop.update_memory(current_memory)
    
    while True:
        next_node, next_role = controller.next(sop)
        current_node = next_node
        sop.current_node = current_node
        current_agent = sop.agents[next_role]
        current_agent = sop.agents[next_role]
        response = current_agent.step(
            sop.shared_memory["chat_history"][-1]["content"],current_node, sop.temperature
        )
        all = f""
        for res in response:
            all += res
            yield res, next_role
            # print(res, end="")
            # time.sleep(0.02)
        print()
        current_memory = (
            {"role": "user", "content": all}
        )
        
        sop.update_memory(current_memory)
        
def init_agents(sop):
    for name,role in sop.agents_role_name.items():
        agent = Agent(role,name)
        sop.agents[role] = agent

"""全局的对话，只用于回答"""
global_dialog = {
    "user":[], 
    "agent":{
        
    },
    "system":[]
}

"""为每个输出弄一个css"""
def wrap_css(content, name) -> str:
    """content: 输出的内容 name: 谁的输出"""
    """确保name这个人是存在的"""
    assert name in OBJECT_INFO, f"'{name}' not in {OBJECT_INFO.keys()}"
    """取出这个人的全部信息"""
    output = ""
    info = OBJECT_INFO[name]
    if info["id"] == "USER":
        # 背景颜色 名字 字体颜色 字体大小 内容 图片地址
        output = BUBBLE_CSS["USER"].format(
            info["bubble_color"],
            name,
            info["text_color"],
            info["font_size"],
            content,
            info["head_url"]
        )
    elif info["id"] == "SYSTEM":
        # 背景颜色 字体大小 字体颜色 名字 内容
        output = BUBBLE_CSS["SYSTEM"].format(
            info["bubble_color"],
            info["font_size"],
            info["text_color"],
            name,
            content
        )
    elif info["id"] == "AGENT":
        # 图片地址 背景颜色 名字 字体颜色 字体大小 内容
        output = BUBBLE_CSS["AGENT"].format(
            info["head_url"],
            info["bubble_color"],
            name,
            info["text_color"],
            info["font_size"],
            content,
        )
    else:
        assert False
    return output

def get_new_message(message, history):
    """将用户的输入存下来"""
    global_dialog["user"].append(message)
    return "", \
        history + [[wrap_css(name="User", content=message), None]]

def get_response(history):
    """此处的history都是有css wrap的，所以一般都不会用，只要是模型的输出"""
    # agent_response = generate_response(history)
    for agent_response in generate_response(history):
        # time.sleep(0.05)
        print(agent_response)
        if len(agent_response) >= 2:
            output = "**OUTPUT**<br>"
        else:
            output = ""
            
        for name in global_dialog["agent"]:
            if name not in agent_response:
                global_dialog["agent"][name].append(None)
            else:
                global_dialog["agent"][name].append(agent_response[name])
                output = f"{output}<br>{wrap_css(content=agent_response[name], name=name)}"
        
        if output == "":
            """表示没有输出"""
            output = wrap_css(content="没有任何输出", name="System")
        
        history[-1] = (history[-1][0], output)
        yield history

def generate_response(history):
    """模型要做的，传入的就是gloabl_dialog"""
    global sop, controller
    # response = {"Mike": "这是来自Mike的输入。第一行很长<br>这是一个测试的例子", 
    #         "John": "这是来自John的输入。第一行很长。<br>这是一个测试的例子"
    #         }
    
    # return_dict = {}
    # for name in response:
    #     return_dict[name] = ""
    #     for i, _ in enumerate(response["Mike"]):
    #         return_dict[name] = response[name][0:i+1]
    #         yield return_dict
    # query = global_dialog["user"][-1]
    content = ""
    wait = "."
    for i, role in autorun(sop, controller, begin_role="大纲写作者1", begin_name="小亮", begin_query="请根据要求开始撰写第一版大纲初稿"):
        content += i
        # if ":" in content:
        # wait = "."
        
        # yield {ROLE_2_NAME[role]: content[content.find(":")+1:]}
        yield {ROLE_2_NAME[role]: content}
        # else:
            # if len(wait) == 6:
            #     wait = ""
            # wait += "."
            # yield {"wait": wait}


if __name__ == '__main__':
    sop = SOP("story.json")
    controller = controller(sop.controller_dict)
    init_agents(sop)
    
    init("story.json")
    
    for name in OBJECT_INFO:
        if name not in ["System", "User"]:
            global_dialog["agent"][name] = []
    print(global_dialog)
    
    with gr.Blocks(css=CSS) as demo:
        chatbot = gr.Chatbot(elem_id="chatbot1")  # elem_id="warning", elem_classes="feedback"
        
        msg = gr.Textbox()
        clear = gr.Button("Clear")

        """第一个参数指的是函数，第二个参数是输入Component，第三个是输出Component"""
        """submit是单击时的操作，then是单击后的操作。chatbot一个是要两次的结果，就是用户输入展示一次，回复再展示一次"""
        msg.submit(get_new_message, [msg, chatbot], [msg, chatbot], queue=False).then(
            get_response, chatbot, chatbot
        )
        clear.click(lambda: None, None, chatbot, queue=False)
    
    demo.queue()
    demo.launch()
    
