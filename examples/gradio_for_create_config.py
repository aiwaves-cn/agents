import gradio as gr 
import os
import sys
sys.path.append("../src/agents")
from utils import process_document

def tool_component_visible1(component_name):
    if "KnowledgeBaseComponent" in component_name and "WebSearchComponent" in component_name:
        return {
            WSC_col1: gr.update(visible=True),
            KBC_col1: gr.update(visible=True),
        }
    elif "KnowledgeBaseComponent" in component_name:
        return {
            WSC_col1: gr.update(),
            KBC_col1: gr.update(visible=True),
        }
    elif "WebSearchComponent" in component_name:
        return {
            WSC_col1: gr.update(visible=True),
            KBC_col1: gr.update(),
        }
    else:
        return {
            WSC_col1: gr.update(),
            KBC_col1: gr.update(),
        }

def tool_component_visible2(component_name):
    if "KnowledgeBaseComponent" in component_name and "WebSearchComponent" in component_name:
        return {
            WSC_col2: gr.update(visible=True),
            KBC_col2: gr.update(visible=True),
        }
    elif "KnowledgeBaseComponent" in component_name:
        return {
            WSC_col2: gr.update(),
            KBC_col2: gr.update(visible=True),
        }
    elif "WebSearchComponent" in component_name:
        return {
            WSC_col2: gr.update(visible=True),
            KBC_col2: gr.update(),
        }
    else:
        return {
            WSC_col2: gr.update(),
            KBC_col2: gr.update(),
        }

def tool_component_visible3(component_name):
    if "KnowledgeBaseComponent" in component_name and "WebSearchComponent" in component_name:
        return {
            WSC_col3: gr.update(visible=True),
            KBC_col3: gr.update(visible=True),
        }
    elif "KnowledgeBaseComponent" in component_name:
        return {
            WSC_col3: gr.update(),
            KBC_col3: gr.update(visible=True),
        }
    elif "WebSearchComponent" in component_name:
        return {
            WSC_col3: gr.update(visible=True),
            KBC_col3: gr.update(),
        }
    else:
        return {
            WSC_col3: gr.update(),
            KBC_col3: gr.update(),
        }

def tool_component_visible4(component_name):
    if "KnowledgeBaseComponent" in component_name and "WebSearchComponent" in component_name:
        return {
            WSC_col4: gr.update(visible=True),
            KBC_col4: gr.update(visible=True),
        }
    elif "KnowledgeBaseComponent" in component_name:
        return {
            WSC_col4: gr.update(),
            KBC_col4: gr.update(visible=True),
        }
    elif "WebSearchComponent" in component_name:
        return {
            WSC_col4: gr.update(visible=True),
            KBC_col4: gr.update(),
        }
    else:
        return {
            WSC_col4: gr.update(),
            KBC_col4: gr.update(),
        }

def add_agent_s1(num):
    num = int(num)
    if num == 1:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            agentc2_s1: gr.update(),
            agentr2_s1: gr.update(),
            makedowns1a2: gr.update(),
            agentc3_s1: gr.update(),
            agentr3_s1: gr.update(),
            makedowns1a3: gr.update(),
            agentc4_s1: gr.update(),
            agentr4_s1: gr.update(),
            makedowns1a4: gr.update(),
            agentc5_s1: gr.update(),
            agentr5_s1: gr.update(),
            makedowns1a5: gr.update(),
            number1: gr.update(visible = False)
        }
    if num == 2:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            agentc2_s1: gr.update(visible = True),
            agentr2_s1: gr.update(visible = True),
            makedowns1a2: gr.update(visible = True),
            agentc3_s1: gr.update(),
            agentr3_s1: gr.update(),
            makedowns1a3: gr.update(),
            agentc4_s1: gr.update(),
            agentr4_s1: gr.update(),
            makedowns1a4: gr.update(),
            agentc5_s1: gr.update(),
            agentr5_s1: gr.update(),
            makedowns1a5: gr.update(),
            number1: gr.update(visible = False)
        }
    if num ==3:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            agentc2_s1: gr.update(visible = True),
            agentr2_s1: gr.update(visible = True),
            makedowns1a2: gr.update(visible = True),
            agentc3_s1: gr.update(visible = True),
            agentr3_s1: gr.update(visible = True),
            makedowns1a3: gr.update(visible = True),
            agentc4_s1: gr.update(),
            agentr4_s1: gr.update(),
            makedowns1a4: gr.update(),
            agentc5_s1: gr.update(),
            agentr5_s1: gr.update(),
            makedowns1a5: gr.update(),
            number1: gr.update(visible = False)
        }
    if num ==4:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            agentc2_s1: gr.update(visible = True),
            agentr2_s1: gr.update(visible = True),
            makedowns1a2: gr.update(visible = True),
            agentc3_s1: gr.update(visible = True),
            agentr3_s1: gr.update(visible = True),
            makedowns1a3: gr.update(visible = True),
            agentc4_s1: gr.update(visible = True),
            agentr4_s1: gr.update(visible = True),
            makedowns1a4: gr.update(visible = True),
            agentc5_s1: gr.update(),
            agentr5_s1: gr.update(),
            makedowns1a5: gr.update(),
            number1: gr.update(visible = False)
        }
    if num ==5:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            agentc2_s1: gr.update(visible = True),
            agentr2_s1: gr.update(visible = True),
            makedowns1a2: gr.update(visible = True),
            agentc3_s1: gr.update(visible = True),
            agentr3_s1: gr.update(visible = True),
            makedowns1a3: gr.update(visible = True),
            agentc4_s1: gr.update(visible = True),
            agentr4_s1: gr.update(visible = True),
            makedowns1a4: gr.update(visible = True),
            agentc5_s1: gr.update(visible = True),
            agentr5_s1: gr.update(visible = True),
            makedowns1a5: gr.update(visible = True),
            number1: gr.update(visible = False)
        }

def add_agent_s2(num):
    num = int(num)
    if num == 1:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            agentc2_s2: gr.update(),
            agentr2_s2: gr.update(),
            makedowns2a2: gr.update(),
            agentc3_s2: gr.update(),
            agentr3_s2: gr.update(),
            makedowns2a3: gr.update(),
            agentc4_s2: gr.update(),
            agentr4_s2: gr.update(),
            makedowns2a4: gr.update(),
            agentc5_s2: gr.update(),
            agentr5_s2: gr.update(),
            makedowns2a5: gr.update(),
            number2: gr.update(visible = False)
        }
    if num == 2:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            agentc2_s2: gr.update(visible = True),
            agentr2_s2: gr.update(visible = True),
            makedowns2a2: gr.update(visible = True),
            agentc3_s2: gr.update(),
            agentr3_s2: gr.update(),
            makedowns2a3: gr.update(),
            agentc4_s2: gr.update(),
            agentr4_s2: gr.update(),
            makedowns2a4: gr.update(),
            agentc5_s2: gr.update(),
            agentr5_s2: gr.update(),
            makedowns2a5: gr.update(),
            number2: gr.update(visible = False)
        }
    if num ==3:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            agentc2_s2: gr.update(visible = True),
            agentr2_s2: gr.update(visible = True),
            makedowns2a2: gr.update(visible = True),
            agentc3_s2: gr.update(visible = True),
            agentr3_s2: gr.update(visible = True),
            makedowns2a3: gr.update(visible = True),
            agentc4_s2: gr.update(),
            agentr4_s2: gr.update(),
            makedowns2a4: gr.update(),
            agentc5_s2: gr.update(),
            agentr5_s2: gr.update(),
            makedowns2a5: gr.update(),
            number2: gr.update(visible = False)
        }
    if num ==4:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            agentc2_s2: gr.update(visible = True),
            agentr2_s2: gr.update(visible = True),
            makedowns2a2: gr.update(visible = True),
            agentc3_s2: gr.update(visible = True),
            agentr3_s2: gr.update(visible = True),
            makedowns2a3: gr.update(visible = True),
            agentc4_s2: gr.update(visible = True),
            agentr4_s2: gr.update(visible = True),
            makedowns2a4: gr.update(visible = True),
            agentc5_s2: gr.update(),
            agentr5_s2: gr.update(),
            makedowns2a5: gr.update(),
            number2: gr.update(visible = False)
        }
    if num ==5:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            agentc2_s2: gr.update(visible = True),
            agentr2_s2: gr.update(visible = True),
            makedowns2a2: gr.update(visible = True),
            agentc3_s2: gr.update(visible = True),
            agentr3_s2: gr.update(visible = True),
            makedowns2a3: gr.update(visible = True),
            agentc4_s2: gr.update(visible = True),
            agentr4_s2: gr.update(visible = True),
            makedowns2a4: gr.update(visible = True),
            agentc5_s2: gr.update(visible = True),
            agentr5_s2: gr.update(visible = True),
            makedowns2a5: gr.update(visible = True),
            number2: gr.update(visible = False)
        }

def add_agent_s3(num):
    num = int(num)
    if num == 1:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            agentc2_s3: gr.update(),
            agentr2_s3: gr.update(),
            makedowns3a2: gr.update(),
            agentc3_s3: gr.update(),
            agentr3_s3: gr.update(),
            makedowns3a3: gr.update(),
            agentc4_s3: gr.update(),
            agentr4_s3: gr.update(),
            makedowns3a4: gr.update(),
            agentc5_s3: gr.update(),
            agentr5_s3: gr.update(),
            makedowns3a5: gr.update(),
            number3: gr.update(visible = False)
        }
    if num == 2:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            agentc2_s3: gr.update(visible = True),
            agentr2_s3: gr.update(visible = True),
            makedowns3a2: gr.update(visible = True),
            agentc3_s3: gr.update(),
            agentr3_s3: gr.update(),
            makedowns3a3: gr.update(),
            agentc4_s3: gr.update(),
            agentr4_s3: gr.update(),
            makedowns3a4: gr.update(),
            agentc5_s3: gr.update(),
            agentr5_s3: gr.update(),
            makedowns3a5: gr.update(),
            number3: gr.update(visible = False)
        }
    if num ==3:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            agentc2_s3: gr.update(visible = True),
            agentr2_s3: gr.update(visible = True),
            makedowns3a2: gr.update(visible = True),
            agentc3_s3: gr.update(visible = True),
            agentr3_s3: gr.update(visible = True),
            makedowns3a3: gr.update(visible = True),
            agentc4_s3: gr.update(),
            agentr4_s3: gr.update(),
            makedowns3a4: gr.update(),
            agentc5_s3: gr.update(),
            agentr5_s3: gr.update(),
            makedowns3a5: gr.update(),
            number3: gr.update(visible = False)
        }
    if num ==4:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            agentc2_s3: gr.update(visible = True),
            agentr2_s3: gr.update(visible = True),
            makedowns3a2: gr.update(visible = True),
            agentc3_s3: gr.update(visible = True),
            agentr3_s3: gr.update(visible = True),
            makedowns3a3: gr.update(visible = True),
            agentc4_s3: gr.update(visible = True),
            agentr4_s3: gr.update(visible = True),
            makedowns3a4: gr.update(visible = True),
            agentc5_s3: gr.update(),
            agentr5_s3: gr.update(),
            makedowns3a5: gr.update(),
            number3: gr.update(visible = False)
        }
    if num ==5:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            agentc2_s3: gr.update(visible = True),
            agentr2_s3: gr.update(visible = True),
            makedowns3a2: gr.update(visible = True),
            agentc3_s3: gr.update(visible = True),
            agentr3_s3: gr.update(visible = True),
            makedowns3a3: gr.update(visible = True),
            agentc4_s3: gr.update(visible = True),
            agentr4_s3: gr.update(visible = True),
            makedowns3a4: gr.update(visible = True),
            agentc5_s3: gr.update(visible = True),
            agentr5_s3: gr.update(visible = True),
            makedowns3a5: gr.update(visible = True),
            number3: gr.update(visible = False)
        }

def add_agent_s4(num):
    num = int(num)
    if num == 1:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            agentc2_s4: gr.update(),
            agentr2_s4: gr.update(),
            makedowns4a2: gr.update(),
            agentc3_s4: gr.update(),
            agentr3_s4: gr.update(),
            makedowns4a3: gr.update(),
            agentc4_s4: gr.update(),
            agentr4_s4: gr.update(),
            makedowns4a4: gr.update(),
            agentc5_s4: gr.update(),
            agentr5_s4: gr.update(),
            makedowns4a5: gr.update(),
            number4: gr.update(visible = False)
        }
    if num == 2:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            agentc2_s4: gr.update(visible = True),
            agentr2_s4: gr.update(visible = True),
            makedowns4a2: gr.update(visible = True),
            agentc3_s4: gr.update(),
            agentr3_s4: gr.update(),
            makedowns4a3: gr.update(),
            agentc4_s4: gr.update(),
            agentr4_s4: gr.update(),
            makedowns4a4: gr.update(),
            agentc5_s4: gr.update(),
            agentr5_s4: gr.update(),
            makedowns4a5: gr.update(),
            number4: gr.update(visible = False)
        }
    if num ==3:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            agentc2_s4: gr.update(visible = True),
            agentr2_s4: gr.update(visible = True),
            makedowns4a2: gr.update(visible = True),
            agentc3_s4: gr.update(visible = True),
            agentr3_s4: gr.update(visible = True),
            makedowns4a3: gr.update(visible = True),
            agentc4_s4: gr.update(),
            agentr4_s4: gr.update(),
            makedowns4a4: gr.update(),
            agentc5_s4: gr.update(),
            agentr5_s4: gr.update(),
            makedowns4a5: gr.update(),
            number4: gr.update(visible = False)
        }
    if num ==4:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            agentc2_s4: gr.update(visible = True),
            agentr2_s4: gr.update(visible = True),
            makedowns4a2: gr.update(visible = True),
            agentc3_s4: gr.update(visible = True),
            agentr3_s4: gr.update(visible = True),
            makedowns4a3: gr.update(visible = True),
            agentc4_s4: gr.update(visible = True),
            agentr4_s4: gr.update(visible = True),
            makedowns4a4: gr.update(visible = True),
            agentc5_s4: gr.update(),
            agentr5_s4: gr.update(),
            makedowns4a5: gr.update(),
            number4: gr.update(visible = False)
        }
    if num ==5:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            agentc2_s4: gr.update(visible = True),
            agentr2_s4: gr.update(visible = True),
            makedowns4a2: gr.update(visible = True),
            agentc3_s4: gr.update(visible = True),
            agentr3_s4: gr.update(visible = True),
            makedowns4a3: gr.update(visible = True),
            agentc4_s4: gr.update(visible = True),
            agentr4_s4: gr.update(visible = True),
            makedowns4a4: gr.update(visible = True),
            agentc5_s4: gr.update(visible = True),
            agentr5_s4: gr.update(visible = True),
            makedowns4a5: gr.update(visible = True),
            number4: gr.update(visible = False)
        }

def generate_json_single_agent(name1,role1,style1,knowledge_path1,engine_name1,nextstate1a,nextstate1b,controller1,name2,role2,style2,knowledge_path2,engine_name2,nextstate2a,nextstate2b,controller2,name3,role3,style3,knowledge_path3,engine_name3,nextstate3a,nextstate3b,controller3,name4,role4,style4,knowledge_path4,engine_name4,nextstate4a,nextstate4b,controller4):
    os.makedirs("output_config", exist_ok=True)
    file_name = "output_code/" + "cofig.json"
    output_adic = {}
    output_adic["LLM_type"] = "OpenAI"
    LLM = {}
    LLM["temperature"] = 0.3
    LLM["model"] = "gpt-3.5-turbo-16k-0613"
    LLM["log_path"] = "logs/god"
    output_adic["root"] = "state1"
    tag = 0
    if name1 != "":
        tag += 1
        state1 = {}
        state1["name"] = name1
        state1["role"] = role1
        state1["style"] = style1
        state1["task"] = name1
        state1["rule"] = rule1
        state1["tool"] = []
        if knowledge_path1:
            knowledge_base_component = {}
            knowledge_base_component["top_k"] = 1
            processed_document = process_document(knowledge_path1)
            knowledge_base_component["type"] = processed_document["type"]
            knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
            state1["KnowledgeBaseComponent"] = knowledge_base_component
        if engine_name1:
            web_search_component = {}
            web_search_component["engine_name"] = engine_name1
            api = {}
            api["google"] = {
                    "cse_id": "04fdc27dcd8d44719",
                    "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                }
            api["bing"] = "f745c2a4186a462181103bf973c21afb"
            web_search_component["api"] = api
            state1["WebSearchComponent"] = web_search_component
        controller = {}
        controller["type"] = "order"
        controller["judge_system_prompt"] = controller1
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        controller["judge_extract_words"] = "end"
        state1["next_state"] = [nextstate1a,nextstate1b]
        state1["controller"] = controller1
        LLM["state1"] = state1
    return file_name

with gr.Blocks(title="Customize Your Agent", css="footer {visibility: hidden}", theme="default") as demo:
    gr.Markdown("""# Customize Your Agent""")
    with gr.Tab("Single-agent Mode"):
        with gr.Tab("state1"):
            gr.Markdown("""PromptComponent""")
            with gr.Row():
                name1 = gr.Textbox(label="Name")
                role1 = gr.Textbox(label="Role")
                style1 = gr.Textbox(label="Style")
            with gr.Row():
                name1 = gr.Textbox(label="Task")
                rule1 = gr.Textbox(label="Rule")
            gr.Markdown("""ToolComponent""")
            symptoms_box1 = gr.CheckboxGroup(["KnowledgeBaseComponent", "WebSearchComponent"],label="Tool Components")
            with gr.Column(visible=False) as KBC_col1:
                with gr.Tab(label= "KnowledgeBaseComponent"):
                    with gr.Row():
                        knowledge_path1 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_col1:
                with gr.Tab(label= "WebSearchComponent"):
                    with gr.Row():
                        engine_name1 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            add_component_buttion = gr.Button("add tool component")
            add_component_buttion.click(tool_component_visible1, 
                            [symptoms_box1],
                            [WSC_col1,KBC_col1],)
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                nextstate1a = gr.Number(label="next state",minimum=1,maximum=4)
                nextstate1b = gr.Number(label="next state",minimum=1,maximum=4)
                controller1 = gr.Textbox(label="controller")
            gr.Markdown("""Initializtion""")
        with gr.Tab("state2"):
            gr.Markdown("""PromptComponent""")
            with gr.Row():
                name2 = gr.Textbox(label="Name")
                role2 = gr.Textbox(label="Role")
                style2 = gr.Textbox(label="Style")
            with gr.Row():
                name2 = gr.Textbox(label="Task")
                rule2 = gr.Textbox(label="Rule")
            gr.Markdown("""ToolComponent""")
            symptoms_box2 = gr.CheckboxGroup(["KnowledgeBaseComponent", "WebSearchComponent"],label="Tool Components")
            with gr.Column(visible=False) as KBC_col2:
                with gr.Tab(label= "KnowledgeBaseComponent"):
                    with gr.Row():
                        knowledge_path2 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_col2:
                with gr.Tab(label= "WebSearchComponent"):
                    with gr.Row():
                        engine_name2 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            add_component_buttion = gr.Button("add tool component")
            add_component_buttion.click(tool_component_visible2, 
                            [symptoms_box2],
                            [WSC_col2,KBC_col2],)
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                nextstate2a = gr.Number(label="next state",minimum=1,maximum=4)
                nextstate2b = gr.Number(label="next state",minimum=1,maximum=4)
                controller2 = gr.Textbox(label="controller")
        with gr.Tab("state3"):
            gr.Markdown("""PromptComponent""")
            with gr.Row():
                name3 = gr.Textbox(label="Name")
                role3 = gr.Textbox(label="Role")
                style3 = gr.Textbox(label="Style")
            with gr.Row():
                name3 = gr.Textbox(label="Task")
                rule3 = gr.Textbox(label="Rule")
            gr.Markdown("""ToolComponent""")
            symptoms_box3 = gr.CheckboxGroup(["KnowledgeBaseComponent", "WebSearchComponent"],label="Tool Components")
            with gr.Column(visible=False) as KBC_col3:
                with gr.Tab(label= "KnowledgeBaseComponent"):
                    with gr.Row():
                        knowledge_path3 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_col3:
                with gr.Tab(label= "WebSearchComponent"):
                    with gr.Row():
                        engine_name3 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            add_component_buttion = gr.Button("add tool component")
            add_component_buttion.click(tool_component_visible3, 
                            [symptoms_box3],
                            [WSC_col3,KBC_col3],)
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                nextstate3a = gr.Number(label="next state",minimum=1,maximum=4)
                nextstate3b = gr.Number(label="next state",minimum=1,maximum=4)
                controller3 = gr.Textbox(label="controller")
        with gr.Tab("state4"):
            gr.Markdown("""PromptComponent""")
            with gr.Row():
                name4 = gr.Textbox(label="Name")
                role4 = gr.Textbox(label="Role")
                style4 = gr.Textbox(label="Style")
            with gr.Row():
                name4 = gr.Textbox(label="Task")
                rule4 = gr.Textbox(label="Rule")
            gr.Markdown("""ToolComponent""")
            symptoms_box4 = gr.CheckboxGroup(["KnowledgeBaseComponent", "WebSearchComponent"],label="Tool Components")
            with gr.Column(visible=False) as KBC_col4:
                with gr.Tab(label= "KnowledgeBaseComponent"):
                    with gr.Row():
                        knowledge_path4 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_col4:
                with gr.Tab(label= "WebSearchComponent"):
                    with gr.Row():
                        engine_name4 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            add_component_buttion = gr.Button("add tool component")
            add_component_buttion.click(tool_component_visible4, 
                            [symptoms_box4],
                            [WSC_col4,KBC_col4],)
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                nextstate4a = gr.Number(label="next state",minimum=1,maximum=4)
                nextstate4b = gr.Number(label="next state",minimum=1,maximum=4)
                controller4 = gr.Textbox(label="controller")
        generate_json_button_single_agent = gr.Button("generate config")
        json_output = gr.File(label="generated config file")
        generate_json_button_single_agent.click(generate_json_single_agent, 
                                [name1,role1,style1,knowledge_path1,engine_name1,nextstate1a,nextstate1b,controller1,
                                 name2,role2,style2,knowledge_path2,engine_name2,nextstate2a,nextstate2b,controller2,
                                 name3,role3,style3,knowledge_path3,engine_name3,nextstate3a,nextstate3b,controller3,
                                 name4,role4,style4,knowledge_path4,engine_name4,nextstate4a,nextstate4b,controller4],
                                [json_output])
    with gr.Tab(label="Multi-agent Mode"):
        #agent1
        with gr.Tab("state1"):
            makedowns1a1 = gr.Markdown("""Agent1""",visible=False)
            with gr.Row(visible=False) as agentr1_s1:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc1_s1:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent2
            makedowns1a2 = gr.Markdown("""Agent2""",visible=False)
            with gr.Row(visible=False) as agentr2_s1:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc2_s1:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent3
            makedowns1a3 = gr.Markdown("""Agent3""",visible=False)
            with gr.Row(visible=False) as agentr3_s1:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc3_s1:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent4
            makedowns1a4 = gr.Markdown("""Agent4""",visible=False)
            with gr.Row(visible=False) as agentr4_s1:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc4_s1:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent5
            makedowns1a5 = gr.Markdown("""Agent5""",visible=False)
            with gr.Row(visible=False) as agentr5_s1:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc5_s1:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            with gr.Column() as number1:
                text_input = gr.Number(label="agent number",minimum=1,maximum=10)
                add_agent_buttion = gr.Button("add agent")
                add_agent_buttion.click(add_agent_s1, 
                                        [text_input],
                                        [agentc1_s1,agentr1_s1,makedowns1a1,
                                         agentc2_s1,agentr2_s1,makedowns1a2,
                                         agentc3_s1,agentr3_s1,makedowns1a3,
                                         agentc4_s1,agentr4_s1,makedowns1a4,
                                         agentc5_s1,agentr5_s1,makedowns1a5,number1])
            gr.Markdown("""Environment""")
            with gr.Row():
                environment1 = gr.Textbox(label="environment")
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                nextstate4a = gr.Number(label="next state",minimum=1,maximum=4)
                nextstate4b = gr.Number(label="next state",minimum=1,maximum=4)
                controller4 = gr.Textbox(label="controller")
        with gr.Tab("state2"):
            makedowns2a1 = gr.Markdown("""Agent1""",visible=False)
            with gr.Row(visible=False) as agentr1_s2:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc1_s2:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent2
            makedowns2a2 = gr.Markdown("""Agent2""",visible=False)
            with gr.Row(visible=False) as agentr2_s2:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc2_s2:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent3
            makedowns2a3 = gr.Markdown("""Agent3""",visible=False)
            with gr.Row(visible=False) as agentr3_s2:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc3_s2:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent4
            makedowns2a4 = gr.Markdown("""Agent4""",visible=False)
            with gr.Row(visible=False) as agentr4_s2:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc4_s2:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent5
            makedowns2a5 = gr.Markdown("""Agent5""",visible=False)
            with gr.Row(visible=False) as agentr5_s2:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc5_s2:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            with gr.Column() as number2:
                text_input = gr.Number(label="agent number",minimum=1,maximum=10)
                add_agent_buttion = gr.Button("add agent")
                add_agent_buttion.click(add_agent_s2, 
                                        [text_input],
                                        [agentc1_s2,agentr1_s2,makedowns2a1,
                                         agentc2_s2,agentr2_s2,makedowns2a2,
                                         agentc3_s2,agentr3_s2,makedowns2a3,
                                         agentc4_s2,agentr4_s2,makedowns2a4,
                                         agentc5_s2,agentr5_s2,makedowns2a5,number2])
            gr.Markdown("""Environment""")
            with gr.Row():
                environment2 = gr.Textbox(label="environment")
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                nextstate4a = gr.Number(label="next state",minimum=1,maximum=4)
                nextstate4b = gr.Number(label="next state",minimum=1,maximum=4)
                controller4 = gr.Textbox(label="controller")
        with gr.Tab("state3"):
            makedowns3a1 = gr.Markdown("""Agent1""",visible=False)
            with gr.Row(visible=False) as agentr1_s3:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc1_s3:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent2
            makedowns3a2 = gr.Markdown("""Agent2""",visible=False)
            with gr.Row(visible=False) as agentr2_s3:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc2_s3:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent3
            makedowns3a3 = gr.Markdown("""Agent3""",visible=False)
            with gr.Row(visible=False) as agentr3_s3:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc3_s3:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent4
            makedowns3a4 = gr.Markdown("""Agent4""",visible=False)
            with gr.Row(visible=False) as agentr4_s3:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc4_s3:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            #agent5
            makedowns3a5 = gr.Markdown("""Agent5""",visible=False)
            with gr.Row(visible=False) as agentr5_s3:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc5_s3:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            with gr.Column() as number3:
                text_input = gr.Number(label="agent number",minimum=1,maximum=10)
                add_agent_buttion = gr.Button("add agent")
                add_agent_buttion.click(add_agent_s3, 
                                        [text_input],
                                        [agentc1_s3,agentr1_s3,makedowns3a1,
                                         agentc2_s3,agentr2_s3,makedowns3a2,
                                         agentc3_s3,agentr3_s3,makedowns3a3,
                                         agentc4_s3,agentr4_s3,makedowns3a4,
                                         agentc5_s3,agentr5_s3,makedowns3a5,number3])
            gr.Markdown("""Environment""")
            with gr.Row():
                environment3 = gr.Textbox(label="environment")
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                nextstate4a = gr.Number(label="next state",minimum=1,maximum=4)
                nextstate4b = gr.Number(label="next state",minimum=1,maximum=4)
                controller4 = gr.Textbox(label="controller")
        with gr.Tab("state4"):
            makedowns4a1 = gr.Markdown("""Agent1""",visible=False)
            with gr.Row(visible=False) as agentr1_s4:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc1_s4:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            makedowns4a2 = gr.Markdown("""Agent2""",visible=False)
            with gr.Row(visible=False) as agentr2_s4:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc2_s4:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            makedowns4a3 = gr.Markdown("""Agent3""",visible=False)
            with gr.Row(visible=False) as agentr3_s4:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc3_s4:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            makedowns4a4 = gr.Markdown("""Agent4""",visible=False)
            with gr.Row(visible=False) as agentr4_s4:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc4_s4:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            makedowns4a5 = gr.Markdown("""Agent5""",visible=False)
            with gr.Row(visible=False) as agentr5_s4:
                name = gr.Textbox(label="Name")
                role = gr.Textbox(label="Role")
                style = gr.Textbox(label="Style")
            with gr.Row(visible=False) as agentc5_s4:
                name = gr.Textbox(label="Task")
                rule = gr.Textbox(label="Rule")
            with gr.Column() as number4:
                text_input = gr.Number(label="agent number",minimum=1,maximum=10)
                add_agent_buttion = gr.Button("add agent")
                add_agent_buttion.click(add_agent_s4, 
                                        [text_input],
                                        [agentc1_s4,agentr1_s4,makedowns4a1,
                                         agentc2_s4,agentr2_s4,makedowns4a2,
                                         agentc3_s4,agentr3_s4,makedowns4a3,
                                         agentc4_s4,agentr4_s4,makedowns4a4,
                                         agentc5_s4,agentr5_s4,makedowns4a5,number4])
            gr.Markdown("""Environment""")
            with gr.Row():
                environment4 = gr.Textbox(label="environment")
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                nextstate4a = gr.Number(label="next state",minimum=1,maximum=4)
                nextstate4b = gr.Number(label="next state",minimum=1,maximum=4)
                controller4 = gr.Textbox(label="controller")
        generate_json_button_single_agent = gr.Button("generate config")
        json_output = gr.File(label="generated config file")
        generate_json_button_single_agent.click(generate_json_single_agent, 
                                [name1,role1,style1,knowledge_path1,engine_name1,
                                 name2,role2,style2,knowledge_path2,engine_name2,
                                 name3,role3,style3,knowledge_path3,engine_name3,],
                                [json_output])
demo.launch(server_port=18870,share=True,debug=True,
            show_api=False)