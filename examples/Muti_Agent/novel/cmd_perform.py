import yaml
import os
import argparse
import random
import sys
sys.path.append("../../../src/agents")
sys.path.append("../../Gradio_Config")
from agents.SOP import SOP
from agents.Agent import Agent
from agents.Environment import Environment
from gradio_base import Client
from agents.Memory import Memory
# from gradio_example import DebateUI

# Client.server.send(str([state, name, chunk, node_name])+"<SELFDEFINESEP>")
# Client.cache["start_agent_name"]
# state = 10, 11, 12, 30

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
            break
        
        if current_state.is_begin:
            print("The new state has begun!")
            # clear agent's long_term_memory
            for agent_name, agent_class in agents.items():
                agent_class.long_term_memory = []
            # clear environment.shared_memory["long_term_memory"]
            environment.shared_memory["long_term_memory"] = []
        
        action = current_agent.step(current_state,"")   #component_dict = current_state[self.role[current_node.name]]   current_agent.compile(component_dict) 
        response = action.response
        ans = ""
        for i,res in enumerate(response):
            # if res == '\n\n':
            #     continue
            state = 10
            if action.state_begin:
                state = 12
                action.state_begin = False
            elif i>0:
                state = 11
            elif action.is_user:
                state = 30
            Client.send_server(str([state, action.name, res, current_state.name, 50]))
            # Client.server.send(str([state, action["name"], res, current_state.name])+"<SELFDEFINESEP>")
            ans += res
            print(res)
        print(ans)
        environment.update_memory(Memory(action.name, action.role, ans),current_state)

if __name__ == '__main__':
    agents,sop,environment = init("novel_outline.json")
    run(agents,sop,environment)