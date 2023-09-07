States
======
Definition:
-----------
As previously mentioned, we utilize SOP to operate the autonomous agent. Our SOP reasoning graph is composed of various States. These states play distinct roles, contributing to the entire system. We've developed a straightforward state, the SIMPLIST state, primarily based on LLM.

Attributes & Examples:
-----------------------
- Basic codes for State class are as follows:

  .. code-block:: python

    class State:
        def __init__(self, **kwargs):
            self.next_states = {}
            self.name = kwargs["name"]
            self.environment_prompt = kwargs["environment_prompt"] if "environment_prompt" in kwargs else ""
            self.begin_role = kwargs["begin_role"] if "begin_role" in kwargs else None
            self.begin_query = kwargs["begin_query"] if "begin_query" in kwargs else None
            self.is_begin = True if self.begin_role else False
            self.summary_prompt = kwargs["summary_prompt"] if "summary_prompt" in kwargs else None
            self.current_role = self.begin_role
            self.roles = kwargs["roles"] if "roles" in kwargs else []
            self.components = self.init_components(kwargs["agent_states"]) if "agent_states" in kwargs else {}
            self.index = self.roles.index(self.begin_role) if self.begin_role in self.roles else 0
            self.chat_nums = 0

  Part of the attributes are shown below:
  
  - agent_states: Components of various types of agents. Whenever the state is activated by users, it will at first select the proper Agent to start its Component.
  - environment_prompt: Prompt given by users. For detailed information, please turn to Component page.
  - summary_prompt: Prompt initiated from the system. For detailed information, please turn to Component page.
  - begin_role & begin_query: Role and query of the agents which are set at the beginning of the conversation.
  - next_states: Relations between states. Extraordinarily useful when the state graph is relatively sophisticated.

Methods:
--------
Our states provide one single method, namely init_components, which is shown as follows:

init_components
^^^^^^^^^^^^^^
The init_components method receives various types of components, and then classifies and places them. Basic codes are omitted.

Environment
===========
Definition:
-----------
Apparently, every autonomous agent should adjust to different circumstances, thus changing their chatting style and information immediately. To help manage their self-evolution, we established the memory mode to guide its behaviors. As its name shows, the memory module stores the whole chatting history of the particular agent. To edit and compile its contents and update the memory in time, we use the Environment module to guide its behavior.

Attributes & Examples:
-----------------------
Basic codes of an Environment module are as follows:

.. code-block:: python

    class Environment:
        def __init__(self, config) -> None:
            self.shared_memory = {"long_term_memory": [], "short_term_memory": None}
            self.agents = None
            self.summary_system_prompt = {}
            self.summary_last_prompt = {}
            self.environment_prompt = {}
            self.environment_type = config["environment_type"] if "environment_type" in config else "cooperate"
            self.current_chat_history_idx = 0

            # Initialize the summary method for each state
            for state_name, state_dict in config["states"].items():
                if state_name != "end_state":
                    self.summary_system_prompt[state_name] = (
                        state_dict["summary_system_prompt"]
                        if "summary_system_prompt" in state_dict
                        else "\nYour task is to summarize the historical dialogue records according to the current scene, and summarize the most important information"
                    )

                    self.summary_last_prompt[state_name] = (
                        state_dict["summary_last_prompt"]
                        if "summary_last_prompt" in state_dict
                        else "Please make a summary based on the historical chat records, the output format is history summary: \{your summary content\} "
                    )

                    self.environment_prompt[state_name] = (
                        state_dict["environment_prompt"]
                        if "environment_prompt" in state_dict
                        else " "
                    )
                    LLM_type = (
                        state_dict["LLM_type"] if "LLM_type" in state_dict else "OpenAI"
                    )
                    if LLM_type == "OpenAI":
                        if "LLM" in state_dict:
                            self.LLM = OpenAILLM(**state_dict["LLM"])
                        else:
                            self.LLM = OpenAILLM()

            self.roles_to_names = None
            self.names_to_roles = None

  Part of the attributes are shown below:
  
  - LLM: As is aforementioned, our autonomous agents are based on LLM. This attribute receives the tag of a certain type of LLM and invokes it.

Methods:
--------
summary:
^^^^^^^
The summary method receives the current chatting history, and then summarizes the situation in the current environment every once in a while.

.. code-block:: python

    def summary(self, current_state):
        """
        Summarize the situation in the current environment every once in a while
        """
        MAX_CHAT_HISTORY = eval(os.environ["MAX_CHAT_HISTORY"])
        current_state_name = current_state.name

        query = self.shared_memory["long_term_memory"][-1]
        key_history = get_key_history(
            query,
            self.shared_memory["long_term_memory"][:-1],
            self.shared_memory["chat_embeddings"][:-1],
        )

        relevant_history = Memory.get_chat_history(key_history)
        chat_history = Memory.get_chat_history(
            self.shared_memory["long_term_memory"][-MAX_CHAT_HISTORY + 1 :]
        )
        summary = self.shared_memory["short_term_memory"]
        
        # current_memory = summary + chat history + relevant history
        current_memory = f"The information you need to know is as follows:\n<information>\n\
            The summary of the previous dialogue history is:<summary>\n{summary}\n.\
            The latest conversation record is as follows:\n<hisroty> {chat_history}\n<history>,\
            the relevant chat history you may need is:<relevant>{relevant_history}<relevant>"

        # system prompt = environment prompt + current memory + system prompt
        system_prompt = (
            self.environment_prompt[current_state_name]
            + current_memory
            + self.summary_system_prompt[current_state_name]
        )
        response = self.LLM.get_response(None, system_prompt, stream=False)
        return response

excute_action:
^^^^^^^^^^^^^
The execute_action method gets certain types of memories and edits the content through given ways.

.. code-block:: python

    def execute_action(self, action):
        """
        get memory by action
        """
        response = action["response"] if "response" in action else ""
        res_dict = action["res_dict"] if "res_dict" in action else {}
        is_user = action["is_user"] if "is_user" in action else False
        send_name = action["name"]
        send_role = action["role"]
        all = ""
        for res in response:
            all += res
        parse = f"{send_name}:"

        # The third person in the dialogue was deleted.
        while parse in all:
            index = all.index(parse) + len(parse)
            all = all[index:]
        if not is_user:
            print(f"{send_name}({send_role}):{all}")
        memory = Memory(send_role, send_name, all)
        return memory

update_memory:
^^^^^^^^^^^^^^
The update_memory method updates memory immediately, enabling the agent to adjust to the current circumstance.

.. code-block:: python

    def update_memory(self, memory, current_state):
        """
        update chat embeddings and long-term memory, short-term memory, agents' long-term memory
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

        if len(self.shared_memory["long_term_memory"]) % MAX_CHAT_HISTORY:
            summary = self.summary(current_state)
            self.shared_memory["short_term_memory"] = summary

        self.agents[memory.send_name].update_memory(memory)
