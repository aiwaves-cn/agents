# -*- coding: utf-8 -*-
import copy
import time
import re
from tree import construct_tree, tree2xml, tree2dict
import json

def extract_tag_names(text):
    # 定义正则表达式模式
    pattern = r'<([^<>]+)>'

    # 使用正则表达式查找匹配项
    matches = re.findall(pattern, text)

    # 剔除结束的，只保留开始的
    stack = []
    answer = []
    for item in matches:
        if item[0] != '/':
            stack.append(item)
        else:
            """说明为结束的，需要判断一下是否有"""
            if item[1:] in stack:
                while stack[-1] != item[1:]:
                    stack.pop()
                answer.append(stack.pop())
    return answer

def print_log(message: str):
    print(f"[{time.ctime()}] {message}")

def simulation():
    content = ""
    for i in range(5000):
        content = f"{content} hello"
    return {
        'id': 'chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
        'object': 'chat.completion',
        'created': 1677649420,
        'model': 'gpt-3.5-turbo',
        'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
        'choices': [
            {
                'message': {
                    'role': 'assistant',
                    'content': content
                },
                'finish_reason': 'stop',
                'index': 0
            }
        ]
    }

def new_parse(content:str, labels: list, return_dict:bool=False):
    """将content里面的labels抽出来，相当于使用tree里面的remain，如果labels为空，则表示全部"""
    tree = construct_tree(content, add_root_label=True)
    tree.first_label = False
    if len(labels) == 0 or labels is None:
        if return_dict:
            return tree2dict(tree)['root']
        else:
            # 去除掉<root>和</root>
            return "\n".join(tree2xml(tree).split('\n')[1:-1])
    else:
        if return_dict:
            tree_dict = tree2dict(tree, filter=labels, mode="remain")['root']
            return tree_dict
        else:
            tree_xml = tree2xml(tree, filter=labels, mode="remain")
            return "\n".join(tree_xml.split('\n')[1:-1])

