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
        current_memory = {"role": "user", "content": f"{query}"}
        sop.update_memory(current_memory)
        while True:
            next_node, next_role = controller.next(sop)
            if next_node != current_node:
                sop.send_memory(next_node)

            flag = next_node.is_interactive
            current_node = next_node
            sop.current_node = current_node

            if next_role == role:
                break

            current_agent = sop.agents[current_node.name][next_role]

            response = current_agent.step(query, current_node, sop.temperature)
            all = ""
            for res in response:
                all += res
                print(res, end="")
            print()
            sop.update_memory(current_memory)

            if flag:
                break


def init_agents(sop):
    for node_name, node_agents in sop.agents_role_name.items():
        for name, role in node_agents.items():
            agent = Agent(role, name)
            if node_name not in sop.agents:
                sop.agents[node_name] = {}
            sop.agents[node_name][role] = agent


if __name__ == "__main__":
    sop = SOP("youcai_base_knowledge.json")
    controller = controller(sop.controller_dict)
    init_agents(sop)
    run(sop, controller)
