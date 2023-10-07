import sys
sys.path.append("../")
import re
from LLM.base_LLM import *
from utils import extract
from single_prompts import *


llm = OpenAILLM()
# design state

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
    role = extract(response,"role")
    pattern = r'<state>(.*?)<\/state>'
    states = re.findall(pattern, response, re.DOTALL)
    style = extract(response,"style")
    # 创建包含字典的列表
    result_list = []
    for state in states:
        state_name = extract(state,"state_name")
        rule = extract(state,"rule")
        task = extract(state,"task")
        judge = extract(state,"judge")
        
        # 创建字典并添加到结果列表
        state_dict = {
            "style":style,
            "role":role,
            "state_name": state_name,
            "task": task,
            "rule": rule,
            "judge" : judge
        }
        result_list.append(state_dict)

    # 打印结果
    print("design states")
    for item in result_list:
        print(item)
    return result_list
        
