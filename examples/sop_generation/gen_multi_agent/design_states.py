import re
from agents.LLM.base_LLM import *
from agents.utils import extract
from multi_prompts import *

llm = OpenAILLM()
# design state

def gen_coder_task(environment_prompt):
    chat_history = [{"role":"user","content":f"<target>{environment_prompt}</target>"}]
    response = llm.get_response(chat_history,gen_coder_task_system_prompt)
    response = extract(response,"task")
    print(f"coder_task = {response}")
    return response


def get_cot_result(target):
    chat_history = [{"role":"user","content":f"<target>{target}</target>"}]
    response = llm.get_response(chat_history,design_states_cot_system_prompt)
    print(response)
    return response

def get_desgin_states(target,index):
    chat_history = [{"role":"user","content":f"<target>{target}</target>"}]
    design_state_system_prompt = get_design_state_system_prompt(index)
    response = llm.get_response(chat_history,system_prompt=design_state_system_prompt)
    print(response)
    # 使用正则表达式提取数据
    pattern = r'<state>(.*?)<\/state>'
    states = re.findall(pattern, response, re.DOTALL)

    # 创建包含字典的列表
    result_list = []
    for state in states:
        state_name = extract(state,"state_name")
        roles = extract(state,"roles")
        environment_prompt = extract(state,"describe")
        
        # 创建字典并添加到结果列表
        state_dict = {
            "state_name": state_name,
            "environment_prompt": environment_prompt,
            "roles": roles.split(" ")
        }
        result_list.append(state_dict)

    # 打印结果
    print("design states")
    for item in result_list:
        print(item)
    return result_list

def gen_agent_style(agents,design_states,index):
    agents_styles = {}
    scene = ""
    design_agents_style_system_prompt = get_design_agents_style_system_prompt(index)
    for design_state in design_states:
        scene +=design_state["environment_prompt"] + "\n"
    for agent in agents:
        chat_history = [{"role":"user","content":f"<scene>{scene}</scene>,<target>{agent}</target>"}]
        style = llm.get_response(chat_history,design_agents_style_system_prompt)
        style = extract(style,"style")
        agents_styles[agent] = style
    print(agents_styles)
    return agents_styles
        

def gen_agent_state(agent,environment_prompt,index):
    design_agent_state_system_prompt = get_design_agent_state_system_prompt(index)
    agent_state = {}
    chat_history = [{"role":"user","content":f"<scene>{environment_prompt}</scene>,<target>{agent}</target>"}]
    response = llm.get_response(chat_history,design_agent_state_system_prompt)
    role = extract(response,"role")
    task = extract(response,"task")
    rule = extract(response,"rule")
    demonstrations = extract(response,"demonstrations")
    agent_state["style"] = {"role":role}
    agent_state["task"] = {"task":task}
    agent_state["rule"] = {"rule":rule}
    agent_state["demonstrations"] = {"demonstrations":demonstrations}
    print(agent_state)
    return agent_state

def gen_begin_role_query(environment_prompt,roles,index):
    roles = " ".join(roles)
    design_begin_role_query_system_prompt = get_design_begin_role_query_system_prompt(index)
    chat_history = [{"role":"user","content":f"<scene>{environment_prompt}</scene>\n<roles>{roles}</roles>"}]
    response = llm.get_response(chat_history,design_begin_role_query_system_prompt)
    begin_role = extract(response,"begin_role")
    begin_query = extract(response,"begin_query")
    print(f"{begin_role}:{begin_query}")
    return begin_role,begin_query
