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
        self.sop = sop
        self.root = None
        self.temperature = sop["temperature"] if "temperature" in sop else 0.3
        self.active_mode = sop["active_mode"] if "active_mode" in sop else False
        self.log_path = sop["log_path"] if "log_path" in sop else "logs"
        
        self.shared_memory = {}
        self.nodes = self.init_nodes(sop)
        self.init_relation(sop)

    def init_nodes(self, sop):
        # node_sop: a list of the node
        node_sop = sop["nodes"]
        nodes_dict = {}
        for node in node_sop.values():
            name = node["name"]
            node_type = node["node_type"]
            is_interactive = node["is_interactive"]
            transition_rule = node["transition_rule"]
            agent_states = self.init_states(node["agent_states"])
            config = node["config"]
            now_node = Node(name=name,
                            node_type=node_type,
                            is_interactive= is_interactive,
                            config = config,
                            transition_rule = transition_rule,
                            agent_states = agent_states)
            nodes_dict[name] = now_node
            if "root" in node.keys() and node["root"]:
                self.root = now_node
        return nodes_dict

    def init_states(self, agent_states_dict: dict):
        agent_states = {}
        for key, value in agent_states_dict.items():
            component_dict = {}
            for component , component_args in value.items():
                if component:
                    if component == "style":
                        component_dict["style"] = StyleComponent(
                            component_args["agent"], component_args["style"])
                    elif component == "task":
                        component_dict["task"] = TaskComponent(component_args["task"])
                    elif component == "rule":
                        component_dict["rule"] = RuleComponent(component_args["rule"])
                    elif component == "demonstration":
                        component_dict["demonstration"] = DemonstrationComponent(
                            component_args["demonstration"])
                    elif component == "output":
                        component_dict["output"] = OutputComponent(component_args["output"])
                    elif component == "cot":
                        component_dict["cot"] = CoTComponent(component_args["demonstration"])                    
                    elif component == "Information_KnowledgeComponent":
                        component_dict[
                            "knowledge"] = Information_KnowledgeComponent()
                    elif component == "kb":
                        component_dict["tool"] = KnowledgeBaseComponent(
                            component_args["knowledge_base"])
            agent_states[key] = component_dict
        return agent_states

    def init_relation(self, sop):
        relation = sop["relation"]
        for key, value in relation.items():
            for keyword, next_node in value.items():
                self.nodes[key].next_nodes[keyword] = self.nodes[next_node]


class Node():

    def __init__(self,
                 name: str = None,
                 agent_states:dict = None,
                 is_interactive=False,
                 config:list = None,
                 transition_rule:str = None):
        
        self.next_nodes = {}
        self.agent_states = agent_states
        self.is_interactive = is_interactive
        self.name = name
        self.config = config
        self.transition_rule = transition_rule
    
    def get_state(self,role,args_dict):
        system_prompt,last_prompt = self.compile(role,args_dict)
        current_role_state = f"目前的角色为：{role}，它的system_prompt为{system_prompt},last_prompt为{last_prompt}"
        return current_role_state
    
    
    def compile(self,role,args_dict:dict):
        components = self.agent_states[role]
        system_prompt = ""
        last_prompt = ""
        res_dict = {}
        for component_name in self.config:
            component = components[component_name]
            if isinstance(component,OutputComponent):
                last_prompt = last_prompt + "\n" +  component.get_prompt(args_dict)
            elif isinstance(component,PromptComponent):
                system_prompt = system_prompt + "\n" + component.get_prompt(args_dict)
            elif isinstance(component,ToolComponent):
                response = component.func(args_dict)
                args_dict.update(response)
                res_dict.update(response)
        return system_prompt,last_prompt,res_dict



# the base of the toolnode
class ToolNode:

    def __init__(self, name="", done=False):
        self.next_nodes = {}
        self.name = name
        self.done = done

    @abstractmethod
    def func(self, args_dict):
        pass


class StaticNode(ToolNode):

    def __init__(self, name="", output="", done=False):
        super().__init__(name, done)
        self.output = output

    def func(self, args_dict):
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

    def func(self, args_dict):
        """
        return the memory of information and determine the next node
        """
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

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

    def func(self, args_dict):
        """
        return the recommend of the search shop
        """
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

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

    def func(self, args_dict):
        """
        return the recommend of the search shop
        """
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

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

    def func(self, args_dict):
        """
        return the recommend of the search shop
        """
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

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
                chat_history,
                prompt,
                None,
                args_dict=args_dict,
                temperature=args_dict["temperature"])
            all = ""
            for chat_answer in chat_answer_generator:
                all += chat_answer
                yield chat_answer
            long_memory["chat_history"].append({
                "role": "assistant",
                "content": all
            })

        elif not request_items:
            chat_answer = "\\n抱歉呢，亲亲，我们目前没有搜索到您需要的商品，您可以继续提出需求方便我们进行搜寻。"
            long_memory["chat_history"].append({
                "role": "assistant",
                "content": chat_answer
            })
            outputdict["response"] = chat_answer
            yield outputdict


class StaticNode(ToolNode):

    def __init__(self, name="", output="", done=False):
        super().__init__(name, done)
        self.output = output

    def func(self, args_dict):
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

        outputdict = {"response": self.output, "next_node_id": "0"}
        long_memory["chat_history"].append({
            "role": "assistant",
            "content": self.output
        })
        yield outputdict


class KnowledgeResponseNode(ToolNode):

    def __init__(self,
                 knowledge_base,
                 system_prompt,
                 last_prompt=None,
                 active_prompt = None,
                 name="",
                 top_k=2,
                 type="QA",
                 done=False) -> None:
        super().__init__(name, done)
        if last_prompt != None:
            self.last_prompt = last_prompt + active_prompt if active_prompt else last_prompt
        else:
            self.last_prompt = active_prompt if active_prompt else last_prompt
        self.system_prompt = system_prompt
        
        self.top_k = top_k
        self.embedding_model = SentenceModel(
            'shibing624/text2vec-base-chinese', device="cpu")
        self.type = type
        if self.type == "QA":
            self.kb_embeddings, self.kb_questions, self.kb_answers, self.kb_chunks = load_knowledge_base_qa(
                knowledge_base)
        else:
            self.kb_embeddings, self.kb_chunks = load_knowledge_base_UnstructuredFile(
                knowledge_base)
        self.functions = [{
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
        }]

    def get_knowledge(self, query):
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
                return "提供的相关内容是： “" + knowledge + "”如果能完全匹配对应的问题，你就完全输出对应的答案，如果只是有参考的内容，你可以根据以上内容进行回答。"
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
                return "相关的内容是： “" + knowledge + "”"

    def func(self, args_dict):
        long_memory = args_dict["long_memory"] if args_dict[
            "long_memory"] else {}
        temp_memory = args_dict["temp_memory"] if args_dict[
            "temp_memory"] else {}

        chat_history = get_keyword_in_long_temp("chat_history", long_memory,
                                                temp_memory).copy()
        outputdict = {"response": "", "next_node_id": "0"}
        yield outputdict

        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        fuction_to_call = self.get_knowledge
        function_response = fuction_to_call(query=chat_history[-1]["content"])
        # Step 4: send the info on the function call and function response to GPT
        chat_history.append({
            "role": "function",
            "name": "get_knowledge_response",
            "content": function_response,
        })  # extend conversation with function response

        second_response = get_gpt_response_rule_stream(
            chat_history,
            system_prompt=self.system_prompt,
            last_prompt=self.last_prompt,
            args_dict=args_dict,
            temperature=args_dict["temperature"])
        all = ""
        for res in second_response:
            all += res
            yield res
        long_memory["chat_history"].append({
            "role": "assistant",
            "content": all
        })