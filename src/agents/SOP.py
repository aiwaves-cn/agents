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
from LLMs.base_LLM import *
from State import State
from utils import extract, get_key_history
from Memorys import Memory
import json


class SOP:
    """
    input:the json of the sop
    sop indispensable attribute: "states"  "relations"  "root"

    output: a sop graph
    """

    # SOP should have args : "states" "relations" "root"

    def __init__(self, **kwargs):
        self.controller_dict = {}
        LLM_type = kwargs["LLM_type"] if "LLM_type" in kwargs else "OpenAI"
        if LLM_type == "OpenAI":
            self.LLM = (
                OpenAILLM(**kwargs["LLM"])
                if "LLM" in kwargs
                else OpenAILLM(log_path="logs/上帝")
            )

        self.states = {}
        self.init_states(kwargs["states"])
        self.init_relation(kwargs["relations"])
        for state_name, states_dict in kwargs["states"].items():
            if state_name != "end_state" and "controller" in states_dict:
                self.controller_dict[state_name] = states_dict["controller"]

        self.user_names = kwargs["user_names"] if "user_names" in kwargs else []
        self.root = self.states[kwargs["root"]]
        self.current_state = self.root
        self.finish_state_name = (
            kwargs["finish_state_name"]
            if "finish_state_name" in kwargs
            else "end_state"
        )
        self.roles_to_names = None
        self.names_to_roles = None
        self.finished = False

    @classmethod
    def from_config(cls, config_path):
        with open(config_path) as f:
            config = json.load(f)
        sop = SOP(**config)
        return sop

    def init_states(self, states_dict):
        for state_name, state_dict in states_dict.items():
            self.states[state_name] = State(**state_dict)

    def init_relation(self, relations):
        for state_name, state_relation in relations.items():
            for idx, next_state_name in state_relation.items():
                self.states[state_name].next_states[idx] = self.states[next_state_name]

    def transit(self, chat_history, **kwargs):
        """
        Determine the next state based on the current situation
        """
        current_state = self.current_state
        controller_dict = self.controller_dict[current_state.name]
        max_chat_nums = controller_dict["max_chat_nums"] if "max_chat_nums" in controller_dict else 1000
        if current_state.chat_nums>=max_chat_nums:
            return "1"
        

        # 否则则让controller判断是否结束
        # Otherwise, let the controller judge whether to end
        system_prompt = (
            "<environment>"
            + current_state.environment_prompt
            + "</environment>\n"
            + controller_dict["judge_system_prompt"]
        )

        
        last_prompt = controller_dict["judge_last_prompt"]
        environment = kwargs["environment"]
        summary = environment.shared_memory["short_term_memory"]

        chat_messages = [
            {
                "role": "user",
                "content": f"The previous summary of chat history is as follows :<summary>\n{summary}\n<summary>.The new chat history is as follows:\n<new chat> {Memory.get_chat_history(chat_history)}\n<new chat>\n<information>.\nYou especially need to pay attention to the last query<query>\n{chat_history[-1].content}\n<query>\n",
            }
        ]
        extract_words = controller_dict["judge_extract_words"]

        response = self.LLM.get_response(
            chat_messages, system_prompt, last_prompt, stream=False, **kwargs
        )
        next_state = (
            response if response.isdigit() else extract(response, extract_words)
        )
        return next_state

    def route(self, chat_history, **kwargs):
        """
        Determine the role that needs action based on the current situation
        """
        # 获取当前状态下的控制器
        # Get the current state of the controller
        current_state = self.current_state
        controller_type = (
            self.controller_dict[current_state.name]["controller_type"]
            if "controller_type" in self.controller_dict[current_state.name]
            else "rule"
        )


        # 如果是rule 控制器，则交由LLM进行分配角色
        # If  controller type is rule, it is left to LLM to assign roles.
        if controller_type == "rule":
            controller_dict = self.controller_dict[current_state.name]
            
            allocate_prompt = ""
            roles = list(set(current_state.roles))
            for role in roles:
                allocate_prompt += f"If it's currently supposed to be speaking for {role}, then output <end>{role}<\end>.\n"
                
            system_prompt = (
                "<environment>"
                + current_state.environment_prompt
                + "</environment>\n"
                + controller_dict["call_system_prompt"] + allocate_prompt
            )

            # last_prompt: note + last_prompt + query
            last_prompt = (
                f"You especially need to pay attention to the last query<query>\n{chat_history[-1].content}\n<query>\n"
                + controller_dict["call_last_prompt"]
                + allocate_prompt
                + f"Note: The person whose turn it is now cannot be the same as the person who spoke last time, so <end>{chat_history[-1].send_name}</end> cannot be output\n."
            )

            # Intermediate historical conversation records
            chat_messages = [
                {
                    "role": "user",
                    "content": f"The chat history is as follows:\n<history>\n{Memory.get_chat_history(chat_history)}<history>\n，\
                    The last person to speak is: {chat_history[-1].send_name}\n.",
                }
            ]

            extract_words = controller_dict["call_extract_words"]

            response = self.LLM.get_response(
                chat_messages, system_prompt, last_prompt, stream=False, **kwargs
            )

            # get next role
            next_role = extract(response, extract_words)

        # Speak in order
        elif controller_type == "order":
            # If there is no begin role, it will be given directly to the first person.
            if not current_state.current_role:
                next_role = current_state.roles[0]
            # otherwise first
            else:
                current_state.index += 1
                current_state.index =  (current_state.index) % len(current_state.roles)
                next_role = current_state.roles[current_state.index]
        # random speak
        elif controller_type == "random":
            next_role = random.choice(current_state.roles)
        current_state.current_role = next_role

        return next_role

    def first_chat(self,environment,agents):
        # 该状态设为非第一次进入,并将聊天记录更新至新状态
        # This state is set to not be the first entry, and the chat history is updated to the new state
        self.current_state.is_begin = False
        print("==============================================================================")
        print(f"Now begin to:{self.current_state.name}")
        print("==============================================================================")
        environment.current_chat_history_idx = (
            len(environment.shared_memory["long_term_memory"]) - 1
        )
        
        current_state = self.current_state

        # 如果该状态下有开场白，则进行以下操作
        # If there is an opening statement in this state, do the following
        if current_state.begin_role:
            current_state.current_role = current_state.begin_role
            current_agent_name = self.roles_to_names[current_state.name][
                current_state.begin_role
            ]

            # 找出当前的agent
            # Find out the current agent
            current_agent = agents[current_agent_name]
            
            # 如果是用户的话,则用户负责输入开场白
            # If it is a user, the user is responsible for entering the begin query
            if current_agent.is_user:
                current_state.begin_query = input(f"{current_agent_name}:")
                
            # Otherwise, enter a preset begin query
            else:
                print(
                    f"{current_agent_name}({current_state.begin_role}):{current_state.begin_query}"
                )

            # 将开场白更新至记忆
            # Update begin query to memory
            memory = Memory(
                current_state.begin_role,
                current_agent_name,
                current_state.begin_query,
            )
            environment.update_memory(memory, current_state)
    
    def next(self, environment, agents):
        """
        Determine the next state and the role that needs action based on the current situation
        """
        
        # 如果是第一次进入该状态
        # If it is the first time to enter this state
        
        if self.current_state.is_begin:
           self.first_chat(environment,agents)

        current_state = self.current_state

        # 如果是单一循环节点，则一直循环即可
        # If it is a single loop node, just keep looping
        if len(current_state.next_states) == 1:
            next_state = "0"

        # 否则则需要controller去判断进入哪一节点
        # Otherwise, the controller needs to determine which node to enter.
        else:
            query = environment.shared_memory["long_term_memory"][-1]

            key_history = get_key_history(
                query,
                environment.shared_memory["long_term_memory"][:-1],
                environment.shared_memory["chat_embeddings"][:-1],
            )

            # 只传入当前状态下的对话记录
            # Only pass in the conversation record in the current state
            next_state = self.transit(
                chat_history=environment.shared_memory["long_term_memory"][
                    environment.current_chat_history_idx :
                ],
                key_history=key_history,
                environment=environment,
            )

        # 如果没有parse出来则继续循环
        # If no parse comes out, continue looping
        if not next_state.isdigit():
            next_state = "0"

        # 如果进入终止节点，则直接终止
        # If you enter the termination node, terminate directly
        if self.current_state.next_states[next_state].name == self.finish_state_name:
            self.finished = True
            return None, None

        self.current_state = current_state.next_states[next_state]
        if self.current_state.is_begin:
           self.first_chat(environment,agents)
           
        current_state = self.current_state
        
        # 知道进入哪一状态后开始分配角色，如果该状态下只有一个角色则直接分配给他
        # Start assigning roles after knowing which state you have entered. If there is only one role in that state, assign it directly to him.
        if len(current_state.roles) == 1:
            current_role = current_state.roles[0]

        # 否则controller进行分配
        # Otherwise the controller determines
        else:
            query = environment.shared_memory["long_term_memory"][-1]

            key_history = get_key_history(
                query,
                environment.shared_memory["long_term_memory"][:-1],
                environment.shared_memory["chat_embeddings"][:-1],
            )
            current_role = self.route(
                chat_history=environment.shared_memory["long_term_memory"][
                    environment.current_chat_history_idx :
                ],
                key_history=key_history,
            )

        # 如果下一角色不在，则随机挑选一个
        # If the next character is not available, pick one at random
        if current_role not in current_state.roles:
            current_role = random.choice(current_state.roles)

        current_agent = agents[self.roles_to_names[current_state.name][current_role]]

        return current_state, current_agent
