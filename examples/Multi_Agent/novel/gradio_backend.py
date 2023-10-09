import sys
sys.path.append("../../../src/agents")
sys.path.append("./novel-server")
sys.path.append("../../Gradio_Config")

import yaml
import os
import argparse
import random

from agents.SOP import SOP
from agents.Agent import Agent
from agents.Environment import Environment
from gradio_base import Client
from agents.Memory import Memory

from myagent import Node, MyAgent, ask_gpt
from typing import List, Tuple
from PROMPT import NOVEL_PROMPT
from myutils import print_log, new_parse
import json
from gradio_base import Client


from cmd_outline import run_node_1, run_node_2
from cmd_perform import init, run
from create_sop import create_sop

def show_in_gradio(state, name, chunk, node_name):
    if state == 30:
        Client.send_server(str([state, name, chunk, node_name, 50]))
        return

    if name.lower() in ["summary", "recorder"]:
        """It is recorder"""
        name = "Recorder"
        if state == 0:
            state = 22
        else:
            state = 21
    else:
        if Client.current_node != node_name and state == 0:
            state = 12
            Client.current_node = node_name
        elif Client.current_node != node_name and state != 0:
            assert False
        else:
            state = 10 + state
    Client.send_server(str([state, name, chunk, node_name, 50]))


if __name__ == "__main__":
    MyAgent.SIMULATION = False
    MyAgent.TEMPERATURE = 0.3
    stream_output = True
    output_func = show_in_gradio
    print("in")

    if output_func is not None:
        client = Client()
        Client.send_server = client.send_message
        client.send_message(
            {
                "agents_name": ['Elmo','Abby', 'Zoe', 'Ernie', 'Bert', 'Oscar'],
                "nodes_name": ['Node 1','Node 2','Node 3', 'Node 4', 'state1', 'state2', 'state3', 'state4'],
                "output_file_path": f"{os.getcwd()+'/novel_outline'}",
                "requirement": NOVEL_PROMPT['Node 1']["task"],
                "api_key": os.environ["API_KEY"]
            }
        )
        client.listening_for_start_()
        os.environ["API_KEY"] = client.cache["api_key"]
        MyAgent.API_KEY = client.cache["api_key"]
        NOVEL_PROMPT['Node 1']['task'] = client.cache['requirement']
        print("Received: ", client.cache['requirement'])
        outline = run_node_1(
            stream_output=stream_output,
            output_func=output_func,
            task_prompt=client.cache['requirement']
        )
    else:
        outline = run_node_1(
            stream_output=stream_output,
            output_func=output_func
        )
        # pass
    print(outline)
    run_node_2(outline, stream_output=stream_output, output_func=output_func)
    print("done")

    create_sop()
    
    with open("novel_outline.json", 'r') as f:
        data = json.load(f)
    name_list = list(data["agents"].keys())
    
    show_in_gradio(30, str(name_list), " ", " ")

    agents,sop,environment = init("novel_outline.json")
    run(agents,sop,environment)
    
