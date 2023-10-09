import os
import argparse
import sys
sys.path.append("../../../src/agents")
sys.path.append("../../Gradio_Config")
from agents.utils import extract
from agents.SOP import SOP
from agents.Agent import Agent
from agents.Environment import Environment
from agents.Memory import Memory
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
        elif action.state_begin:
            state = 12
            action.state_begin = False
        elif i>0:
            state = 11
        send_name = f"{action.name}({action.role})"
        Client.send_server(str([state, send_name, res, current_state.name]))
        if state == 30:
            # print("client: waiting for user input")
            data: list = next(Client.receive_server)
            content = ""
            for item in data:
                if item.startswith("<USER>"):
                    content = item.split("<USER>")[1]
                    break
            # print(f"client: received `{content}` from server.")
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

def block_when_next(current_agent, current_state):
    if Client.LAST_USER:
        assert not current_agent.is_user
        Client.LAST_USER = False
        return
    if current_agent.is_user:
        # if next turn is user, we don't handle it here
        Client.LAST_USER = True
        return
    if Client.FIRST_RUN:
        Client.FIRST_RUN = False
    else:
        # block current process
        if Client.mode == Client.SINGLE_MODE:
            Client.send_server(str([98, f"{current_agent.name}({current_agent.state_roles[current_state.name]})", " ", current_state.name]))
            data: list = next(Client.receive_server)

def run(agents,sop,environment):
    while True:      
        current_state,current_agent= sop.next(environment,agents)
        if sop.finished:
            print("finished!")
            Client.send_server(str([99, ' ', ' ', 'done']))
            os.environ.clear()
            break
        block_when_next(current_agent, current_state)
        action = current_agent.step(current_state)   #component_dict = current_state[self.role[current_node.name]]   current_agent.compile(component_dict) 
        gradio_process(action,current_state)
        memory = process(action)
        environment.update_memory(memory,current_state)

def prepare(agents, sop, environment):
    client = Client()
    Client.send_server = client.send_message

    requirement_game_name = extract(sop.states['design_state'].environment_prompt,"target")
    client.send_message(
        {
            "requirement": requirement_game_name,
            "agents_name": convert2list4agentname(sop)[0],
            # "only_name":  DebateUI.convert2list4agentname(sop)[1],
            "only_name":  convert2list4agentname(sop)[0],
            "default_cos_play_id": -1,
            "api_key": os.environ["API_KEY"]
        }
    )
    # print(f"client: send {requirement_game_name}")
    client.listening_for_start_()
    client.mode = Client.mode = client.cache["mode"]
    new_requirement = Client.cache['requirement']
    os.environ["API_KEY"] = client.cache["api_key"]
    for state in sop.states.values():
        state.environment_prompt = state.environment_prompt.replace("<target>a snake game with python</target>", f"<target>{new_requirement}</target>")
    # print(f"client: received {Client.cache['requirement']} from server.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A demo of chatbot')
    parser.add_argument('--agent', type=str, help='path to SOP json', default="config.json")
    args = parser.parse_args()
    
    agents,sop,environment = init(args.agent)
    # add================================
    prepare(agents, sop, environment)
    # ===================================
    run(agents,sop,environment)
