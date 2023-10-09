from agents.utils import get_relevant_history, get_embedding
import torch
from agents.LLM.base_LLM import *
from agents.Memory import Memory
from agents.Prompt import * 
import json
class Environment:
    """
    The place where the agent activities, responsible for storing some shared memories
    """
    def __init__(self, config) -> None:
        self.shared_memory = {"long_term_memory": [], "short_term_memory": None}
        self.agents = None

        self.summary_system_prompt = {}
        self.summary_last_prompt = {}
        self.environment_prompt = {}
        self.environment_type = config["environment_type"] if "environment_type" in config else "cooperative"
        self.current_chat_history_idx = 0
        self.LLMs = {}
        
        # 初始化每个state 的summary 方法
        # Initialize the summary method for each state
        for state_name, state_dict in config["states"].items():
            if state_name != "end_state":
                self.summary_system_prompt[state_name] = (
                    state_dict["summary_system_prompt"]
                    if "summary_system_prompt" in state_dict
                    else eval(Default_environment_summary_system_prompt)
                )

                self.summary_last_prompt[state_name] = (
                    state_dict["summary_last_prompt"]
                    if "summary_last_prompt" in state_dict
                    else eval(Default_environment_summary_last_prompt)
                )

                self.environment_prompt[state_name] = (
                    state_dict["environment_prompt"]
                    if "environment_prompt" in state_dict
                    else " "
                )
                self.LLMs[state_name] = init_LLM("logs"+os.sep+f"{state_name}",**state_dict)
        self.roles_to_names = None
        self.names_to_roles = None

    @classmethod
    def from_config(cls, config_path):
        with open(config_path) as f:
            config = json.load(f)
        return cls(config)

    def summary(self, current_state):
        """
        Summarize the situation in the current environment every once in a while
        """
        MAX_CHAT_HISTORY = eval(os.environ["MAX_CHAT_HISTORY"])
        current_state_name = current_state.name

        if len(self.shared_memory["long_term_memory"])>1:
            query = self.shared_memory["long_term_memory"][-1].content
            relevant_history = get_relevant_history(
                query,
                self.shared_memory["long_term_memory"][:-1],
                self.shared_memory["chat_embeddings"][:-1],
            )

            relevant_history = Memory.get_chat_history(relevant_history)
        else:
            relevant_history = ""
        chat_history = Memory.get_chat_history(
            self.shared_memory["long_term_memory"][-MAX_CHAT_HISTORY + 1 :]
        )
        summary = self.shared_memory["short_term_memory"]
        
        
        # system prompt = environment prompt + current memory + system prompt
        # current_memory = summary + chat history + relevant history
        current_memory = eval(Environment_summary_memory)
        environment_prompt = self.environment_prompt[current_state_name]
        summary_system_prompt = self.summary_system_prompt[current_state_name]
        
        environment_summary_system_prompt = eval(Environment_summary_system_prompt)
        response = self.LLMs[current_state_name].get_response(None, environment_summary_system_prompt, stream=False)
        return response

    def update_memory(self, memory, current_state):
        """
        update chat embbedings and long term memory,short term memory,agents long term memory
        """
        MAX_CHAT_HISTORY = eval(os.environ["MAX_CHAT_HISTORY"])
        self.shared_memory["long_term_memory"].append(memory)
        current_embedding = get_embedding(memory.content)
        if "chat_embeddings" not in self.shared_memory:
            self.shared_memory["chat_embeddings"] = current_embedding
        else:
            self.shared_memory["chat_embeddings"] = torch.cat(
                [self.shared_memory["chat_embeddings"], current_embedding], dim=0
            )
        if len(self.shared_memory["long_term_memory"]) % MAX_CHAT_HISTORY == 0:
            summary = self.summary(current_state)
            self.shared_memory["short_term_memory"] = summary

        self.agents[memory.send_name].update_memory(memory)
    
    
    def _get_agent_last_conversation_idx(self,agent,current_long_term_memory):
        last_conversation_idx = -1
        for i, history in enumerate(current_long_term_memory):
            if history.send_name == agent.name:
                last_conversation_idx = i
        return last_conversation_idx
    
    
    def _get_agent_new_memory(self,agent,current_long_term_memory):
        # get new conversation
        last_conversation_idx = self._get_agent_last_conversation_idx(agent,current_long_term_memory)

        if last_conversation_idx == -1:
            new_conversation =current_long_term_memory
        elif (
            last_conversation_idx
            == len(current_long_term_memory) - 1
        ):
            new_conversation = []
        else:
            new_conversation = current_long_term_memory[
                last_conversation_idx + 1 :
            ]
        MAX_CHAT_HISTORY = eval(os.environ["MAX_CHAT_HISTORY"])
        if len(new_conversation) > 2 * MAX_CHAT_HISTORY:
            new_conversation = new_conversation[-2*MAX_CHAT_HISTORY+1:]

        # get chat history from new conversation
        return Memory.get_chat_history(new_conversation)
    
    
    def _observe(self,agent):
        MAX_CHAT_HISTORY = eval(os.environ["MAX_CHAT_HISTORY"])
        current_state = agent.current_state
        current_role = agent.state_roles[current_state.name]
        current_component_dict = current_state.components[current_role]
        
        # cooperative:Sharing information between different states ;  competive: No information is shared between different states
        current_chat_history_idx = self.current_chat_history_idx if self.environment_type == "competive" else 0
        current_long_term_memory = self.shared_memory["long_term_memory"][current_chat_history_idx:]
        current_chat_embbedings = self.shared_memory["chat_embeddings"][current_chat_history_idx:]
            
        if len(current_long_term_memory)>MAX_CHAT_HISTORY:
            current_long_term_memory = current_long_term_memory[-MAX_CHAT_HISTORY+1:]
            current_chat_embbedings = current_chat_embbedings[-MAX_CHAT_HISTORY+1:]
        # relevant_memory
        if len(current_long_term_memory)>1:
            query = current_long_term_memory[-1].content
            relevant_memory = get_relevant_history(
                query,
                current_long_term_memory[:-2],
                current_chat_embbedings[:-2],
            )
            relevant_memory = Memory.get_chat_history(relevant_memory,agent.name)
        else:
            relevant_memory = ""
        
        relevant_memory = eval(Agent_observe_relevant_memory)
        agent.relevant_memory = relevant_memory
        
        
        # get chat history from new conversation
        conversations = self._get_agent_new_memory(agent,current_long_term_memory)

        # memory = relevant_memory + summary + history + query
        current_memory = eval(Agent_observe_memory)

        return {"role": "user", "content": current_memory}


