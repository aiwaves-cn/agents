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
import csv
import random
import openai
import json
import pandas
import numpy as np
import requests
import torch
from tqdm import tqdm
from text2vec import semantic_search
import re
import datetime
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import string
import random
import os
import time


API_KEY = os.environ["API_KEY"]
PROXY = os.environ["PROXY"]
MAX_CHAT_HISTORY = eval(
    os.environ["MAX_CHAT_HISTORY"]) if "MAX_CHAT_HISTORY" in os.environ else 10
MIN_CATEGORY_SIM = eval(os.environ["MIN_CATEGORY_SIM"]
                        ) if "MIN_CATEGORY_SIM" in os.environ else 0.7
FETSIZE = eval(os.environ["FETSIZE"]) if "FETSIZE" in os.environ else 5
TOP_K = eval(os.environ["TOP_K"]) if "TOP_K" in os.environ else 5


embedding_model = SentenceTransformer(
            "BAAI/bge-large-zh", device=torch.device("cpu")
        )

def get_embedding(sentence):
    embed = embedding_model.encode(sentence,convert_to_tensor=True)
    if len(embed.shape)==1:
        embed = embed.unsqueeze(0)
    return embed


def get_code():
    return "".join(random.sample(string.ascii_letters + string.digits, 8))


def get_content_between_a_b(start_tag, end_tag, text):
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
            extracted_text += text[start_index +
                                   len(start_tag):end_index] + " "
            start_index = text.find(start_tag, end_index + len(end_tag))
        else:
            break

    return extracted_text.strip()


def extract(text, type):
    """extract the content between <type></type>

    Args:
        text (str): complete sentence
        type (str): tag

    Returns:
        str: content between <type></type>
    """
    target_str = get_content_between_a_b(f"<{type}>", f"</{type}>", text)
    return target_str


def save_logs(log_path, messages, response):
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_path = log_path if log_path else "logs"
    log = {}
    log["input"] = messages
    log["output"] = response
    os.makedirs(log_path, exist_ok=True)
    log_file = os.path.join(
        log_path,
        datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S") + ".json")
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def get_stream(response, log_path, messages):
    ans = ""
    for res in response:
        if res:
            r = (res.choices[0]["delta"].get("content")
                 if res.choices[0]["delta"].get("content") else "")
            ans += r
            yield r
    save_logs(log_path, messages, ans)
    


def get_response(chat_history,
                 system_prompt,
                 last_prompt=None,
                 stream=True,
                 model="gpt-3.5-turbo-16k-0613",
                 functions=None,
                 function_call="auto",
                 temperature=0,
                 WAIT_TIME=20,
                 **kwargs):
    openai.api_key = API_KEY
    openai.proxy = PROXY
    active_mode = kwargs["active_mode"] if "active_mode" in kwargs else False
    summary = kwargs["summary"] if "summary" in kwargs else None
    key_history = kwargs["key_history"] if "key_history" in kwargs else None
    key_his = "Relevant historical chat records are as follows <history>\n{\n"
    if key_history:
        for his in key_history:
            key_his += his["content"] + "\n"
        key_his +="}\n</history>\n"
    
    
    messages = [{
        "role": "system",
        "content": system_prompt
    }] if system_prompt else []

    if active_mode:
        system_prompt = system_prompt + "Please keep your reply as concise as possible"

    if chat_history:
        if len(chat_history) > 2 * MAX_CHAT_HISTORY:
            chat_history = chat_history[-2 * MAX_CHAT_HISTORY:]
        messages += chat_history

    if last_prompt or summary or key_history:
        last_prompt = last_prompt if last_prompt else ""
        last_prompt = f"The information you know is:\n<summary>\n{summary}\n</summary>" + last_prompt if summary else last_prompt
        last_prompt = key_his + last_prompt if key_his else last_prompt
        if active_mode:
            last_prompt = last_prompt + "Please keep your reply as concise as possible"
        # messages += [{"role": "system", "content": f"{last_prompt}"}]
        messages += [{"role": "user", "content": f"{last_prompt}"}]
    

    while True:
        try:
            if functions:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    functions=functions,
                    function_call=function_call,
                    temperature=temperature,
                )
            else:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    stream=stream)
            break
        except Exception as e:
            print(e)
            if "maximum context length is" in str(e):
                assert False, "exceed max length"
                break
            else:
                print("Please wait {WAIT_TIME} seconds and resend later ...")
                time.sleep(WAIT_TIME)

    log_path = kwargs["log_path"] if "log_path" in kwargs else "logs"
    if functions:
        save_logs(log_path, messages, response)
        return response.choices[0].message
    elif stream:
        return get_stream(response, log_path, messages)
    else:
        save_logs(log_path, messages, response)
        return response.choices[0].message["content"]


def semantic_search_word2vec(query_embedding, kb_embeddings, top_k):
    return semantic_search(query_embedding, kb_embeddings, top_k=top_k)


def cut_sent(para):
    para = re.sub("([。！？\?])([^”’])", r"\1\n\2", para)
    para = re.sub("(\.{6})([^”’])", r"\1\n\2", para)
    para = re.sub("(\…{2})([^”’])", r"\1\n\2", para)
    para = re.sub("([。！？\?][”’])([^，。！？\?])", r"\1\n\2", para)
    para = para.rstrip()
    pieces = [i for i in para.split("\n") if i]
    batch_size = 3
    chucks = [
        " ".join(pieces[i:i + batch_size])
        for i in range(0, len(pieces), batch_size)
    ]
    return chucks


def process_document(file_path):
    """
    Save QA_csv to json.
    Args:
        model: LLM to generate embeddings
        qa_dict: A dict contains Q&A
        save_path: where to save the json file.
    Json format:
        Dict[num,Dict[q:str,a:str,chunk:str,emb:List[float]]
    """
    final_dict = {}
    count = 0
    if file_path.endswith(".csv"):
        dataset = pandas.read_csv(file_path)
        questions = dataset["question"]
        answers = dataset["answer"]
        # embedding q+chunk
        for q, a in zip(questions, answers):
            for text in cut_sent(a):
                temp_dict = {}
                temp_dict["q"] = q
                temp_dict["a"] = a
                temp_dict["chunk"] = text
                temp_dict["emb"] = get_embedding(q + text).tolist()
                final_dict[count] = temp_dict
                count += 1
        # embedding chunk
        for q, a in zip(questions, answers):
            for text in cut_sent(a):
                temp_dict = {}
                temp_dict["q"] = q
                temp_dict["a"] = a
                temp_dict["chunk"] = text
                temp_dict["emb"] = get_embedding(text).tolist()
                final_dict[count] = temp_dict
                count += 1
        # embedding q
        for q, a in zip(questions, answers):
            temp_dict = {}
            temp_dict["q"] = q
            temp_dict["a"] = a
            temp_dict["chunk"] = a
            temp_dict["emb"] = get_embedding(q).tolist()
            final_dict[count] = temp_dict
            count += 1
        # embedding q+a
        for q, a in zip(questions, answers):
            temp_dict = {}
            temp_dict["q"] = q
            temp_dict["a"] = a
            temp_dict["chunk"] = a
            temp_dict["emb"] = get_embedding(q + a).tolist()
            final_dict[count] = temp_dict
            count += 1
        # embedding a
        for q, a in zip(questions, answers):
            temp_dict = {}
            temp_dict["q"] = q
            temp_dict["a"] = a
            temp_dict["chunk"] = a
            temp_dict["emb"] = get_embedding(a).tolist()
            final_dict[count] = temp_dict
            count += 1
        print(f"finish updating {len(final_dict)} data!")
        os.makedirs("temp_database", exist_ok=True)
        save_path = os.path.join(
            "temp_database/",
            file_path.split("/")[-1].replace("." + file_path.split(".")[1],
                                             ".json"),
        )
        print(save_path)
        with open(save_path, "w") as f:
            json.dump(final_dict, f, ensure_ascii=False, indent=2)
        return {"knowledge_base": save_path, "type": "QA"}
    else:
        loader = UnstructuredFileLoader(file_path)
        docs = loader.load()
        text_spiltter = CharacterTextSplitter(chunk_size=200,
                                              chunk_overlap=100)
        docs = text_spiltter.split_text(docs[0].page_content)
        os.makedirs("temp_database", exist_ok=True)
        save_path = os.path.join(
            "temp_database/",
            file_path.replace("." + file_path.split(".")[1], ".json"))
        final_dict = {}
        count = 0
        for c in tqdm(docs):
            temp_dict = {}
            temp_dict["chunk"] = c
            temp_dict["emb"] = get_embedding(c).tolist()
            final_dict[count] = temp_dict
            count += 1
        print(f"finish updating {len(final_dict)} data!")
        with open(save_path, "w") as f:
            json.dump(final_dict, f, ensure_ascii=False, indent=2)
        return {"knowledge_base": save_path, "type": "UnstructuredFile"}


def load_knowledge_base_qa(path):
    """
    Load json format knowledge base.
    """
    print("path", path)
    current_path = os.path.abspath(__file__)
    current_path = os.path.dirname(current_path)
    path = os.path.join(current_path, path)
    with open(path, "r") as f:
        data = json.load(f)
    embeddings = []
    questions = []
    answers = []
    chunks = []
    for idx in range(len(data.keys())):
        embeddings.append(data[str(idx)]["emb"])
        questions.append(data[str(idx)]["q"])
        answers.append(data[str(idx)]["a"])
        chunks.append(data[str(idx)]["chunk"])
    embeddings = np.array(embeddings, dtype=np.float32)
    return embeddings, questions, answers, chunks


def load_knowledge_base_UnstructuredFile(path):
    """
    Load json format knowledge base.
    """
    with open(path, "r") as f:
        data = json.load(f)
    embeddings = []
    chunks = []
    for idx in range(len(data.keys())):
        embeddings.append(data[str(idx)]["emb"])
        chunks.append(data[str(idx)]["chunk"])
    embeddings = np.array(embeddings, dtype=np.float32)
    return embeddings, chunks


def cos_sim(a: torch.Tensor, b: torch.Tensor):
    """
    Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
    :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
    """
    if not isinstance(a, torch.Tensor):
        a = torch.tensor(a)

    if not isinstance(b, torch.Tensor):
        b = torch.tensor(b)

    if len(a.shape) == 1:
        a = a.unsqueeze(0)

    if len(b.shape) == 1:
        b = b.unsqueeze(0)

    a_norm = torch.nn.functional.normalize(a, p=2, dim=1)
    b_norm = torch.nn.functional.normalize(b, p=2, dim=1)
    return torch.mm(a_norm, b_norm.transpose(0, 1))


def matching_a_b(a, b, requirements=None):
    a_embedder = get_embedding(a)
    # 获取embedder
    b_embeder = get_embedding(b)
    sim_scores = cos_sim(a_embedder, b_embeder)[0]
    return sim_scores


def matching_category(inputtext,
                      forest_name,
                      requirements=None,
                      cat_embedder=None,
                      top_k=3):
    """
    Args:
        inputtext: the category name to be matched
        forest: search tree
        top_k: the default three highest scoring results
    Return：
        topk matching_result. List[List] [[top1_name,top2_name,top3_name],[top1_score,top2_score,top3_score]]
    """

    sim_scores = torch.zeros([100])
    if inputtext:
        input_embeder = get_embedding(inputtext)
        sim_scores = cos_sim(input_embeder, cat_embedder)[0]

    if requirements:
        requirements = requirements.split(" ")
        requirements_embedder = get_embedding(requirements)
        req_scores = cos_sim(requirements_embedder, cat_embedder)
        req_scores = torch.mean(req_scores, dim=0)
        total_scores = req_scores
    else:
        total_scores = sim_scores

    top_k_cat = torch.topk(total_scores, k=top_k)
    top_k_score, top_k_idx = top_k_cat[0], top_k_cat[1]
    top_k_name = [forest_name[top_k_idx[i]] for i in range(0, top_k)]

    return [top_k_name, top_k_score.tolist(), top_k_idx]


class Leaf_Node:

    def __init__(self, val) -> None:
        self.val = val
        self.son = []

    def add(self, son):
        self.son.append(son)


def create_forest(csv_file):
    json_list = []
    node_dict = {}
    node_id = 0
    node_list = []
    name_list = []

    with open(csv_file, "r") as file:
        csv_data = csv.reader(file)
        headers = next(csv_data)  

        for row in csv_data:
            json_data = {}
            for i in range(len(headers)):
                json_data[headers[i]] = row[i]
            json_list.append(json_data)

    for d in json_list:
        cat_root_name = d["cat_root_name"]
        cat_leaf_name = d["cat_leaf_name"]
        father_names = cat_root_name.split("/")
        son_names = cat_leaf_name.split("/")

        for father_name in father_names:
            if father_name not in list(node_dict.keys()):
                father = Leaf_Node(father_name)
                node_list.append(father)
                name_list.append(father_name)
                node_dict[father_name] = node_id
                node_id += 1
            else:
                father = node_list[node_dict[father_name]]
            for son_name in son_names:
                if son_name not in list(node_dict.keys()):
                    son = Leaf_Node(son_name)
                    node_list.append(son)
                    node_dict[son_name] = node_id
                    name_list.append(son_name)
                    node_id += 1
                else:
                    son = node_list[node_dict[son_name]]
                if son not in father.son:
                    father.add(son)

    return node_list, name_list


def sample_with_order_preserved(lst, num):
    """Randomly sample from the list while maintaining the original order."""
    indices = list(range(len(lst)))
    sampled_indices = random.sample(indices, num)
    sampled_indices.sort()  # 保持原顺序
    return [lst[i] for i in sampled_indices]


def limit_values(data, max_values):
    """Reduce each key-value list in the dictionary to the specified size, keeping the order of the original list unchanged."""
    for key, values in data.items():
        if len(values) > max_values:
            data[key] = sample_with_order_preserved(values, max_values)
    return data


def limit_keys(data, max_keys):
    """Reduce the dictionary to the specified number of keys."""
    keys = list(data.keys())
    if len(keys) > max_keys:
        keys = sample_with_order_preserved(keys, max_keys)
        data = {key: data[key] for key in keys}
    return data


def flatten_dict(nested_dict):
    """
    flatten the dictionary
    """
    flattened_dict = {}
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            flattened_subdict = flatten_dict(value)
            flattened_dict.update(flattened_subdict)
        else:
            flattened_dict[key] = value
    return flattened_dict


def merge_list(list1, list2):
    for l in list2:
        if l not in list1:
            list1.append(l)
    return list1


def Search_Engines(req):
    new_dict = {"keyword": req, "catLeafName": "", "fetchSize": FETSIZE}
    res = requests.post(
        url="https://k8s-api-dev.fenxianglife.com/dev1/fenxiang-ai/search/item",
        json=new_dict,
    )
    user_dict = json.loads(res.text)
    if "data" in user_dict.keys():
        request_items = user_dict["data"]["items"]  # 查询到的商品信息JSON
        top_category = user_dict["data"]["topCategories"]
        return request_items, top_category
    else:
        return []


def search_with_api(requirements, categery):
    request_items = []
    all_req_list = requirements.split(" ")  
    count = 0  

    while len(request_items) < FETSIZE and len(all_req_list) > 0:
        if count: 
            all_req_list.pop(0)  
        all_req = (" ").join(all_req_list)  
        if categery not in all_req_list:
            all_req = all_req + " " + categery
        now_request_items, top_category = Search_Engines(all_req)  
        request_items = merge_list(request_items, now_request_items)
        count += 1
    new_top = []
    for category in top_category:
        if "其它" in category or "其它" in category:
            continue
        else:
            new_top.append(category)
    if len(request_items) > FETSIZE:
        request_items = request_items[:FETSIZE]
    return request_items, new_top


def get_memory_from_long_short(agent_dict, keywords):
    if keywords in agent_dict["long_memory"]:
        return agent_dict["long_memory"][keywords]

    elif keywords in agent_dict["short_memory"]:
        return agent_dict["short_memory"][keywords]

    else:
        return ""


def get_key_history(query,history,embeddings):
    key_history = []
    query = query["content"]
    query_embedding = get_embedding(query)
    hits = semantic_search(query_embedding, embeddings, top_k=min(TOP_K,embeddings.shape[0]))
    hits = hits[0]
    for hit in hits:
        matching_idx = hit["corpus_id"]
        key_history.append(history[matching_idx])
    return key_history


    