import gradio as gr 
import os
import sys
import json
from agents.utils import process_document

def tool_component_visible1(component_name):
    adic = {
        WSC_col1: gr.update(),
        KBC_col1: gr.update(),
        mail_col1: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_col1] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_col1] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_col1] = gr.update(visible=True)
    return adic

def tool_component_visible2(component_name):
    adic = {
        WSC_col2: gr.update(),
        KBC_col2: gr.update(),
        mail_col2: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_col2] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_col2] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_col2] = gr.update(visible=True)
    return adic

def tool_component_visible3(component_name):
    adic = {
        WSC_col3: gr.update(),
        KBC_col3: gr.update(),
        mail_col3: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_col3] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_col3] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_col3] = gr.update(visible=True)
    return adic

def tool_component_visible4(component_name):
    adic = {
        WSC_col4: gr.update(),
        KBC_col4: gr.update(),
        mail_col4: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_col4] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_col4] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_col4] = gr.update(visible=True)
    return adic

def tool_component_visible5(component_name):
    adic = {
        WSC_col5: gr.update(),
        KBC_col5: gr.update(),
        mail_col5: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_col5] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_col5] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_col5] = gr.update(visible=True)
    return adic

def tool_component_visible_s1a1(component_name):
    adic = {
        WSC_s1a1: gr.update(),
        KBC_s1a1: gr.update(),
        mail_s1a1: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s1a1] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s1a1] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s1a1] = gr.update(visible=True)
    return adic

def tool_component_visible_s1a2(component_name):
    adic = {
        WSC_s1a2: gr.update(),
        KBC_s1a2: gr.update(),
        mail_s1a2: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s1a2] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s1a2] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s1a2] = gr.update(visible=True)
    return adic

def tool_component_visible_s1a3(component_name):
    adic = {
        WSC_s1a3: gr.update(),
        KBC_s1a3: gr.update(),
        mail_s1a3: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s1a3] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s1a3] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s1a3] = gr.update(visible=True)
    return adic

def tool_component_visible_s1a4(component_name):
    adic = {
        WSC_s1a4: gr.update(),
        KBC_s1a4: gr.update(),
        mail_s1a4: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s1a4] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s1a4] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s1a4] = gr.update(visible=True)
    return adic

def tool_component_visible_s1a5(component_name):
    adic = {
        WSC_s1a5: gr.update(),
        KBC_s1a5: gr.update(),
        mail_s1a5: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s1a5] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s1a5] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s1a5] = gr.update(visible=True)
    return adic

def tool_component_visible_s2a1(component_name):
    adic = {
        WSC_s2a1: gr.update(),
        KBC_s2a1: gr.update(),
        mail_s2a1: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s2a1] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s2a1] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s2a1] = gr.update(visible=True)
    return adic

def tool_component_visible_s2a2(component_name):
    adic = {
        WSC_s2a2: gr.update(),
        KBC_s2a2: gr.update(),
        mail_s2a2: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s2a2] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s2a2] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s2a2] = gr.update(visible=True)
    return adic

def tool_component_visible_s2a3(component_name):
    adic = {
        WSC_s2a3: gr.update(),
        KBC_s2a3: gr.update(),
        mail_s2a3: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s2a3] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s2a3] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s2a3] = gr.update(visible=True)
    return adic

def tool_component_visible_s2a4(component_name):
    adic = {
        WSC_s2a4: gr.update(),
        KBC_s2a4: gr.update(),
        mail_s2a4: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s2a4] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s2a4] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s2a4] = gr.update(visible=True)
    return adic

def tool_component_visible_s2a5(component_name):
    adic = {
        WSC_s2a5: gr.update(),
        KBC_s2a5: gr.update(),
        mail_s2a5: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s2a5] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s2a5] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s2a5] = gr.update(visible=True)
    return adic

def tool_component_visible_s3a1(component_name):
    adic = {
        WSC_s3a1: gr.update(),
        KBC_s3a1: gr.update(),
        mail_s3a1: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s3a1] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s3a1] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s3a1] = gr.update(visible=True)
    return adic

def tool_component_visible_s3a2(component_name):
    adic = {
        WSC_s3a2: gr.update(),
        KBC_s3a2: gr.update(),
        mail_s3a2: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s3a2] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s3a2] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s3a2] = gr.update(visible=True)
    return adic

def tool_component_visible_s3a3(component_name):
    adic = {
        WSC_s3a3: gr.update(),
        KBC_s3a3: gr.update(),
        mail_s3a3: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s3a3] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s3a3] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s3a3] = gr.update(visible=True)
    return adic

def tool_component_visible_s3a4(component_name):
    adic = {
        WSC_s3a4: gr.update(),
        KBC_s3a4: gr.update(),
        mail_s3a4: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s3a4] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s3a4] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s3a4] = gr.update(visible=True)
    return adic

def tool_component_visible_s3a5(component_name):
    adic = {
        WSC_s3a5: gr.update(),
        KBC_s3a5: gr.update(),
        mail_s3a5: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s3a5] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s3a5] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s3a5] = gr.update(visible=True)
    return adic

def tool_component_visible_s4a1(component_name):
    adic = {
        WSC_s4a1: gr.update(),
        KBC_s4a1: gr.update(),
        mail_s4a1: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s4a1] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s4a1] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s4a1] = gr.update(visible=True)
    return adic

def tool_component_visible_s4a2(component_name):
    adic = {
        WSC_s4a2: gr.update(),
        KBC_s4a2: gr.update(),
        mail_s4a2: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s4a2] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s4a2] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s4a2] = gr.update(visible=True)
    return adic

def tool_component_visible_s4a3(component_name):
    adic = {
        WSC_s4a3: gr.update(),
        KBC_s4a3: gr.update(),
        mail_s4a3: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s4a3] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s4a3] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s4a3] = gr.update(visible=True)
    return adic

def tool_component_visible_s4a4(component_name):
    adic = {
        WSC_s4a4: gr.update(),
        KBC_s4a4: gr.update(),
        mail_s4a4: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s4a4] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s4a4] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s4a4] = gr.update(visible=True)
    return adic

def tool_component_visible_s4a5(component_name):
    adic = {
        WSC_s4a5: gr.update(),
        KBC_s4a5: gr.update(),
        mail_s4a5: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s4a5] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s4a5] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s4a5] = gr.update(visible=True)
    return adic

def tool_component_visible_s5a1(component_name):
    adic = {
        WSC_s5a1: gr.update(),
        KBC_s5a1: gr.update(),
        mail_s5a1: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s5a1] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s5a1] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s5a1] = gr.update(visible=True)
    return adic

def tool_component_visible_s5a2(component_name):
    adic = {
        WSC_s5a2: gr.update(),
        KBC_s5a2: gr.update(),
        mail_s5a2: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s5a2] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s5a2] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s5a2] = gr.update(visible=True)
    return adic

def tool_component_visible_s5a3(component_name):
    adic = {
        WSC_s5a3: gr.update(),
        KBC_s5a3: gr.update(),
        mail_s5a3: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s5a3] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s5a3] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s5a3] = gr.update(visible=True)
    return adic

def tool_component_visible_s5a4(component_name):
    adic = {
        WSC_s5a4: gr.update(),
        KBC_s5a4: gr.update(),
        mail_s5a4: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s5a4] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s5a4] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s5a4] = gr.update(visible=True)
    return adic

def tool_component_visible_s5a5(component_name):
    adic = {
        WSC_s5a5: gr.update(),
        KBC_s5a5: gr.update(),
        mail_s5a5: gr.update(),
    }
    if "KnowledgeBase" in component_name:
        adic[KBC_s5a5] = gr.update(visible=True)
    if "WebSearch" in component_name:
        adic[WSC_s5a5] = gr.update(visible=True)
    if "Mail" in component_name:
        adic[mail_s5a5] = gr.update(visible=True)
    return adic

def add_agent_s1(num):
    num = int(num)
    if num == 1:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            symptoms_box_s1a1: gr.update(visible = True),
            agentc2_s1: gr.update(),
            agentr2_s1: gr.update(),
            makedowns1a2: gr.update(),
            symptoms_box_s1a2: gr.update(),
            agentc3_s1: gr.update(),
            agentr3_s1: gr.update(),
            makedowns1a3: gr.update(),
            symptoms_box_s1a3: gr.update(),
            agentc4_s1: gr.update(),
            agentr4_s1: gr.update(),
            makedowns1a4: gr.update(),
            symptoms_box_s1a4: gr.update(),
            agentc5_s1: gr.update(),
            agentr5_s1: gr.update(),
            makedowns1a5: gr.update(),
            symptoms_box_s1a5: gr.update(),
            add_component_buttion_s1a1: gr.update(visible = True),
            add_component_buttion_s1a2: gr.update(),
            add_component_buttion_s1a3: gr.update(),
            add_component_buttion_s1a4: gr.update(),
            add_component_buttion_s1a5: gr.update(),
            number1: gr.update(visible = False)
        }
    if num == 2:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            symptoms_box_s1a1: gr.update(visible = True),
            agentc2_s1: gr.update(visible = True),
            agentr2_s1: gr.update(visible = True),
            makedowns1a2: gr.update(visible = True),
            symptoms_box_s1a2: gr.update(visible = True),
            agentc3_s1: gr.update(),
            agentr3_s1: gr.update(),
            makedowns1a3: gr.update(),
            symptoms_box_s1a3: gr.update(),
            agentc4_s1: gr.update(),
            agentr4_s1: gr.update(),
            makedowns1a4: gr.update(),
            symptoms_box_s1a4: gr.update(),
            agentc5_s1: gr.update(),
            agentr5_s1: gr.update(),
            makedowns1a5: gr.update(),
            symptoms_box_s1a5: gr.update(),
            add_component_buttion_s1a1: gr.update(visible = True),
            add_component_buttion_s1a2: gr.update(visible = True),
            add_component_buttion_s1a3: gr.update(),
            add_component_buttion_s1a4: gr.update(),
            add_component_buttion_s1a5: gr.update(),
            number1: gr.update(visible = False)
        }
    if num ==3:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            symptoms_box_s1a1: gr.update(visible = True),
            agentc2_s1: gr.update(visible = True),
            agentr2_s1: gr.update(visible = True),
            makedowns1a2: gr.update(visible = True),
            symptoms_box_s1a2: gr.update(visible = True),
            agentc3_s1: gr.update(visible = True),
            agentr3_s1: gr.update(visible = True),
            makedowns1a3: gr.update(visible = True),
            symptoms_box_s1a3: gr.update(visible = True),
            agentc4_s1: gr.update(),
            agentr4_s1: gr.update(),
            makedowns1a4: gr.update(),
            symptoms_box_s1a4: gr.update(),
            agentc5_s1: gr.update(),
            agentr5_s1: gr.update(),
            makedowns1a5: gr.update(),
            symptoms_box_s1a5: gr.update(),
            add_component_buttion_s1a1: gr.update(visible = True),
            add_component_buttion_s1a2: gr.update(visible = True),
            add_component_buttion_s1a3: gr.update(visible = True),
            add_component_buttion_s1a4: gr.update(),
            add_component_buttion_s1a5: gr.update(),
            number1: gr.update(visible = False)
        }
    if num ==4:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            symptoms_box_s1a1: gr.update(visible = True),
            agentc2_s1: gr.update(visible = True),
            agentr2_s1: gr.update(visible = True),
            makedowns1a2: gr.update(visible = True),
            symptoms_box_s1a2: gr.update(visible = True),
            agentc3_s1: gr.update(visible = True),
            agentr3_s1: gr.update(visible = True),
            makedowns1a3: gr.update(visible = True),
            symptoms_box_s1a3: gr.update(visible = True),
            agentc4_s1: gr.update(visible = True),
            agentr4_s1: gr.update(visible = True),
            makedowns1a4: gr.update(visible = True),
            symptoms_box_s1a4: gr.update(visible = True),
            agentc5_s1: gr.update(),
            agentr5_s1: gr.update(),
            makedowns1a5: gr.update(),
            symptoms_box_s1a5: gr.update(),
            add_component_buttion_s1a1: gr.update(visible = True),
            add_component_buttion_s1a2: gr.update(visible = True),
            add_component_buttion_s1a3: gr.update(visible = True),
            add_component_buttion_s1a4: gr.update(visible = True),
            add_component_buttion_s1a5: gr.update(),
            number1: gr.update(visible = False)
        }
    if num ==5:
        return {
            agentc1_s1: gr.update(visible = True),
            agentr1_s1: gr.update(visible = True),
            makedowns1a1: gr.update(visible = True),
            symptoms_box_s1a1: gr.update(visible = True),
            agentc2_s1: gr.update(visible = True),
            agentr2_s1: gr.update(visible = True),
            makedowns1a2: gr.update(visible = True),
            symptoms_box_s1a2: gr.update(visible = True),
            agentc3_s1: gr.update(visible = True),
            agentr3_s1: gr.update(visible = True),
            makedowns1a3: gr.update(visible = True),
            symptoms_box_s1a3: gr.update(visible = True),
            agentc4_s1: gr.update(visible = True),
            agentr4_s1: gr.update(visible = True),
            makedowns1a4: gr.update(visible = True),
            symptoms_box_s1a4: gr.update(visible = True),
            agentc5_s1: gr.update(visible = True),
            agentr5_s1: gr.update(visible = True),
            makedowns1a5: gr.update(visible = True),
            symptoms_box_s1a5: gr.update(visible = True),
            add_component_buttion_s1a1: gr.update(visible = True),
            add_component_buttion_s1a2: gr.update(visible = True),
            add_component_buttion_s1a3: gr.update(visible = True),
            add_component_buttion_s1a4: gr.update(visible = True),
            add_component_buttion_s1a5: gr.update(visible = True),
            number1: gr.update(visible = False)
        }

def add_agent_s2(num):
    num = int(num)
    if num == 1:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            symptoms_box_s2a1: gr.update(visible = True),
            agentc2_s2: gr.update(),
            agentr2_s2: gr.update(),
            makedowns2a2: gr.update(),
            symptoms_box_s2a2: gr.update(),
            agentc3_s2: gr.update(),
            agentr3_s2: gr.update(),
            makedowns2a3: gr.update(),
            symptoms_box_s2a3: gr.update(),
            agentc4_s2: gr.update(),
            agentr4_s2: gr.update(),
            makedowns2a4: gr.update(),
            symptoms_box_s2a4: gr.update(),
            agentc5_s2: gr.update(),
            agentr5_s2: gr.update(),
            makedowns2a5: gr.update(),
            symptoms_box_s2a5: gr.update(),
            add_component_buttion_s2a1: gr.update(visible = True),
            add_component_buttion_s2a2: gr.update(),
            add_component_buttion_s2a3: gr.update(),
            add_component_buttion_s2a4: gr.update(),
            add_component_buttion_s2a5: gr.update(),
            number2: gr.update(visible = False)
        }
    if num == 2:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            symptoms_box_s2a1: gr.update(visible = True),
            agentc2_s2: gr.update(visible = True),
            agentr2_s2: gr.update(visible = True),
            makedowns2a2: gr.update(visible = True),
            symptoms_box_s2a2: gr.update(visible = True),
            agentc3_s2: gr.update(),
            agentr3_s2: gr.update(),
            makedowns2a3: gr.update(),
            symptoms_box_s2a3: gr.update(),
            agentc4_s2: gr.update(),
            agentr4_s2: gr.update(),
            makedowns2a4: gr.update(),
            symptoms_box_s2a4: gr.update(),
            agentc5_s2: gr.update(),
            agentr5_s2: gr.update(),
            makedowns2a5: gr.update(),
            symptoms_box_s2a5: gr.update(),
            add_component_buttion_s2a1: gr.update(visible = True),
            add_component_buttion_s2a2: gr.update(visible = True),
            add_component_buttion_s2a3: gr.update(),
            add_component_buttion_s2a4: gr.update(),
            add_component_buttion_s2a5: gr.update(),
            number2: gr.update(visible = False)
        }
    if num ==3:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            symptoms_box_s2a1: gr.update(visible = True),
            agentc2_s2: gr.update(visible = True),
            agentr2_s2: gr.update(visible = True),
            makedowns2a2: gr.update(visible = True),
            symptoms_box_s2a2: gr.update(visible = True),
            agentc3_s2: gr.update(visible = True),
            agentr3_s2: gr.update(visible = True),
            makedowns2a3: gr.update(visible = True),
            symptoms_box_s2a3: gr.update(visible = True),
            agentc4_s2: gr.update(),
            agentr4_s2: gr.update(),
            makedowns2a4: gr.update(),
            symptoms_box_s2a4: gr.update(),
            agentc5_s2: gr.update(),
            agentr5_s2: gr.update(),
            makedowns2a5: gr.update(),
            symptoms_box_s2a5: gr.update(),
            add_component_buttion_s2a1: gr.update(visible = True),
            add_component_buttion_s2a2: gr.update(visible = True),
            add_component_buttion_s2a3: gr.update(visible = True),
            add_component_buttion_s2a4: gr.update(),
            add_component_buttion_s2a5: gr.update(),
            number2: gr.update(visible = False)
        }
    if num ==4:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            symptoms_box_s2a1: gr.update(visible = True),
            agentc2_s2: gr.update(visible = True),
            agentr2_s2: gr.update(visible = True),
            makedowns2a2: gr.update(visible = True),
            symptoms_box_s2a2: gr.update(visible = True),
            agentc3_s2: gr.update(visible = True),
            agentr3_s2: gr.update(visible = True),
            makedowns2a3: gr.update(visible = True),
            symptoms_box_s2a3: gr.update(visible = True),
            agentc4_s2: gr.update(visible = True),
            agentr4_s2: gr.update(visible = True),
            makedowns2a4: gr.update(visible = True),
            symptoms_box_s2a4: gr.update(visible = True),
            agentc5_s2: gr.update(),
            agentr5_s2: gr.update(),
            makedowns2a5: gr.update(),
            symptoms_box_s2a5: gr.update(),
            add_component_buttion_s2a1: gr.update(visible = True),
            add_component_buttion_s2a2: gr.update(visible = True),
            add_component_buttion_s2a3: gr.update(visible = True),
            add_component_buttion_s2a4: gr.update(visible = True),
            add_component_buttion_s2a5: gr.update(),
            number2: gr.update(visible = False)
        }
    if num ==5:
        return {
            agentc1_s2: gr.update(visible = True),
            agentr1_s2: gr.update(visible = True),
            makedowns2a1: gr.update(visible = True),
            symptoms_box_s2a1: gr.update(visible = True),
            agentc2_s2: gr.update(visible = True),
            agentr2_s2: gr.update(visible = True),
            makedowns2a2: gr.update(visible = True),
            symptoms_box_s2a2: gr.update(visible = True),
            agentc3_s2: gr.update(visible = True),
            agentr3_s2: gr.update(visible = True),
            makedowns2a3: gr.update(visible = True),
            symptoms_box_s2a3: gr.update(visible = True),
            agentc4_s2: gr.update(visible = True),
            agentr4_s2: gr.update(visible = True),
            makedowns2a4: gr.update(visible = True),
            symptoms_box_s2a4: gr.update(visible = True),
            agentc5_s2: gr.update(visible = True),
            agentr5_s2: gr.update(visible = True),
            makedowns2a5: gr.update(visible = True),
            symptoms_box_s2a5: gr.update(visible = True),
            add_component_buttion_s2a1: gr.update(visible = True),
            add_component_buttion_s2a2: gr.update(visible = True),
            add_component_buttion_s2a3: gr.update(visible = True),
            add_component_buttion_s2a4: gr.update(visible = True),
            add_component_buttion_s2a5: gr.update(visible = True),
            number2: gr.update(visible = False)
        }

def add_agent_s3(num):
    num = int(num)
    if num == 1:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            symptoms_box_s3a1: gr.update(visible = True),
            agentc2_s3: gr.update(),
            agentr2_s3: gr.update(),
            makedowns3a2: gr.update(),
            symptoms_box_s3a2: gr.update(),
            agentc3_s3: gr.update(),
            agentr3_s3: gr.update(),
            makedowns3a3: gr.update(),
            symptoms_box_s3a3: gr.update(),
            agentc4_s3: gr.update(),
            agentr4_s3: gr.update(),
            makedowns3a4: gr.update(),
            symptoms_box_s3a4: gr.update(),
            agentc5_s3: gr.update(),
            agentr5_s3: gr.update(),
            makedowns3a5: gr.update(),
            symptoms_box_s3a5: gr.update(),
            add_component_buttion_s3a1: gr.update(visible = True),
            add_component_buttion_s3a2: gr.update(),
            add_component_buttion_s3a3: gr.update(),
            add_component_buttion_s3a4: gr.update(),
            add_component_buttion_s3a5: gr.update(),
            number3: gr.update(visible = False)
        }
    if num == 2:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            symptoms_box_s3a1: gr.update(visible = True),
            agentc2_s3: gr.update(visible = True),
            agentr2_s3: gr.update(visible = True),
            makedowns3a2: gr.update(visible = True),
            symptoms_box_s3a2: gr.update(visible = True),
            agentc3_s3: gr.update(),
            agentr3_s3: gr.update(),
            makedowns3a3: gr.update(),
            symptoms_box_s3a3: gr.update(),
            agentc4_s3: gr.update(),
            agentr4_s3: gr.update(),
            makedowns3a4: gr.update(),
            symptoms_box_s3a4: gr.update(),
            agentc5_s3: gr.update(),
            agentr5_s3: gr.update(),
            makedowns3a5: gr.update(),
            symptoms_box_s3a5: gr.update(),
            add_component_buttion_s3a1: gr.update(visible = True),
            add_component_buttion_s3a2: gr.update(visible = True),
            add_component_buttion_s3a3: gr.update(),
            add_component_buttion_s3a4: gr.update(),
            add_component_buttion_s3a5: gr.update(),
            number3: gr.update(visible = False)
        }
    if num ==3:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            symptoms_box_s3a1: gr.update(visible = True),
            agentc2_s3: gr.update(visible = True),
            agentr2_s3: gr.update(visible = True),
            makedowns3a2: gr.update(visible = True),
            symptoms_box_s3a2: gr.update(visible = True),
            agentc3_s3: gr.update(),
            agentr3_s3: gr.update(),
            makedowns3a3: gr.update(),
            symptoms_box_s3a3: gr.update(),
            agentc4_s3: gr.update(),
            agentr4_s3: gr.update(),
            makedowns3a4: gr.update(),
            symptoms_box_s3a4: gr.update(),
            agentc5_s3: gr.update(),
            agentr5_s3: gr.update(),
            makedowns3a5: gr.update(),
            symptoms_box_s3a5: gr.update(),
            add_component_buttion_s3a1: gr.update(visible = True),
            add_component_buttion_s3a2: gr.update(visible = True),
            add_component_buttion_s3a3: gr.update(visible = True),
            add_component_buttion_s3a4: gr.update(),
            add_component_buttion_s3a5: gr.update(),
            number3: gr.update(visible = False)
        }
    if num ==4:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            symptoms_box_s3a1: gr.update(visible = True),
            agentc2_s3: gr.update(visible = True),
            agentr2_s3: gr.update(visible = True),
            makedowns3a2: gr.update(visible = True),
            symptoms_box_s3a2: gr.update(visible = True),
            agentc3_s3: gr.update(visible = True),
            agentr3_s3: gr.update(visible = True),
            makedowns3a3: gr.update(visible = True),
            symptoms_box_s3a3: gr.update(visible = True),
            agentc4_s3: gr.update(visible = True),
            agentr4_s3: gr.update(visible = True),
            makedowns3a4: gr.update(visible = True),
            symptoms_box_s3a4: gr.update(visible = True),
            agentc5_s3: gr.update(),
            agentr5_s3: gr.update(),
            makedowns3a5: gr.update(),
            symptoms_box_s3a5: gr.update(),
            add_component_buttion_s3a1: gr.update(visible = True),
            add_component_buttion_s3a2: gr.update(visible = True),
            add_component_buttion_s3a3: gr.update(visible = True),
            add_component_buttion_s3a4: gr.update(visible = True),
            add_component_buttion_s3a5: gr.update(),
            number3: gr.update(visible = False)
        }
    if num ==5:
        return {
            agentc1_s3: gr.update(visible = True),
            agentr1_s3: gr.update(visible = True),
            makedowns3a1: gr.update(visible = True),
            symptoms_box_s3a1: gr.update(visible = True),
            agentc2_s3: gr.update(visible = True),
            agentr2_s3: gr.update(visible = True),
            makedowns3a2: gr.update(visible = True),
            symptoms_box_s3a2: gr.update(visible = True),
            agentc3_s3: gr.update(visible = True),
            agentr3_s3: gr.update(visible = True),
            makedowns3a3: gr.update(visible = True),
            symptoms_box_s3a3: gr.update(visible = True),
            agentc4_s3: gr.update(visible = True),
            agentr4_s3: gr.update(visible = True),
            makedowns3a4: gr.update(visible = True),
            symptoms_box_s3a4: gr.update(visible = True),
            agentc5_s3: gr.update(visible = True),
            agentr5_s3: gr.update(visible = True),
            makedowns3a5: gr.update(visible = True),
            symptoms_box_s3a5: gr.update(visible = True),
            add_component_buttion_s3a1: gr.update(visible = True),
            add_component_buttion_s3a2: gr.update(visible = True),
            add_component_buttion_s3a3: gr.update(visible = True),
            add_component_buttion_s3a4: gr.update(visible = True),
            add_component_buttion_s3a5: gr.update(visible = True),
            number3: gr.update(visible = False)
        }

def add_agent_s4(num):
    num = int(num)
    if num == 1:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            symptoms_box_s4a1:gr.update(visible =True),
            agentc2_s4: gr.update(),
            agentr2_s4: gr.update(),
            makedowns4a2: gr.update(),
            symptoms_box_s4a2:gr.update(),
            agentc3_s4: gr.update(),
            agentr3_s4: gr.update(),
            makedowns4a3: gr.update(),
            symptoms_box_s4a3:gr.update(),
            agentc4_s4: gr.update(),
            agentr4_s4: gr.update(),
            makedowns4a4: gr.update(),
            symptoms_box_s4a4:gr.update(),
            agentc5_s4: gr.update(),
            agentr5_s4: gr.update(),
            makedowns4a5: gr.update(),
            symptoms_box_s4a5:gr.update(),
            add_component_buttion_s4a1: gr.update(visible = True),
            add_component_buttion_s4a2: gr.update(),
            add_component_buttion_s4a3: gr.update(),
            add_component_buttion_s4a4: gr.update(),
            add_component_buttion_s4a5: gr.update(),
            number4: gr.update(visible = False)
        }
    if num == 2:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            symptoms_box_s4a1:gr.update(visible =True),
            agentc2_s4: gr.update(visible =True),
            agentr2_s4: gr.update(visible =True),
            makedowns4a2: gr.update(visible =True),
            symptoms_box_s4a2:gr.update(visible =True),
            agentc3_s4: gr.update(),
            agentr3_s4: gr.update(),
            makedowns4a3: gr.update(),
            symptoms_box_s4a3:gr.update(),
            agentc4_s4: gr.update(),
            agentr4_s4: gr.update(),
            makedowns4a4: gr.update(),
            symptoms_box_s4a4:gr.update(),
            agentc5_s4: gr.update(),
            agentr5_s4: gr.update(),
            makedowns4a5: gr.update(),
            symptoms_box_s4a5:gr.update(),
            add_component_buttion_s4a1: gr.update(visible = True),
            add_component_buttion_s4a2: gr.update(visible = True),
            add_component_buttion_s4a3: gr.update(),
            add_component_buttion_s4a4: gr.update(),
            add_component_buttion_s4a5: gr.update(),
            number4: gr.update(visible = False)
        }
    if num ==3:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            symptoms_box_s4a1:gr.update(visible =True),
            agentc2_s4: gr.update(visible =True),
            agentr2_s4: gr.update(visible =True),
            makedowns4a2: gr.update(visible =True),
            symptoms_box_s4a2:gr.update(visible =True),
            agentc3_s4: gr.update(visible =True),
            agentr3_s4: gr.update(visible =True),
            makedowns4a3: gr.update(visible =True),
            symptoms_box_s4a3:gr.update(visible =True),
            agentc4_s4: gr.update(),
            agentr4_s4: gr.update(),
            makedowns4a4: gr.update(),
            symptoms_box_s4a4:gr.update(),
            agentc5_s4: gr.update(),
            agentr5_s4: gr.update(),
            makedowns4a5: gr.update(),
            symptoms_box_s4a5:gr.update(),
            add_component_buttion_s4a1: gr.update(visible = True),
            add_component_buttion_s4a2: gr.update(visible = True),
            add_component_buttion_s4a3: gr.update(visible = True),
            add_component_buttion_s4a4: gr.update(),
            add_component_buttion_s4a5: gr.update(),
            number4: gr.update(visible = False)
        }
    if num ==4:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            symptoms_box_s4a1:gr.update(visible =True),
            agentc2_s4: gr.update(visible =True),
            agentr2_s4: gr.update(visible =True),
            makedowns4a2: gr.update(visible =True),
            symptoms_box_s4a2:gr.update(visible =True),
            agentc3_s4: gr.update(visible =True),
            agentr3_s4: gr.update(visible =True),
            makedowns4a3: gr.update(visible =True),
            symptoms_box_s4a3:gr.update(visible =True),
            agentc4_s4: gr.update(visible =True),
            agentr4_s4: gr.update(visible =True),
            makedowns4a4: gr.update(visible =True),
            symptoms_box_s4a4:gr.update(visible =True),
            agentc5_s4: gr.update(),
            agentr5_s4: gr.update(),
            makedowns4a5: gr.update(),
            symptoms_box_s4a5:gr.update(),
            add_component_buttion_s4a1: gr.update(visible = True),
            add_component_buttion_s4a2: gr.update(visible = True),
            add_component_buttion_s4a3: gr.update(visible = True),
            add_component_buttion_s4a4: gr.update(visible = True),
            add_component_buttion_s4a5: gr.update(),
            number4: gr.update(visible = False)
        }
    if num ==5:
        return {
            agentc1_s4: gr.update(visible = True),
            agentr1_s4: gr.update(visible = True),
            makedowns4a1: gr.update(visible = True),
            symptoms_box_s4a1:gr.update(visible =True),
            agentc2_s4: gr.update(visible =True),
            agentr2_s4: gr.update(visible =True),
            makedowns4a2: gr.update(visible =True),
            symptoms_box_s4a2:gr.update(visible =True),
            agentc3_s4: gr.update(visible =True),
            agentr3_s4: gr.update(visible =True),
            makedowns4a3: gr.update(visible =True),
            symptoms_box_s4a3:gr.update(visible =True),
            agentc4_s4: gr.update(visible =True),
            agentr4_s4: gr.update(visible =True),
            makedowns4a4: gr.update(visible =True),
            symptoms_box_s4a4:gr.update(visible =True),
            agentc5_s4: gr.update(visible =True),
            agentr5_s4: gr.update(visible =True),
            makedowns4a5: gr.update(visible =True),
            symptoms_box_s4a5:gr.update(visible =True),
            add_component_buttion_s4a1: gr.update(visible = True),
            add_component_buttion_s4a2: gr.update(visible = True),
            add_component_buttion_s4a3: gr.update(visible = True),
            add_component_buttion_s4a4: gr.update(visible = True),
            add_component_buttion_s4a5: gr.update(visible = True),
            number4: gr.update(visible = False)
        }

def add_agent_s5(num):
    num = int(num)
    if num == 1:
        return {
            agentc1_s5: gr.update(visible = True),
            agentr1_s5: gr.update(visible = True),
            makedowns5a1: gr.update(visible = True),
            symptoms_box_s5a1:gr.update(visible =True),
            agentc2_s5: gr.update(),
            agentr2_s5: gr.update(),
            makedowns5a2: gr.update(),
            symptoms_box_s5a2:gr.update(),
            agentc3_s5: gr.update(),
            agentr3_s5: gr.update(),
            makedowns5a3: gr.update(),
            symptoms_box_s5a3:gr.update(),
            agentc4_s5: gr.update(),
            agentr4_s5: gr.update(),
            makedowns5a4: gr.update(),
            symptoms_box_s5a4:gr.update(),
            agentc5_s5: gr.update(),
            agentr5_s5: gr.update(),
            makedowns5a5: gr.update(),
            symptoms_box_s5a5:gr.update(),
            add_component_buttion_s5a1: gr.update(visible = True),
            add_component_buttion_s5a2: gr.update(),
            add_component_buttion_s5a3: gr.update(),
            add_component_buttion_s5a4: gr.update(),
            add_component_buttion_s5a5: gr.update(),
            number5: gr.update(visible = False)
        }
    if num == 2:
        return {
            agentc1_s5: gr.update(visible = True),
            agentr1_s5: gr.update(visible = True),
            makedowns5a1: gr.update(visible = True),
            symptoms_box_s5a1:gr.update(visible =True),
            agentc2_s5: gr.update(visible =True),
            agentr2_s5: gr.update(visible =True),
            makedowns5a2: gr.update(visible =True),
            symptoms_box_s5a2:gr.update(visible =True),
            agentc3_s5: gr.update(),
            agentr3_s5: gr.update(),
            makedowns5a3: gr.update(),
            symptoms_box_s5a3:gr.update(),
            agentc4_s5: gr.update(),
            agentr4_s5: gr.update(),
            makedowns5a4: gr.update(),
            symptoms_box_s5a4:gr.update(),
            agentc5_s5: gr.update(),
            agentr5_s5: gr.update(),
            makedowns5a5: gr.update(),
            symptoms_box_s5a5:gr.update(),
            add_component_buttion_s5a1: gr.update(visible = True),
            add_component_buttion_s5a2: gr.update(visible = True),
            add_component_buttion_s5a3: gr.update(),
            add_component_buttion_s5a4: gr.update(),
            add_component_buttion_s5a5: gr.update(),
            number5: gr.update(visible = False)
        }
    if num ==3:
        return {
            agentc1_s5: gr.update(visible = True),
            agentr1_s5: gr.update(visible = True),
            makedowns5a1: gr.update(visible = True),
            symptoms_box_s5a1:gr.update(visible =True),
            agentc2_s5: gr.update(visible =True),
            agentr2_s5: gr.update(visible =True),
            makedowns5a2: gr.update(visible =True),
            symptoms_box_s5a2:gr.update(visible =True),
            agentc3_s5: gr.update(visible =True),
            agentr3_s5: gr.update(visible =True),
            makedowns5a3: gr.update(visible =True),
            symptoms_box_s5a3:gr.update(visible =True),
            agentc4_s5: gr.update(),
            agentr4_s5: gr.update(),
            makedowns5a4: gr.update(),
            symptoms_box_s5a4:gr.update(),
            agentc5_s5: gr.update(),
            agentr5_s5: gr.update(),
            makedowns5a5: gr.update(),
            symptoms_box_s5a5:gr.update(),
            add_component_buttion_s5a1: gr.update(visible = True),
            add_component_buttion_s5a2: gr.update(visible = True),
            add_component_buttion_s5a3: gr.update(visible = True),
            add_component_buttion_s5a4: gr.update(),
            add_component_buttion_s5a5: gr.update(),
            number5: gr.update(visible = False)
        }
    if num ==4:
        return {
            agentc1_s5: gr.update(visible = True),
            agentr1_s5: gr.update(visible = True),
            makedowns5a1: gr.update(visible = True),
            symptoms_box_s5a1:gr.update(visible =True),
            agentc2_s5: gr.update(visible =True),
            agentr2_s5: gr.update(visible =True),
            makedowns5a2: gr.update(visible =True),
            symptoms_box_s5a2:gr.update(visible =True),
            agentc3_s5: gr.update(visible =True),
            agentr3_s5: gr.update(visible =True),
            makedowns5a3: gr.update(visible =True),
            symptoms_box_s5a3:gr.update(visible =True),
            agentc4_s5: gr.update(visible =True),
            agentr4_s5: gr.update(visible =True),
            makedowns5a4: gr.update(visible =True),
            symptoms_box_s5a4:gr.update(visible =True),
            agentc5_s5: gr.update(),
            agentr5_s5: gr.update(),
            makedowns5a5: gr.update(),
            symptoms_box_s5a5:gr.update(),
            add_component_buttion_s5a1: gr.update(visible = True),
            add_component_buttion_s5a2: gr.update(visible = True),
            add_component_buttion_s5a3: gr.update(visible = True),
            add_component_buttion_s5a4: gr.update(visible = True),
            add_component_buttion_s5a5: gr.update(),
            number5: gr.update(visible = False)
        }
    if num ==5:
        return {
            agentc1_s5: gr.update(visible = True),
            agentr1_s5: gr.update(visible = True),
            makedowns5a1: gr.update(visible = True),
            symptoms_box_s5a1:gr.update(visible =True),
            agentc2_s5: gr.update(visible =True),
            agentr2_s5: gr.update(visible =True),
            makedowns5a2: gr.update(visible =True),
            symptoms_box_s5a2:gr.update(visible =True),
            agentc3_s5: gr.update(visible =True),
            agentr3_s5: gr.update(visible =True),
            makedowns5a3: gr.update(visible =True),
            symptoms_box_s5a3:gr.update(visible =True),
            agentc4_s5: gr.update(visible =True),
            agentr4_s5: gr.update(visible =True),
            makedowns5a4: gr.update(visible =True),
            symptoms_box_s5a4:gr.update(visible =True),
            agentc5_s5: gr.update(visible =True),
            agentr5_s5: gr.update(visible =True),
            makedowns5a5: gr.update(visible =True),
            symptoms_box_s5a5:gr.update(visible =True),
            add_component_buttion_s5a1: gr.update(visible = True),
            add_component_buttion_s5a2: gr.update(visible = True),
            add_component_buttion_s5a3: gr.update(visible = True),
            add_component_buttion_s5a4: gr.update(visible = True),
            add_component_buttion_s5a5: gr.update(visible = True),
            number5: gr.update(visible = False)
        }

def generate_json_single_agent(api_key,proxy,name1,role1,style1,task1,rule1,knowledge_path1,engine_name1,cfg_file1,action1,symptoms_box1,controller1,name2,role2,style2,task2,rule2,knowledge_path2,engine_name2,cfg_file2,action2,symptoms_box2,controller2,name3,role3,style3,task3,rule3,knowledge_path3,engine_name3,cfg_file3,action3,symptoms_box3,controller3,name4,role4,style4,task4,rule4,knowledge_path4,engine_name4,cfg_file4,action4,symptoms_box4,controller4,name5,role5,style5,task5,rule5,knowledge_path5,engine_name5,cfg_file5,action5,symptoms_box5,controller5,max_chat_num1,max_chat_num2,max_chat_num3,max_chat_num4,max_chat_num5):
    relation_state1 = {}
    relation_state2 = {}
    relation_state3 = {}
    relation_state4 = {}
    relation_state5 = {}
    os.makedirs("output_config", exist_ok=True)
    file_name = "output_config/" + "config.json"
    output_adic = {}
    config = {}
    config["API_KEY"] = api_key
    config["PROXY"] = "http://127.0.0.1:"+proxy
    config["MAX_CHAT_HISTORY"] = "1000"
    config["Embed_Model"] = "intfloat/multilingual-e5-large"
    output_adic["config"] = config
    output_adic["root"] = "state1"
    states = {}
    states["end_state"] = {"name":"end_state","agent_states":{}}
    tag = 0
    agents = {}
    if name1 != "":
        state1 = {}
        tag += 1
        agent1 = {}
        if name1 not in agents:
            temp1 = {}
            temp1["style"] = style1
            temp1["roles"] = {"state1":role1}
        agents[name1] = temp1
        agent1["style"] = style1
        agent1["task"] = task1
        agent1["rule"] = rule1
        if knowledge_path1:
            knowledge_base_component = {}
            knowledge_base_component["top_k"] = 1
            processed_document = process_document(knowledge_path1)
            knowledge_base_component["type"] = processed_document["type"]
            knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
            agent1["KnowledgeBaseComponent"] = knowledge_base_component
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
            agent1["WebSearchComponent"] = web_search_component
        if action1:
            mail_component = {}
            mail_component["cfg_file"] = cfg_file1
            mail_component["default_action"] = action1
            mail_component["name"] = "e-mail"
            agent1["MailComponent"] = mail_component
        if "Weather" in symptoms_box1:
            weather_component = {}
            weather_component["name"] = "weather"
            weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
            agent1["WeatherComponent"] = weather_component
        controller = {}
        controller["type"] = "order"
        controller1_prompt = ""
        cnt = 0
        if controller1 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller1.split("\n"):
                a,b = i.split(":",1)
                relation_state1[str(cnt)] = a
                controller1_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
        controller["judge_system_prompt"] = controller1_prompt
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        if max_chat_num1:
            controller["max_chat_num"] = int(max_chat_num1)
        controller["judge_extract_words"] = "end"
        state1["controller"] = controller
        state1[role1] = agent1
        state1["roles"] = [role1]
        states["state1"] = state1
    if name2 != "":
        state2 = {}
        tag += 1
        agent2 = {}
        if name2 not in agents:
            temp2 = {}
            temp2["style"] = style2
            temp2["roles"] = {"state2":role2}
        else:
            agents[name2]["roles"]["state2"] = role2
        agents[name2] = temp2
        agent2["style"] = style2
        agent2["task"] = task2
        agent2["rule"] = rule2
        if knowledge_path2:
            knowledge_base_component = {}
            knowledge_base_component["top_k"] = 1
            processed_document = process_document(knowledge_path2)
            knowledge_base_component["type"] = processed_document["type"]
            knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
            agent2["KnowledgeBaseComponent"] = knowledge_base_component
        if engine_name2:
            web_search_component = {}
            web_search_component["engine_name"] = engine_name1
            api = {}
            api["google"] = {
                    "cse_id": "04fdc27dcd8d44719",
                    "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                }
            api["bing"] = "f745c2a4186a462181103bf973c21afb"
            web_search_component["api"] = api
            agent2["WebSearchComponent"] = web_search_component
        if action2:
            mail_component = {}
            mail_component["cfg_file"] = cfg_file2
            mail_component["default_action"] = action2
            mail_component["name"] = "e-mail"
            agent2["MailComponent"] = mail_component
        if "Weather" in symptoms_box2:
            weather_component = {}
            weather_component["name"] = "weather"
            weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
            agent2["WeatherComponent"] = weather_component
        controller = {}
        controller["type"] = "order"
        controller2_prompt = ""
        cnt = 0
        if controller2 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller2.split("\n"):
                a,b = i.split(":",1)
                relation_state2[str(cnt)] = a
                controller2_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
        controller["judge_system_prompt"] = controller2_prompt
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        controller["judge_extract_words"] = "end"
        if max_chat_num2:
            controller["max_chat_num"] = int(max_chat_num2)
        state2["controller"] = controller
        state2[role2] = agent2
        state2["roles"] = [role2]
        states["state2"] = state2
    if name3 != "":
        state3 = {}
        tag += 1
        agent3 = {}
        if name3 not in agents:
            temp3 = {}
            temp3["style"] = style3
            temp3["roles"] = {"state3":role3}
        else:
            agents[name3]["roles"]["state3"] = role3
        agents[name3] = temp3
        state3["style"] = style3
        state3["task"] = task3
        state3["rule"] = rule3
        state3["tool"] = []
        if knowledge_path3:
            knowledge_base_component = {}
            knowledge_base_component["top_k"] = 1
            processed_document = process_document(knowledge_path3)
            knowledge_base_component["type"] = processed_document["type"]
            knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
            state3["KnowledgeBaseComponent"] = knowledge_base_component
        if engine_name3:
            web_search_component = {}
            web_search_component["engine_name"] = engine_name3
            api = {}
            api["google"] = {
                    "cse_id": "04fdc27dcd8d44719",
                    "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                }
            api["bing"] = "f745c2a4186a462181103bf973c21afb"
            web_search_component["api"] = api
            state3["WebSearchComponent"] = web_search_component
        if action3:
            mail_component = {}
            mail_component["cfg_file"] = cfg_file3
            mail_component["default_action"] = action3
            mail_component["name"] = "e-mail"
            agent3["MailComponent"] = mail_component
        if "Weather" in symptoms_box3:
            weather_component = {}
            weather_component["name"] = "weather"
            weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
            agent3["WeatherComponent"] = weather_component
        controller = {}
        controller["type"] = "order"
        controller3_prompt = ""
        cnt = 0
        if controller3 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller3.split("\n"):
                a,b = i.split(":",1)
                relation_state3[str(cnt)] = a
                controller3_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
        controller["judge_system_prompt"] = controller3_prompt
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        controller["judge_extract_words"] = "end"
        if max_chat_num3:
            controller["max_chat_num"] = int(max_chat_num3)
        state3["controller"] = controller
        state3[role3] = agent3
        state3["roles"] = [role3]
        states["state3"] = state3
    if name4 != "":
        state4 = {}
        tag += 1
        agent4 = {}
        if name4 not in agents:
            temp4 = {}
            temp4["style"] = style4
            temp4["roles"] = {"state4":role4}
        else:
            agents[name4]["roles"]["state4"] = role4
        agents[name4] = temp4
        state4["style"] = style4
        state4["task"] = task4
        state4["rule"] = rule4
        if knowledge_path4:
            knowledge_base_component = {}
            knowledge_base_component["top_k"] = 1
            processed_document = process_document(knowledge_path4)
            knowledge_base_component["type"] = processed_document["type"]
            knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
            state4["KnowledgeBaseComponent"] = knowledge_base_component
        if engine_name4:
            web_search_component = {}
            web_search_component["engine_name"] = engine_name4
            api = {}
            api["google"] = {
                    "cse_id": "04fdc27dcd8d44719",
                    "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                }
            api["bing"] = "f745c2a4186a462181103bf973c21afb"
            web_search_component["api"] = api
            state4["WebSearchComponent"] = web_search_component
        if action4:
            mail_component = {}
            mail_component["cfg_file"] = cfg_file4
            mail_component["default_action"] = action4
            mail_component["name"] = "e-mail"
            agent4["MailComponent"] = mail_component
        if "Weather" in symptoms_box4:
            weather_component = {}
            weather_component["name"] = "weather"
            weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
            agent4["WeatherComponent"] = weather_component
        controller = {}
        controller["type"] = "order"
        controller4_prompt = ""
        cnt = 0
        if controller4 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller4.split("\n"):
                a,b = i.split(":",1)
                relation_state4[str(cnt)] = a
                controller4_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
        controller["judge_system_prompt"] = controller4_prompt
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        controller["judge_extract_words"] = "end"
        if max_chat_num4:
            controller["max_chat_num"] = int(max_chat_num4)
        state4["controller"] = controller
        state4[role4] = agent4
        state4["roles"] = [role4]
        states["state4"] = state4
    if name5 != "":
        state5 = {}
        tag += 1
        agent5 = {}
        if name5 not in agents:
            temp = {}
            temp["style"] = style5
            temp["roles"] = {"state5":role4}
        else:
            agents[name5]["roles"]["state5"] = role5
        agents[name5] = temp
        state5["style"] = style5
        state5["task"] = task5
        state5["rule"] = rule5
        if knowledge_path5:
            knowledge_base_component = {}
            knowledge_base_component["top_k"] = 1
            processed_document = process_document(knowledge_path5)
            knowledge_base_component["type"] = processed_document["type"]
            knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
            state5["KnowledgeBaseComponent"] = knowledge_base_component
        if engine_name5:
            web_search_component = {}
            web_search_component["engine_name"] = engine_name5
            api = {}
            api["google"] = {
                    "cse_id": "04fdc27dcd8d44719",
                    "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                }
            api["bing"] = "f745c2a4186a462181103bf973c21afb"
            web_search_component["api"] = api
            state5["WebSearchComponent"] = web_search_component
        if action5:
            mail_component = {}
            mail_component["cfg_file"] = cfg_file5
            mail_component["default_action"] = action5
            mail_component["name"] = "e-mail"
            agent5["MailComponent"] = mail_component
        if "Weather" in symptoms_box5:
            weather_component = {}
            weather_component["name"] = "weather"
            weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
            agent5["WeatherComponent"] = weather_component
        controller = {}
        controller["type"] = "order"
        controller5_prompt = ""
        cnt = 0
        if controller5 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller5.split("\n"):
                a,b = i.split(":",1)
                relation_state5[str(cnt)] = a
                controller5_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
        controller["judge_system_prompt"] = controller5_prompt
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        controller["judge_extract_words"] = "end"
        if max_chat_num5:
            controller["max_chat_num"] = int(max_chat_num5)
        state5["controller"] = controller
        state5[role5] = agent5
        state5["roles"] = [role5]
        states["state5"] = state5
    output_adic["agents"] = agents
    output_adic["states"] = states
    if tag == 1:
        relations = {}
        relations["state1"] = relation_state1
        output_adic["relations"] = relations
    if tag == 2:
        relations = {}
        relations["state1"] = relation_state1
        relations["state2"] = relation_state2
        output_adic["relations"] = relations
    if tag == 3:
        relations = {}
        relations["state1"] = relation_state1
        relations["state2"] = relation_state2
        relations["state3"] = relation_state3
        output_adic["relations"] = relations
    if tag == 4:
        relations = {}
        relations["state1"] = relation_state1
        relations["state2"] = relation_state2
        relations["state3"] = relation_state3
        relations["state4"] = relation_state4
        output_adic["relations"] = relations
    if tag == 5:
        relations = {}
        relations["state1"] = relation_state1
        relations["state2"] = relation_state2
        relations["state3"] = relation_state3
        relations["state4"] = relation_state4
        relations["state4"] = relation_state5
        output_adic["relations"] = relations
    with open(file_name,"w",encoding="utf-8") as f:
        json.dump(output_adic,f,ensure_ascii=False,indent=2)
    return file_name

def generate_json_multi_agent(api_key,proxy,name_s1a1,role_s1a1,style_s1a1,task_s1a1,rule_s1a1,
                                 name_s1a2,role_s1a2,style_s1a2,task_s1a2,rule_s1a2,
                                 name_s1a3,role_s1a3,style_s1a3,task_s1a3,rule_s1a3,
                                 name_s1a4,role_s1a4,style_s1a4,task_s1a4,rule_s1a4,
                                 name_s1a5,role_s1a5,style_s1a5,task_s1a5,rule_s1a5,
                                 name_s2a1,role_s2a1,style_s2a1,task_s2a1,rule_s2a1,
                                 name_s2a2,role_s2a2,style_s2a2,task_s2a2,rule_s2a2,
                                 name_s2a3,role_s2a3,style_s2a3,task_s2a3,rule_s2a3,
                                 name_s2a4,role_s2a4,style_s2a4,task_s2a4,rule_s2a4,
                                 name_s2a5,role_s2a5,style_s2a5,task_s2a5,rule_s2a5,
                                 name_s3a1,role_s3a1,style_s3a1,task_s3a1,rule_s3a1,
                                 name_s3a2,role_s3a2,style_s3a2,task_s3a2,rule_s3a2,
                                 name_s3a3,role_s3a3,style_s3a3,task_s3a3,rule_s3a3,
                                 name_s3a4,role_s3a4,style_s3a4,task_s3a4,rule_s3a4,
                                 name_s3a5,role_s3a5,style_s3a5,task_s3a5,rule_s3a5,
                                 name_s4a1,role_s4a1,style_s4a1,task_s4a1,rule_s4a1,
                                 name_s4a2,role_s4a2,style_s4a2,task_s4a2,rule_s4a2,
                                 name_s4a3,role_s4a3,style_s4a3,task_s4a3,rule_s4a3,
                                 name_s4a4,role_s4a4,style_s4a4,task_s4a4,rule_s4a4,
                                 name_s4a5,role_s4a5,style_s4a5,task_s4a5,rule_s4a5,
                                 name_s5a1,role_s5a1,style_s5a1,task_s5a1,rule_s5a1,
                                 name_s5a2,role_s5a2,style_s5a2,task_s5a2,rule_s5a2,
                                 name_s5a3,role_s5a3,style_s5a3,task_s5a3,rule_s5a3,
                                 name_s5a4,role_s5a4,style_s5a4,task_s5a4,rule_s5a4,
                                 name_s5a5,role_s5a5,style_s5a5,task_s5a5,rule_s5a5,
                                 environment1,environment2,environment3,environment4,environment5,
                                 cfg_file_s1a1,action_s1a1,cfg_file_s1a2,action_s1a2,
                                 cfg_file_s1a3,action_s1a3,cfg_file_s1a4,action_s1a4,
                                 cfg_file_s1a5,action_s1a5,cfg_file_s2a1,action_s2a1,
                                 cfg_file_s2a2,action_s2a2,cfg_file_s2a3,action_s2a3,
                                 cfg_file_s2a4,action_s2a4,cfg_file_s2a5,action_s2a5,
                                 cfg_file_s3a1,action_s3a1,cfg_file_s3a2,action_s3a2,
                                 cfg_file_s3a3,action_s3a3,cfg_file_s3a4,action_s3a4,
                                 cfg_file_s3a5,action_s3a5,cfg_file_s4a1,action_s4a1,
                                 cfg_file_s4a2,action_s4a2,cfg_file_s4a3,action_s4a3,
                                 cfg_file_s4a4,action_s4a4,cfg_file_s4a5,action_s4a5,
                                 cfg_file_s5a1,action_s5a1,cfg_file_s5a2,action_s5a2,
                                 cfg_file_s5a3,action_s5a3,cfg_file_s5a4,action_s5a4,
                                 cfg_file_s5a5,action_s5a5,
                                 knowledge_path_s1a1,engine_name_s1a1,knowledge_path_s1a2,engine_name_s1a2,
                                 knowledge_path_s1a3,engine_name_s1a3,knowledge_path_s1a4,engine_name_s1a4,
                                 knowledge_path_s1a5,engine_name_s1a5,knowledge_path_s2a1,engine_name_s2a1,
                                 knowledge_path_s2a2,engine_name_s2a2,knowledge_path_s2a3,engine_name_s2a3,
                                 knowledge_path_s2a4,engine_name_s2a4,knowledge_path_s2a5,engine_name_s2a5,
                                 knowledge_path_s3a1,engine_name_s3a1,knowledge_path_s3a2,engine_name_s3a2,
                                 knowledge_path_s3a3,engine_name_s3a3,knowledge_path_s3a4,engine_name_s3a4,
                                 knowledge_path_s3a5,engine_name_s3a5,knowledge_path_s4a1,engine_name_s4a1,
                                 knowledge_path_s4a2,engine_name_s4a2,knowledge_path_s4a3,engine_name_s4a3,
                                 knowledge_path_s4a4,engine_name_s4a4,knowledge_path_s4a5,engine_name_s4a5,
                                 knowledge_path_s5a1,engine_name_s5a1,knowledge_path_s5a2,engine_name_s5a2,
                                 knowledge_path_s5a3,engine_name_s5a3,knowledge_path_s5a4,engine_name_s5a4,knowledge_path_s5a5,engine_name_s5a5,
                                 symptoms_box_s1a1,symptoms_box_s1a2,symptoms_box_s1a3,symptoms_box_s1a4,symptoms_box_s1a5,symptoms_box_s2a1,symptoms_box_s2a2,symptoms_box_s2a3,symptoms_box_s2a4,symptoms_box_s2a5,symptoms_box_s3a1,symptoms_box_s3a2,
                                 symptoms_box_s3a3,symptoms_box_s3a4,symptoms_box_s3a5,symptoms_box_s4a1,symptoms_box_s4a2,symptoms_box_s4a3,symptoms_box_s4a4,symptoms_box_s4a5,
                                 symptoms_box_s5a1,symptoms_box_s5a2,symptoms_box_s5a3,symptoms_box_s5a4,symptoms_box_s5a5,
                                 controller1,controller2,controller3,controller4,controller5,
                                 environment_type1,environment_type2,environment_type3,environment_type4,environment_type5,
                                 begin_role1,begin_role2,begin_role3,begin_role4,begin_role5,
                                 begin_query1,begin_query2,begin_query3,begin_query4,begin_query5,
                                 max_chat_num_m1,max_chat_num_m2,max_chat_num_m3,max_chat_num_m4,max_chat_num_m5):
    relation_state1 = {}
    relation_state2 = {}
    relation_state3 = {}
    relation_state4 = {}
    relation_state5 = {}
    os.makedirs("output_config", exist_ok=True)
    file_name = "output_config/" + "config.json"
    output_adic = {}
    config = {}
    config["API_KEY"] = api_key
    config["PROXY"] = "http://127.0.0.1:"+proxy
    config["MAX_CHAT_HISTORY"] = "1000"
    config["Embed_Model"] = "intfloat/multilingual-e5-large"
    output_adic["config"] = config
    output_adic["environment_type"] = environment_type1
    output_adic["root"] = "state1"
    states = {}
    states["end_state"] = {"name":"end_state","agent_states":{}}
    tag = 0
    agents = {}
    if name_s1a1 != "":
        state1 = {}
        tag += 1
        if name_s1a1:
            agent_s1a1 = {}
            if name_s1a1 not in agents:
                temp1 = {}
                temp1["style"] = style_s1a1
                temp1["roles"] = {"state1":role_s1a1}
                agents[name_s1a1] = temp1
            else:
                agents[name_s1a1]["roles"]["state1"] = role_s1a1
            agent_s1a1["style"] = {"role":role_s1a1,"style":style_s1a1}
            agent_s1a1["task"] = {"task":task_s1a1}
            agent_s1a1["rule"] = {"rule":rule_s1a1}
            if knowledge_path_s1a1:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s1a1)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s1a1["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s1a1:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s1a1
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s1a1["WebSearchComponent"] = web_search_component
            if action_s1a1:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s1a1
                mail_component["default_action"] = action_s1a1
                mail_component["name"] = "e-mail"
                agent_s1a1["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s1a1:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s1a1["WeatherComponent"] = weather_component
            state1[role_s1a1] = agent_s1a1
        if name_s1a2:
            agent_s1a2 = {}
            if name_s1a2 not in agents:
                temp1 = {}
                temp1["style"] = style_s1a2
                temp1["roles"] = {"state1":role_s1a2}
                agents[name_s1a2] = temp1
            else:
                agents[name_s1a2]["roles"]["state1"] = role_s1a2
            agent_s1a2["style"] = {"role":role_s1a2,"style":style_s1a2}
            agent_s1a2["task"] = {"task":task_s1a2}
            agent_s1a2["rule"] = {"rule":rule_s1a2}
            if knowledge_path_s1a2:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s1a2)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s1a2["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s1a2:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s1a2
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s1a2["WebSearchComponent"] = web_search_component
            if action_s1a2:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s1a2
                mail_component["default_action"] = action_s1a2
                mail_component["name"] = "e-mail"
                agent_s1a2["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s1a2:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s1a2["WeatherComponent"] = weather_component
            state1[role_s1a2] = agent_s1a2
        if name_s1a3:
            agent_s1a3 = {}
            if name_s1a3 not in agents:
                temp1 = {}
                temp1["style"] = style_s1a3
                temp1["roles"] = {"state1":role_s1a3}
                agents[name_s1a3] = temp1
            else:
                agents[name_s1a3]["roles"]["state1"] = role_s1a3
            agent_s1a3["style"] = {"role":role_s1a3,"style":style_s1a3}
            agent_s1a3["task"] = {"task":task_s1a3}
            agent_s1a3["rule"] = {"rule":rule_s1a3}
            if knowledge_path_s1a3:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s1a3)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s1a3["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s1a3:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s1a3
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s1a3["WebSearchComponent"] = web_search_component
            if action_s1a3:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s1a3
                mail_component["default_action"] = action_s1a3
                mail_component["name"] = "e-mail"
                agent_s1a3["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s1a3:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s1a3["WeatherComponent"] = weather_component
            state1[role_s1a3] = agent_s1a3
        if name_s1a4:
            agent_s1a4 = {}
            if name_s1a4 not in agents:
                temp1 = {}
                temp1["style"] = style_s1a4
                temp1["roles"] = {"state1":role_s1a4}
                agents[name_s1a4] = temp1
            else:
                agents[name_s1a4]["roles"]["state1"] = role_s1a4
            agent_s1a4["style"] = {"role":role_s1a4,"style":style_s1a4}
            agent_s1a4["task"] = {"task":task_s1a4}
            agent_s1a4["rule"] = {"rule":rule_s1a4}
            if knowledge_path_s1a4:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s1a4)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s1a4["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s1a4:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s1a4
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s1a4["WebSearchComponent"] = web_search_component
            if action_s1a4:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s1a4
                mail_component["default_action"] = action_s1a4
                mail_component["name"] = "e-mail"
                agent_s1a4["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s1a4:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s1a4["WeatherComponent"] = weather_component
            state1[role_s1a4] = agent_s1a4
        if name_s1a5:
            agent_s1a5 = {}
            if name_s1a5 not in agents:
                temp1 = {}
                temp1["style"] = style_s1a5
                temp1["roles"] = {"state1":role_s1a5}
                agents[name_s1a5] = temp1
            else:
                agents[name_s1a5]["roles"]["state1"] = role_s1a5
            agent_s1a5["style"] = {"role":role_s1a5,"style":style_s1a5}
            agent_s1a5["task"] = {"task":task_s1a5}
            agent_s1a5["rule"] = {"rule":rule_s1a5}
            if knowledge_path_s1a5:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s1a5)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s1a5["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s1a5:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s1a5
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s1a5["WebSearchComponent"] = web_search_component
            if action_s1a5:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s1a5
                mail_component["default_action"] = action_s1a5
                mail_component["name"] = "e-mail"
                agent_s1a5["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s1a5:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s1a5["WeatherComponent"] = weather_component
            state1[role_s1a5] = agent_s1a5
        controller = {}
        controller1_prompt = ""
        cnt = 0
        if controller1 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller1.split("\n"):
                a,b = i.split(":",1)
                relation_state1[str(cnt)] = a
                controller1_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
        controller["judge_system_prompt"] = controller1_prompt
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        controller["judge_extract_words"] = "end"
        if max_chat_num_m1:
            controller["max_chat_num"] = int(max_chat_num_m1)
        state1["controller"] = controller
        state1["environment_prompt"] = environment1
        state1["begin_role"] = begin_role1
        state1["begin_query"] = begin_query1
        roles = [role_s1a1,role_s1a2,role_s1a3,role_s1a4,role_s1a5]
        state1["roles"] = [i for i in roles if i!=""]
        states["state1"] = state1
    if name_s2a1 != "":
        state2 = {}
        tag += 1
        if name_s2a1:
            agent_s2a1 = {}
            if name_s2a1 not in agents:
                temp1 = {}
                temp1["style"] = style_s2a1
                temp1["roles"] = {"state2":role_s2a1}
                agents[name_s2a1] = temp1
            else:
                agents[name_s2a1]["roles"]["state2"] = role_s2a1
            agent_s2a1["style"] = {"role":role_s2a1,"style":style_s2a1}
            agent_s2a1["task"] = {"task":task_s2a1}
            agent_s2a1["rule"] = {"rule":rule_s2a1}
            if knowledge_path_s2a1:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s2a1)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s2a1["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s2a1:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s2a1
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s2a1["WebSearchComponent"] = web_search_component
            if action_s2a1:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s2a1
                mail_component["default_action"] = action_s2a1
                mail_component["name"] = "e-mail"
                agent_s2a1["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s2a1:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s2a1["WeatherComponent"] = weather_component
            state2[role_s2a1] = agent_s2a1
        if name_s2a2:
            agent_s2a2 = {}
            if name_s2a2 not in agents:
                temp1 = {}
                temp1["style"] = style_s2a2
                temp1["roles"] = {"state2":role_s2a2}
                agents[name_s2a2] = temp1
            else:
                agents[name_s2a2]["roles"]["state2"] = role_s2a2
            agent_s2a2["style"] = {"role":role_s2a2,"style":style_s2a2}
            agent_s2a2["task"] = {"task":task_s2a2}
            agent_s2a2["rule"] = {"rule":rule_s2a2}
            if knowledge_path_s2a2:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s2a2)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s2a2["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s2a2:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s2a2
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s2a2["WebSearchComponent"] = web_search_component
            if action_s2a2:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s2a2
                mail_component["default_action"] = action_s2a2
                mail_component["name"] = "e-mail"
                agent_s2a2["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s2a2:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s2a2["WeatherComponent"] = weather_component
            state2[role_s2a2] = agent_s2a2
        if name_s2a3:
            agent_s2a3 = {}
            if name_s2a3 not in agents:
                temp1 = {}
                temp1["style"] = style_s2a3
                temp1["roles"] = {"state2":role_s2a3}
                agents[name_s2a3] = temp1
            else:
                agents[name_s2a3]["roles"]["state2"] = role_s2a3
            agent_s2a3["style"] = {"role":role_s2a3,"style":style_s2a3}
            agent_s2a3["task"] = {"task":task_s2a3}
            agent_s2a3["rule"] = {"rule":rule_s2a3}
            if knowledge_path_s2a3:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s2a3)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s2a3["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s2a3:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s2a3
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s2a3["WebSearchComponent"] = web_search_component
            if action_s2a3:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s2a3
                mail_component["default_action"] = action_s2a3
                mail_component["name"] = "e-mail"
                agent_s2a3["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s2a3:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s2a3["WeatherComponent"] = weather_component
            state2[role_s2a3] = agent_s2a3
        if name_s2a4:
            agent_s2a4 = {}
            if name_s2a4 not in agents:
                temp1 = {}
                temp1["style"] = style_s2a4
                temp1["roles"] = {"state2":role_s2a4}
                agents[name_s2a4] = temp1
            else:
                agents[name_s2a4]["roles"]["state2"] = role_s2a4
            agent_s2a4["style"] = {"role":role_s2a4,"style":style_s2a4}
            agent_s2a4["task"] = {"task":task_s2a4}
            agent_s2a4["rule"] = {"rule":rule_s2a4}
            if knowledge_path_s2a4:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s2a4)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s2a4["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s2a4:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s2a4
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s2a4["WebSearchComponent"] = web_search_component
            if action_s2a4:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s2a4
                mail_component["default_action"] = action_s2a4
                mail_component["name"] = "e-mail"
                agent_s2a4["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s2a4:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s2a4["WeatherComponent"] = weather_component
            state2[role_s2a4] = agent_s2a4
        if name_s2a5:
            agent_s2a5 = {}
            if name_s2a5 not in agents:
                temp1 = {}
                temp1["style"] = style_s2a5
                temp1["roles"] = {"state2":role_s2a5}
                agents[name_s2a5] = temp1
            else:
                agents[name_s2a5]["roles"]["state2"] = role_s2a5
            agent_s2a5["style"] = {"role":role_s2a5,"style":style_s2a5}
            agent_s2a5["task"] = {"task":task_s2a5}
            agent_s2a5["rule"] = {"rule":rule_s2a5}
            if knowledge_path_s2a5:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s2a5)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s2a5["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s2a5:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s2a5
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s2a5["WebSearchComponent"] = web_search_component
            if action_s2a5:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s2a5
                mail_component["default_action"] = action_s2a5
                mail_component["name"] = "e-mail"
                agent_s2a5["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s2a5:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s2a5["WeatherComponent"] = weather_component
            state2[role_s2a5] = agent_s2a5
        controller = {}
        controller["type"] = "order"
        controller2_prompt = ""
        cnt = 0
        if controller2 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller2.split("\n"):
                a,b = i.split(":",1)
                relation_state2[str(cnt)] = a
                controller2_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
        controller["judge_system_prompt"] = controller2_prompt
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        controller["judge_extract_words"] = "end"
        if max_chat_num_m2:
            controller["max_chat_num"] = int(max_chat_num_m2)
        state2["controller"] = controller
        state2["environment_prompt"] = environment2
        state2["begin_role"] = begin_role2
        state2["begin_query"] = begin_query2
        roles = [role_s2a1,role_s2a2,role_s2a3,role_s2a4,role_s2a5]
        state2["roles"] = [i for i in roles if i!=""]
        states["state2"] = state2
    if name_s3a1 != "":
        state3 = {}
        tag += 1
        if name_s3a1:
            agent_s3a1 = {}
            if name_s3a1 not in agents:
                temp1 = {}
                temp1["style"] = style_s3a1
                temp1["roles"] = {"state3":role_s3a1}
                agents[name_s3a1] = temp1
            else:
                agents[name_s3a1]["roles"]["state3"] = role_s3a1
            agent_s3a1["style"] = {"role":role_s3a1,"style":style_s3a1}
            agent_s3a1["task"] = {"task":task_s3a1}
            agent_s3a1["rule"] = {"rule":rule_s3a1}
            if knowledge_path_s3a1:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s3a1)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s3a1["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s3a1:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s3a1
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s3a1["WebSearchComponent"] = web_search_component
            if action_s3a1:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s3a1
                mail_component["default_action"] = action_s3a1
                mail_component["name"] = "e-mail"
                agent_s3a1["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s3a1:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s3a1["WeatherComponent"] = weather_component
            state3[role_s3a1] = agent_s3a1
        if name_s3a2:
            agent_s3a2 = {}
            if name_s3a2 not in agents:
                temp1 = {}
                temp1["style"] = style_s3a2
                temp1["roles"] = {"state3":role_s3a2}
                agents[name_s3a2] = temp1
            else:
                agents[name_s3a2]["roles"]["state3"] = role_s3a2
            agent_s3a2["style"] = {"role":role_s3a2,"style":style_s3a2}
            agent_s3a2["task"] = {"task":task_s3a2}
            agent_s3a2["rule"] = {"rule":rule_s3a2}
            if knowledge_path_s3a2:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s3a2)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s3a2["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s3a2:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s3a2 
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s3a2["WebSearchComponent"] = web_search_component
            if action_s3a2:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s3a2
                mail_component["default_action"] = action_s3a2
                mail_component["name"] = "e-mail"
                agent_s3a2["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s3a2:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s3a2["WeatherComponent"] = weather_component
            state3[role_s3a2] = agent_s3a2
        if name_s3a3:
            agent_s3a3 = {}
            if name_s3a3 not in agents:
                temp1 = {}
                temp1["style"] = style_s3a3
                temp1["roles"] = {"state3":role_s3a3}
                agents[name_s3a3] = temp1
            else:
                agents[name_s3a3]["roles"]["state3"] = role_s3a3
            agent_s3a3["style"] = {"role":role_s3a3,"style":style_s3a3}
            agent_s3a3["task"] = {"task":task_s3a3}
            agent_s3a3["rule"] = {"rule":rule_s3a3}
            if knowledge_path_s3a3:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s3a3)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s3a3["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s3a3:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s3a3
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s3a3["WebSearchComponent"] = web_search_component
            if action_s3a3:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s3a3
                mail_component["default_action"] = action_s3a3
                mail_component["name"] = "e-mail"
                agent_s3a3["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s3a3:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s3a3["WeatherComponent"] = weather_component
            state3[role_s3a3] = agent_s3a3
        if name_s3a4:
            agent_s3a4 = {}
            if name_s3a4 not in agents:
                temp1 = {}
                temp1["style"] = style_s3a4
                temp1["roles"] = {"state3":role_s3a4}
                agents[name_s3a4] = temp1
            else:
                agents[name_s3a4]["roles"]["state3"] = role_s3a4
            agent_s3a4["style"] = {"role":role_s3a4,"style":style_s3a4}
            agent_s3a4["task"] = {"task":task_s3a4}
            agent_s3a4["rule"] = {"rule":rule_s3a4}
            if knowledge_path_s3a4:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s3a4)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s3a4["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s3a4:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s3a4
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s3a4["WebSearchComponent"] = web_search_component
            if action_s3a4:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s3a4
                mail_component["default_action"] = action_s3a4
                mail_component["name"] = "e-mail"
                agent_s3a4["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s3a4:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s3a4["WeatherComponent"] = weather_component
            state3[role_s3a4] = agent_s3a4
        if name_s3a5:
            agent_s3a5 = {}
            if name_s3a5 not in agents:
                temp1 = {}
                temp1["style"] = style_s3a5
                temp1["roles"] = {"state3":role_s3a5}
                agents[name_s3a5] = temp1
            else:
                agents[name_s3a5]["roles"]["state3"] = role_s3a5
            agent_s3a5["style"] = {"role":role_s3a5,"style":style_s3a5}
            agent_s3a5["task"] = {"task":task_s3a5}
            agent_s3a5["rule"] = {"rule":rule_s3a5}
            if knowledge_path_s3a5:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s3a5)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s3a5["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s3a5:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s3a5
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s3a5["WebSearchComponent"] = web_search_component
            if action_s3a5:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s3a5
                mail_component["default_action"] = action_s3a5
                mail_component["name"] = "e-mail"
                agent_s3a5["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s3a5:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s3a5["WeatherComponent"] = weather_component
            state3[role_s3a5] = agent_s3a5
        controller = {}
        controller["type"] = "order"
        controller3_prompt = ""
        cnt = 0
        if controller3 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller3.split("\n"):
                a,b = i.split(":",1)
                relation_state3[str(cnt)] = a
                controller3_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
        controller["judge_system_prompt"] = controller3_prompt
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        controller["judge_extract_words"] = "end"
        if max_chat_num_m3:
            controller["max_chat_num"] = int(max_chat_num_m3)
        state3["controller"] = controller
        state3["environment_prompt"] = environment3
        state3["begin_role"] = begin_role3
        state3["begin_query"] = begin_query3
        roles = [role_s3a1,role_s3a2,role_s3a3,role_s3a4,role_s3a5]
        state3["roles"] = [i for i in roles if i!=""]
        states["state3"] = state3
    if name_s4a1!= "":
        state4 = {}
        tag += 1
        if name_s4a1:
            agent_s4a1 = {}
            if name_s4a1 not in agents:
                temp1 = {}
                temp1["style"] = style_s4a1
                temp1["roles"] = {"state4":role_s4a1}
                agents[name_s4a1] = temp1
            else:
                agents[name_s4a1]["roles"]["state4"] = role_s4a1
            agent_s4a1["style"] = {"role":role_s4a1,"style":style_s4a1}
            agent_s4a1["task"] = {"task":task_s4a1}
            agent_s4a1["rule"] = {"rule":rule_s4a1}
            if knowledge_path_s4a1:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s4a1)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s4a1["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s4a1:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s4a1
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s4a1["WebSearchComponent"] = web_search_component
            if action_s4a1:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s4a1
                mail_component["default_action"] = action_s4a1
                mail_component["name"] = "e-mail"
                agent_s4a1["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s4a1:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s4a1["WeatherComponent"] = weather_component
            state4[role_s4a1] = agent_s4a1
        if name_s4a2:
            agent_s4a2 = {}
            if name_s4a2 not in agents:
                temp1 = {}
                temp1["style"] = style_s4a2
                temp1["roles"] = {"state4":role_s4a2}
                agents[name_s4a2] = temp1
            else:
                agents[name_s4a2]["roles"]["state4"] = role_s4a2
            agent_s4a2["style"] = {"role":role_s4a2,"style":style_s4a2}
            agent_s4a2["task"] = {"task":task_s4a2}
            agent_s4a2["rule"] = {"rule":rule_s4a2}
            if knowledge_path_s4a2:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s4a2)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s4a2["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s4a2:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s4a2
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s4a2["WebSearchComponent"] = web_search_component
            if action_s4a2:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s4a2
                mail_component["default_action"] = action_s4a2
                mail_component["name"] = "e-mail"
                agent_s4a2["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s4a2:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s4a2["WeatherComponent"] = weather_component
            state4[role_s4a2] = agent_s4a2
        if name_s4a3:
            agent_s4a3 = {}
            if name_s4a3 not in agents:
                temp1 = {}
                temp1["style"] = style_s4a3
                temp1["roles"] = {"state4":role_s4a3}
                agents[name_s4a3] = temp1
            else:
                agents[name_s4a3]["roles"]["state4"] = role_s4a3
            agent_s4a3["style"] = {"role":role_s4a3,"style":style_s4a3}
            agent_s4a3["task"] = {"task":task_s4a3}
            agent_s4a3["rule"] = {"rule":rule_s4a3}
            if knowledge_path_s4a3:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s4a3)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s4a3["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s4a3:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s4a3
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s4a3["WebSearchComponent"] = web_search_component
            if action_s4a3:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s4a3
                mail_component["default_action"] = action_s4a3
                mail_component["name"] = "e-mail"
                agent_s4a3["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s4a3:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s4a3["WeatherComponent"] = weather_component
            state4[role_s4a3] = agent_s4a3
        if name_s4a4:
            agent_s4a4 = {}
            if name_s4a4 not in agents:
                temp1 = {}
                temp1["style"] = style_s4a4
                temp1["roles"] = {"state4":role_s4a4}
                agents[name_s4a4] = temp1
            else:
                agents[name_s4a4]["roles"]["state4"] = role_s4a4
            agent_s4a4["style"] = {"role":role_s4a4,"style":style_s4a4}
            agent_s4a4["task"] = {"task":task_s4a4}
            agent_s4a4["rule"] = {"rule":rule_s4a4}
            if knowledge_path_s4a4:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s4a4)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s4a4["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s4a4:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s4a4
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s4a4["WebSearchComponent"] = web_search_component
            if action_s4a4:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s4a4
                mail_component["default_action"] = action_s4a4
                mail_component["name"] = "e-mail"
                agent_s4a4["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s4a4:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s4a4["WeatherComponent"] = weather_component
            state3[role_s4a4] = agent_s4a4
        if name_s4a5:
            agent_s4a5 = {}
            if name_s4a5 not in agents:
                temp1 = {}
                temp1["style"] = style_s4a5 
                temp1["roles"] = {"state4":role_s4a5}
                agents[name_s4a5] = temp1
            else:
                agents[name_s4a5]["roles"]["state4"] = role_s4a5
            agent_s4a5["style"] = {"role":role_s4a5,"style":style_s4a5}
            agent_s4a5["task"] = {"task":task_s4a5}
            agent_s4a5["rule"] = {"rule":rule_s4a5}
            if knowledge_path_s4a5:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s4a5)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s4a5["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s4a5:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s4a5
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s4a5["WebSearchComponent"] = web_search_component
            if action_s4a5:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s4a5
                mail_component["default_action"] = action_s4a5
                mail_component["name"] = "e-mail"
                agent_s4a5["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s4a5:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s4a5["WeatherComponent"] = weather_component
            state4[role_s4a5] = agent_s4a5
        controller = {}
        controller["type"] = "order"
        controller4_prompt = ""
        cnt = 0
        if controller4 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller4.split("\n"):
                a,b = i.split(":",1)
                relation_state4[str(cnt)] = a
                controller4_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
        controller["judge_system_prompt"] = controller4_prompt
        controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
        controller["judge_extract_words"] = "end"
        if max_chat_num_m4:
            controller["max_chat_num"] = int(max_chat_num_m4)
        state4["environment_prompt"] = environment4
        state4["begin_role"] = begin_role4
        state4["begin_query"] = begin_query4
        roles = [role_s4a1,role_s4a2,role_s4a3,role_s4a4,role_s4a5]
        state4["roles"] = [i for i in roles if i!=""]
        states["state4"] = state4
    if name_s5a1!= "":
        state5 = {}
        tag += 1
        if name_s5a1:
            agent_s5a1 = {}
            if name_s5a1 not in agents:
                temp1 = {}
                temp1["style"] = style_s5a1
                temp1["roles"] = {"state5":role_s5a1}
                agents[name_s5a1] = temp1
            else:
                agents[name_s5a1]["roles"]["state5"] = role_s5a1
            agent_s5a1["style"] = {"role":role_s5a1,"style":style_s5a1}
            agent_s5a1["task"] = {"task":task_s5a1}
            agent_s5a1["rule"] = {"rule":rule_s5a1}
            if knowledge_path_s5a1:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s5a1)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s5a1["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s5a1:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s5a1
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s5a1["WebSearchComponent"] = web_search_component
            if action_s5a1:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s5a1
                mail_component["default_action"] = action_s5a1
                mail_component["name"] = "e-mail"
                agent_s5a1["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s5a1:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s5a1["WeatherComponent"] = weather_component
            state5[role_s5a1] = agent_s5a1
        if name_s5a2:
            agent_s5a2 = {}
            if name_s5a2 not in agents:
                temp1 = {}
                temp1["style"] = style_s5a2
                temp1["roles"] = {"state5":role_s5a2}
                agents[name_s5a2] = temp1
            else:
                agents[name_s5a2]["roles"]["state5"] = role_s5a2
            agent_s5a2["style"] = {"role":role_s5a2,"style":style_s5a2}
            agent_s5a2["task"] = {"task":task_s5a2}
            agent_s5a2["rule"] = {"rule":rule_s5a2}
            if knowledge_path_s5a2:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s5a2)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s5a2["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s5a2:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s5a2
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s5a2["WebSearchComponent"] = web_search_component
            if action_s5a2:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s5a2
                mail_component["default_action"] = action_s5a2
                mail_component["name"] = "e-mail"
                agent_s5a2["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s5a2:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s5a2["WeatherComponent"] = weather_component
            state5[role_s5a2] = agent_s5a2
        if name_s5a3:
            agent_s5a3 = {}
            if name_s5a3 not in agents:
                temp1 = {}
                temp1["style"] = style_s5a3
                temp1["roles"] = {"state5":role_s5a3}
                agents[name_s5a3] = temp1
            else:
                agents[name_s5a3]["roles"]["state5"] = role_s5a3
            agent_s5a3["style"] = {"role":role_s5a3,"style":style_s5a3}
            agent_s5a3["task"] = {"task":task_s5a3}
            agent_s5a3["rule"] = {"rule":rule_s5a3}
            if knowledge_path_s5a3:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s5a3)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s5a3["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s5a3:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s5a3
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s5a3["WebSearchComponent"] = web_search_component
            if action_s5a3:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s5a3
                mail_component["default_action"] = action_s5a3
                mail_component["name"] = "e-mail"
                agent_s5a3["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s5a3:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s5a3["WeatherComponent"] = weather_component
            state5[role_s5a3] = agent_s5a3
        if name_s5a4:
            agent_s5a4 = {}
            if name_s5a4 not in agents:
                temp1 = {}
                temp1["style"] = style_s5a4
                temp1["roles"] = {"state5":role_s5a4}
                agents[name_s5a4] = temp1
            else:
                agents[name_s5a4]["roles"]["state5"] = role_s5a4
            agent_s5a4["style"] = {"role":role_s5a4,"style":style_s5a4}
            agent_s5a4["task"] = {"task":task_s5a4}
            agent_s5a4["rule"] = {"rule":rule_s5a4}
            if knowledge_path_s5a4:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s5a4)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s5a4["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s5a4:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s5a4
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s5a4["WebSearchComponent"] = web_search_component
            if action_s5a4:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s5a4
                mail_component["default_action"] = action_s5a4
                mail_component["name"] = "e-mail"
                agent_s5a4["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s5a4:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s5a4["WeatherComponent"] = weather_component
            state3[role_s5a4] = agent_s5a4
        if name_s5a5:
            agent_s5a5 = {}
            if name_s5a5 not in agents:
                temp1 = {}
                temp1["style"] = style_s5a5 
                temp1["roles"] = {"state5":role_s5a5}
                agents[name_s5a5] = temp1
            else:
                agents[name_s5a5]["roles"]["state5"] = role_s5a5
            agent_s5a5["style"] = {"role":role_s5a5,"style":style_s5a5}
            agent_s5a5["task"] = {"task":task_s5a5}
            agent_s5a5["rule"] = {"rule":rule_s5a5}
            if knowledge_path_s5a5:
                knowledge_base_component = {}
                knowledge_base_component["top_k"] = 1
                processed_document = process_document(knowledge_path_s5a5)
                knowledge_base_component["type"] = processed_document["type"]
                knowledge_base_component["knowledge_path"] = processed_document["knowledge_base"]
                agent_s5a5["KnowledgeBaseComponent"] = knowledge_base_component
            if engine_name_s5a5:
                web_search_component = {}
                web_search_component["engine_name"] = engine_name_s5a5
                api = {}
                api["google"] = {
                        "cse_id": "04fdc27dcd8d44719",
                        "api_key": "AIzaSyB63w8H3K77KYpgl7MW53oErJvL8O1x4_U"
                    }
                api["bing"] = "f745c2a4186a462181103bf973c21afb"
                web_search_component["api"] = api
                agent_s5a5["WebSearchComponent"] = web_search_component
            if action_s5a5:
                mail_component = {}
                mail_component["cfg_file"] = cfg_file_s5a5
                mail_component["default_action"] = action_s5a5
                mail_component["name"] = "e-mail"
                agent_s5a5["MailComponent"] = mail_component
            if "Weather" in symptoms_box_s5a5:
                weather_component = {}
                weather_component["name"] = "weather"
                weather_component["api-key"] = "038cb34a387b4c9c9ef2ae1f82adc15e"
                agent_s5a5["WeatherComponent"] = weather_component
            state5[role_s5a5] = agent_s5a5
        controller = {}
        controller["type"] = "order"
        controller5_prompt = ""
        cnt = 0
        if controller5 == "":
            controller["judge_system_prompt"] = ""
            controller["judge_last_prompt"] = ""
            controller["judge_extract_words"] = "end"
        else:
            for i in controller5.split("\n"):
                a,b = i.split(":",1)
                relation_state5[str(cnt)] = a
                controller5_prompt += "If the following is now satisfied:" + b +"output <end>" + str(cnt) + "</end>."
                cnt += 1
            controller["judge_system_prompt"] = controller5_prompt
            controller["judge_last_prompt"] = "Please contact the above to extract <end> and </end>. Do not perform additional output. Please strictly follow the above format for output! Remember, please strictly follow the above format for output!"
            controller["judge_extract_words"] = "end"
        if max_chat_num_m5:
            controller["max_chat_num"] = int(max_chat_num_m5)
        state5["controller"] = controller5
        state5["environment_prompt"] = environment5
        state5["begin_role"] = begin_role5
        state5["begin_query"] = begin_query5
        roles = [role_s5a1,role_s5a2,role_s5a3,role_s5a4,role_s5a5]
        state5["roles"] = [i for i in roles if i!=""]
        states["state5"] = state5
    output_adic["agents"] = agents
    output_adic["states"] = states
    if tag == 1:
        relations = {}
        relations["state1"] = relation_state1
        output_adic["relations"] = relations
    if tag == 2:
        relations = {}
        relations["state1"] = relation_state1
        relations["state2"] = relation_state2
        output_adic["relations"] = relations
    if tag == 3:
        relations = {}
        relations["state1"] = relation_state1
        relations["state2"] = relation_state2
        relations["state3"] = relation_state3
        output_adic["relations"] = relations
    if tag == 4:
        relations = {}
        relations["state1"] = relation_state1
        relations["state2"] = relation_state2
        relations["state3"] = relation_state3
        relations["state4"] = relation_state4
        output_adic["relations"] = relations
    if tag == 4:
        relations = {}
        relations["state1"] = relation_state1
        relations["state2"] = relation_state2
        relations["state3"] = relation_state3
        relations["state4"] = relation_state4
        relations["state5"] = relation_state5
        output_adic["relations"] = relations
    print(output_adic)
    with open(file_name,"w",encoding="utf-8") as f:
        json.dump(output_adic,f,ensure_ascii=False,indent=2)
    return file_name

with gr.Blocks(title="Customize Your Agent", css="footer {visibility: hidden}", theme="soft") as demo:
    gr.Markdown("""# Customize Your Agent""")
    with gr.Row():
        api_key = gr.Textbox(label="api_key")
        proxy = gr.Textbox(label="proxy")
    with gr.Tab("Single-agent Mode"):
        with gr.Tab("state1"):
            gr.Markdown("""PromptComponent""")
            with gr.Row():
                name1 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role1 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style1 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row():
                task1 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule1 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            gr.Markdown("""Tool""")
            symptoms_box1 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","Mail","Weather"],label="Tools")
            with gr.Column(visible=False) as KBC_col1:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path1 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_col1:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name1 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_col1:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file1 = gr.File(label="google_mail.json")
                        action1= gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion = gr.Button("add tool component")
            add_component_buttion.click(tool_component_visible1, 
                            [symptoms_box1],
                            [WSC_col1,KBC_col1,mail_col1],)
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller1 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num1 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        with gr.Tab("state2"):
            gr.Markdown("""PromptComponent""")
            with gr.Row():
                name2 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice here, e.g., Alice")
                role2 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style2 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row():
                task2 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule2 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            gr.Markdown("""Tool""")
            symptoms_box2 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","Mail","Weather"],label="Tool Components")
            with gr.Column(visible=False) as KBC_col2:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path2 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_col2:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name2 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_col2:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file2 = gr.File(label="google_mail.json")
                        action2= gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion = gr.Button("add tool")
            add_component_buttion.click(tool_component_visible2, 
                            [symptoms_box2],
                            [WSC_col2,KBC_col2,mail_col2],)
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller2 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num2 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        with gr.Tab("state3"):
            gr.Markdown("""PromptComponent""")
            with gr.Row():
                name3 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role3 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style3 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row():
                task3 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital, e.g., oculist")
                rule3 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            gr.Markdown("""Tool""")
            symptoms_box3 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","Mail","Weather"],label="Tools")
            with gr.Column(visible=False) as KBC_col3:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path3 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_col3:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name3 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_col3:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file3 = gr.File(label="google_mail.json")
                        action3 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion = gr.Button("add tool component")
            add_component_buttion.click(tool_component_visible3, 
                            [symptoms_box3],
                            [WSC_col3,KBC_col3,mail_col3],)
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller3 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num3 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        with gr.Tab("state4"):
            gr.Markdown("""PromptComponent""")
            with gr.Row():
                name4 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role4 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style4 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row():
                task4 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule4 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            gr.Markdown("""Tool""")
            symptoms_box4 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","Mail","Weather"],label="Tools")
            with gr.Column(visible=False) as KBC_col4:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path4 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_col4:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name4 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_col4:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file4 = gr.File(label="google_mail.json")
                        action4 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion = gr.Button("add tool component")
            add_component_buttion.click(tool_component_visible4, 
                            [symptoms_box4],
                            [WSC_col4,KBC_col4,mail_col4],)
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller4 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num4 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        with gr.Tab("state5"):
            gr.Markdown("""PromptComponent""")
            with gr.Row():
                name5 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role5 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style5 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row():
                task5 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule5 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            gr.Markdown("""Tool""")
            symptoms_box5 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","Mail","Weather"],label="Tools")
            with gr.Column(visible=False) as KBC_col5:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path5 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_col5:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name5 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_col5:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file5 = gr.File(label="google_mail.json")
                        action5 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion = gr.Button("add tool component")
            add_component_buttion.click(tool_component_visible5, 
                            [symptoms_box5],
                            [WSC_col5,KBC_col5,mail_col5],)
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller5 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num5 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        gr.Markdown("""Initializtion""")
        generate_json_button_single_agent = gr.Button("generate config")
        json_output = gr.File(label="generated config file")
        generate_json_button_single_agent.click(generate_json_single_agent, 
                                [api_key,proxy,name1,role1,style1,task1,rule1,knowledge_path1,engine_name1,cfg_file1,action1,symptoms_box1,controller1,
                                 name2,role2,style2,task2,rule2,knowledge_path2,engine_name2,cfg_file2,action2,symptoms_box2,controller2,
                                 name3,role3,style3,task3,rule3,knowledge_path3,engine_name3,cfg_file3,action3,symptoms_box3,controller3,
                                 name4,role4,style4,task4,rule4,knowledge_path4,engine_name4,cfg_file4,action4,symptoms_box4,controller4,
                                 name5,role5,style5,task5,rule5,knowledge_path5,engine_name5,cfg_file5,action5,symptoms_box5,controller5,
                                 max_chat_num1,max_chat_num2,max_chat_num3,max_chat_num4,max_chat_num5],
                                [json_output])
    with gr.Tab(label="Multi-agent Mode"):
        #agent1
        with gr.Tab("state1"):
            makedowns1a1 = gr.Markdown("""Agent1""",visible=False)
            with gr.Row(visible=False) as agentr1_s1:
                name_s1a1 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s1a1 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s1a1 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc1_s1:
                task_s1a1 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s1a1 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s1a1 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s1a1:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s1a1 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s1a1:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s1a1 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s1a1:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s1a1 = gr.File(label="google_mail.json")
                        action_s1a1 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s1a1 = gr.Button("add tool component",visible=False)
            add_component_buttion_s1a1.click(tool_component_visible_s1a1, 
                            [symptoms_box_s1a1],
                            [WSC_s1a1,KBC_s1a1,mail_s1a1],)
            #agent2
            makedowns1a2 = gr.Markdown("""Agent2""",visible=False)
            with gr.Row(visible=False) as agentr2_s1:
                name_s1a2 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s1a2 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s1a2 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc2_s1:
                task_s1a2 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s1a2 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s1a2 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s1a2:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s1a2 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s1a2:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s1a2 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s1a2:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s1a2 = gr.File(label="google_mail.json")
                        action_s1a2 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s1a2 = gr.Button("add tool component",visible=False)
            add_component_buttion_s1a2.click(tool_component_visible_s1a2, 
                            [symptoms_box_s1a2],
                            [WSC_s1a2,KBC_s1a2,mail_s1a2],)
            #agent3
            makedowns1a3 = gr.Markdown("""Agent3""",visible=False)
            with gr.Row(visible=False) as agentr3_s1:
                name_s1a3 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s1a3 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s1a3 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc3_s1:
                task_s1a3 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s1a3 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s1a3 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s1a3:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s1a3 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s1a3:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s1a3 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s1a3:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s1a3 = gr.File(label="google_mail.json")
                        action_s1a3 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s1a3 = gr.Button("add tool component",visible=False)
            add_component_buttion_s1a3.click(tool_component_visible_s1a3, 
                            [symptoms_box_s1a3],
                            [WSC_s1a3,KBC_s1a3,mail_s1a3],)
            #agent4
            makedowns1a4 = gr.Markdown("""Agent4""",visible=False)
            with gr.Row(visible=False) as agentr4_s1:
                name_s1a4 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s1a4 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s1a4 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc4_s1:
                task_s1a4 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s1a4 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s1a4 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s1a4:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s1a4 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s1a4:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s1a4 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s1a4:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s1a4 = gr.File(label="google_mail.json")
                        action_s1a4 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s1a4 = gr.Button("add tool component",visible=False)
            add_component_buttion_s1a4.click(tool_component_visible_s1a4, 
                            [symptoms_box_s1a4],
                            [WSC_s1a4,KBC_s1a4,mail_s1a4],)
            #agent5
            makedowns1a5 = gr.Markdown("""Agent5""",visible=False)
            with gr.Row(visible=False) as agentr5_s1:
                name_s1a5 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s1a5 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s1a5 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc5_s1:
                task_s1a5 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s1a5 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s1a5 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s1a5:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s1a5 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s1a5:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s1a5 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s1a5:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s1a5 = gr.File(label="google_mail.json")
                        action_s1a5 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s1a5 = gr.Button("add tool component",visible=False)
            add_component_buttion_s1a5.click(tool_component_visible_s1a5, 
                            [symptoms_box_s1a5],
                            [WSC_s1a5,KBC_s1a5,mail_s1a5],)
            with gr.Column() as number1:
                text_input_s1 = gr.Number(label="agent number",minimum=1,maximum=5)
                add_agent_buttion = gr.Button("add agent")
                add_agent_buttion.click(add_agent_s1, 
                                        [text_input_s1],
                                        [agentc1_s1,agentr1_s1,makedowns1a1,symptoms_box_s1a1,
                                         agentc2_s1,agentr2_s1,makedowns1a2,symptoms_box_s1a2,
                                         agentc3_s1,agentr3_s1,makedowns1a3,symptoms_box_s1a3,
                                         agentc4_s1,agentr4_s1,makedowns1a4,symptoms_box_s1a4,
                                         agentc5_s1,agentr5_s1,makedowns1a5,symptoms_box_s1a5,
                                         add_component_buttion_s1a1,add_component_buttion_s1a2,
                                         add_component_buttion_s1a3,
                                         add_component_buttion_s1a4,
                                         add_component_buttion_s1a5,number1])
            with gr.Row():
                begin_role1 = gr.Text(label="begin_role(optional)",placeholder="set the role of the agent who speaks at the beginning of the scene, e.g., oculist")
                begin_query1  = gr.Text(label="begin_query(optional)",placeholder="set the speech of the agent who speaks at the beginning of the scene, e.g., welcome to our hospital")
            gr.Markdown("""Environment""")
            with gr.Row():
                environment1 = gr.Textbox(label="environment(optional)",placeholder="describe the scene as it is happening now, e.g, It is currently the debate stage, where the positive side is assigning tasks.")
                environment_type1 = gr.Dropdown(choices = ["cooperative","compete"],label="environment type")
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller_m1 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num_m1 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        with gr.Tab("state2"):
            makedowns2a1 = gr.Markdown("""Agent1""",visible=False)
            with gr.Row(visible=False) as agentr1_s2:
                name_s2a1 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s2a1 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s2a1 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc1_s2:
                task_s2a1 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s2a1 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s2a1 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s2a1:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s2a1 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s2a1:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s2a1 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s2a1:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s2a1 = gr.File(label="google_mail.json")
                        action_s2a1 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s2a1 = gr.Button("add tool component",visible=False)
            add_component_buttion_s2a1.click(tool_component_visible_s2a1, 
                            [symptoms_box_s2a1],
                            [WSC_s2a1,KBC_s2a1,mail_s2a1],)
            #agent2
            makedowns2a2 = gr.Markdown("""Agent2""",visible=False)
            with gr.Row(visible=False) as agentr2_s2:
                name_s2a2 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s2a2 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s2a2= gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc2_s2:
                task_s2a2 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s2a2 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s2a2 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s2a2:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s2a2 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s2a2:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s2a2 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s2a2:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s2a2 = gr.File(label="google_mail.json")
                        action_s2a2 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s2a2 = gr.Button("add tool component",visible=False)
            add_component_buttion_s2a2.click(tool_component_visible_s2a2, 
                            [symptoms_box_s2a2],
                            [WSC_s2a2,KBC_s2a2,mail_s2a2],)
            #agent3
            makedowns2a3 = gr.Markdown("""Agent3""",visible=False)
            with gr.Row(visible=False) as agentr3_s2:
                name_s2a3 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s2a3 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s2a3 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc3_s2:
                task_s2a3 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s2a3 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s2a3 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s2a3:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s2a3 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s2a3:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s2a3 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s2a3:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s2a3 = gr.File(label="google_mail.json")
                        action_s2a3 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s2a3 = gr.Button("add tool component",visible=False)
            add_component_buttion_s2a3.click(tool_component_visible_s2a3, 
                            [symptoms_box_s2a3],
                            [WSC_s2a3,KBC_s2a3,mail_s2a3],)
            #agent4
            makedowns2a4 = gr.Markdown("""Agent4""",visible=False)
            with gr.Row(visible=False) as agentr4_s2:
                name_s2a4 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s2a4 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s2a4 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc4_s2:
                task_s2a4 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s2a4 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s2a4 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s2a4:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s2a4 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s2a4:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s2a4 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s2a4:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s2a4 = gr.File(label="google_mail.json")
                        action_s2a4 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s2a4 = gr.Button("add tool component",visible=False)
            add_component_buttion_s2a4.click(tool_component_visible_s2a4, 
                            [symptoms_box_s2a4],
                            [WSC_s2a4,KBC_s2a4,mail_s2a4],)
            #agent5
            makedowns2a5 = gr.Markdown("""Agent5""",visible=False)
            with gr.Row(visible=False) as agentr5_s2:
                name_s2a5 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s2a5 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s2a5 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc5_s2:
                task_s2a5 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s2a5 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s2a5 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s2a5:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s2a5 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s2a5:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s2a5 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s2a5:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s2a5 = gr.File(label="google_mail.json")
                        action_s2a5 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s2a5 = gr.Button("add tool component",visible=False)
            add_component_buttion_s2a5.click(tool_component_visible_s2a5, 
                            [symptoms_box_s2a5],
                            [WSC_s2a5,KBC_s2a5,mail_s2a5],)
            with gr.Column() as number2:
                text_input_s2 = gr.Number(label="agent number",minimum=1,maximum=5)
                add_agent_buttion = gr.Button("add agent")
                add_agent_buttion.click(add_agent_s2, 
                                        [text_input_s2],
                                        [agentc1_s2,agentr1_s2,makedowns2a1,symptoms_box_s2a1,
                                         agentc2_s2,agentr2_s2,makedowns2a2,symptoms_box_s2a2,
                                         agentc3_s2,agentr3_s2,makedowns2a3,symptoms_box_s2a3,
                                         agentc4_s2,agentr4_s2,makedowns2a4,symptoms_box_s2a4,
                                         agentc5_s2,agentr5_s2,makedowns2a5,symptoms_box_s2a5,
                                         add_component_buttion_s2a1,add_component_buttion_s2a2,add_component_buttion_s2a3,add_component_buttion_s2a4,add_component_buttion_s2a5,number2])
            with gr.Row():
                begin_role2 = gr.Text(label="begin_role(optional)",placeholder="set the role of the agent who speaks at the beginning of the scene, e.g., oculist")
                begin_query2  = gr.Text(label="begin_query(optional)",placeholder="set the speech of the agent who speaks at the beginning of the scene, e.g., welcome to our hospital")
            gr.Markdown("""Environment""")
            with gr.Row():
                environment2 = gr.Textbox(label="environment(optional)",placeholder="describe the scene as it is happening now, e.g, It is currently the debate stage, where the positive side is assigning tasks.")
                environment_type2 = gr.Dropdown(choices = ["cooperative","compete"],label="environment type")
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller_m2 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num_m2 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        with gr.Tab("state3"):
            makedowns3a1 = gr.Markdown("""Agent1""",visible=False)
            with gr.Row(visible=False) as agentr1_s3:
                name_s3a1 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s3a1 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s3a1 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc1_s3:
                task_s3a1 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s3a1 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s3a1 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s3a1:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s3a1 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s3a1:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s3a1 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s3a1:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s3a1 = gr.File(label="google_mail.json")
                        action_s3a1 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s3a1 = gr.Button("add tool component",visible=False)
            add_component_buttion_s3a1.click(tool_component_visible_s3a1, 
                            [symptoms_box_s3a1],
                            [WSC_s3a1,KBC_s3a1,mail_s3a1],)
            #agent2
            makedowns3a2 = gr.Markdown("""Agent2""",visible=False)
            with gr.Row(visible=False) as agentr2_s3:
                name_s3a2 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s3a2 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s3a2 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc2_s3:
                task_s3a2 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s3a2 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s3a2 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s3a2:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s3a2 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s3a2:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s3a2 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s3a2:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s3a2 = gr.File(label="google_mail.json")
                        action_s3a2 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s3a2 = gr.Button("add tool component",visible=False)
            add_component_buttion_s3a2.click(tool_component_visible_s3a2, 
                            [symptoms_box_s3a2],
                            [WSC_s3a2,KBC_s3a2,mail_s3a2],)
            #agent3
            makedowns3a3 = gr.Markdown("""Agent3""",visible=False)
            with gr.Row(visible=False) as agentr3_s3:
                name_s3a3 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s3a3 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s3a3 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc3_s3:
                task_s3a3 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s3a3 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s3a3 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s3a3:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s3a3 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s3a3:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s3a3 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s3a3:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s3a3 = gr.File(label="google_mail.json")
                        action_s3a3 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s3a3 = gr.Button("add tool component",visible=False)
            add_component_buttion_s3a3.click(tool_component_visible_s3a3, 
                            [symptoms_box_s3a3],
                            [WSC_s3a3,KBC_s3a3,mail_s3a3],)
            #agent4
            makedowns3a4 = gr.Markdown("""Agent4""",visible=False)
            with gr.Row(visible=False) as agentr4_s3:
                name_s3a4 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s3a4 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s3a4 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc4_s3:
                task_s3a4 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s3a4 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s3a4 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s3a4:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s3a4 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s3a4:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s3a4 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s3a4:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s3a4 = gr.File(label="google_mail.json")
                        action_s3a4 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s3a4 = gr.Button("add tool component",visible=False)
            add_component_buttion_s3a4.click(tool_component_visible_s3a4, 
                            [symptoms_box_s3a4],
                            [WSC_s3a4,KBC_s3a4,mail_s3a4],)
            #agent5
            makedowns3a5 = gr.Markdown("""Agent5""",visible=False)
            with gr.Row(visible=False) as agentr5_s3:
                name_s3a5 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s3a5 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s3a5 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc5_s3:
                task_s3a5 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s3a5 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s3a5 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s3a5:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s3a5 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s3a5:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s3a5 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s3a5:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s3a5 = gr.File(label="google_mail.json")
                        action_s3a5 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s3a5 = gr.Button("add tool component",visible=False)
            add_component_buttion_s3a5.click(tool_component_visible_s3a5, 
                            [symptoms_box_s3a5],
                            [WSC_s3a5,KBC_s3a5,mail_s3a5],)
            with gr.Column() as number3:
                text_input_s3 = gr.Number(label="agent number",minimum=1,maximum=5)
                add_agent_buttion = gr.Button("add agent")
                add_agent_buttion.click(add_agent_s3, 
                                        [text_input_s3],
                                        [agentc1_s3,agentr1_s3,makedowns3a1,symptoms_box_s3a1,
                                         agentc2_s3,agentr2_s3,makedowns3a2,symptoms_box_s3a2,
                                         agentc3_s3,agentr3_s3,makedowns3a3,symptoms_box_s3a3,
                                         agentc4_s3,agentr4_s3,makedowns3a4,symptoms_box_s3a4,
                                         agentc5_s3,agentr5_s3,makedowns3a5,symptoms_box_s3a5,add_component_buttion_s3a1,add_component_buttion_s3a2,add_component_buttion_s3a3,add_component_buttion_s3a4,add_component_buttion_s3a5,number3])
            with gr.Row():
                begin_role3 = gr.Text(label="begin_role(optional)",placeholder="set the role of the agent who speaks at the beginning of the scene, e.g., oculist")
                begin_query3  = gr.Text(label="begin_query(optional)",placeholder="set the speech of the agent who speaks at the beginning of the scene, e.g., welcome to our hospital")
            gr.Markdown("""Environment""")
            with gr.Row():
                environment3 = gr.Textbox(label="environment(optional)",placeholder="describe the scene as it is happening now, e.g, It is currently the debate stage, where the positive side is assigning tasks.")
                environment_type3 = gr.Dropdown(choices = ["cooperative","compete"],label="environment type")
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller_m3 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num_m3 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        with gr.Tab("state4"):
            makedowns4a1 = gr.Markdown("""Agent1""",visible=False)
            with gr.Row(visible=False) as agentr1_s4:
                name_s4a1 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s4a1 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s4a1 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc1_s4:
                task_s4a1 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s4a1 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s4a1 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s4a1:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s4a1 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s4a1:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s4a1 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s4a1:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s4a1 = gr.File(label="google_mail.json")
                        action_s4a1 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s4a1 = gr.Button("add tool component",visible=False)
            add_component_buttion_s4a1.click(tool_component_visible_s4a1, 
                            [symptoms_box_s4a1],
                            [WSC_s4a1,KBC_s4a1,mail_s4a1],)
            #agent2
            makedowns4a2 = gr.Markdown("""Agent2""",visible=False)
            with gr.Row(visible=False) as agentr2_s4:
                name_s4a2 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s4a2 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s4a2 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc2_s4:
                task_s4a2 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s4a2 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s4a2 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s4a2:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s4a2 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s4a2:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s4a2 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s4a2:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s4a2 = gr.File(label="google_mail.json")
                        action_s4a2 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s4a2 = gr.Button("add tool component",visible=False)
            add_component_buttion_s4a2.click(tool_component_visible_s4a2, 
                            [symptoms_box_s4a2],
                            [WSC_s4a2,KBC_s4a2,mail_s4a2],)
            #agent3
            makedowns4a3 = gr.Markdown("""Agent3""",visible=False)
            with gr.Row(visible=False) as agentr3_s4:
                name_s4a3 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s4a3 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s4a3 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc3_s4:
                task_s4a3 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s4a3 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s4a3 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s4a3:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s4a3 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s4a3:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s4a3 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s4a3:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s4a3 = gr.File(label="google_mail.json")
                        action_s4a3 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s4a3 = gr.Button("add tool component",visible=False)
            add_component_buttion_s4a3.click(tool_component_visible_s4a3, 
                            [symptoms_box_s4a3],
                            [WSC_s4a3,KBC_s4a3,mail_s4a3],)
            makedowns4a4 = gr.Markdown("""Agent4""",visible=False)
            with gr.Row(visible=False) as agentr4_s4:
                name_s4a4 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s4a4 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s4a4 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc4_s4:
                task_s4a4 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s4a4 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s4a4 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s4a4:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s4a4 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s4a4:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s4a4 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s4a4:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s4a4 = gr.File(label="google_mail.json")
                        action_s4a4 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s4a4 = gr.Button("add tool component",visible=False)
            add_component_buttion_s4a4.click(tool_component_visible_s4a4, 
                            [symptoms_box_s4a4],
                            [WSC_s4a4,KBC_s4a4,mail_s4a4],)
            makedowns4a5 = gr.Markdown("""Agent5""",visible=False)
            with gr.Row(visible=False) as agentr5_s4:
                name_s4a5 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s4a5 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s4a5 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc5_s4:
                task_s4a5 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s4a5 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s4a5 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s4a5:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s4a5 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s4a5:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s4a5 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s4a5:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s4a5 = gr.File(label="google_mail.json")
                        action_s4a5 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s4a5 = gr.Button("add tool component",visible=False)
            add_component_buttion_s4a5.click(tool_component_visible_s4a5, 
                            [symptoms_box_s4a5],
                            [WSC_s4a5,KBC_s4a5,mail_s4a5],)
            with gr.Column() as number4:
                text_input_s4 = gr.Number(label="agent number",minimum=1,maximum=5)
                add_agent_buttion = gr.Button("add agent")
                add_agent_buttion.click(add_agent_s4, 
                                        [text_input_s4],
                                        [agentc1_s4,agentr1_s4,makedowns4a1,symptoms_box_s4a1,
                                         agentc2_s4,agentr2_s4,makedowns4a2,symptoms_box_s4a2,
                                         agentc3_s4,agentr3_s4,makedowns4a3,symptoms_box_s4a3,
                                         agentc4_s4,agentr4_s4,makedowns4a4,symptoms_box_s4a4,
                                         agentc5_s4,agentr5_s4,makedowns4a5,symptoms_box_s4a5,add_component_buttion_s4a1,add_component_buttion_s4a2,add_component_buttion_s4a3,add_component_buttion_s4a4,add_component_buttion_s4a5,number4])
            with gr.Row():
                begin_role4 = gr.Text(label="begin_role(optional)",placeholder="set the role of the agent who speaks at the beginning of the scene, e.g., oculist")
                begin_query4  = gr.Text(label="begin_query(optional)",placeholder="set the speech of the agent who speaks at the beginning of the scene, e.g., welcome to our hospital")
            gr.Markdown("""Environment""")
            with gr.Row():
                environment4 = gr.Textbox(label="environment(optional)",placeholder="describe the scene as it is happening now, e.g, It is currently the debate stage, where the positive side is assigning tasks.")
                environment_type4 = gr.Dropdown(choices = ["cooperative","compete"],label="environment type")
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller_m4 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num_m4 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        with gr.Tab("state5"):
            makedowns5a1 = gr.Markdown("""Agent1""",visible=False)
            with gr.Row(visible=False) as agentr1_s5:
                name_s5a1 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s5a1 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s5a1 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc1_s5:
                task_s5a1 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s5a1 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s5a1 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s5a1:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s5a1 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s5a1:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s5a1 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s5a1:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s5a1 = gr.File(label="google_mail.json")
                        action_s5a1 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s5a1 = gr.Button("add tool component",visible=False)
            add_component_buttion_s5a1.click(tool_component_visible_s5a1, 
                            [symptoms_box_s5a1],
                            [WSC_s5a1,KBC_s5a1,mail_s5a1],)
            #agent2
            makedowns5a2 = gr.Markdown("""Agent2""",visible=False)
            with gr.Row(visible=False) as agentr2_s5:
                name_s5a2 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s5a2 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s5a2 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc2_s5:
                task_s5a2 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s5a2 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s5a2 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s5a2:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s5a2 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s5a2:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s5a2 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s5a2:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s5a2 = gr.File(label="google_mail.json")
                        action_s5a2 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s5a2 = gr.Button("add tool component",visible=False)
            add_component_buttion_s5a2.click(tool_component_visible_s5a2, 
                            [symptoms_box_s5a2],
                            [WSC_s5a2,KBC_s5a2,mail_s5a2],)
            #agent3
            makedowns5a3 = gr.Markdown("""Agent3""",visible=False)
            with gr.Row(visible=False) as agentr3_s5:
                name_s5a3 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s5a3 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s5a3 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc3_s5:
                task_s5a3 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s5a3 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s5a3 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s5a3:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s5a3 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s5a3:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s5a3 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s5a3:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s5a3 = gr.File(label="google_mail.json")
                        action_s5a3 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s5a3 = gr.Button("add tool component",visible=False)
            add_component_buttion_s5a3.click(tool_component_visible_s5a3, 
                            [symptoms_box_s5a3],
                            [WSC_s5a3,KBC_s5a3,mail_s5a3],)
            makedowns5a4 = gr.Markdown("""Agent4""",visible=False)
            with gr.Row(visible=False) as agentr4_s5:
                name_s5a4 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s5a4 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s5a4 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc4_s5:
                task_s5a4 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s5a4 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s5a4 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s5a4:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s5a4 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s5a4:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s5a4 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s5a4:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s5a4 = gr.File(label="google_mail.json")
                        action_s5a4 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s5a4 = gr.Button("add tool component",visible=False)
            add_component_buttion_s5a4.click(tool_component_visible_s5a4, 
                            [symptoms_box_s5a4],
                            [WSC_s5a4,KBC_s5a4,mail_s5a4],)
            makedowns5a5 = gr.Markdown("""Agent5""",visible=False)
            with gr.Row(visible=False) as agentr5_s5:
                name_s5a5 = gr.Textbox(label="Name",placeholder="input agent's name here, e.g., Alice")
                role_s5a5 = gr.Textbox(label="Role",placeholder="describe agent's role or persona, e.g., oculist")
                style_s5a5 = gr.Textbox(label="Style",placeholder="describe the personality and style of the agent here, e.g., professional")
            with gr.Row(visible=False) as agentc5_s5:
                task_s5a5 = gr.Textbox(label="Task",placeholder="descripe the task you want the agent to perform which is clear and specific , e.g., guide the user to go to the hospital for an examination and answer questions related to hospital")
                rule_s5a5 = gr.Textbox(label="Rule",placeholder="describe the rules that the agent needs to enforce, and you can have further restrictions or descriptions of the task, e.g., Your language should be concise and avoid excessive words. You need to guide user repeatedly. When the user explicitly refuses to visit the hospital, inquire about their concerns and encourage them to come.")
            symptoms_box_s5a5 = gr.CheckboxGroup(["KnowledgeBase", "WebSearch","WeatherComponet","Mail","Weather"],label="Tool",visible=False)
            with gr.Column(visible=False) as KBC_s5a5:
                with gr.Tab(label= "KnowledgeBase"):
                    with gr.Row():
                        knowledge_path_s5a5 = gr.File(label="knowledge_file")
            with gr.Column(visible=False) as WSC_s5a5:
                with gr.Tab(label= "WebSearch"):
                    with gr.Row():
                        engine_name_s5a5 = gr.CheckboxGroup(["bing", "google"],label="engine_name")
            with gr.Column(visible=False) as mail_s5a5:
                with gr.Tab(label= "Mail"):
                    with gr.Row():
                        cfg_file_s5a5 = gr.File(label="google_mail.json")
                        action_s5a5 = gr.CheckboxGroup(["read", "send"],label="action")
            add_component_buttion_s5a5 = gr.Button("add tool component",visible=False)
            add_component_buttion_s5a5.click(tool_component_visible_s5a5, 
                            [symptoms_box_s5a5],
                            [WSC_s5a5,KBC_s5a5,mail_s5a5],)
            with gr.Column() as number5:
                text_input_s5 = gr.Number(label="agent number",minimum=1,maximum=5)
                add_agent_buttion = gr.Button("add agent")
                add_agent_buttion.click(add_agent_s5, 
                                        [text_input_s5],
                                        [agentc1_s5,agentr1_s5,makedowns5a1,symptoms_box_s5a1,
                                         agentc2_s5,agentr2_s5,makedowns5a2,symptoms_box_s5a2,
                                         agentc3_s5,agentr3_s5,makedowns5a3,symptoms_box_s5a3,
                                         agentc4_s5,agentr4_s5,makedowns5a4,symptoms_box_s5a4,
                                         agentc5_s5,agentr5_s5,makedowns5a5,symptoms_box_s5a5,add_component_buttion_s5a1,add_component_buttion_s5a2,add_component_buttion_s5a3,add_component_buttion_s5a4,add_component_buttion_s5a5,number5])
            with gr.Row():
                begin_role5 = gr.Text(label="begin_role(optional)",placeholder="set the role of the agent who speaks at the beginning of the scene, e.g., oculist")
                begin_query5  = gr.Text(label="begin_query(optional)",placeholder="set the speech of the agent who speaks at the beginning of the scene, e.g., welcome to our hospital")
            gr.Markdown("""Environment""")
            with gr.Row():
                environment5 = gr.Textbox(label="environment(optional)",placeholder="describe the scene as it is happening now, e.g, It is currently the debate stage, where the positive side is assigning tasks.")
                environment_type5 = gr.Dropdown(choices = ["cooperative","compete"],label="environment type")
            gr.Markdown("""Relation and Controller""")
            with gr.Row():
                controller_m5 = gr.Textbox(label="controller",placeholder="""Please write in the following format:
stateX:Reason for entering stateX
stateY:Reason for entering stateY
There is no limit to the number of next states. If the current state is the last state, there is no need to fill in the stuff of the next states.""")
                max_chat_num_m5 = gr.Textbox(label="max chat num(optional)",placeholder="set a integer that represents the maximum number of rounds to run the chat in this state phase.")
        gr.Markdown("""Initializtion""")
        generate_json_button_multi_agent = gr.Button("generate config")
        json_output = gr.File(label="generated config file")
        generate_json_button_multi_agent.click(generate_json_multi_agent, 
                                [api_key,proxy,name_s1a1,role_s1a1,style_s1a1,task_s1a1,rule_s1a1,
                                 name_s1a2,role_s1a2,style_s1a2,task_s1a2,rule_s1a2,
                                 name_s1a3,role_s1a3,style_s1a3,task_s1a3,rule_s1a3,
                                 name_s1a4,role_s1a4,style_s1a4,task_s1a4,rule_s1a4,
                                 name_s1a5,role_s1a5,style_s1a5,task_s1a5,rule_s1a5,
                                 name_s2a1,role_s2a1,style_s2a1,task_s2a1,rule_s2a1,
                                 name_s2a2,role_s2a2,style_s2a2,task_s2a2,rule_s2a2,
                                 name_s2a3,role_s2a3,style_s2a3,task_s2a3,rule_s2a3,
                                 name_s2a4,role_s2a4,style_s2a4,task_s2a4,rule_s2a4,
                                 name_s2a5,role_s2a5,style_s2a5,task_s2a5,rule_s2a5,
                                 name_s3a1,role_s3a1,style_s3a1,task_s3a1,rule_s3a1,
                                 name_s3a2,role_s3a2,style_s3a2,task_s3a2,rule_s3a2,
                                 name_s3a3,role_s3a3,style_s3a3,task_s3a3,rule_s3a3,
                                 name_s3a4,role_s3a4,style_s3a4,task_s3a4,rule_s3a4,
                                 name_s3a5,role_s3a5,style_s3a5,task_s3a5,rule_s3a5,
                                 name_s4a1,role_s4a1,style_s4a1,task_s4a1,rule_s4a1,
                                 name_s4a2,role_s4a2,style_s4a2,task_s4a2,rule_s4a2,
                                 name_s4a3,role_s4a3,style_s4a3,task_s4a3,rule_s4a3,
                                 name_s4a4,role_s4a4,style_s4a4,task_s4a4,rule_s4a4,
                                 name_s4a5,role_s4a5,style_s4a5,task_s4a5,rule_s4a5,
                                 name_s5a1,role_s5a1,style_s5a1,task_s5a1,rule_s5a1,
                                 name_s5a2,role_s5a2,style_s5a2,task_s5a2,rule_s5a2,
                                 name_s5a3,role_s5a3,style_s5a3,task_s5a3,rule_s5a3,
                                 name_s5a4,role_s5a4,style_s5a4,task_s5a4,rule_s5a4,
                                 name_s5a5,role_s5a5,style_s5a5,task_s5a5,rule_s5a5,
                                 environment1,environment2,environment3,environment4,environment5,
                                 cfg_file_s1a1,action_s1a1,cfg_file_s1a2,action_s1a2,
                                 cfg_file_s1a3,action_s1a3,cfg_file_s1a4,action_s1a4,
                                 cfg_file_s1a5,action_s1a5,cfg_file_s2a1,action_s2a1,
                                 cfg_file_s2a2,action_s2a2,cfg_file_s2a3,action_s2a3,
                                 cfg_file_s2a4,action_s2a4,cfg_file_s2a5,action_s2a5,
                                 cfg_file_s3a1,action_s3a1,cfg_file_s3a2,action_s3a2,
                                 cfg_file_s3a3,action_s3a3,cfg_file_s3a4,action_s3a4,
                                 cfg_file_s3a5,action_s3a5,cfg_file_s4a1,action_s4a1,
                                 cfg_file_s4a2,action_s4a2,cfg_file_s4a3,action_s4a3,
                                 cfg_file_s4a4,action_s4a4,cfg_file_s4a5,action_s4a5,
                                 cfg_file_s5a1,action_s5a1,cfg_file_s5a2,action_s5a2,
                                 cfg_file_s5a3,action_s5a3,cfg_file_s5a4,action_s5a4,
                                 cfg_file_s5a5,action_s5a5,
                                 knowledge_path_s1a1,engine_name_s1a1,knowledge_path_s1a2,engine_name_s1a2,
                                 knowledge_path_s1a3,engine_name_s1a3,knowledge_path_s1a4,engine_name_s1a4,
                                 knowledge_path_s1a5,engine_name_s1a5,knowledge_path_s2a1,engine_name_s2a1,
                                 knowledge_path_s2a2,engine_name_s2a2,knowledge_path_s2a3,engine_name_s2a3,
                                 knowledge_path_s2a4,engine_name_s2a4,knowledge_path_s2a5,engine_name_s2a5,
                                 knowledge_path_s3a1,engine_name_s3a1,knowledge_path_s3a2,engine_name_s3a2,
                                 knowledge_path_s3a3,engine_name_s3a3,knowledge_path_s3a4,engine_name_s3a4,
                                 knowledge_path_s3a5,engine_name_s3a5,knowledge_path_s4a1,engine_name_s4a1,
                                 knowledge_path_s4a2,engine_name_s4a2,knowledge_path_s4a3,engine_name_s4a3,
                                 knowledge_path_s4a4,engine_name_s4a4,knowledge_path_s4a5,engine_name_s4a5,
                                 knowledge_path_s5a1,engine_name_s5a1,knowledge_path_s5a2,engine_name_s5a2,
                                 knowledge_path_s5a3,engine_name_s5a3,knowledge_path_s5a4,engine_name_s5a4,knowledge_path_s5a5,engine_name_s5a5,
                                 symptoms_box_s1a1,symptoms_box_s1a2,symptoms_box_s1a3,symptoms_box_s1a4,symptoms_box_s1a5,symptoms_box_s2a1,symptoms_box_s2a2,symptoms_box_s2a3,symptoms_box_s2a4,symptoms_box_s2a5,symptoms_box_s3a1,symptoms_box_s3a2,
                                 symptoms_box_s3a3,symptoms_box_s3a4,symptoms_box_s3a5,symptoms_box_s4a1,symptoms_box_s4a2,symptoms_box_s4a3,symptoms_box_s4a4,symptoms_box_s4a5,
                                 symptoms_box_s5a1,symptoms_box_s5a2,symptoms_box_s5a3,symptoms_box_s5a4,symptoms_box_s5a5,
                                 controller_m1,controller_m2,controller_m3,controller_m4,controller_m5,
                                 environment_type1,environment_type2,environment_type3,environment_type4,environment_type5,
                                 begin_role1,begin_role2,begin_role3,begin_role4,begin_role5,
                                 begin_query1,begin_query2,begin_query3,begin_query4,begin_query5,
                                 max_chat_num_m1,max_chat_num_m2,max_chat_num_m3,max_chat_num_m4,max_chat_num_m5],
                                [json_output])
demo.launch(server_port=18870,share=True,debug=True,
            show_api=False)