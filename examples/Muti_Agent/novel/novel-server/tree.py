# -*- coding: utf-8 -*-
import copy
from typing import List, Tuple, Any
import re

class Item:
    def __init__(self, value, start, end):
        self.value = value
        self.start = start
        self.end = end

class TreeNode:
    def __init__(self, item:Item):
        self.item = item
        self.state = 0
        self.sons = []
        self.parent = None

class Tree:
    def __init__(self, item: Item, text:str):
        self.root = TreeNode(item)
        self.text = text
        self.first_label = True

    def isNodeIn(self, node1:TreeNode, node2:TreeNode):
        """判断Node1是不是Node2的孩子"""
        if node1.item.start > node2.item.start and node1.item.end < node2.item.end:
            return True
        return False

    def insert(self, new_node: TreeNode, current_node: TreeNode):
        if len(current_node.sons) == 0:
            """表明是叶子结点"""
            if self.isNodeIn(new_node, current_node):
                """是叶子结点的孩子"""
                current_node.sons.append(new_node)
                new_node.parent = current_node
                return True
            else:
                """表明不是叶子结点的孩子"""
                return False
        for son in current_node.sons:
            """遍历儿子"""
            done = self.insert(new_node, son)

            if done:
                return True
        if self.isNodeIn(new_node, current_node):
            current_node.sons.append(new_node)
            new_node.parent = current_node
            return True
        else:
            return False

    def node_count(self):
        cnt = 0
        if self.root is not None:
            cnt = 1
        sons = self.root.sons
        while len(sons) > 0:
            current: TreeNode = sons.pop()
            cnt += 1
            if len(current.sons) > 0:
                sons.extend(current.sons)
        return cnt

    def reset_state(self, reset_value, current_node:TreeNode=None):
        if current_node == None:
            current_node = self.root
        current_node.state = reset_value
        for i in range(len(current_node.sons)):
            self.reset_state(reset_value, current_node=current_node.sons[i])

    def get_node_content(self, node:TreeNode):
        value_length = len(node.item.value)
        start = node.item.start
        end = node.item.end
        return self.text[
            start+value_length+1:end-1
        ]

    def build_dict(self, current_dict:dict, current_root:TreeNode, filter_value:list=None, mode:str="filter"):
        assert mode.lower() in ["filter", "remain"], \
            f"mode `{mode}` is not in ['filter', 'remain']"
        """根据根结点建立嵌套字典"""
        if len(current_root.sons) == 0:
            """就是叶子结点"""
            if filter_value is None or (mode.lower() == "remain" and current_root.state == 1):
                return {current_root.item.value: self.get_node_content(current_root)}
            if mode.lower() == "filter" and current_root.item.value in filter_value:
                return None
            elif mode.lower() == "filter" and current_root.item.value not in filter_value:
                return {current_root.item.value: self.get_node_content(current_root)}
            elif mode.lower() == "remain" and current_root.item.value in filter_value:
                return {current_root.item.value: self.get_node_content(current_root)}
            elif mode.lower() == "remain" and current_root.item.value not in filter_value:
                return None
        else:
            if filter_value is not None:
                if mode.lower() == "filter" and current_root.item.value in filter_value:
                    return None
                if self.first_label:
                    if mode.lower() == "remain" and current_root.item.value not in filter_value and current_root.item.value != "root" and current_root.state==0:
                        return None
            current_dict[current_root.item.value] = {}
            for i in range(len(current_root.sons)):
                """染色"""
                if mode.lower() == "remain":
                    if current_root.parent is not None and current_root.parent.state == 1:
                        """当前节点的父节点被保留，则该结点也会被保留"""
                        current_root.state = 1
                    if current_root.item.value in filter_value:
                        """如果当前节点是需要被保留的，则设为1"""
                        current_root.state = 1
                        current_root.sons[i].state = 1
                    if current_root.state == 1:
                        """如果当前节点是被保留的，则儿子也会被保留"""
                        current_root.sons[i].state = 1
                    if current_root.sons[i].item.value in filter_value:
                        current_root.sons[i].state = 1
                item = self.build_dict(current_dict[current_root.item.value], current_root.sons[i], filter_value, mode)
                if isinstance(item, dict):
                    current_dict[current_root.item.value].update(item)

    def build_xml(self, current_item: list, current_root:TreeNode, filter_value:list=None, mode:str="filter"):
        assert mode.lower() in ["filter", "remain"], \
            f"mode `{mode}` is not in ['filter', 'remain']"
        if len(current_root.sons) == 0:
            """就是叶子结点"""
            if filter_value is None or (mode.lower() == "remain" and current_root.state == 1):
                return f"<{current_root.item.value}>{self.get_node_content(current_root)}</{current_root.item.value}>"
            if mode.lower() == "filter" and current_root.item.value in filter_value:
                return None
            elif mode.lower() == "filter" and current_root.item.value not in filter_value:
                return f"<{current_root.item.value}>{self.get_node_content(current_root)}</{current_root.item.value}>"
            elif mode.lower() == "remain" and current_root.item.value in filter_value:
                return f"<{current_root.item.value}>{self.get_node_content(current_root)}</{current_root.item.value}>"
            elif mode.lower() == "remain" and current_root.item.value not in filter_value:
                return None
        else:
            if filter_value is not None:
                if mode.lower() == "filter" and current_root.item.value in filter_value:
                    return None
                if self.first_label:
                    if mode.lower() == "remain" and current_root.item.value not in filter_value and current_root.item.value != "root" and current_root.state==0:
                        return None
            current_item.append(f"<{current_root.item.value}>")
            for i in range(len(current_root.sons)):
                """染色"""
                if mode.lower() == "remain":
                    if current_root.parent is not None and current_root.parent.state == 1:
                        """当前节点的父节点被保留，则该结点也会被保留"""
                        current_root.state = 1
                    if current_root.item.value in filter_value:
                        """如果当前节点是需要被保留的，则设为1"""
                        current_root.state = 1
                        current_root.sons[i].state = 1
                    if current_root.state == 1:
                        """如果当前节点是被保留的，则儿子也会被保留"""
                        current_root.sons[i].state = 1
                    if current_root.sons[i].item.value in filter_value:
                        current_root.sons[i].state = 1
                item = self.build_xml(current_item, current_root.sons[i], filter_value, mode)
                if isinstance(item, str):
                    current_item.append(f"{item}")
            current_item.append(f"</{current_root.item.value}>")

def extract_tag_names(text: str, sort:bool=True)->List[Tuple[str, int, int]]:
    # 定义正则表达式模式
    pattern = r'<([^<>]+)>'

    # 使用正则表达式查找匹配项
    matches = re.findall(pattern, text)
    # 匹配每个项目的开始位置
    pos = []
    start = 0
    for item in matches:
        pos.append(
            text[start:].find(item)+start
        )
        start = text[start:].find(item)+start + len(item)

    # 剔除结束的，只保留开始的
    stack_item = []
    stack_pos = []
    answer = []
    for idx, item in enumerate(matches):
        if item[0] != '/':
            stack_item.append(item)
            stack_pos.append(pos[idx])
        else:
            end_pos = pos[idx]
            """说明为结束的，需要判断一下是否有"""
            if item[1:] in stack_item:
                while stack_item[-1] != item[1:]:
                    stack_item.pop()
                    stack_pos.pop()
                # 值，开始位置（不含<），结束位置（不含<）
                answer.append((stack_item.pop(), stack_pos.pop(), end_pos))
    if sort:
        return sorted(answer, key=lambda x: x[1])
    return answer

def construct_tree(text, add_root_label:bool=True):
    if add_root_label:
        print("root label is added!")
        text = f"<root>\n{text}\n</root>"
    data = extract_tag_names(text)
    tree = Tree(Item(*data[0]), text)
    nodes_list = []
    for d in data[1:]:
        new_node = TreeNode(
            Item(*d)
        )
        nodes_list.append(new_node)
    for i in range(len(nodes_list)):
        tree.insert(
            new_node=nodes_list[i],
            current_node=tree.root
        )
    return tree

def tree2dict(tree:Tree, filter:list=None, mode="filter"):
    answer = {}
    tree.reset_state(0)
    tree.build_dict(answer, tree.root, filter, mode)
    return answer

def tree2xml(tree, filter:list=None, mode="filter"):
    answer = []
    tree.reset_state(0)
    tree.build_xml(answer, tree.root, filter, mode)
    return "\n".join(answer)

