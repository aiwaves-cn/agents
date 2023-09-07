Standard Operation Procedure (SOP) System
=========================================

Definition
----------
A Standard Operating Procedure (SOP) is a reasoning graph that consists of a set of step-by-step instructions outlining how to execute a specific task or process. Overall, the SOP System enables users to communicate with different agents simultaneously or create virtual cases, allowing agents to interact with each other.

Demonstrations & Remarks
------------------------
Our SOP System provides several distinct functions: `init_series`, `transit`, `route`, `load_date`, and `send_memory`, which are shown as follows:

Init_series
~~~~~~~~~~~

SOP_init
~~~~~~~~

.. code-block:: python

    class SOP:
        """
        input: the json of the sop
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

Part of the attributes of the whole SOP System is shown as follows:
- LLM: As is aforementioned, our autonomous agents are based on LLM. This attribute receives the tag of a certain type of LLM and invokes it.
- states: The fundamental attribute of an SOP. It stores the information of various agents, including their data and background, which helps run the whole reasoning graph.
- name & role & relation: Basic attributes between various types of agents. Act as tags of the agents.
- controller: To manage our states' activation order, we introduce the controller module. By sending instructions and orders, our controller allocates tasks for each Node and comes up with a proper system order.

States_init
~~~~~~~~~~~

.. code-block:: python

    def init_states(self, states_dict):
        for state_name, state_dict in states_dict.items():
            self.states[state_name] = State(**state_dict)

- states_dict: Components of various types of agents. Whenever the node is activated by users, it will at first select the proper Agent to start its Component.
- Please refer to Environment part for detailed definitions and explanations on other aforementioned attributes.

Relation_init
~~~~~~~~~~~~~

.. code-block:: python

    def init_relation(self, relations):
        for state_name, state_relation in relations.items():
            for idx, next_state_name in state_relation.items():
                self.states[state_name].next_states[idx] = self.states[next_state_name]

- Please refer to States part for detailed definitions and explanations.

Transit
~~~~~~~

.. code-block:: python

    def transit(self, chat_history, **kwargs):
        """
        Determine the next state based on the current situation
        """
        current_state = self.current_state
        controller_dict = self.controller_dict[current_state.name]
        judge_system_prompt = controller_dict["judge_system_prompt"]
        
        max_chat_nums = controller_dict["max_chat_nums"] if "max_chat_nums" in controller_dict else 1000
        if current_state.chat_nums>=max_chat_nums:
            return "1"
        
        # Otherwise, let the controller judge whether to end
        system_prompt = (
            "<environment>"
            + current_state.environment_prompt
            + "</environment>\n"
            + judge_system_prompt
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
        extract_words = controller_dict["judge_extract_words"] if "judge_extract_words" in controller_dict else "end"

        response = self.LLM.get_response(
            chat_messages, system_prompt, last_prompt, stream=False, **kwargs
        )
        next_state = (
            response if response.isdigit() else extract(response, extract_words)
        )
        return next_state

The Transit method judges which state the SOP graph should run based on the current situation. It can also invoke the controller module to automatically determine which state should be called for.

Route
~~~~~

.. code-block:: python

    def route(self, chat_history, **kwargs):
        """
        Determine the role that needs action based on the current situation
        """
        # Get the current state of the controller
        current_state = self.current_state
        controller_type = (
            self.controller_dict[current_state.name]["controller_type"]
            if "controller_type" in self.controller_dict[current_state.name]
            else "rule"
        )

        # If controller type is rule, it is left to LLM to assign roles.
        if controller_type == "rule":
            controller_dict = self.controller_dict[current_state.name]
            
            call_system_prompt = controller_dict["call_system_prompt"]  if "call_system_prompt" in controller_dict else ""
            call_last_prompt = controller_dict["call_last_prompt"] if "call_last_prompt" in controller_dict else ""
            
            allocate_prompt = ""
            roles = list(set(current_state.roles))
            for role in roles:
                allocate_prompt += f"If it's currently supposed to be speaking for {role}, then output <end>{role}<\end>.\n"
                
            system_prompt = (
                "<environment>"
                + current_state.environment_prompt
                + "</environment>\n"
                + call_system_prompt + allocate_prompt
            )

            # last_prompt: note + last_prompt + query
            last_prompt = (
                f"You especially need to pay attention to the last query<query>\n{chat_history[-1].content}\n<query>\n"
                + call_last_prompt
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

            extract_words = controller_dict["call_extract_words"] if "call_extract_words" in controller_dict else "end"

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

The Route method judges which role of agent should be invoked based on the current situation. The Route method first gets the state of the controller, then makes actions based on the type of the controller.

Chatting_series
~~~~~~~~~~~~~~~

First_chat
~~~~~~~~~~

.. code-block:: python

    def first_chat(self, environment, agents):
        # This state is set to not be the first entry, and the chat history is updated to the new state
        self.current_state.is_begin = False
        print("==============================================================================")
        print(f"Now begin to:{self.current_state.name}")
        print("==============================================================================")
        environment.current_chat_history_idx = (
            len(environment.shared_memory["long_term_memory"]) - 1
        )
        
        current_state = self.current_state

        # If this state has an opening statement, do the following
        if current_state.begin_role:
            current_state.current_role = current_state.begin_role
            current_agent_name = self.roles_to_names[current_state.name][
                current_state.begin_role
            ]

            # Find out the current agent
            current_agent = agents[current_agent_name]
            
            # If it is a user, the user is responsible for entering the begin query
            if current_agent.is_user:
                current_state.begin_query = input(f"{current_agent_name}:")
                
            # Otherwise, enter a preset begin query
            else:
                print(
                    f"{current_agent_name}({current_state.begin_role}):{current_state.begin_query}"
                )

            # Update begin query to memory
            memory = Memory(
                current_state.begin_role,
                current_agent_name,
                current_state.begin_query,
            )
            environment.update_memory(memory, current_state)

The First_chat method begins and reloads the situation, changing it into the first-chat circumstance, initializing all the fundamental settings.

Next
~~~~

.. code-block:: python

    def next(self, environment, agents):
        """
        Determine the next state and the role that needs action based on the current situation
        """

        # If it is the first time entering this state
        if self.current_state.is_begin:
           self.first_chat(environment, agents)

        current_state = self.current_state

        # If it is a single loop node, just keep looping
        if len(current_state.next_states) == 1:
            next_state = "0"

        # Otherwise, the controller needs to determine which node to enter.
        else:
            query = environment.shared_memory["long_term_memory"][-1]

            key_history = get_key_history(
                query,
                environment.shared_memory["long_term_memory"][:-1],
                environment.shared_memory["chat_embeddings"][:-1],
            )
            next_state = self.transit(
                chat_history=environment.shared_memory["long_term_memory"][
                    environment.current_chat_history_idx :
                ],
                key_history=key_history,
                environment=environment,
            )

        # If no parse comes out, continue looping
        if not next_state.isdigit():
            next_state = "0"

        # If you enter the termination node, terminate directly
        if self.current_state.next_states[next_state].name == self.finish_state_name:
            self.finished = True
            return None, None

        self.current_state = current_state.next_states[next_state]
        if self.current_state.is_begin:
           self.first_chat(environment, agents)
           
        current_state = self.current_state
        
        # Start assigning roles after knowing which state you have entered. If there is only one role in that state, assign it directly to him.
        if len(current_state.roles) == 1:
            current_role = current_state.roles[0]
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

        # If the next character is not available, pick one at random
        if current_role not in current_state.roles:
            current_role = random.choice(current_state.roles)

        current_agent = agents[self.roles_to_names[current_state.name][current_role]]

        return current_state, current_agent

Examples
--------

We provide diverse SOP Systems of various types of Agents. Get to know in our QuickStart part!🌟
