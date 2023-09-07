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


# BAAI/bge-large-zh
# intfloat/multilingual-e5-large

embed_model_name = os.environ["Embed_Model"] if "Embed_Model" in os.environ else "BAAI/bge-large-zh"

embedding_model = SentenceTransformer(
            "intfloat/multilingual-e5-large", device=torch.device("cpu")
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

def count_files_in_directory(directory):
    # 获取指定目录下的文件数目
    file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    return file_count

def delete_oldest_files(directory, num_to_keep):
    # 获取目录下文件列表，并按修改时间排序
    files = [(f, os.path.getmtime(os.path.join(directory, f))) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # 删除最开始的 num_to_keep 个文件
    for i in range(min(num_to_keep, len(files))):
        file_to_delete = os.path.join(directory, files[i][0])
        os.remove(file_to_delete)

def delete_files_if_exceed_threshold(directory, threshold, num_to_keep):
    # 获取文件数目并进行处理
    file_count = count_files_in_directory(directory)
    if file_count > threshold:
        delete_count = file_count - num_to_keep
        delete_oldest_files(directory, delete_count)

def save_logs(log_path, messages, response):
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    delete_files_if_exceed_threshold(log_path, 20, 10)
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
    embeddings = torch.from_numpy(embeddings).squeeze()
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
    embeddings = torch.from_numpy(embeddings).squeeze()
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
    FETSIZE = eval(os.environ["FETSIZE"]) if "FETSIZE" in os.environ else 5

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
    
    FETSIZE = eval(os.environ["FETSIZE"]) if "FETSIZE" in os.environ else 5

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



def get_key_history(query,history,embeddings):
    """
    Retrieve a list of key history entries based on a query using semantic search.

    Args:
        query (object): The input query for which key history is to be retrieved.
        history (list): A list of historical key entries.
        embeddings (numpy.ndarray): An array of embedding vectors for historical entries.

    Returns:
        list: A list of key history entries most similar to the query.
    """
    TOP_K = eval(os.environ["TOP_K"]) if "TOP_K" in os.environ else 2
    key_history = []
    query = query.content
    query_embedding = get_embedding(query)
    hits = semantic_search(query_embedding, embeddings, top_k=min(TOP_K,embeddings.shape[0]))
    hits = hits[0]
    for hit in hits:
        matching_idx = hit["corpus_id"]
        key_history.append(history[matching_idx])
    return key_history


    