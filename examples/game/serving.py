import sys

sys.path.append("../../src/agents")
from agent import Agent
from sop import SOP, controller


def autorun(sop: SOP, controller: controller,user_roles=None):
    current_node = sop.current_node
    current_agent = sop.agents[current_node.name][current_node.begin_role]
    current_memory = {"role": "user", "content": f"{current_agent.name}:{current_node.begin_query}"}
    sop.update_memory(current_memory)
    print(current_node.name)
    print(f"{current_agent.name}:{current_node.begin_query}")
    
    while True:
        next_node, next_role = controller.next(sop)
        if next_node != current_node:
            sop.send_memory(next_node)
            break
            
        is_user = True if next_role in user_roles else False
        
        current_node = next_node
        sop.current_node = current_node
        current_agent = sop.agents[current_node.name][next_role]
        response = current_agent.step(
            current_node, temperature = sop.temperature,is_user = is_user
        )
        all = f""
        for res in response:
            all += res
            if not is_user:
                print(res, end="")
        print()
        current_memory = {"role": "user", "content": all}
        sop.update_memory(current_memory)
        
        
def init_agents(sop):
    for node_name,node_agents in sop.agents_role_name.items():
        for name,role in node_agents.items():
            agent = Agent(role,name)
            if node_name not in sop.agents:
                sop.agents[node_name] = {}
            sop.agents[node_name][role] = agent
            sop.nodes[node_name].roles.append(role)

if __name__ == "__main__":
    
    sop = SOP("game.json")
    controller = controller(sop.controller_dict)
    init_agents(sop)
    user_roles = sop.user_roles
    autorun(sop, controller,user_roles)
