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
"""standard operation procedure of an LLM Autonomous agent"""
from abc import abstractmethod
import json
from utils import *
from component import *


class SOP:
    """
    input:the json of the sop
    output: a sop graph
    """

    def __init__(self, json_path):
        with open(json_path) as f:
            sop = json.load(f)
        self.root = None
        self.judge_idle_node = None
        self.idle_response_node = None

        self.nodes = {}
        if "temperature" in sop:
            self.temperature = sop["temperature"]
            
        if "gpt_nodes" in sop:
            gpt_nodes = self.init_gpt_nodes(sop)
            self.nodes.update(gpt_nodes)
        if "tool_nodes" in sop:
            tool_nodes = self.init_tool_nodes(sop)
            self.nodes.update(tool_nodes)
        if "relation" in sop:
            self.init_relation(sop)

    def init_gpt_nodes(self, sop):
        # node_sop: a list of the node
        node_sop = sop["gpt_nodes"]
        nodes_dict = {}
        for node in node_sop:
            node = node_sop[node]
            name = node["name"]
            node_type = node["node_type"]
            extract_word = node["extract_word"]
            done = node["done"]
            components_dict = self.init_components(node["components"])

            now_node = GPTNode(name=name,
                               node_type=node_type,
                               extract_words=extract_word,
                               done=done,
                               components=components_dict)
            nodes_dict[name] = now_node
            if "root" in node.keys() and node["root"]:
                self.root = now_node
            if "judge_idle_node" in node.keys() and node["judge_idle_node"]:
                self.judge_idle_node = now_node
            if "idle_response_node" in node.keys(
            ) and node["idle_response_node"]:
                self.idle_response_node = now_node
        return nodes_dict

    def init_tool_nodes(self, sop):
        # node_sop:a list of the node
        node_sop = sop["tool_nodes"]
        nodes_dict = {}
        for node in node_sop:
            node = node_sop[node]
            name = node["name"]
            done = node["done"]
            tool_name = node["tool_name"]
            
            if tool_name == "MatchNode":
                now_node = MatchNode(name=name, done=done)
            elif tool_name == "SearchNode":
                now_node = SearchNode(name=name, done=done)
            elif tool_name == "SearchRecomNode":
                now_node = SearchRecomNode(name=name, done=done)
            elif tool_name == "RecomTopNode":
                now_node = RecomTopNode(name=name, done=done)
            elif tool_name == "StaticNode":
                now_node = StaticNode(name=name,
                                      done=done,
                                      output=node["output"])
            elif tool_name == "KnowledgeResponseNode":
                last_prompt = node["last_prompt"] if "last_prompt" in node else None
                system_prompt = node["system_prompt"] if "system_prompt" in node else None
                knowledge_base = node["knowledge_base"] if "knowledge_base" in node else None
                type = node["type"] if "type" in node else None
                now_node = KnowledgeResponseNode(knowledge_base=knowledge_base,system_prompt=system_prompt,last_prompt=last_prompt,name=name,
                                                 type=type,done=done)
            else:
                assert 1==False,"wrong tool node name"
            nodes_dict[name] = now_node

            if "root" in node.keys() and node["root"]:
                self.root = now_node
            if "judge_idle_node" in node.keys() and node["judge_idle_node"]:
                self.judge_idle_node = now_node
            if "idle_response_node" in node.keys(
            ) and node["idle_response_node"]:
                self.idle_response_node = now_node

        return nodes_dict

    def init_components(self, components_dict: dict):
        args_dict = {}
        for key, value in components_dict.items():
            value = components_dict[key]
            if value:
                if key == "style":
                    args_dict["style"] = StyleComponent(
                        value["agent"], value["style"])
                elif key == "task":
                    args_dict["task"] = TaskComponent(value["task"])
                elif key == "rule":
                    args_dict["rule"] = RuleComponent(value["rule"])
                elif key == "demonstration":
                    args_dict["demonstration"] = DemonstrationComponent(
                        value["demonstration"])
                elif key == "tool":
                    args_dict["tool"] = KnowledgeBaseComponent(
                        value["knowledge_base"])
                elif key == "output":
                    args_dict["output"] = OutputComponent(value["output"])
                elif key == "knowledge":
                    if value == "Information_KnowledgeComponent":
                        args_dict[
                            "knowledge"] = Information_KnowledgeComponent()
        return args_dict

    def init_relation(self, sop):
        relation = sop["relation"]

        for key, value in relation.items():
            for keyword, next_node in value.items():
                self.nodes[key].next_nodes[keyword] = self.nodes[next_node]


class GPTNode():

    def __init__(self,
                 name: str = None,
                 node_type: str = None,
                 extract_words=None,
                 done=False,
                 user_input: str = "",
                 components: dict = {}):
        """the simplist node mainly based on gpt:
            input the prompt,output the response.Afterwards, use response for different operations

        Args:
            tool (Tool, optional): _description_. Defaults to None.
            node_type (str, optional): three type (response, extract,judge)  
                                        ---response:return a response
                                        ---extract:return a keyword for memory
                                        ---judge:return the keyword to determine which node for next
            extract_words (str, optional): _description_. Defaults to "".
            next_nodes (dict, optional): _description_. Defaults to {}.
            done (bool, optional):   True:When the program runs to this node, it will be interrupted, allowing the user to input.
            user_input (str, optional): The content you want to agent know. Defaults to "".
            
            components(dict) : Contains the definition of various components
           { 
           "style":{"agent":"" , "style": "" } ,
            *"task"*:{"task":""} , 
            "rule":{"rule":""}, 
            "knowledge" (str): ""
            "demonstration":{"demonstration":[]} , 
            "input":true or false,
            "tool":{tool_name:"",**args} ,
            *"output"*:{"output":""} 
            }
           --style(agent,style) : agent(str):the role of the agent.   style(str):the style of the agent
           --task(task) : task(str):the task of the agent
           --rule(rule) : rule(str):the rule of the agent
           --knowledge(str) : the name of knowledge component
           --demonstration: demenstration(list):the example of answer
           --input : yet have external inputs , always be last input
           --tool(tool_name,**args) : tool_name(str):the name of tool,**args(Dict):the parameters of tool
           --output(output) : output(str):the html wrap of response
        """
        self.prompt = ""
        self.node_type = node_type

        self.next_nodes = {}

        self.components = components
        self.extract_words = extract_words
        self.done = done
        self.name = name

    # get complete prompt
    def get_prompt(self, long_memory={}, temp_memory={}, query=""):
        prompt = ""
        last_prompt = ""
        for value in self.components.values():
            if isinstance(value, KnowledgeBaseComponent):
                value.user_input = query
                prompt = prompt + "\n" + value.get_prompt()
            elif isinstance(value, OutputComponent):
                last_prompt += value.get_prompt()
            elif isinstance(value, Information_KnowledgeComponent):
                prompt = prompt + "\n" + value.get_prompt(
                    long_memory, temp_memory)
            else:
                prompt = prompt + "\n" + value.get_prompt()

        return prompt, last_prompt


# the base of the toolnode
class ToolNode:

    def __init__(self, name="", done=False):
        self.next_nodes = {}
        self.name = name
        self.done = done

    @abstractmethod
    def func(self, long_memory, temp_memory):
        pass


class StaticNode(ToolNode):

    def __init__(self, name="", output="", done=False):
        super().__init__(name, done)
        self.output = output

    def func(self, long_memory, temp_memory):
        outputdict = {"response": self.output, "next_node_id": "0"}
        return outputdict


class MatchNode(ToolNode):

    def __init__(self, name="", done=False):
        super().__init__(name, done)

        # create dateset
        self.information_dataset = []
        self.leaf_name = []
        for toy_path in TOY_INFO_PATH:
            with open(toy_path, encoding='utf-8') as json_file:
                data = json.load(json_file)
            for d in data:
                if "/" in d["cat_leaf_name"]:
                    leaf_names = d["cat_leaf_name"].split("/") + [
                        d["cat_leaf_name"]
                    ]
                else:
                    leaf_names = [d["cat_leaf_name"]]
                for name in leaf_names:
                    self.leaf_name.append(name)
                    new_d = d.copy()
                    new_d["cat_leaf_name"] = name
                    new_d["information"] = flatten_dict(new_d["information"])
                    self.information_dataset.append(new_d)
        self.embedder = SentenceModel('shibing624/text2vec-base-chinese',
                                      device=torch.device("cpu"))
        self.target_embbeding = self.embedder.encode(self.leaf_name,
                                                     convert_to_tensor=True)

    def search_information(self, category, information_dataset):
        """
        Args:
            category (str): Categories that need to be matched in the database
            information_dataset (list): the dateset

        Returns:
            dict: Information on target categories
        """
        knowledge = {}
        for d in information_dataset:
            if category == d["cat_leaf_name"]:
                knowledge = d["information"]
                knowledge = {
                    key: value
                    for key, value in knowledge.items()
                    if (value and key != "相关分类")
                }
                break
        return knowledge

    def func(self, long_memory, temp_memory):
        """
        return the memory of information and determine the next node
        """
        extract_category = get_keyword_in_long_temp("extract_category",
                                                    long_memory, temp_memory)

        outputdict = {"response": "", "next_node_id": "0"}

        topk_result = matching_category(extract_category,
                                        self.leaf_name,
                                        None,
                                        self.target_embbeding,
                                        top_k=3)
        top1_score = topk_result[1][0]
        if top1_score > MIN_CATEGORY_SIM:
            long_memory['category'] = topk_result[0][0]
            information = self.search_information(topk_result[0][0],
                                                  self.information_dataset)
            information = limit_keys(information, 3)
            information = limit_values(information, 2)
            outputdict["next_node_id"] = "1"
            temp_memory["information"] = information
        else:
            temp_memory["possible_category"] = topk_result[0][0]

        yield outputdict


class SearchNode(ToolNode):

    def __init__(self, name="", done=False):
        super().__init__(name, done)

    def func(self, long_memory, temp_memory):
        """
        return the recommend of the search shop
        """
        outputdict = {"response": "", "next_node_id": "0"}
        requirements = get_keyword_in_long_temp("requirements", long_memory,
                                                temp_memory)
        category = get_keyword_in_long_temp("category", long_memory,
                                            temp_memory)
        if category == "":
            category = get_keyword_in_long_temp("extract_category",
                                                long_memory, temp_memory)

        request_items, top_category = search_with_api(requirements, category)
        if category in top_category:
            top_category.remove(category)

        temp_memory["top_category"] = top_category
        long_memory["request_items"] = request_items
        yield outputdict


class SearchRecomNode(ToolNode):

    def __init__(self, name="", done=False):
        super().__init__(name, done)

    def func(self, long_memory, temp_memory):
        """
        return the recommend of the search shop
        """
        outputdict = {"response": "", "next_node_id": "0"}
        request_items = get_keyword_in_long_temp("request_items", long_memory,
                                                 temp_memory)
        chat_answer = ""
        if request_items:
            if len(request_items):
                chat_answer += f"""\\n经过搜索后,给你推荐产品:\\n"""
                for i in range(0, len(request_items)):
                    chat_answer += f"""{str(i+1)}:“{request_items[i]['itemTitle']}\\n"""
        outputdict["response"] = chat_answer
        yield outputdict


class RecomTopNode(ToolNode):

    def __init__(self, name="", done=False):
        super().__init__(name, done)

    def func(self, long_memory, temp_memory):
        """
        return the recommend of the search shop
        """
        outputdict = {"response": "", "next_node_id": "0"}
        top_category = get_keyword_in_long_temp("top_category", long_memory,
                                                temp_memory)
        request_items = get_keyword_in_long_temp("request_items", long_memory,
                                                 temp_memory)
        chat_history = get_keyword_in_long_temp("chat_history", long_memory,
                                                temp_memory)

        if top_category:
            yield outputdict
            import sys
            import os
            current_path = os.path.abspath(__file__)
            current_path = os.path.dirname(current_path)
            sys.path.append(
                os.path.join(current_path,
                             '../../examples/shopping_assistant'))
            from tool_prompt import prompt_cat_recom_top
            prompt = prompt_cat_recom_top(top_category)
            chat_answer_generator = get_gpt_response_rule_stream(
                chat_history, prompt, None)
            all = ""
            for chat_answer in chat_answer_generator:
                all += chat_answer
                yield chat_answer
            long_memory["chat_history"].append({
                "role": "assistant",
                "content": all
            })
            long_memory["idle_history"].append({
                "role": "assistant",
                "content": all
            })

        elif not request_items:
            chat_answer = "\\n抱歉呢，亲亲，我们目前没有搜索到您需要的商品，您可以继续提出需求方便我们进行搜寻。"
            long_memory["chat_history"].append({
                "role": "assistant",
                "content": chat_answer
            })
            long_memory["idle_history"].append({
                "role": "assistant",
                "content": chat_answer
            })
            outputdict["response"] = chat_answer
            yield outputdict


class StaticNode(ToolNode):

    def __init__(self, name="", output="", done=False):
        super().__init__(name, done)
        self.output = output

    def func(self, long_memory, temp_memory):
        outputdict = {"response": self.output, "next_node_id": "0"}
        long_memory["chat_history"].append({
            "role": "assistant",
            "content": self.output
        })
        long_memory["idle_history"].append({
            "role": "assistant",
            "content": self.output
        })
        yield outputdict
        



class KnowledgeResponseNode(ToolNode):
    def __init__(self,knowledge_base,system_prompt,last_prompt = None,name="",top_k=2,type = "QA",done = False) -> None:
        super().__init__(name, done)
        self.last_prompt = last_prompt
        self.system_prompt = system_prompt
        self.top_k = top_k
        self.embedding_model = SentenceModel(
            'shibing624/text2vec-base-chinese', device="cpu")
        self.type = type
        if self.type == "QA":
            self.kb_embeddings, self.kb_questions, self.kb_answers, self.kb_chunks = load_knowledge_base_qa(
                knowledge_base)
        else:
            self.kb_embeddings,self.kb_chunks = load_knowledge_base_UnstructuredFile(
                knowledge_base)
        self.functions = [
        {
            "name": "get_knowledge_response",
            "description": "根据你所知道的知识库知识来回答用户的问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用户当前所提出的问题",
                    },
                },
                "required": ["query"],
            },
        }
    ]
    
    def get_knowledge(self,query):
        knowledge = ""
        query_embedding = self.embedding_model.encode(query)
        hits = semantic_search(query_embedding, self.kb_embeddings, top_k=50)
        hits = hits[0]
        temp = []
        if self.type == "QA":
            for hit in hits:
                matching_idx = hit['corpus_id']
                if self.kb_chunks[matching_idx] in temp:
                    pass
                else:
                    knowledge = knowledge + f'问题：{self.kb_questions[matching_idx]}，答案：{self.kb_chunks[matching_idx]}\n\n'
                    temp.append(self.kb_chunks[matching_idx])
                    if len(temp) == 1:
                        break
            print(hits[0]["score"])
            score = hits[0]["score"]
            if score < 0.5:
                return "没有匹配到相关的知识库"
            else:
                print(knowledge)
                return "相关的内容是： “"+knowledge + "”如果能完全匹配对应的问题，你就完全输出对应的答案，如果只是有参考的内容，你可以根据以上内容进行回答。"
        else:
            for hit in hits:
                matching_idx = hit['corpus_id']
                if self.kb_chunks[matching_idx] in temp:
                    pass
                else:
                    knowledge = knowledge + f'{self.kb_chunks[matching_idx]}\n\n'
                    temp.append(self.kb_chunks[matching_idx])
                    if len(temp) == self.top_k:
                        break
            print(hits[0]["score"])
            score = hits[0]["score"]
            if score < 0.5:
                return "没有匹配到相关的知识库"
            else:
                print(knowledge)
                return "相关的内容是： “"+knowledge+ "”"
    
    def func(self,long_memory, temp_memory):
        chat_history = get_keyword_in_long_temp("chat_history", long_memory,
                                                temp_memory).copy()
        outputdict = {"response": "", "next_node_id": "0"}
        yield outputdict
        
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        fuction_to_call = self.get_knowledge
        function_response = fuction_to_call(
            query=chat_history[-1]["content"]
        )
        # Step 4: send the info on the function call and function response to GPT
        chat_history.append(
            {
                "role": "function",
                "name": "get_knowledge_response",
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = get_gpt_response_rule_stream(chat_history,system_prompt=self.system_prompt,last_prompt=self.last_prompt)
        all = ""
        for res in second_response:
            all += res
            yield res
        long_memory["chat_history"].append({
            "role": "assistant",
            "content": all
        })
        long_memory["idle_history"].append({
            "role": "assistant",
            "content": all
        })