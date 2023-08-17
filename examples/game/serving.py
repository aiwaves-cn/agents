import time
import sys
import os


sys.path.append("../../src/agents")
from agent import Agent
from sop import SOP, controller

def autorun(sop: SOP, controller: controller,begin_name,begin_role,begin_query):
    current_node = sop.current_node
    print(current_node.name)
    current_memory = {"role": "user", "content": f"{begin_name}({begin_role}):{begin_query}"}
    sop.update_memory(current_memory)
    
    while True:
        next_node, next_role = controller.next(sop)
        if next_node != current_node:
            sop.send_memory(next_node)
            
        current_node = next_node
        sop.current_node = current_node
        current_agent = sop.agents[current_node.name][next_role]
        response = current_agent.step(
            current_node, sop.temperature
        )
        all = f""
        for res in response:
            all += res
            print(res, end="")
            time.sleep(0.02)
        print()
        current_memory = (
            {"role": "user", "content": all}
        )
        
        sop.update_memory(current_memory)
        
def init_agents(sop):
    for node_name,node_agents in sop.agents_role_name.items():
        for name,role in node_agents.items():
            agent = Agent(role,name)
            if node_name not in sop.agents:
                sop.agents[node_name] = {}
            sop.agents[node_name][role] = agent

if __name__ == "__main__":
    sop = SOP("game.json")
    controller = controller(sop.controller_dict)
    init_agents(sop)
    autorun(sop, controller,begin_name="球球",begin_role="裁判员",begin_query="现在开始真假杨不凡游戏")
