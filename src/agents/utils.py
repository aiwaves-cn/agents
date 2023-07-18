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

"""helper functions for an LLM autonoumous agent"""
import openai
MAX_CHAT_HISTORY = 5
API_KEY = ''
PROXY = 'http://127.0.0.1:7000'

def process_history(chat_history):
#函数：历史信息的处理
#入参 chat_history 类型：dict 含义：message携带的历史信息
#出参 ch_dict 类型：list 含义：处理后的历史记录信息 
    ch_dict = []
    for ch in chat_history:
        if ch.role=="user":
            ch_dict.append(  {"role": "user", "content": ch.content})
        else:
            ch_dict.append(  {"role": "assistant", "content": ch.content})
    #保留最近三轮的对话历史
    if len(ch_dict)>2*MAX_CHAT_HISTORY:
        ch_dict = ch_dict[-(2*MAX_CHAT_HISTORY+1):]
    return ch_dict


def get_content_between_a_b(start_tag,end_tag,text):
    extracted_text = ""
    start_index = text.find(start_tag)
    while start_index != -1:
        end_index = text.find(end_tag, start_index + len(start_tag))
        if end_index != -1:
            extracted_text += text[start_index + len(start_tag):end_index] + " "
            start_index = text.find(start_tag, end_index + len(end_tag))
        else:
            break

    return extracted_text.strip()

def extract(text,type):
    target_str = get_content_between_a_b(f'<{type}>',f'</{type}>',text)
    return target_str

def get_gpt_response_rule(ch_dict,
                          system_prompt,
                          last_prompt,
                          model="gpt-3.5-turbo-16k-0613",
                          temperature=0):
    """基本的prompt调用方法

    Args:
        ch_dict (_type_): 历史记忆
        system_prompt (_type_): 系统提示词
        last_prompt (_type_): 任务提示词

    Returns:
        _type_: chatgpt的回答
    """
    openai.api_key = API_KEY
    openai.proxy = PROXY

    messages = [{"role": "system", "content": system_prompt}]
    if ch_dict:
        messages += ch_dict
    messages += [{"role": "user", "content": f"{last_prompt}"}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,  # 模型输出的温度系数，控制输出的随机程度
    )

    # 调用 OpenAI 的 ChatCompletion 接口
    return response.choices[0].message["content"]


if __name__ == '__main__':
    str = "hello 123 hello"
    x = get_content_between_a_b("hello1","hello1",str)
