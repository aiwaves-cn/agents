import yaml
import os
import argparse
import sys
sys.path.append("../src/agents")
from SOP import SOP
from Agents import Agent
from Environments import Environment
from Memorys import Memory

def init(config): 
    if not os.path.exists("logs"):
        os.mkdir("logs")
    agents,roles_to_names,names_to_roles = Agent.from_config(config)
    sop = SOP.from_config(config)
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
        user_input = input(f"{current_agent.name}:") if current_agent.is_user else ""
        
        action = current_agent.step(current_state,environment,user_input)   #component_dict = current_state[self.role[current_node.name]]   current_agent.compile(component_dict) 
        memory = action.process()
        environment.update_memory(memory,current_state)
        

parser = argparse.ArgumentParser(description='A demo of chatbot')
parser.add_argument('--agent', type=str, help='path to SOP json')
parser.add_argument('--config', type=str, help='path to config')
args = parser.parse_args()
with open(args.config, "r") as file:
    config = yaml.safe_load(file)

for key, value in config.items():
    os.environ[key] = value
    

agents,sop,environment = init(args.agent)
run(agents,sop,environment)


for key, value in config.items():
    del os.environ[key]