import sys
from serving import run, step
from gradio_config import CSS, OBJECT_INFO, BUBBLE_CSS, init
import gradio as gr

sys.path.append("../../src/agents")
from agent import Agent
from sop import SOP, controller

def act(query,name="A神", role="user"):
    global sop, controller
    current_node = sop.current_node
    current_memory = {"role": "user", "content": f"{name}({role}):{query}"}
    sop.shared_memory["chat_history"].append(current_memory)
    while True:
        next_node, next_role = step(sop, controller)
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
        print(f"{current_agent.name}({current_agent.role}):", end="")
        all = f"{current_agent.name}({current_agent.role}):"
        for res in response:
            all += res
            yield res
        sop.shared_memory["chat_history"].append(
            {"role": "assistant", "content": all}
        )

        if flag:
            break

"""全局的对话，只用于回答"""
global_dialog = {
    "user":[], 
    "agent":{
        "吴家隆":[],
        "John":[],
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
    global sop, controller
    """模型要做的，传入的就是gloabl_dialog"""
    
    # response = {"Mike": "这是来自Mike的输入。第一行很长<br>这是一个测试的例子", 
    #         "John": "这是来自John的输入。第一行很长。<br>这是一个测试的例子"
    #         }
    
    # return_dict = {}
    # for name in response:
    #     return_dict[name] = ""
    #     for i, _ in enumerate(response["Mike"]):
    #         return_dict[name] = response[name][0:i+1]
    #         yield return_dict
    query = global_dialog["user"][-1]
    content = ""
    for i in act(query):
        content += i
        yield {"吴家隆": content}



if __name__ == '__main__':
    
        
    agent = Agent("眼科客服", "吴家隆")
    sop = SOP("eye_newnew.json")
    controller = controller(sop.controller_dict)
    sop.agents = {"眼科客服": agent}
    agent.sop = sop

    init()
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
    
