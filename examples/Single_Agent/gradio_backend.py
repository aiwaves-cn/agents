import yaml
import os
import argparse
import sys
sys.path.append("../src/agents")
sys.path.append("Gradio_Config")
from agents.SOP import SOP
from agents.Agent import Agent
from agents.Environment import Environment
from agents.Memory import Memory
from gradio_base import Client

def process(action):
    response = action.response
    send_name = action.name
    send_role = action.role
    parse = f"{send_name}:"
    # The third person in the dialogue was deleted.
    while parse in response:
        index = response.index(parse) + len(parse)
        response = response[index:]
    if not action.is_user:
        print(f"{send_name}({send_role}):{response}")
    memory = Memory(send_role, send_name, response)
    return memory

def gradio_process(action,current_state):
    response = action.response
    res_dict = action.res_dict
    all = ""
    response_list = [response]
    if "recommend" in res_dict:
        response_list.append(res_dict["recommend"])
        
    i = 0
    for r in response_list:
        for res in r:
            all+=res
            state = 10
            if action.is_user:
                state = 30
            elif action.state_begin:
                state = 12
                action.state_begin = False
            elif i>0:
                state = 11
            i+=1
            Client.send_server(str([state, action.name, res, current_state.name]))
            if state == 30:
                # print("client: waiting for input.")
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

def run(agents,sop,environment):
    while True:      
        current_state,current_agent= sop.next(environment,agents)
        if sop.finished:
            print("finished!")
            Client.send_server(str([99, ' ', ' ', current_state.name]))
            os.environ.clear()
            break
        action = current_agent.step(current_state,True)   #component_dict = current_state[self.role[current_node.name]]   current_agent.compile(component_dict) 
        gradio_process(action,current_state)
        memory = process(action)
        environment.update_memory(memory,current_state)
        

def prepare(agents, sop, environment):
    client = Client()
    Client.send_server = client.send_message
    client.send_message(
        {
            # "hello": f"{sop.root.begin_query}",  # sop.states['knowledge_response'].begin_query     sop.states.begin_query
            "user_first": agents[sop.roles_to_names[sop.root.name][sop.root.begin_role]].is_user,
            "agent_name": f"{list(agents.keys())[0]}"  # 
        }
    )
    client.listening_for_start_()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A demo of chatbot')
    parser.add_argument('--agent', type=str, help='path to SOP json')
    args = parser.parse_args()

    agents,sop,environment = init(args.agent)
    # add ==================================
    prepare(agents, sop, environment)
    # ======================================
    run(agents,sop,environment)
