
# SOP========================================================================================================
# "environment_prompt"
# current_state , self(sop)
Get_environment_prompt = "f\"Here are the description of current scenario:{self.current_state.environment_prompt};\\n\""


# sop.transit
#================================================================
Transit_system_prompt = "f\"{environment_prompt};\\n{judge_system_prompt}\\n\"";

#  transit chat message 
#  "environment_prompt" is get from "Get_environment_prompt" ; "chat_history_message" if from Memory
Transit_message = "f\"{environment_summary};\\n Here is the The chat history:\\n {chat_history_message};\\nHere is the last query you especially need to pay attention:\\n{query};\\n Here is the relevant conversation: \\n{relevant_history} \\n\\n\""


Transit_last_prompt = "f\"{judge_last_prompt}\""
#sop.transit================================================================

# sop.call
#================================================================
# help controller to determine the next role to speak.(the {} is agent role)    call_prompt + allocate_component  
Allocate_component = "f\"If it's currently supposed to be speaking for {role}, then output <end>{role}</end>.\\n\""

# environment_prompt is get from "Get_environment_prompt" ; "chat_history_message" if from Memory
Call_system_prompt = "f\"{environment_prompt};\\n{call_system_prompt};\\n{allocate_prompt}.\\n\""

#
Call_last_prompt = "f\"Here is the last query you especially need to pay attention:\\n{query};\\n Here is the the relevant conversation :\\n{relevant_history};\\nNow please choose the person to speak according to the following rules :{allocate_prompt};\\nNote: The person whose turn it is now cannot be the same as the person who spoke last time, so {last_name} cannot be output\\n.\""

Call_message = "f\"Here is the chat history:\\n{chat_history_message};\\nHere is the name of the person who last speak: {last_name}.\\n \""
#sop.call================================================================
# SOP========================================================================================================






# Memory========================================================================================================
Single_message = "f\"role: {role} \\n speak content : {content}; \""

Chat_total_message = "f\"<chat history>{{{chat_history}}}</chat history>\""
# Memory========================================================================================================






# Environment========================================================================================================
Default_environment_summary_system_prompt = "\"\\nYour task is to summarize the historical dialogue records according to the current scene, and summarize the most important information\""

Default_environment_summary_last_prompt = "\"Please make a summary based on the historical chat records, the output format is history summary: \{your summary content\} \""

Environment_summary_memory =  "f\"Here is the information you need to know:\\n\\n\
            Here is the summary of the previous dialogue history:\\n{summary}.\\n\
            Here is the latest conversation record:\\n {chat_history},\\n\
            Here is the relevant chat history you may need:{relevant_history}.\\n\""
            
Environment_summary_system_prompt = "f\"{environment_prompt};\\n{current_memory};\\n{summary_system_prompt};\\n\""


# observe
Agent_observe_relevant_memory = "f\"\\n{relevant_memory}. \\n\""


Agent_observe_memory = "f\"Here's what you need to know(Remember, this is just information, Try not to repeat what's inside):\\nHere is the relevant chat history you may need:{relevant_memory};\\n\
Here is the previous summary of chat history :\\n{agent.short_term_memory}.\\n\
Here is the relevant memory :\\n{agent.relevant_memory}.\\n\
Here is the new chat history:\\n {conversations};\\n\
            \""
# Environment========================================================================================================




# Agent========================================================================================================
Agent_summary_system_prompt = "f\"{summary_prompt};\\n Here is the past summary:{self.short_term_memory};\\nHere is the new chat_history:\\n{conversations};\\nPlease summary Please summarize based on the above information;\\n\""          
            
Agent_last_prompt = "f\"{last_prompt};Please continue the conversation on behalf of {name} based on your known information;\""
Agent_system_prompt = "f\"{system_prompt},\""
# Agent========================================================================================================
