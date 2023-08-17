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
            next_node, next_role = controller.next(sop, controller)
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
            
            
def autorun(sop: SOP, controller: controller,begin_name,begin_role,begin_query):
    current_node = sop.current_node
    print(current_node.name)
    current_memory = {"role": "user", "content": f"{begin_name}({begin_role}):{begin_query}"}
    sop.update_memory(current_memory)
    
    while True:
        next_node, next_role = controller.next(sop)
        current_node = next_node
        sop.current_node = current_node
        current_agent = sop.agents[next_role]
        current_agent = sop.agents[next_role]
        response = current_agent.step(
            sop.shared_memory["chat_history"][-1]["content"],current_node, sop.temperature
        )
        all = f""
        for res in response:
            all += res
            yield res, next_role
            # print(res, end="")
            # time.sleep(0.02)
        print()
        current_memory = (
            {"role": "user", "content": all}
        )
        
        sop.update_memory(current_memory)
        
def init_agents(sop):
    for name,role in sop.agents_role_name.items():
        agent = Agent(role,name)
        sop.agents[role] = agent

if __name__ == "__main__":
    sop = SOP("story.json")
    controller = controller(sop.controller_dict)
    init_agents(sop)
    
    autorun(sop, controller, begin_role="大纲写作者1", begin_name="小亮", begin_query="请根据要求开始撰写第一版大纲初稿")