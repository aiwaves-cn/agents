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
"""standard operation procedure of an LLM Autonomous agent"""
import random
from LLM import *
from State import State
from utils import extract,get_key_history
from Memory import Memory

class SOP:
    """
    input:the json of the sop
    sop indispensable attribute: begin_role   begin_query begin_query states(agent_states)  relation

    output: a sop graph
    """

    def __init__(self, **kwargs):
        
        self.controller_dict = {}
        LLM_type = kwargs['LLM_type'] if "LLM_type" in kwargs else "OpenAI"
        if LLM_type == "OpenAI":
            self.LLM = OpenAILLM(**kwargs["LLM"])
            
        self.states = {}
        self.init_states(kwargs["states"])
        self.init_relation(kwargs["relations"])
        for state_name,states_dict in kwargs["states"].items():
            self.controller_dict[state_name] = states_dict["controller"]
            
            
        self.user_roles = kwargs["user_roles"] if "user_roles" in kwargs else []
        self.root = self.states[kwargs["root"]]
        self.current_state = self.root
        self.finish_state_name =  kwargs["finish_state_name"] if "finish_state_name" in kwargs else "end_state"
        self.roles_to_names = None
        self.names_to_roles = None
        self.finished = False

    @classmethod
    def from_config(cls,config_path):
        with open(config_path) as f:
            config = json.load(f)
        sop = SOP(**config)
        return sop
    
    
    def init_states(self,states_dict):
        for state_name,state_dict in states_dict.items():
            self.states[state_name] = State(**state_dict)
    
    def init_relation(self,relations):
        for state_name,state_relation in relations.items():
            for idx , next_state_name in state_relation.items():
                self.states[state_name].next_states[idx] = self.states[next_state_name] 
                
    def transit(self, chat_history,**kwargs):
        
        current_state = self.current_state
        controller_dict = self.controller_dict[current_state.name]
        system_prompt = (
            "<environment>"
            + current_state.environment_prompt
            + "</environment>\n"
            + controller_dict["judge_system_prompt"]
        )

        last_prompt = controller_dict["judge_last_prompt"]
        extract_words = controller_dict["judge_extract_words"]
        response = self.LLM.get_response(
            chat_history, system_prompt, last_prompt, stream=False, **kwargs
        )
        next_state = extract(response, extract_words)
        return next_state

    def route(self, current_state,chat_history,**kwargs):
        controller_type = (
            self.controller_dict[current_state.name]["controller_type"]
            if "controller_type" in self.controller_dict[current_state.name]
            else "rule"
        )
        if controller_type == "rule":
            controller_dict = self.controller_dict[current_state.name]
            system_prompt = (
                "<environment>"
                + current_state.environment_prompt
                + "</environment>\n"
                + controller_dict["call_system_prompt"]
            )


            last_name = chat_history[-1].send_name
            last_prompt = f"The last person to speak is: {last_name}\nNote: The person whose turn it is now cannot be the same as the person who spoke last time, so <end>{last_name}</end> cannot be output"

            last_prompt += controller_dict["call_last_prompt"]
            extract_words = controller_dict["call_extract_words"]

            chat_history = Memory.get_chat_history(chat_history)

            system_prompt += f"The dialogue is recorded as follows:\n<history>\n{chat_history}<history>\n"
            
            response = self.LLM.get_response(
                None, system_prompt, last_prompt, stream=False,**kwargs
            )
            
            next_role = extract(response, extract_words)
            
        elif controller_type == "order":
            if not current_state.current_role:
                next_role = current_state.roles[0]
            else:
                index = current_state.roles.index(current_state.current_role)
                next_role = current_state.roles[(index + 1) % len(current_state.roles)]

        elif controller_type == "random":
            next_role = random.choice(current_state.roles)

        return next_role

    def next(self,environment,agents):
        if self.current_state.is_begin:
            current_state = self.root
            current_agent_name = self.roles_to_names[current_state.name][current_state.begin_role]
            memory =Memory(current_state.begin_role,current_agent_name,current_state.begin_query)
            print(f"{current_agent_name}({current_state.begin_role}):{current_state.begin_query}")
            environment.update_memory(memory,current_state)
            self.current_state.is_begin = False
            return self.next(environment,agents)
        
        current_state = self.current_state
        if len(current_state.next_states) == 1:
            next_state = "0"
        else:
            query = environment.shared_memory["long_term_memory"][-1]

            key_history = get_key_history(
                query,
                environment.shared_memory["long_term_memory"][:-1],
                environment.shared_memory["chat_embeddings"][:-1],
            )
            next_state = self.transit(
                chat_history=environment.shared_memory["long_term_memory"],
                summary=environment.shared_memory["short_term_memory"],
                key_history=key_history,
                environment_prompt=current_state.environment_prompt,
            )

        if not next_state.isdigit():
            next_state = "0"

        next_state = current_state.next_states[next_state]
        
        if len(current_state.roles) == 1:
            next_role = current_state.roles[0]
        else:
            query = environment.shared_memory["long_term_memory"][-1]
               
            key_history = get_key_history(
                query,
                environment.shared_memory["long_term_memory"][:-1],
                environment.shared_memory["chat_embeddings"][:-1],
            )
            next_role = self.route(
                current_state=next_state,
                chat_history=environment.shared_memory["long_term_memory"],
                summary=environment.shared_memory["short_term_memory"],
                key_history=key_history,
                environment_prompt=current_state.environment_prompt,
            )

        if next_role not in next_state.roles:
            next_role = random.choice(next_state.roles)
        
        is_user = next_role in self.user_roles
        
        while current_state!=next_state:
            environment.send_message(next_state)
            current_state = next_state
            current_agent_name = self.roles_to_names[current_state.name][current_state.begin_role]
            memory = {"role":"user","content":f"{current_agent_name}({current_state.begin_role}):{current_state.begin_query}"}
            print(f"{current_agent_name}({current_state.begin_role}):{current_state.begin_query}")
            environment.update_memory(memory,current_state)
            next_state,next_agent = self.next(environment,agents)


        self.current_state = next_state
        if next_state.name == self.finish_state_name:
            self.finished = True
            return None , None
        current_agent = agents[self.roles_to_names[next_state.name][next_role]]
        current_agent.is_user = is_user
        current_state.current_role = next_role

        return current_state,current_agent
