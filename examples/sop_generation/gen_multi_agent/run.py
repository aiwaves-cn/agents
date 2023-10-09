coder = {
        "task" : {
            "task":""
        },
        "rule" : {"rule": "1.write code that conforms to standards like PEP8, is modular, easy to read, and maintainable.\n 2.The output strictly follows the following format:<title>{the file name}</title>\n<python>{the target code}</python>\n3.Please carefully modify the code based on feedback from others.\n4.Output the code only."},
        "last" : {
            "last_prompt" : "The output strictly follows the following format:<title>{the file name}</title>\n<python>{the target code}</python>,Output the code only."
        }
    }
# default finish_state_name is "end_state"
# "environment_type" : "competive" : different states not share the memory; "cooperative":diffrent states share the memory
sop = {
    "config" : {
    "API_KEY": "API_KEY",
    "PROXY": "PROXY",
    "API_BASE":"API_BASE",
    "MAX_CHAT_HISTORY" : "5",
    "ACTIVE_MODE" : "0"
    },
    "root": "state1",
    "relations": {
        "state1": {
            "0": "state1",
            "1": "state2"
        },
        "state2":{
            "0":"state2",
            "1":"end_state"
        }
    },
    "agents": None,
    "states": None,
}
from design_states import get_desgin_states,get_cot_result,gen_coder_task
from gen_utils import *
import json
from agents.utils import get_embedding,cos_sim
import torch
import os

API_KEY = "API_KEY"
PROXY = "PROXY"
target = """A web-based shopping guide responsible for directing users to purchase the products they need."""
need_coder = True

os.environ["API_KEY"] = API_KEY
os.environ["PROXY"] = PROXY
sop["config"]["API_KEY"] = API_KEY
sop["config"]["PROXY"] = PROXY


software = "You are a software,aim to write a snake game with python"
debate = "Simulate a debate competition"
ecological_environment = "Simulate the interactions and competition among different organisms within an ecosystem"
software = get_embedding(software)
debate = get_embedding(debate)
ecological_environment = get_embedding(ecological_environment)
embeddings = torch.cat([software,debate,ecological_environment],dim = 0) 
target_tensor = get_embedding(target)
sim_scores = cos_sim(target_tensor, embeddings)[0]
top_k_score, top_k_idx = torch.topk(sim_scores,k = 1)

if top_k_score > 0.7:
    index = top_k_idx
else:
    index = 0

target = get_cot_result(target)
design_states = get_desgin_states(target,index)
root = design_states[0]["state_name"]
agents = get_agents(design_states,index)
relations = get_relations(design_states)
states = gen_states(design_states,index)

if need_coder:
    agents["coder"] = {"style":"professional","roles":{}}
    for state_name,state in states.items():
        if state_name!="end_state":
            agents["coder"]["roles"][state_name] = "coder"
            state["roles"].append("coder")
            task = gen_coder_task(state["environment_prompt"])
            now_coder = coder.copy()
            now_coder["task"]["task"] = task
            state["agent_states"]["coder"] = now_coder
            state["controller"]["max_chat_nums"] = str(int(state["controller"]["max_chat_nums"])+2)
            for name,agent in state["agent_states"].items():
                if name!="coder":
                    agent["rule"]["rule"] +="\nEvaluate the code of the coder and provide feedback and response as concise as possible.It is best not to exceed 100 words"
                    agent["task"]["task"] += "\nEvaluate the code of the coder and provide feedback."


sop["root"] = root
sop["relations"] = relations
sop["agents"] = agents
sop["states"] = states
# 将字典写入JSON文件
with open("gen.json", 'w') as json_file:
    json.dump(sop, json_file)

