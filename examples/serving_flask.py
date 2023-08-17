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
import logging
import time
from flask import Flask,request,Response,jsonify
from fastapi import APIRouter, Request, Body
# from gevent import pywsgi
import requests
from multiprocessing import Process
import sys
sys.path.append("../../agents/src/agents/")
from sop import SOP
from agent import Agent
import os
import json
import asyncio
import aiohttp
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from utils import *
from threading import  Thread
import os
from multiprocessing import Process
from fastapi import FastAPI,Request
from fastapi.responses import  JSONResponse,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
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
parser = argparse.ArgumentParser(description='A demo of chatbot')
parser.add_argument('--customize',type=int,default=1)
# customize
parser.add_argument('--ansDiversity',type=str)
parser.add_argument('--ansSimplify',type=str)
parser.add_argument('--activeMode',type=str)
parser.add_argument('--agent_setting',type=str)
parser.add_argument('--agent_style',type=str)
parser.add_argument('--docPath',type=str)
# general
parser.add_argument('--botCode',type=str)
parser.add_argument('--logPath',type=str)
parser.add_argument('--agent', type=str, help='path to SOP json')
parser.add_argument('--port', type=int, help='server port')
parser.add_argument('--router', type=str, default='/api/v1/ask/')
args = parser.parse_args()
#print(args.ansDiversity,args.ansSimplify,args.activeMode,args.agent_setting,args.agent_style,args.docPath,args.botCode,args.logPath,args.port,sep='\n')
ping_port=7889

addr="192.168.110.201"

ping_flag=True

if args.customize == 1:
   assert args.agent_setting != None
   assert args.agent_style != None
   assert args.ansDiversity != None
   assert args.ansSimplify != None
   assert args.activeMode != None
   assert args.port != None
   assert args.router != None
   output = process_document(args.docPath)
   knowledge_base = output["knowledge_base"]
   type = output["type"]
   data = {}
   sop = {}
   data["system_prompt"] =  args.agent_setting + "你的语言风格是：" + args.agent_style
   data["last_prompt"] = None
   data["done"] = True
   data["tool_name"] = "KnowledgeResponseNode"
   data["name"] = "node1"
   data["root"] = True
   data["type"] = type
   data["knowledge_base"] = knowledge_base
   sop["tool_nodes"] = {"node1":data}
   sop["relation"] =  {"node1": {"0": "node1"}}
   sop["temperature"] = int(args.ansDiversity)*0.1
   sop["log_path"] = args.logPath
   sop["active_mode"] = True if args.activeMode == "True" else False
   sop["answer_simplify"] = True if int(args.ansSimplify) <= 5 else False
   os.makedirs("temp_agent", exist_ok=True)
   save_path = os.path.join("temp_agent/",get_code()+".json")
   with open(save_path,"w",encoding="utf-8") as f:
       json.dump(sop,f,ensure_ascii=False,indent=2)
   agent_file = save_path
else:
   assert args.agent != None
   assert args.router != None
   agent_file = args.agent

agent = Agent(agent_file)
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
def extract_answer(text):
    return text

async def generate_events(response):
    msg=""
    for data in response:
        if data:
            #last_length = len(extract_answer(data))
            #all += data.choices[0]['delta'].get('content') if data.choices[0]['delta'].get('content') else ''
            chat_answer = extract_answer(data)
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
@app.post('/api/v1/ask')
async def reply(request:Request):
   #print(request.json.ge)

    data=await request.json()
    userName = data.get('userName')
    query = data.get('query')
    response = agent.reply(userName,query)

    async def event_stream():
        async for event in generate_events(response):
            if event:
                yield f'data:{event}'
                await asyncio.sleep(0.02)
    return StreamingResponse(event_stream(),media_type="text/event-stream")

async def ping_task():
    ping_url = f"http://0.0.0.0:{ping_port}/trigger/v1/bot/callback/health?botCode={args.botCode}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url=ping_url) as resp:
            pass
    return

@app.on_event("startup")
async def send_ping():
    if ping_flag:
        await asyncio.create_task(ping_task())
    return

if __name__ == '__main__':
    uvicorn.run('serving:app', host=addr, port=args.port, reload=False)



