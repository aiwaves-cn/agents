# default finish_state_name is "end_state"
# "environment_type" : "competive" : different states not share the memory; "cooperative":diffrent states share the memory
SOP = {
    "config": {
        "API_KEY": "API_KEY",
        "PROXY": "PROXY",
        "API_BASE":"API_BASE",
        "MAX_CHAT_HISTORY": "5",
        "User_Names": '["User"]',
    },
    "root": "state1",
    "relations": {
        "state1": {"0": "state1", "1": "state2"},
        "state2": {"0": "state2", "1": "end_state"},
    },
    "agents": None,
    "states": None,
}
from design_states import get_desgin_states,get_cot_result
from gen_utils import *
import json
from agents.utils import get_embedding,cos_sim
import torch

design_assistant = "An assistant that can help users create content such as articles, blogs, advertising copy, etc"
tutor = "A tutor who provides personalized learning resources for students to help them understand complex concepts and problems"
online_medical_consultant = "An online medical consultant who offers preliminary medical advice to patients and answers common questions about diseases, symptoms, and treatments."
online_legal_consultant = "An online legal advisor who can respond to inquiries related to legal matters, providing basic legal information and advice."
online_financial_advisor = "An online financial advisor who can analyze financial markets and data, offering investment advice and market forecasts to users."
virtual_tour_guide = "A virtual tour guide providing destination information, travel recommendations, and virtual travel experiences for travelers."
design_assistant = get_embedding(design_assistant)
tutor = get_embedding(tutor)
online_medical_consultant = get_embedding(online_medical_consultant)
online_legal_consultant = get_embedding(online_legal_consultant)
online_financial_advisor = get_embedding(online_financial_advisor)
virtual_tour_guide = get_embedding(virtual_tour_guide)
embeddings = torch.cat([design_assistant,tutor,online_medical_consultant,online_legal_consultant,online_financial_advisor,virtual_tour_guide],dim = 0)


if __name__ == "__main__":
    target = """a shopping assistant help customer to buy the commodity"""
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
    agents = get_agents(design_states)
    relations = get_relations(design_states)
    states = gen_states(design_states)
    for state_name,state_dict in states.items():
        state_dict["begin_role"] = list(agents.keys())[0]
        state_dict["begin_query"] = "Now that we are in the **{}**, I'm glad to offer you assistance.".format(state_name)
    SOP["root"] = root
    SOP["relations"] = relations
    SOP["agents"] = agents
    SOP["states"] = states
    # 将字典写入JSON文件
    with open("gen.json", "w") as json_file:
        json.dump(SOP, json_file)
