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
API_KEY = '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'
PROXY = 'http://127.0.0.1:7000'


def get_content_between_a_b(start_tag,end_tag,text):
    """

    Args:
        start_tag (str): start_tag
        end_tag (str): end_tag
        text (str): complete sentence

    Returns:
        str: the content between start_tag and end_tag
    """
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
    """extract the content between <type></type>

    Args:
        text (str): complete sentence
        type (str): tag

    Returns:
        str: content between <type></type>
    """
    target_str = get_content_between_a_b(f'<{type}>',f'</{type}>',text)
    return target_str

def get_gpt_response_rule(ch_dict,
                          system_prompt,
                          last_prompt,
                          model="gpt-3.5-turbo-16k-0613",
                          temperature=0):
    """get the response of chatgpt

    Args:
        ch_dict (list): the history of chat
        system_prompt (str): the main task set in the first
        last_prompt (str): attached to the final task
        temperature(float):randomness of GPT responses

    Returns:
        str: the response of chatgpt
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
        temperature=temperature,  
    )

    return response.choices[0].message["content"]


if __name__ == '__main__':
    str = "hello 123 hello"
    x = get_content_between_a_b("hello1","hello1",str)
