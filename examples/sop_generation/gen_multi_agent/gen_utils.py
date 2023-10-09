from design_states import gen_agent_style,gen_agent_state,gen_begin_role_query

def get_agent_names(design_states):
    agents_name = set()
    for design_state in design_states:
        for role in design_state["roles"]:
            agents_name.add(role)
    return list(agents_name)

def get_final_agents(agents,design_states):
    final_agents = {}
    for agent,style in agents.items():
        final_agents[agent] = {"style":"","roles":{}}
        final_agents[agent]["style"] = style
        for design_state in design_states:
            if agent in design_state["roles"]:
                final_agents[agent]["roles"][design_state["state_name"]] = agent
    return final_agents

def get_agents(design_states,index):
    agents = get_agent_names(design_states)
    agents = gen_agent_style(agents,design_states,index)
    agents = get_final_agents(agents,design_states)
    return agents

def get_relations(design_states):
    relations = {}
    n = len(design_states)
    for i in range(n):
        relations[design_states[i]["state_name"]] = {}
        relations[design_states[i]["state_name"]]["0"] = design_states[i]["state_name"]
        relations[design_states[i]["state_name"]]["1"] = design_states[i+1]["state_name"]  if i!=n-1 else "end_state"
    return relations


def gen_states(design_states,index):
    states = {"end_state":{
            "agent_states":{}
        }}
    for design_state in design_states:
        state_name = design_state["state_name"]
        environment_prompt = design_state["environment_prompt"]
        roles = design_state["roles"]
        max_chat_nums = 1 if len(roles)==1 else len(roles)*2
        states[state_name] = {"controller":{"controller_type": "order", "max_chat_nums" : max_chat_nums},"environment_prompt":environment_prompt,"roles":roles}
        agent_state = {}
        for role in roles:
            agent_state[role] = gen_agent_state(role,environment_prompt,index)
        states[state_name]["agent_states"] = agent_state
        begin_role,begin_query = gen_begin_role_query(environment_prompt,roles,index)
        begin_role = ("_").join(begin_role.split(" "))
        print(begin_role)
        if begin_role not in roles:
            begin_role = begin_role +"_1"
        if begin_role in roles:
            states[state_name]["begin_role"] = begin_role
            states[state_name]["begin_query"] = begin_query
    return states

