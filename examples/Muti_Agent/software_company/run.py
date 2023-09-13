import yaml
import os
import argparse
import sys
sys.path.append("../../../src/agents")
sys.path.append("../../Gradio_Config")
from SOP import SOP
from Agent import Agent
from Environment import Environment
from Memory import Memory
from gradio_base import Client, convert2list4agentname



def process(action):
    response = action.response
    send_name = action.name
    send_role = action.role
    if not action.is_user:
        print(f"{send_name}({send_role}):{response}")
    memory = Memory(send_role, send_name, response)
    return memory

def gradio_process(action,current_state):
    response = action.response
    all = ""
    for i,res in enumerate(response):
        all+=res
        state = 10
        if action.is_user:
            state = 30
            print("state:", state)
        elif action.state_begin:
            state = 12
            action.state_begin = False
        elif i>0:
            state = 11
        print("long:", state)
        send_name = f"{action.name}({action.role})"
        Client.send_server(str([state, send_name, res, current_state.name]))
        if state == 30:
            """阻塞当前进程，等待接收"""
            print("client:阻塞等待输入")
            data: list = next(Client.receive_server)
            content = ""
            for item in data:
                if item.startswith("<USER>"):
                    content = item.split("<USER>")[1]
                    break
            print(f"client:接收到了`{content}`")
            action.response = content
            break
        else:
            action.response = all

def init(config): 
    if not os.path.exists("logs"):
        os.mkdir("logs")
    sop = SOP.from_config(config)
    agents,roles_to_names,names_to_roles = Agent.from_config(config)
    environment = Environment.from_config(config)
    environment.agents = agents
    environment.roles_to_names,environment.names_to_roles = roles_to_names,names_to_roles
    sop.roles_to_names,sop.names_to_roles = roles_to_names,names_to_roles
    for name,agent in agents.items():
        agent.environment = environment
    return agents,sop,environment

def run(agents,sop,environment):
    while True:      
        current_state,current_agent= sop.next(environment,agents)
        if sop.finished:
            print("finished!")
            os.environ.clear()
            break
        action = current_agent.step(current_state)   #component_dict = current_state[self.role[current_node.name]]   current_agent.compile(component_dict) 
        gradio_process(action,current_state)
        memory = process(action)
        environment.update_memory(memory,current_state)



def prepare(agents, sop, environment):
    """建立连接+发送数据+等待接收和启动命令"""
    client = Client()
    Client.send_server = client.send_message
    # 这边需要解析一下，到时候传的时候还要在拼起来

    client.send_message(
        {
            "requirement": f"{sop.states['design_state'].begin_query}",
            "agents_name": convert2list4agentname(sop)[0],
            # "only_name":  DebateUI.convert2list4agentname(sop)[1],
            "only_name":  convert2list4agentname(sop)[0],
            "default_cos_play_id": -1
        }
    )
    print(f"client: {list(agents.keys())}")
    print(f"client:发送的值为{sop.states['design_state'].begin_query}")
    client.listening_for_start_()
    """覆盖参数"""
    sop.states['design_state'].begin_query = Client.cache['requirement']
    print(f"client:传入的值为{Client.cache['requirement']}")


if __name__ == '__main__':
    GRADIO = True
    parser = argparse.ArgumentParser(description='A demo of chatbot')
    parser.add_argument('--agent', type=str, help='path to SOP json', default="config.json")
    args = parser.parse_args()
    
    agents,sop,environment = init(args.agent)
    
    if GRADIO:
        prepare(agents, sop, environment)

    run(agents,sop,environment)
