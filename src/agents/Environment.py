from utils import get_key_history,get_embedding
import torch
import json
from LLM import *


class Environment:
    def __init__(self,config) -> None:
        self.shared_memory = {"chat_history":[],"summary":" "}
        self.agents = None
        
        self.summary_system_prompt = {}
        self.summary_last_prompt = {}
        self.environment_prompt = {}
        for state_name,state_dict in config["states"].items():
            
            self.summary_system_prompt[state_name] = state_dict["summary_system_prompt"] if "summary_system_prompt" in state_dict else  "\nYour task is to summarize the historical dialogue records according to the current scene, and summarize the most important information"
            
            self.summary_last_prompt[state_name] = state_dict["summary_last_prompt"] if "summary_last_prompt" in state_dict else  "Please make a summary based on the historical chat records, the output format is history summary: \{your summary content\} "
            
            self.environment_prompt[state_name] = state_dict["environment_prompt"] if "environment_prompt" in state_dict else  " "
            LLM_type = state_dict['LLM_type'] if "LLM_type" in state_dict else "OpenAI"
            if LLM_type == "OpenAI":
                self.LLM = OpenAILLM(**state_dict["LLM"])
                
    
    @classmethod
    def from_config(cls,config):
        return cls(config)
        
    
    def summary(self,current_state):
        current_state_name = current_state.name
        environment_prompt = self.environment_prompt[current_state_name]
        system_prompt = environment_prompt + self.summary_system_prompt[current_state_name]
        last_prompt = self.summary_last_prompt[current_state_name]
        
        query = (
            self.shared_memory["chat_history"][-1]
            if len(self.shared_memory["chat_history"]) > 0
            else " "
        )
        key_history = get_key_history(
            query,
            self.shared_memory["chat_history"][:-1],
            self.shared_memory["chat_embeddings"][:-1],
        )
        
        response = self.LLM.get_response(
            self.shared_memory["chat_history"],
            system_prompt,
            last_prompt,
            stream=False,
            summary=self.shared_memory["summary"],
            key_history=key_history,
        )
        return response
    
    def excute_action(self,action):
        response = action["response"] if "response" in action else ""
        res_dict = action["res_dict"] if "res_dict" in action else {}
        is_user =  action["is_user"] if "is_user" in action else False
        all = ""
        for res in response:
            all += res
            if not is_user:
                print(res,end="")
        if not is_user:
            print()
        memory = {"role":"user","content":all}
        return memory
    
    
    def update_memory(self, memory,current_state,roles_to_names):
        global MAX_CHAT_HISTORY
        self.shared_memory["chat_history"].append(memory)
        current_embedding = get_embedding(memory["content"])
        if "chat_embeddings" not in self.shared_memory:
            self.shared_memory["chat_embeddings"] = current_embedding
        else:
            self.shared_memory["chat_embeddings"] = torch.cat(
                [self.shared_memory["chat_embeddings"], current_embedding], dim=0
            )

        summary = None

        if len(self.shared_memory["chat_history"]) % MAX_CHAT_HISTORY:
            summary = self.summary(current_state)
            self.shared_memory["summary"] = summary
        
        for agent_role in current_state.roles:
            agent_name = roles_to_names[current_state.name][agent_role]
            self.agents[agent_name].update_memory(memory, summary, current_embedding)


    def send_memory(self, next_state):
        summary = self.summary(next_state)
        self.shared_memory["summary"] = summary
        self.shared_memory["chat_history"] = []
        for agent in self.agents[next_state.name].values():
            agent.agent_dict["summary"] = summary
