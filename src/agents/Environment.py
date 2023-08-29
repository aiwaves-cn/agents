from utils import get_key_history,get_embedding
import torch
from LLM import *
from Memory import Memory

class Environment:
    def __init__(self,config) -> None:
        self.shared_memory = {"long_term_memory":[],"short_term_memory":None}
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
        self.roles_to_names = None
        self.names_to_roles = None           
    
    @classmethod
    def from_config(cls,config_path):
        
        with open(config_path) as f:
            config = json.load(f)
        return cls(config)
        
    
    def summary(self,current_state):
        current_state_name = current_state.name
        environment_prompt = self.environment_prompt[current_state_name]
        system_prompt = environment_prompt + self.summary_system_prompt[current_state_name]

        current_memory = "The dialogues you may need to pay attention to are as follows:\n<relevant_history>"

        # get relevant memory
        query = self.shared_memory["long_term_memory"][-1]
        key_history = get_key_history(
            query,
            self.shared_memory["long_term_memory"][:-1],
            self.shared_memory["chat_embeddings"][:-1],
        )
        # get chat history
        for history in key_history:
           current_memory += f"{history.send_name}({history.send_role}):{history.content}\n"
        current_memory += "<relevant_history>\n"
        
        chat_history = "The dialogue is recorded as follows:\n<history>"
        for his in self.shared_memory["long_term_memory"]:
            chat_history += f"{his.send_name}({his.send_role}):{his.content}\n"
        
        summary = self.shared_memory["short_term_memory"]
        current_memory += f"The summary of the previous dialogue history is as follows :<summary>\n{summary}\n.The latest conversation record is as follows:\n<hisroty> {chat_history}\n<history>"

        
        response = self.LLM.get_response(
            None,
            system_prompt,
            stream=False
        )
        return response
    
    def excute_action(self,action):
        response = action["response"] if "response" in action else ""
        res_dict = action["res_dict"] if "res_dict" in action else {}
        is_user =  action["is_user"] if "is_user" in action else False
        send_name = action["name"]
        send_role = action["role"]
        all = ""
        for res in response:
            all += res
        if not is_user:
            print(f"{send_name}({send_role}):{all}")
        memory = Memory(send_role,send_name,all)
        return memory
    
    
    def update_memory(self, memory,current_state):
        MAX_CHAT_HISTORY = eval(os.environ["MAX_CHAT_HISTORY"])
        self.shared_memory["long_term_memory"].append(memory)
        current_embedding = get_embedding(memory.content)
        if "chat_embeddings" not in self.shared_memory:
            self.shared_memory["chat_embeddings"] = current_embedding
        else:
            self.shared_memory["chat_embeddings"] = torch.cat(
                [self.shared_memory["chat_embeddings"], current_embedding], dim=0
            )

        if len(self.shared_memory["long_term_memory"]) % MAX_CHAT_HISTORY:
            summary = self.summary(current_state)
            self.shared_memory["short_term_memory"] = summary
        
        self.agents[memory.send_name].update_memory(memory)

