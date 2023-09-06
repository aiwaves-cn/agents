import yaml
import os
import argparse
import sys
sys.path.append("../../../src/agents")
sys.path.append("../../cfg")
from SOP import SOP
from Agents import Agent
from Environments import Environment
from gradio_base import Client
from gradio_example import DebateUI

# Client.server.send(str([state, name, chunk, node_name])+"<SELFDEFINESEP>")
# Client.cache["start_agent_name"]
# state = 10, 11, 12, 30

def init(config):
    
    agents,roles_to_names,names_to_roles = Agent.from_config(config)
    sop = SOP.from_config(config)
    environment = Environment.from_config(config)
    environment.agents = agents
    environment.roles_to_names,environment.names_to_roles = roles_to_names,names_to_roles
    sop.roles_to_names,sop.names_to_roles = roles_to_names,names_to_roles
    
    
    topic = input("topic:")
    Affirmative_topic = input("Affirmative topic:")
    Negative_topic = input("Negative topic")
    topic = f"The debate topic is as follows: \n<debate topic>\n{topic} Affirmative viewpoint: {Affirmative_topic}, negative viewpoint: {Negative_topic}.\n<debate topic>\n, now , begin to discuss!"
    sop.states["Affirmative_Task_Allocation_state"].begin_query = topic
    sop.states["Negative_Task_Allocation_state"].begin_query = topic
    return agents,sop,environment



def run(agents,sop,environment,is_gradio = False):
    while True:
        current_state,current_agent= sop.next(environment,agents)
        if sop.finished:
            print("finished!")
            break
        action = current_agent.step(current_state,environment,is_gradio)   #component_dict = current_state[self.role[current_node.name]]   current_agent.compile(component_dict) 
        response = action["response"]
        for i,res in enumerate(response):
            state = 10
            if action["is_begin"]:
                state = 12
            elif i>0:
                state = 11
            elif action["is_user"]:
                state = 30
            
            Client.server.send(str([state, action["name"], res, current_state.name])+"<SELFDEFINESEP>")
        
        environment.update(action,current_state)

parser = argparse.ArgumentParser(description='A demo of chatbot')
parser.add_argument('--config', type=str, help='path to config')
args = parser.parse_args()
with open(args.config, "r") as file:
    config = yaml.safe_load(file)

for key, value in config.items():
    os.environ[key] = value
    

agents,sop,environment = init("debate.json")
run(agents,sop,environment)