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
sys.path.append("/home/aiwaves/jlwu/agents-2/src/agents")
from sop import SOP
from agent import Agent

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='A demo of chatbot')
    parser.add_argument('--model_ckpt', type=str, default='shibing624/text2vec-base-chinese', help='model checkpoint')
    parser.add_argument('--model_type', type=str, default='SentenceModel', help='model name')
    parser.add_argument('--topk', type=int, default=3)
    parser.add_argument('--logger_dir', type=str, default='logs/test_log')
    parser.add_argument('--knowledge_path', type=str, default='data/text_embeddings_yc_enhanced.json', help='path to save new_quries')
    parser.add_argument('--agent', type=str, help='path to SOP json')
    args = parser.parse_args()
    
    agent = Agent(args.agent)
    app = Flask(__name__)
    headers = {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
    # {'userName': '', 'query': '你好', 'history': [{'type': 1, 'message': '您好，我是导购机器人，您有什么问题需要我的帮助？', 'http': '', 'timestamp': 1690429363521, 'img': ''}, {'type': 0, 'message': '你好', 'http': '', 'timestamp': 1690429366306, 'img': ''}, {'type': 1, 'message': '', 'http': '', 'timestamp': 1690429366306, 'img': ''}, {'type': 1, 'message': '', 'http': '', 'timestamp': 1690429366306, 'img': ''}]}
    @app.route('/api/v1/ask/',methods=['post'])
    def reply():
        userName = request.json.get('userName')
        query = request.json.get('query')
        response = agent.reply(userName,query)
        return Response(response, mimetype='text/event-stream', headers=headers)
    
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app)
    server.serve_forever()