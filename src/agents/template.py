## default { "temperature": 0.3, "model": "gpt-3.5-turbo-16k-0613","log_path": "logs/{your name}"}
LLM = {
    "temperature": 0.0,
    "model": "gpt-3.5-turbo-16k-0613",
    "log_path": "logs/god"
}


Agents = {
    "Lilong" : {
        "style" : "professional",
        "roles" : {
            "company" : "coder",
            "state2" : "role2",
        },
    "name2" : {   
        "style" : "professional",
            "roles" : {
                "company" : "coder",
                "state2" : "role2",
            },
        }
    }
}

# indispensable parameter:  "controller_type"（"order","random","rule"）
controller = {
    "controller_type": "order",
    "max_chat_nums" : 12,
    "judge_system_prompt": "",
    "judge_last_prompt": "",
    "judge_extract_words": "end",
    "call_system_prompt" : "",
    "call_last_prompt": "",
    "call_extract_words": ""
}


Agent_state = {
    "role": {
    "LLM_type": "OpenAI",
    "LLM": LLM,
    "style": {
        "role": "Opening Advocate for the Affirmative",
        "style": "professional"
    },
    "task": {
        "task": ""
    },
    "rule": {
        "rule": ""
    }
},
}


# indispensable parameter:  "name" and "agent_states"
State = {
    "controller": controller,
    "begin_role": "",
    "begin_query": "",
    "environment_prompt": "",
    "name": "state1",
    "roles": ["role1","role2"],
    "LLM_type": "OpenAI",
    "LLM": LLM,
    "agent_state" : Agent_state,
    
    
    
}


States = {
    "end_state":{
            "name":"end_state",
            "agent_states":{}
        },
    "state1" : State
    
}


# default finish_state_name is "end_state"
SOP = {
    "config" : {
    "API_KEY" : "Your key",
    "PROXY" : "Your PROXY",
    "MAX_CHAT_HISTORY" : "5",
    "User_Names" : "[\"alexander\"]"
    },
    "environment_type" : "competive",
    "LLM_type": "OpenAI",
    "LLM" :LLM,
    "root": "state1",
    "finish_state_name" : "end_state",
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
    "agents": Agents,
    "states": States,
}

