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

from flask import Flask,request,Response
from gevent import pywsgi
import sys
sys.path.append("../src/agents")
from sop import SOP
from agent import Agent
import os



if __name__ == '__main__':
    
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
    parser.add_argument('--ansDiversity',type=int)
    parser.add_argument('--ansSimplify',type=int)
    parser.add_argument('--botCode',type=int)
    parser.add_argument('--logPath',type=int)
    parser.add_argument('--docPath',type=int)
    parser.add_argument('--activeMode',type=int)
    
    parser.add_argument('--agent', type=str, help='path to SOP json')
    parser.add_argument('--port', type=int, help='server port')
    parser.add_argument('--router', type=str, default='/api/v1/ask/')
    args = parser.parse_args()
    
    agent = Agent(args.agent)
    app = Flask(__name__)
    headers = {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
    os.makedirs("logs",exist_ok=True)
    
    # {'userName': '', 'query': '你好', 'history': [{'type': 1, 'message': '您好，我是导购机器人，您有什么问题需要我的帮助？', 'http': '', 'timestamp': 1690429363521, 'img': ''}, {'type': 0, 'message': '你好', 'http': '', 'timestamp': 1690429366306, 'img': ''}, {'type': 1, 'message': '', 'http': '', 'timestamp': 1690429366306, 'img': ''}, {'type': 1, 'message': '', 'http': '', 'timestamp': 1690429366306, 'img': ''}]}
    @app.route(args.router,methods=['post'])
    def reply():
        userName = request.json.get('userName')
        query = request.json.get('query')
        response = agent.reply(userName,query)
        return Response(response, mimetype='text/event-stream', headers=headers)
    
    server = pywsgi.WSGIServer(('0.0.0.0', args.port), app)
    server.serve_forever()
    
    
    