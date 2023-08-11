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
            print(f"{current_agent.name}({current_agent.role}):", end="")
            all = f"{current_agent.name}({current_agent.role}):"
            for res in response:
                all += res
                print(res, end="")
                time.sleep(0.02)
            print()
            sop.shared_memory["chat_history"].append(
                {"role": "assistant", "content": all}
            )

            if flag:
                break

def act(query,name="A神", role="user"):
    global sop,controller
    current_node = sop.current_node
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
        print(f"{current_agent.name}({current_agent.role}):", end="")
        all = f"{current_agent.name}({current_agent.role}):"
        for res in response:
            all += res
            yield res
        sop.shared_memory["chat_history"].append(
            {"role": "assistant", "content": all}
        )

        if flag:
            break
            
def step(sop: SOP, controller: controller):
    current_node = sop.current_node
    if len(current_node.next_nodes) == 1:
        next_node = "0"
    else:
        next_node = controller.judge(current_node, sop.shared_memory["chat_history"])
    next_node = current_node.next_nodes[next_node]
    if len(sop.agents.keys()) == 1:
        next_role = list(sop.agents.keys())[0]
    else:
        next_role = controller.allocate_task(
            next_node, sop.shared_memory["chat_history"]
        )
    return next_node, next_role


if __name__ == "__main__":
    agent = Agent("眼科客服", "吴家隆")
    sop = SOP("eye_newnew.json")
    controller = controller(sop.controller_dict)
    sop.agents = {"眼科客服": agent}
    agent.sop = sop
    query = "111111111"
    response =act(query)
    for res in response:
        print(res,end="")
    # run(my_sop, my_controller)
