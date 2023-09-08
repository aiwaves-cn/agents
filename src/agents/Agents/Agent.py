# coding=utf-8
# Copyright 2023  The AIWaves Inc. team.

#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""LLM autonoumous agent"""
from utils import get_relevant_history
from LLMs.base_LLM import *
from Componenets.base_component import *
from Componenets.extra_component import *
from Actions import Action
from Prompts import *

headers = {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}
    
    
    

class Agent:
    """
    Auto agent, input the JSON of SOP.
    """

    # Agent should have args: agents,states
    def __init__(self, name, agent_state_roles, **kwargs) -> None:
        self.state_roles = agent_state_roles
        self.name = name
        
        self.style = kwargs["style"]
        self.LLMs = kwargs["LLMs"]
        self.LLM = None
        self.is_user = kwargs["is_user"]
        self.begins = kwargs["begins"] if "begins" in kwargs else False
        self.current_role = ""
        self.long_term_memory = []
        self.short_term_memory = ""
        self.relevant_history = ""
        self.current_state = None
        self.first_speak = True
    

    @classmethod
    def from_config(cls, config_path):
        with open(config_path) as f:
            config = json.load(f)
        roles_to_names = {}
        names_to_roles = {}
        agents = {}
        user_names = json.loads(os.environ["User_Names"]) if "User_Names" in os.environ else []
        for agent_name, agent_dict in config["agents"].items():
            agent_state_roles = {}
            agent_LLMs = {}
            agent_begins = {}
            for state_name, agent_role in agent_dict["roles"].items():
                
                agent_begins[state_name] = {}
                
                if state_name not in roles_to_names:
                    roles_to_names[state_name] = {}
                if state_name not in names_to_roles:
                    names_to_roles[state_name] = {}
                roles_to_names[state_name][agent_role] = agent_name
                names_to_roles[state_name][agent_name] = agent_role
                agent_state_roles[state_name] = agent_role
                current_state = config["states"][state_name]
                
                current_state_begin_role = current_state["begin_role"] if "begin_role" in current_state else current_state["roles"][0]
                agent_begins[state_name]["is_begin"] = current_state_begin_role==agent_role if "begin_role" in current_state else False
                agent_begins[state_name]["begin_query"] = current_state["begin_query"] if "begin_query" in current_state else " "
                
                LLM_type = (
                    current_state["agent_states"][agent_role]["LLM_type"]
                    if "LLM_type" in current_state["agent_states"][agent_role]
                    else "OpenAI"
                )
                if LLM_type == "OpenAI":
                    if "LLM" in current_state["agent_states"][agent_role]:
                        agent_LLMs[state_name] = OpenAILLM(
                            **current_state["agent_states"][agent_role]["LLM"]
                        )
                    else:
                        agent_LLMs[state_name] = OpenAILLM(model = "gpt-3.5-turbo-16k-0613",temperature=0.3,log_path=f"logs/{agent_name}")
            agents[agent_name] = cls(
                agent_name,
                agent_state_roles,
                LLMs=agent_LLMs,
                is_user=agent_name in user_names,
                style = agent_dict["style"],
                begins = agent_begins
            )
        return agents, roles_to_names, names_to_roles

    def step(self, current_state, environment,input):
        """
        return actions by current state and environment
        """
        current_state.chat_nums +=1
        state_begin = current_state.is_begin
        agent_begin = self.begins[current_state.name]["is_begin"]
        self.begins[current_state.name]["is_begin"] = False
        current_state.is_begin = False
        
        self.current_state = current_state
        # 先根据当前环境更新信息
        # First update the information according to the current environment
        
        if len(environment.shared_memory["long_term_memory"])>0:
            current_history = self.observe(environment)
            self.long_term_memory.append(current_history)
        
        response = " "
        res_dict = {}
        
        if self.is_user:
            response = f"{self.name}:{input}"
        else:
            if agent_begin:
                response = (char for char in self.begins[current_state.name]["begin_query"])
            else:
                response,res_dict = self.act()
        
        
        action_dict =  {
            "response": response,
            "res_dict": res_dict,
            "role": self.state_roles[current_state.name],
            "name": self.name,
            "state_begin" : state_begin,
            "agent_begin" : agent_begin,
            "is_user" : self.is_user
        }
        return  Action(**action_dict)

    def act(self):
        """
        return actions by the current state
        """
        current_state = self.current_state
        system_prompt, last_prompt, res_dict = self.compile()
        chat_history = self.long_term_memory

        current_LLM = self.LLMs[current_state.name]

        response = current_LLM.get_response(
            chat_history, system_prompt, last_prompt, stream=True
        )
        return response,res_dict 

    def update_memory(self, memory):
        self.long_term_memory.append(
            {"role": "assistant", "content": memory.content}
        )

    def compile(self):
        """
        get prompt from state depend on your role
        """
        current_state = self.current_state
        self.current_roles = self.state_roles[current_state.name]
        current_state_name = current_state.name
        self.LLM = self.LLMs[current_state_name]
        components = current_state.components[self.state_roles[current_state_name]]

        system_prompt = self.current_state.environment_prompt
        last_prompt = ""

        res_dict = {}
        for component in components.values():
            if isinstance(component, (OutputComponent, LastComponent)):
                last_prompt = last_prompt + "\n" + component.get_prompt(self)
            elif isinstance(component, PromptComponent):
                system_prompt = (
                    system_prompt + "\n" + component.get_prompt(self)
                )
            elif isinstance(component, ToolComponent):
                response = component.func(self)
                if "prompt" in response and response["prompt"]:
                    last_prompt = last_prompt + "\n" + response["prompt"]
                res_dict.update(response)
        return system_prompt, last_prompt, res_dict

    def observe(self, environment):
        """
        get new memory from environment
        """
        MAX_CHAT_HISTORY = eval(os.environ["MAX_CHAT_HISTORY"])
        current_state = self.current_state
        current_role = self.state_roles[current_state.name]
        current_component_dict = current_state.components[current_role]
        
        
        if environment.environment_type == "compete":
            current_long_term_memory = environment.shared_memory["long_term_memory"][environment.current_chat_history_idx:]
            current_chat_embbedings = environment.shared_memory["chat_embeddings"][environment.current_chat_history_idx:]
        else:
            current_long_term_memory = environment.shared_memory["long_term_memory"]
            current_chat_embbedings = environment.shared_memory["chat_embeddings"]
            
        
        # relevant_memory
        query = current_long_term_memory[-1].content

        relevant_memory = get_relevant_history(
            query,
            current_long_term_memory[:-1],
            current_chat_embbedings[:-1],
        )
        relevant_memory = Memory.get_chat_history(relevant_memory)
        
        relevant_memory = eval(Agent_observe_relevant_memory)
        self.relevant_memory = relevant_memory
        

        # get new conversation
        last_conversation_idx = -1
        for i, history in enumerate(current_long_term_memory):
            if history.send_name == self.name:
                last_conversation_idx = i

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

        
        # get chat history from new conversation
        conversations = Memory.get_chat_history(new_conversation)


        if len(current_long_term_memory) % MAX_CHAT_HISTORY == 0:
            # get summary
            summary_prompt = (
                current_state.summary_prompt[current_role]
                if current_state.summary_prompt
                else f"""your name is {self.name},your role is{current_component_dict["style"].role},your task is {current_component_dict["task"].task}.\n"""
            )
            summary_prompt =eval(Agent_summary_system_prompt)
            response = self.LLMs[current_state.name].get_response(None, summary_prompt)
            summary = ""
            for res in response:
                summary += res
            self.short_term_memory = summary
            

        # memory = relevant_memory + summary + history + query
        query = current_long_term_memory[-1]
        current_memory = eval(Agent_observe_memory)

        return {"role": "user", "content": current_memory}
        
    
    def generate_sop(self):
        pass

    def reflection(self):
        pass


