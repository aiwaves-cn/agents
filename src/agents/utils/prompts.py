SUMMARY_PROMPT_TEMPLATE = """Summarize the lines of conversation provided.

EXAMPLE
Conversation:
role: Human
speak content: What do you think of artificial intelligence?

role: AI
speak content: I think artificial intelligence is a force for good.

role: Human
speak content: Why do you think artificial intelligence is a force for good?

role: AI
speak content: Because artificial intelligence will help humans reach their full potential.

Summary:
The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good because it will help humans reach their full potential.
END OF EXAMPLE

Conversation:
{conversation}

Summary:"""

SINGLE_MESSAGE_TEMPLATE = "name: {name}\nrole: {role}\nspeak content: {content}\n"

NODE_DESCRIPTION_TEMPLATE = (
    "Here is the description of the current scenario: {node_description}\n"
)

TRANSIT_LAST_PROMPT_TEMPLATE = "The nodes that can be transited to are: {next_nodes}. Please decide the next node that should be transited to, and finally, output <{extract_word}>node_name</{extract_word}> where node_name is the name of the next node. Let's think step by step."

TRASNSIT_MESSAGE_TEMPLATE = "{environment_summary}\nHere is the the chat history:\n {chat_history_message}\nHere is the last query you especially need to pay attention:\n{query}\n"

RELEVANT_HISTORY_TEMPLATE = (
    "Here is the relevant history conversation:\n{relevant_history}\n"
)

ASSIGN_ROLE_PROMPT_TEMPLATE = "If it's currently supposed to be speaking for {role}, then output <{extract_word}>{role}</{extract_word}>.\n"

ROUTE_LAST_PROMPT_TEMPLATE = "Here is the last query you especially need to pay attention:\n{query}\nHere is the the relevant conversation:\n{relevant_history}\nNow please choose the person to speak according to the following rules: \n{assign_role_prompt}\nNote: The person whose turn it is now cannot be the same as the person who spoke last time, so {last_name} cannot be output.\n"

ROUTE_MESSAGE_TEMPLATE = "Here is the the chat history:\n{chat_history_message}\nHere is the name of the person who last speak: {last_name}\n"

AGENT_LAST_PROMPT_TEMPLATE = "{last_prompt}; Please continue the conversation on behalf of {name}, making your answer appear as natural and coherent as possible, and try to speak differently from what others have already said."

OBSERVATION_TEMPLATE = "Here's what you need to know(Remember, this is just information, Try not to repeat what's inside):\nHere is the relevant history you may need:\n{environment_relevant_memory}\nHere is the new chat history:\n{agent_relevant_memory}\n"


# The following prompt templates are used in the node prompts

STYLE_PROMPT_TEMPLATE = "You need to follow the output style: {style}.\n"

TASK_PROMPT_TEMPLATE = "The task you need to execute is: {task}.\n"

RULE_PROMPT_TEMPLATE = "The rule you need to follow is: {rule}.\n"

DEMONSTRATIONS_PROMPT_TEMPLATE = (
    "Here are the demonstrations you can refer to:\n{demonstrations}.\n"
)

OUTPUT_PROMPT_TEMPLATE = "Please contact the above to extract <{output}> and </{output}>, do not perform additional output, please output in strict accordance with the above format!\n"

LAST_PROMPT_TEMPLATE = "{last}"

DEFAULT_NODE_PROMPT_TEMPLATES = {
    # "style": STYLE_PROMPT_TEMPLATE,
    # "task": TASK_PROMPT_TEMPLATE,
    # "rule": RULE_PROMPT_TEMPLATE,
    # "demonstrations": DEMONSTRATIONS_PROMPT_TEMPLATE,
    # "output": OUTPUT_PROMPT_TEMPLATE,
    # "last": LAST_PROMPT_TEMPLATE,
}

# The following prompt templates are used in the config generation

TASK_CONFIG_GENERATION_PROMPT_TEMPLATE = "Please summarise and generate a task JSON based on a user's query. The JSON must contain three string fields: 'task_name', 'task_type' and 'task_description'. The user's query is as follows: '{query}'."

SOP_CONFIG_GENERATION_PROMPT_TEMPLATE = "Standard Operating Procedure, or SOP, refers to the standard operating procedures and requirements of a task described in a uniform format for guiding and standardising the work of agents. SOP is represented in the form of a directed graph, please break down the task into multiple subtasks. The subtasks should be relatively independent of each other. Each node in the SOP needs to complete a subtask before going to transit to the next node. You need to define an SOP based on the given task description, containing one or more nodes and the corresponding edge relationships. The SOP JSON must contain four fields: 'nodes', 'edges', 'root' and 'end'. The 'nodes' field is a dictionary with key being the node name in string format and value being the detailed node subtask description in string format. The edges field is a dictionary, where key is the node name in string format and value is a list of all subsequent nodes of all that node. The 'root' field is the name of the root node in string format. The 'end' field is the name of the end node in string format(default to be 'end_node'). The user's query is as follows: '{query}', the task description is as follows: '{task_description}'."

NODE_ROLES_CONFIG_GENERATION_PROMPT_TEMPLATE = "You are an experienced project manager and your team is working on a task as follows: '{task_description}'. Now you have been assigned a subtask as follows: '{node_description}'. You will need to assign one or more roles to this task in the most efficient way possible, taking care to assign as few roles as possible and to keep each role's job assignment as independent as possible. Outputs the role assignment as a JSON, which must contain two fields: 'roles' and 'begin_role'. The 'roles' filed is a dictionary with key being the role name in string format and value being the role description in string format. The 'begin_role' field is the name of the role to work in a subtask."

NODE_PROMPTS_CONFIG_GENERATION_PROMPT_TEMPLATE = "You are an experienced project manager and your team is working on a task as follows: '{task_description}'. Now you have been assigned a subtask as follows: '{node_description}'. You have assigned the roles needed to complete the task as follows: '{node_roles_description}'. Now you need to define the prompts to regulate the specific behavior of the role '{role}'. Output the prompts as a JSON, which must contain two fields: 'prompt_templates' and 'prompt_paddings'. The 'prompt_templates' field is a dictionary with key being the 'prompt_type' and value being the prompt template with at least one or more blank paddings. The blank paddings must be in the form of __padding_name__, where 'padding_name' can be different. Note that 'prompt_templates' can be shared between roles and the prompt templates that already exist are as follows: {node_prompt_templates}. Note that you need to avoid duplicating already existing prompt templates with the same 'prompt_type' in the 'prompt_templates' field. The 'prompt_paddings' field is a dict where the key is the 'prompt_type' and value is a dict with key being the padding name and the value being the padding content that can be filled in the specific blank of the prompt template of the same type. Note that 'prompt_paddings' may be specific to each role."

TRANSIT_CONTROLLER_CONFIG_GENERATION_PROMPT_TEMPLATE = "You are an experienced project manager and your team is working on a task as follows: '{task_description}'. You have been assigned a subtask as follows: '{node_description}'. You have assigned the roles needed to complete the task as follows: '{node_roles_description}'. Now You need to define a set of rules to determine when this subtask is complete, based on the output of the roles."

ROUTE_CONTROLLER_CONFIG_GENERATION_PROMPT_TEMPLATE = "You are an experienced project manager and your team is working on a task as follows: '{task_description}'. You have been assigned a subtask as follows: '{node_description}'. You have assigned the roles needed to complete the task as follows: '{node_roles_description}'. Now You need to define a set of rules to determine how to route to the next role after a role. Output the rules as a JSON, which must contain two fields: 'route_type' and 'route_system_prompt'. The 'route_type' field is a string that can be 'order', 'random' and 'llm'. 'order' means the next role is the successor role in the order of the roles. 'random' means the next role is randomly selected from the roles. 'llm' means the next role is selected by the AI model. The 'route_system_prompt' field is a string that describes the rules for routing. The 'route_system_prompt' field is a string that describes the rules for routing, which is necessary if the 'route_type' is 'llm', otherwise it can be empty."

AGENT_TEAM_CONFIG_GENERATION_PROMPT_TEMPLATE = "You are a human resource specialist and you need to assign the minimum number of person to different roles in the project based on the task requirements, which can be done by having the same person play roles with similar skills required. Note that one people cannot play different roles at the same node. The task description is as follows: '{task_description}'. All roles description is as follows: '{all_roles_description}'. Now you need to output a dict in JSON format for people allocation, where the key of the dict is the person's name that matches '^[a-zA-Z0-9_-]{{1,64}}$' and the value of the dict is another dict with the key being the node name and the value being the allocated role name at the node. Note that the name of the person cannot be duplicated, and there is one and only one person who can play a particular role, but a person can play more than one role. Note that all the roles must be allocated to specific people."
