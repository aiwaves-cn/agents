
# SOP========================================================================================================
# "environment_prompt"
# current_state , self(sop)
Get_environment_prompt = "f\"The current scenario is as follows <environment> {self.current_state.environment_prompt} </environment>\""


# sop.transit
#================================================================
Transit_system_prompt = "f\"{environment_prompt};{judge_system_prompt}\""

#  transit chat message 
#  "environment_prompt" is get from "Get_environment_prompt" ; "chat_history_message" if from Memory
Transit_message = "f\"{environment_summary};The chat history is as follows:\\n<chat> {chat_history_message}\\n</chat>;You especially need to pay attention to the last query<query>\\n{query}\\n</query> and the relevant conversation <relevant>\\n{relevant_history} \\n</relevant>\\n\""


Transit_last_prompt = "f\"{judge_last_prompt}\""
#sop.transit================================================================

# sop.call
#================================================================
# help controller to determine the next role to speak.(the {} is agent role)    call_prompt + allocate_component  
Allocate_component = "f\"If it's currently supposed to be speaking for {role}, then output <end>{role}</end>.\\n\""

# environment_prompt is get from "Get_environment_prompt" ; "chat_history_message" if from Memory
Call_system_prompt = "f\"{environment_prompt};{call_system_prompt};{allocate_prompt}\""

#
Call_last_prompt = "f\"You especially need to pay attention to the last query<query>\\n{query}\\n</query> and the relevant conversation <relevant>\\n{relevant_history} \\n</relevant>\\n;{allocate_prompt};Note: The person whose turn it is now cannot be the same as the person who spoke last time, so {last_name} cannot be output\\n.\""

Call_message = "f\"The chat history is as follows:\\n<history>\\n{chat_history_message}</history>\\n;The last person to speak is: {last_name}\\n. \""
#sop.call================================================================
# SOP========================================================================================================






# Memory========================================================================================================
Single_message = "f\"{name} said that :{content}\""

Chat_total_message = "f\"{chat_history}\""
# Memory========================================================================================================






# Environment========================================================================================================
Default_environment_summary_system_prompt = "\"\\nYour task is to summarize the historical dialogue records according to the current scene, and summarize the most important information\""

Default_environment_summary_last_prompt = "\"Please make a summary based on the historical chat records, the output format is history summary: \{your summary content\} \""

Environment_summary_memory =  "f\"The information you need to know is as follows:\\n</information>\\n\
            The summary of the previous dialogue history is:<summary>\\n{summary}\\n.</summary>\
            The latest conversation record is as follows:\\n<hisroty> {chat_history}\\n</history>,\
            the relevant chat history you may need is:<relevant>{relevant_history}</relevant>\""
            
Environment_summary_system_prompt = "f\"{environment_prompt};{current_memory};{summary_system_prompt};\""


# observe
Agent_observe_relevant_memory = "f\"The relevant chat history are as follows:\\n<relevant_history>{relevant_memory} </relevant_history>\\n\""


Agent_observe_memory = "f\"Here's what you need to know(Remember, this is just information, Try not to repeat what's inside):\\n<information>\\n{relevant_memory};\
            The previous summary of chat history is as follows :<summary>\\n{agent.short_term_memory}\\n</summary>.\
            The new chat history is as follows:\\n<new chat> {conversations}\\n</new chat>\\n\
            </information>\""
# Environment========================================================================================================




# Agent========================================================================================================
Agent_summary_system_prompt = "f\"{summary_prompt};Please summarize past key summary \\n<summary>\\n {self.short_term_memory} </summary>and new chat_history as follows: <new chat>\\n{conversations}</new chat>\""          
            
Agent_last_prompt = "f\"{last_prompt};\\n{query.send_name} said that: {query.content};Please try to respond differently from your existing knowledge, and avoid repeating what others have said.Please just talk as normal.\""

Agent_system_prompt = "f\"{system_prompt},\""
# Agent========================================================================================================