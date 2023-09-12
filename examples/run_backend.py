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

"""
example code for serving an autonomous agents with Flask/FastAPI backend
"""

import argparse
from fastapi import APIRouter, Request, Body
# from gevent import pywsgi
from multiprocessing import Process
import sys
import os
import json
import asyncio
import aiohttp
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from threading import  Thread
import os
from multiprocessing import Process
from fastapi import FastAPI,Request
from fastapi.responses import  JSONResponse,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
sys.path.append("../src/agents")
from SOP import SOP
from Agent import Agent
from Environment import Environment
from Memory import Memory

# -*- coding: utf-8 -*-

"""
port=$1
ansDiversity=$2
ansSimplify=$3
activeMode=$4
botCode=$5
logPath=$6
docPath=$7
"""

ping_port=7889
addr="192.168.110.201"

ping_flag=True

app = FastAPI()
# 跨域设置，因为测试需要前端访问，所以允许所有域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 路由设置

headers = {
           'Content-Type': 'text/event-stream',
           'Cache-Control': 'no-cache',
           'X-Accel-Buffering': 'no',
       }
# {'userName': '', 'query': '你好', 'history': [{'type': 1, 'message': '您好，我是导购机器人，您有什么问题需要我的帮助？', 'http': '', 'timestamp': 1690429363521, 'img': ''}, {'type': 0, 'message': '你好', 'http': '', 'timestamp': 1690429366306, 'img': ''}, {'type': 1, 'message': '', 'http': '', 'timestamp': 1690429366306, 'img': ''}, {'type': 1, 'message': '', 'http': '', 'timestamp': 1690429366306, 'img': ''}]}
@app.get('/ping')
async def ping():
   print("finish!!")
   return{
        "message":"pong"
   }


async def generate_events(response):
    msg=""
    for chat_answer in response:
        if chat_answer:
            msg+=chat_answer
            if chat_answer:
                new_dict = {
                        "content": msg,
                        "type": "chat",
                        "done": False,

                    }
                json_dict = json.dumps(new_dict, ensure_ascii=False)
                yield json_dict
        else:
            continue
        
def init(config): 
    if not os.path.exists("logs"):
        os.mkdir("logs")
    sop = SOP.from_config(config)
    agents,roles_to_names,names_to_roles = Agent.from_config(config)
    environment = Environment.from_config(config)
    environment.agents = agents
    environment.roles_to_names,environment.names_to_roles = roles_to_names,names_to_roles
    sop.roles_to_names,sop.names_to_roles = roles_to_names,names_to_roles
    for name,agent in agents.items():
        agent.environment = environment
    return agents,sop,environment

parser = argparse.ArgumentParser(description='A demo of chatbot')
parser.add_argument('--agent', type=str, help='path to SOP json')
parser.add_argument('--port', type=str, help='your port')
parser.add_argument('--route', type=str, help='your route')
args = parser.parse_args()


agents,sop,environment = init(args.agent)


@app.post(args.route)
async def reply(request:Request):
   #print(request.json.ge)
    data=await request.json()
    userName = data.get('userName')
    userRole = data.get('userRole')
    query = data.get('query')
    memory = Memory(userRole, userName, query)
    environment.update_memory(memory,sop.current_state)
    environment.current_state.index = 1
    
    current_state,current_agent= sop.next(environment,agents)
    action = current_agent.step(current_state)   #component_dict = current_state[self.role[current_node.name]]   current_agent.compile(component_dict) 
    memory = action.process()
    environment.update_memory(memory,current_state)
    
    response = action.response

    async def event_stream():
        async for event in generate_events(response):
            if event:
                yield f'data:{event}'
                await asyncio.sleep(0.02)
    return StreamingResponse(event_stream(),media_type="text/event-stream")


if __name__ == '__main__':
    uvicorn.run('serving:app', host=addr, port=args.port, reload=False)



