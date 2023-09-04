import yaml
import os
import argparse
import sys
sys.path.append("../../../src/agents")
from SOP import SOP
from Agents import Agent
from Environments import Environment

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

def run(agents,sop,environment):
    while True:
        current_state,current_agent= sop.next(environment,agents)
        if sop.finished:
            print("finished!")
            break
        action = current_agent.step(current_state,environment)   #component_dict = current_state[self.role[current_node.name]]   current_agent.compile(component_dict) 
        environment.update(action,current_state)

parser = argparse.ArgumentParser(description='A demo of chatbot')
parser.add_argument('--config', type=str, help='path to config')
args = parser.parse_args()
with open("args.config", "r") as file:
    config = yaml.safe_load(file)

for key, value in config.items():
    os.environ[key] = value
    

agents,sop,environment = init("/home/aiwaves/longli/agents/examples/Muti_Agent/debate/debate.json")
run(agents,sop,environment)