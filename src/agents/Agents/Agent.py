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
from utils import get_key_history
from LLMs.base_LLM import *
from Componenets.base_component import *
from Componenets.extra_component import *

headers = {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}


class Agent:
    """
    Auto agent, input the JSON of SOP.
    """


    def __init__(self, name,agent_state_roles,**kwargs) -> None:
        self.state_roles = agent_state_roles
        self.name = name
        self.LLMs = kwargs["LLMs"]
        self.long_term_memory = []
        self.short_term_memory = ""
        self.current_state = None
        self.is_user = False
        self.agent_dict = {
            "name" :name,
            "current_roles":"",
            "long_term_memory":self.long_term_memory,
            "short_term_memory": self.short_term_memory
        }
        

    @classmethod
    def from_config(cls,config_path):
        with open(config_path) as f:
            config = json.load(f)
        roles_to_names = {}
        names_to_roles = {}
        agents = {}
        for agent_name,agent_dict in config["agents"].items():
            agent_state_roles = {}
            agent_LLMs = {}
            for state_name,agent_role in agent_dict.items():
                if state_name not in roles_to_names:
                    roles_to_names[state_name] = {}
                if state_name not in names_to_roles:
                    names_to_roles[state_name] = {}                
                roles_to_names[state_name][agent_role] = agent_name
                names_to_roles[state_name][agent_name] = agent_role
                agent_state_roles[state_name] = agent_role
                current_state = config["states"][state_name]
                LLM_type = current_state["agent_states"][agent_role]['LLM_type'] if "LLM_type" in current_state["agent_states"][agent_role] else "OpenAI"
                if LLM_type == "OpenAI":
                    agent_LLMs[state_name] = OpenAILLM(**current_state["agent_states"][agent_role]['LLM'])
            agents[agent_name] = cls(agent_name,agent_state_roles,LLMs = agent_LLMs)
        return agents,roles_to_names,names_to_roles
    
    
    def step(self, current_state,environment):
        self.current_state = current_state
        self.observe(environment)
        if self.is_user:
            response = input(f"{self.name}:")
            response = f"{self.name}:{response}"
            return {"response":response,"is_user":True,"role":self.state_roles[current_state.name],"name":self.name}
        else:
            current_history = self.observe(environment)
            self.agent_dict["long_term_memory"].append(current_history)
            return self.act()
    
    def act(self):
        current_state = self.current_state
        system_prompt, last_prompt, res_dict = self.compile()
        chat_history = self.agent_dict["long_term_memory"]

        current_LLM = self.LLMs[current_state.name]

        response = current_LLM.get_response(
            chat_history,
            system_prompt,
            last_prompt,
            stream=True
        )
        return {"response":response,"res_dict":res_dict,"role":self.state_roles[current_state.name],"name":self.name}
        

    def update_memory(self, memory):
        self.agent_dict["long_term_memory"].append({"role":"assistant","content":memory.content})
        
            
    def compile(self):
        current_state  = self.current_state
        self.agent_dict["current_roles"] = self.state_roles[current_state.name]
        current_state_name = current_state.name
        self.agent_dict["LLM"] = self.LLMs[current_state_name]
        components = current_state.components[self.state_roles[current_state_name]]
        
        system_prompt =  self.current_state.environment_prompt
        last_prompt = ""
        
        res_dict = {}
        for component in components.values():
            if isinstance(component, (OutputComponent, LastComponent)):
                last_prompt = last_prompt + "\n" + component.get_prompt(self.agent_dict)
            elif isinstance(component, PromptComponent):
                system_prompt = system_prompt + "\n" + component.get_prompt(self.agent_dict)
            elif isinstance(component, ToolComponent):
                response = component.func(self.agent_dict)
                if "prompt" in response and response["prompt"]:
                    last_prompt = last_prompt + "\n" + response["prompt"]
                self.agent_dict.update(response)
                res_dict.update(response)
        return system_prompt, last_prompt, res_dict
    
    def observe(self,environment):
        MAX_CHAT_HISTORY = eval(os.environ["MAX_CHAT_HISTORY"])
        current_memory = "Here's what you need to know(Remember, this is just information, Try not to repeat what's inside):\n<information>\nThe relevant chat history are as follows:\n<relevant_history>"
        query = environment.shared_memory["long_term_memory"][-1]
        current_state = self.current_state
        current_role = self.state_roles[current_state.name]
        current_component_dict = current_state.components[current_role]

        # get relevant memory
        key_history = get_key_history(
            query,
            environment.shared_memory["long_term_memory"][:-1],
            environment.shared_memory["chat_embeddings"][:-1],
        )
        for history in key_history:
           current_memory += f"{history.send_name}({history.send_role}):{history.content}\n"
        current_memory += "<relevant_history>\n"
        self.agent_dict["relevant_history"] = current_memory
        
        
        last_conversation_idx = -1
        for i,history in enumerate(environment.shared_memory["long_term_memory"]):
            if history.send_name == self.name:
                last_conversation_idx = i

        if last_conversation_idx == -1:
            new_conversation = environment.shared_memory["long_term_memory"]
        elif last_conversation_idx == len(environment.shared_memory["long_term_memory"])-1:
            new_conversation = []
        else:
            new_conversation = environment.shared_memory["long_term_memory"][last_conversation_idx+1:]



        # get chat history
        conversations = Memory.get_chat_history(new_conversation)


        if len(environment.shared_memory["long_term_memory"]) % MAX_CHAT_HISTORY ==0:
            # get summary
            summary_prompt = current_state.summary_prompt[current_role] if current_state.summary_prompt else f"""your name is {self.name},your role is{current_component_dict["style"].role},your task is {current_component_dict["task"].task}.\n"""
            summary_prompt += """Please summarize and extract the information you need based on past key information \n<information>\n {self.short_term_memory} and new chat_history as follows: <new chat>\n"""
            summary_prompt += conversations + "<new chat>\n"
            response = self.LLMs[current_state.name].get_response(None,summary_prompt)
            summary = ""
            for res in response:
                summary += res
            self.agent_dict["short_term_memory"] = summary
            self.short_term_memory = summary

            # memory = relevant_memory + summary + history + query
        current_memory += f"The previous summary of chat history is as follows :<summary>\n{self.short_term_memory}\n<summary>.The new chat history is as follows:\n<new chat> {conversations}\n<new chat>\n<information>,You especially need to pay attention to the last query<query>\n{query.send_name}({query.send_role}):{query.content}\n<query>\n"

        return {"role":"user","content":current_memory}
    

    def generate_sop(self):
        pass

    def reflection(self):
        pass
