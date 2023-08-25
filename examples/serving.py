import yaml
import os
import argparse
with open("/home/aiwaves/longli/agents/examples/game/config.yaml", "r") as file:
    config = yaml.safe_load(file)

for key, value in config.items():
    os.environ[key] = value
import sys
sys.path.append("../src/agents")
from SOP import SOP
from agent import Agent
from State import State
from Environment import Environment
import json

parser = argparse.ArgumentParser(description='A demo of chatbot')
parser.add_argument('--agent', type=str, help='path to SOP json')
parser.add_argument('--config', type=str, help='path to config')


def run(agents,sop,environment,role_to_names,names_to_roles):
    current_state = sop.root
    while True:
        current_agent_name = role_to_names[current_state.name][current_state.begin_role]
        memory = {"role":"user","content":f"{current_agent_name}({current_state.begin_role}):{current_state.begin_query}"}
        print(f"{current_agent_name}({current_state.begin_role}):{current_state.begin_query}")
        environment.update_memory(memory,current_state,roles_to_names)
        while True:
            current_state,current_agent,is_changed,is_user = sop.next(environment,agents,role_to_names)
            if is_changed:
                break
            action = current_agent.step(current_state,is_user)   #component_dict = current_state[self.role[current_node.name]]   current_agent.compile(component_dict) 
            memory = environment.excute_action(action)
            environment.update_memory(memory,current_state,roles_to_names)


with open("/home/aiwaves/longli/agents/examples/game/game.json") as f:
    config = json.load(f)

agents,roles_to_names,names_to_roles = Agent.from_config(config)
sop = SOP.from_config(config)
environment = Environment.from_config(config)
environment.agents = agents

run(agents,sop,environment,roles_to_names,names_to_roles)