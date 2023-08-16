import time
import sys
import os


sys.path.append("../../src/agents")
from agent import Agent
from sop import SOP, controller


def run(sop: SOP, controller: controller, name="A神", role="user"):
    while True:
        current_node = sop.current_node
        print(current_node.name)
        query = input(f"{name}({role}):")
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
            all = ""
            for res in response:
                all += res
                print(res, end="")
                time.sleep(0.02)
            print()
            sop.shared_memory["chat_history"].append(
                {"role": "user", "content": all}
            )

            if flag:
                break
            
            
def step(sop: SOP, controller: controller):
    current_node = sop.current_node
    if len(current_node.next_nodes) == 1:
        next_node = "0"
    else:
        next_node = controller.judge(current_node, sop.shared_memory["chat_history"],summary = sop.shared_memory["summary"],environment_prompt = sop.environment_prompt)
    next_node = current_node.next_nodes[next_node]
    if len(sop.agents.keys()) == 1:
        next_role = list(sop.agents.keys())[0]
    else:
        next_role = controller.allocate_task(
            next_node, sop.shared_memory["chat_history"],summary = sop.shared_memory["summary"],environment_prompt = sop.environment_prompt
        )
    return next_node, next_role


def autorun(sop: SOP, controller: controller, role="大纲写作者1", name="小亮"):
    current_node = sop.current_node
    print(current_node.name)
    current_memory = {"role": "user", "content": f"{name}({role}):请根据要求写大纲。"}
    sop.updatememory(current_memory)
    
    while True:
        next_node, next_role = step(sop, controller)
        current_node = next_node
        sop.current_node = current_node
        current_agent = sop.agents[next_role]
        current_agent = sop.agents[next_role]
        response = current_agent.step(
            sop.shared_memory["chat_history"][-1]["content"], role, name, current_node, sop.temperature
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
        
        sop.updatememory(current_memory)
        
def init_agents(sop):
    for name,role in sop.agents_role_name.items():
        agent = Agent(role,name)
        sop.agents[role] = agent

if __name__ == "__main__":
    sop = SOP("story.json")
    controller = controller(sop.controller_dict)
    init_agents(sop)
    autorun(sop, controller)