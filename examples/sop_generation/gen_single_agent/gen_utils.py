def get_agents(design_states):
    final_agents = {}
    role = design_states[0]["role"]
    style = design_states[0]["style"]
    agent_name = "_".join(role.split(" "))
    final_agents[agent_name] = {"style":style,"roles":{}}
    final_agents["User"] = {"style":"","roles":{}}
    for design_state in design_states:
        final_agents[agent_name]["roles"][design_state["state_name"]] = agent_name
        final_agents["User"]["roles"][design_state["state_name"]] = "User"
    return final_agents

def get_relations(design_states):
    relations = {}
    n = len(design_states)
    for i in range(n):
        relations[design_states[i]["state_name"]] = {}
        relations[design_states[i]["state_name"]]["0"] = design_states[i]["state_name"]
        relations[design_states[i]["state_name"]]["1"] = design_states[i+1]["state_name"]  if i!=n-1 else "end_state"
    return relations


def gen_states(design_states):
    states = {"end_state":{
            "agent_states":{}
        }}
    for design_state in design_states:
        state_name = design_state["state_name"]
        role = design_state["role"]
        agent_name = "_".join(role.split(" "))
        states[state_name] = {"controller":{"controller_type": "order", "max_chat_nums" : 1000,"judge_system_prompt":design_state["judge"],"judge_last_prompt":"Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"}}
        states[state_name]["agent_states"] = {
            agent_name : {
                "role" : {"role" : role},
                "task" : {"task" : design_state["task"]},
                "rule" : {"rule" : design_state["rule"]}
            },
            "User" : {
            }
        }

    return states

