import os
import json

def create_sop(folder_name: str = "novel_outline", encoding: str = "utf-8", save_name: str = "novel_outline") -> None:
    folder = f'./{folder_name}'
    file_list = os.listdir(folder)
    plot_list = []

    for file in file_list:
        if "character" in file:
            character_file = file
        # elif "chapter" in file and "plot" in file:
        elif "plot" in file:
            plot_list.append(file)
    plot_list.sort()

    with open(os.path.join(folder, character_file), 'r', encoding=encoding) as f:
        character_settings = json.load(f)

    plot_list_new = []
    for plot_name in plot_list:
        legal = True
        with open(os.path.join(folder, plot_name), 'r', encoding=encoding) as f:
            plot = json.load(f)
        c_mentioned = plot["characters"]
        for c in c_mentioned:
            if c not in character_settings:
                legal = False
                break
        if legal:
            plot_list_new.append(plot_name)
    plot_list = plot_list_new
    plot_list.sort()
            

    # creat json file of sop
    sop_file = f"./{save_name}.json"
    sop_dict = {
        "config": {
            "API_KEY" : "API_KEY",
            "PROXY" : "PROXY",
            "MAX_CHAT_HISTORY" : "100",
            "TOP_K" : "1",
            "ACTIVE_MODE" : "0",
            "GRADIO" : "0",
            "User_Names" : "[]"
        },
        "LLM_type": "OpenAI",
        "LLM": {
            "temperature": 0.0,
            "model": "gpt-3.5-turbo-16k-0613",
            "log_path": "logs/god"
        },
        "agents": {},
        "root": "state1",
        "relations": {},
        "states": {
            "end_state":{
                "name":"end_state",
                "agent_states":{}
            }
        }
    }
    
    nodes_num = len(plot_list)
    # nodes_num = 4 if nodes_num > 4 else nodes_num
    plot_list_new = []
    for i in range(nodes_num):
        plot_file = plot_list[i]
        with open(os.path.join(folder, plot_file), 'r', encoding=encoding) as f:
            plot = json.load(f)
        plot_content = plot["plot"] 
        c_mentioned = plot["characters"]
        if len(c_mentioned) > 1:
            plot_list_new.append(plot_file)
    plot_list = plot_list_new
    nodes_num = len(plot_list)
    nodes_num = 4 if nodes_num > 4 else nodes_num
    
    for i in range(nodes_num):
        node_name = f"state{i+1}"
        plot_file = plot_list[i]
        with open(os.path.join(folder, plot_file), 'r', encoding=encoding) as f:
            plot = json.load(f)
        c_mentioned = plot["characters"]
        if "Director" not in sop_dict["agents"]:
            sop_dict["agents"]["Director"] = {}
        if "style" not in sop_dict["agents"]["Director"]:
            sop_dict["agents"]["Director"]["style"] = "Commanding, directive"
        if "roles" not in sop_dict["agents"]["Director"]:
            sop_dict["agents"]["Director"]["roles"] = {}
        sop_dict["agents"]["Director"]["roles"][node_name] = "Director"
        
        for c in c_mentioned:
            if c not in sop_dict["agents"]:
                sop_dict["agents"][c] = {}
            if "style" not in sop_dict["agents"][c]:
                sop_dict["agents"][c]["style"] = character_settings[c]["speaking_style"]
            if "roles" not in sop_dict["agents"][c]:
                sop_dict["agents"][c]["roles"] = {}
            sop_dict["agents"][c]["roles"][node_name] = c

    for i in range(nodes_num):
        if i == nodes_num - 1:
            node_name = f"state{i+1}"
            sop_dict["relations"][node_name] = {"0": node_name, "1": "end_state"}
            sop_dict["relations"]["end_state"] = {"0": "end_state"}
        else:
            node_name = f"state{i+1}"
            sop_dict["relations"][node_name] = {"0": node_name, "1": f"state{i+2}"}


    for i in range(nodes_num):
        node_name = f"state{i+1}"
        plot_file = plot_list[i]
        with open(os.path.join(folder, plot_file), 'r', encoding=encoding) as f:
            plot = json.load(f)
        plot_content = plot["plot"] 
        c_mentioned = plot["characters"]

        c_string = ", ".join(c_mentioned)
        sop_dict["states"][node_name] = {"begin_role" : "Director", "begin_query" : "<Director>I'm going to start posting performance instructions now, so please follow my instructions, actors and actresses.</Director>", }
        sop_dict["states"][node_name]["environment_prompt"] = f"The current scene is a playing of a \"script\", with the main characters involved: Director, {c_string}. The content of the \"script\" that these characters need to play is: \"{plot_content}\". The characters have to act out the \"script\" together. One character performs in each round."
        sop_dict["states"][node_name]["name"] = node_name
        sop_dict["states"][node_name]["roles"] = ["Director"] + c_mentioned
        sop_dict["states"][node_name]["LLM_type"] = "OpenAI"
        sop_dict["states"][node_name]["LLM"] = {
                "temperature": 1.0,
                "model": "gpt-3.5-turbo-16k-0613",
                "log_path": f"logs/{node_name}"
            }
        sop_dict["states"][node_name]["agent_states"] = {}
        sop_dict["states"][node_name]["agent_states"]["Director"] = {
                        "LLM_type": "OpenAI",
                        "LLM": {
                            "temperature": 1.0,
                            "model": "gpt-3.5-turbo-16k-0613",
                            "log_path": "logs/director"
                        },
                        "style": {
                        "role": "Director",
                        "style": "Commanding, directive"
                        },
                        "task": {
                        "task": "You are the director of this \"script\", you need to plan the content of the \"script\" into small segments, each segment should be expanded with more detailed details, and then you need to use these subdivided segments one at a time as instructions to direct the actors to perform, you need to specify which actor or actors are to perform each time you issue instructions.  Your instructions must include what the actors are going to do next, and cannot end with \"Please take a break\" or \"Prepare for the next round of performances\". You can't repeat instructions you've given in the history of the dialog! Each time you give a new instruction, it must be different from the one you gave before! When you have given all your instructions, reply with \"Show is over\" and do not repeat the same instruction! Note: You can only output in English!"
                        },
                        "rule": {
                        "rule": "You are only the Director, responsible for giving acting instructions, you cannot output the content of other characters."
                        },
                        "last":{
                        "last_prompt":"Remember, your identity is the Director, you can only output content on behalf of the Director, the output format is \n<Director>\n....\n</Director>\n Only need to output one round of dialog!"
                        }
                    }
        for c in c_mentioned:
            c_other = [item for item in c_mentioned if item != c]
            c_other_string = ', '.join(c_other)
            c_setting = character_settings[c]
            sop_dict["states"][node_name]["agent_states"][c] = {
                        "LLM_type": "OpenAI",
                        "LLM": {
                            "temperature": 1.0,
                            "model": "gpt-3.5-turbo-16k-0613",
                            "log_path": f"logs/{c}"
                        },
                        "style": {
                        "role": c,
                        "style": c_setting["speaking_style"]
                        },
                        "task": {
                        "task": f"You are {c} in this \"script\" and you need to follow the Director's instructions and act with {c_other_string}."
                        },
                        "rule": {
                        "rule": f'Your settings are: your name is {c_setting["role_name"]}, your gender is {c_setting["gender"]}, your age is {c_setting["age"]} years old, your occupation is {c_setting["occupation"]}, your personality is {c_setting["personality"]}, your speaking style is {c_setting["speaking_style"]}, your relationship with other people is {c_setting["relation_with_others"]}, your background is {c_setting["background"]}. Your performance should match your setting, the content of the "script" and the Director\'s instructions. Note: Do not respond to the Director by saying things like "yes" or "yes, director", just follow the Director\'s instructions and interact with the other actors! You need to output NULL when the Director\'s current instruction does not specify you to perform, or when you think the Director\'s current instruction does not require you to perform; you cannot repeat what you have said in the dialog history! Each time you speak, it has to be different from previous speeches you have made! Your performances can only contain your words, actions, etc. alone, not the performances of others!'
                        },
                        "last":{
                        "last_prompt": f"Remember, your identity is {c} and you can only output content on behalf of {c}, the output format is \n<{c}>\n....\n</{c}>\n Just output one round of dialog!\nWhen the current instruction posted by the Director does not specify you to perform or when you think the current instruction from the Director does not require you to perform, you need to output \n<{c}>\nNULL\n</{c}>\n"
                        }
                    }
        
        c_call_string = ""
        for c in c_mentioned:
            c_call_string += f", if it is {c}, then output <output>{c}</output>"
        c_string_2 = ", ".join(c_mentioned)

        sop_dict["states"][node_name]["controller"] = {
                    "controller_type": "order",
                    "max_chat_nums": 80,
                    "judge_system_prompt": f"Determine whether the Director, {c_string} have finished the \"script\", if so, output <output>1</output>; if not, output <output>0</output>. Note: If the Director says \"Show is over\" or something similar to \"Show is over\", output <output>1</output>; if the Director's instructions state that this is the last scene, you should wait until the actors have finished the scene before outputting <output>1</output>; if you find that a character has repeated the same dialog many times, output <output>1</output>.",
                    "judge_last_prompt": f"Depending on the current status of the performance process, determine whether the Director, {c_string} have finished the \"script\", if so, output <output>1</output>; if not, output <output>0</output>. Note: If the Director says \"Show is over\" or something similar to \"Show is over\", output <output>1</output>; if the Director's instructions state that this is the last scene, you should wait until the actors have finished the scene before outputting <output>1</output>; if you find that a character has repeated the same dialog many times, output <output>1</output>.",
                    "judge_extract_words": "output",
                    "call_system_prompt": f"You need to determine whose turn it is to output the content, if it is the Director, then output <output>Director</output>{c_call_string}, {c_string_2} are actors, you should let the Director output the performance instruction first each time, and then arrange which actor to output the content for the next round according to the specified person in the Director's instruction, you may need to arrange the actor to perform the performance for several rounds after the Director has given the instruction. When the actors' several rounds of output contents have finished the last instruction, you should let the Director continue to output the instruction.",
                    "call_last_prompt": f"Depending on the current status of the performance process, you need to determine whose turn it is to output the content, if it is the Director, then output <output>Director</output>{c_call_string}, {c_string_2} are actors, you should let the Director output the performance instruction first each time, and then arrange which actor to output the content for the next round according to the specified person in the Director's instruction, you may need to arrange the actor to perform the performance for several rounds after the Director has given the instruction. When the actors' several rounds of output contents have finished the last instruction, you should let the Director continue to output the instruction.",
                    "call_extract_words": "output"
                    }
        
    # save
    json_obj = json.dumps(sop_dict, ensure_ascii=False, indent=4, )
    with open(sop_file, 'w') as f:
        f.write(json_obj)

if __name__ == "__main__":
    # create_sop(folder_name='jintian_ver1_cn', encoding='GB2312', save_name="jintian_ver1_cn")
    # create_sop(folder_name='jintian', encoding='utf-8', save_name="jintian")
    create_sop()
