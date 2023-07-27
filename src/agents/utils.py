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
import numpy as np
import requests
import torch
import tqdm
from text2vec import SentenceModel, semantic_search
MAX_CHAT_HISTORY = 5
API_KEY = "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"
PROXY = 'http://127.0.0.1:7000'
FETSIZE = 5

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
                          last_prompt = None,
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
    if last_prompt:
        messages += [{"role": "user", "content": f"{last_prompt}"}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,  
    )

    return response.choices[0].message["content"]


def get_gpt_response_rule_stream(ch_dict,
                          system_prompt,
                          last_prompt = None,
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
    if last_prompt:
        messages += [{"role": "user", "content": f"{last_prompt}"}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        stream = True 
    )
    for res in response:
        if res:
            print(res['choices'][0]['delta'].get('content'),end = "")
            yield json.dumps(res['choices'][0]['delta'].get('content'),ensure_ascii=False) + "\n"
            
def load_knowledge_base_chunk(path):
    """
    Load json format knowledge base.
    """
    with open(path, 'r') as f:
        data = json.load(f)
    embeddings = []
    questions = []
    answers =[]
    chunks = []
    for idx in range(len(data.keys())):
        embeddings.append(data[str(idx)]['emb'])
        questions.append(data[str(idx)]['q'])
        answers.append(data[str(idx)]['a'])
        chunks.append(data[str(idx)]['chunk'])
    embeddings = np.array(embeddings,dtype=np.float32)
    return embeddings, chunks



def encode_word2vec(sentence):
    # embedding_model = SentenceModel('GanymedeNil/text2vec-large-chinese',device="cpu")
    return embedding_model.encode(sentence)



def semantic_search_word2vec(query_embedding, kb_embeddings,top_k):
    return semantic_search(query_embedding,kb_embeddings,top_k= top_k)



def save_qadict(questions,answers,save_path):
    """
    Save QA_dict to json.
    Args:
        model: LLM to generate embeddings
        qa_dict: A dict contains Q&A
        save_path: where to save the json file.
    Json format:
        Dict[num,Dict[q:str,a:str,chunk:str,emb:List[float]]
    """
    final_dict = {}
    count = 0
    for q,a in tqdm(zip(questions,answers)):
        temp_dict = {}
        temp_dict['q'] = q
        temp_dict['a'] = a
        temp_dict['chunk'] = a
        temp_dict['emb'] = encode_word2vec(q).tolist()
        final_dict[count] = temp_dict
        count+=1
    print("len:",len(final_dict))
    with open(save_path, 'w') as f:
        json.dump(final_dict, f, ensure_ascii=False,indent=2)



def load_knowledge_base(path):
    """
    Load json format knowledge base.
    """
    with open(path, 'r') as f:
        data = json.load(f)
    embeddings = []
    questions = []
    answers =[]
    chunks = []
    for idx in range(len(data.keys())):
        embeddings.append(data[str(idx)]['emb'])
        questions.append(data[str(idx)]['q'])
        answers.append(data[str(idx)]['a'])
        chunks.append(data[str(idx)]['chunk'])
    embeddings = np.array(embeddings,dtype=np.float32)
    return embeddings, questions,answers,chunks



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

def matching_a_b(a, b, requirements= None):
    """
    Args:
        inputtext: 待匹配的类目名称
        json_file_path: 类目表路径
        top_k:默认三个最高得分的结果
    Return：
        topk matching_result. List[List] [[top1_name,top2_name,top3_name],[top1_score,top2_score,top3_score]]
    """
    #读取
    embedder  = SentenceModel('shibing624/text2vec-base-chinese',device = torch.device("cpu"))
    a_embedder = embedder.encode(a, convert_to_tensor=True)
    #获取embedder
    b_embeder = embedder.encode(b, convert_to_tensor=True)
    sim_scores = cos_sim(a_embedder, b_embeder)[0]
    return sim_scores

def matching_category(inputtext,forest_name, requirements= None, cat_embedder=None,top_k=3):
    """
    Args:
        inputtext: 待匹配的类目名称
        forest: 搜索树
        top_k:默认三个最高得分的结果
    Return：
        topk matching_result. List[List] [[top1_name,top2_name,top3_name],[top1_score,top2_score,top3_score]]
    """
    #读取
    embedder  = SentenceModel('shibing624/text2vec-base-chinese',device = torch.device("cpu"))
    #获取embedder
    sim_scores = torch.zeros([100])
    if inputtext:
        input_embeder = embedder.encode(inputtext, convert_to_tensor=True)
        sim_scores = cos_sim(input_embeder, cat_embedder)[0]

    #有需求匹配需求，没需求匹配类目
    if requirements:
        requirements = requirements.split(" ")
        requirements_embedder = embedder.encode(requirements, convert_to_tensor=True)
        req_scores = cos_sim(requirements_embedder, cat_embedder)
        req_scores = torch.mean(req_scores, dim=0)
        # total_scores = req_scores*0.8 + sim_scores*0.2
        total_scores = req_scores
    else:
        total_scores = sim_scores
        
    top_k_cat = torch.topk(total_scores, k=top_k)
    top_k_score,top_k_idx = top_k_cat[0],top_k_cat[1]
    top_k_name = [forest_name[top_k_idx[i]] for i in range(0,top_k)]

    return [top_k_name,top_k_score.tolist(),top_k_idx]


class Leaf_Node:
    def __init__(self,val) -> None:
        self.val = val
        self.son = []
    
    def add(self,son):
        self.son.append(son)
    
        
def create_forest(csv_file):
    # 储存所有csv关系
    json_list = []
    # 记录节点是否出现
    node_dict = {}
    # 记录当前id
    node_id = 0
    # 存储所有节点
    node_list = []
    name_list = []
    
    # 将csv里所有关系存进json_list
    with open(csv_file, 'r') as file:
        csv_data = csv.reader(file)
        headers = next(csv_data)  # 获取标题行

        for row in csv_data:
            json_data = {}
            for i in range(len(headers)):
                json_data[headers[i]] = row[i]
            json_list.append(json_data)
    
    # 将json_list 转化为node_list
    for d in json_list:
        # 读取父类跟子类的名字
        cat_root_name = d['cat_root_name']
        cat_leaf_name = d['cat_leaf_name']
        father_names = cat_root_name.split("/")
        son_names = cat_leaf_name.split("/")
        
        for father_name in father_names:
            if father_name not in list(node_dict.keys()):
                father = Leaf_Node(father_name)
                node_list.append(father)
                name_list.append(father_name)
                node_dict[father_name] = node_id
                node_id+=1
            else:
                father = node_list[node_dict[father_name]]
            for son_name in son_names:
                if son_name not in list(node_dict.keys()):
                    son = Leaf_Node(son_name)
                    node_list.append(son)
                    node_dict[son_name] = node_id
                    name_list.append(son_name)
                    node_id +=1
                else:
                    son = node_list[node_dict[son_name]]
                if son not in father.son:
                    father.add(son)
                
        
        
    return node_list,name_list


def sample_with_order_preserved(lst, num):
    """在保持原顺序的情况下从列表中随机抽样。"""
    indices = list(range(len(lst)))
    sampled_indices = random.sample(indices, num)
    sampled_indices.sort()  # 保持原顺序
    return [lst[i] for i in sampled_indices]


def limit_values(data, max_values):
    """将字典中的每个键值列表缩减至指定大小，保持原列表中的顺序不变。"""
    for key, values in data.items():
        if len(values) > max_values:
            # 使用带顺序的随机抽样方法限制列表长度
            data[key] = sample_with_order_preserved(values, max_values)
    return data

def limit_keys(data, max_keys):
    """将字典缩减至指定的键数。"""
    keys = list(data.keys())
    if len(keys) > max_keys:
        # 使用带顺序的随机抽样方法限制键的数量
        keys = sample_with_order_preserved(keys, max_keys)
        data = {key: data[key] for key in keys}
    return data


def flatten_dict(nested_dict):
    """
    将字典平坦
    """
    flattened_dict = {}
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            flattened_subdict = flatten_dict(value)
            flattened_dict.update(flattened_subdict)
        else:
            flattened_dict[key] = value
    return flattened_dict

def merge_list(list1,list2):
    for l in list2:
        if l not in list1:
            list1.append(l)
    return list1

def Search_Engines(req):
    #函数：调用搜索引擎，这里调用的粉象api
    #入参 req 类型：str 含义：表示当前需要检索的需求
    #出参 request_items 类型：List 含义：返回的商品需求
    #出参 top_category 类型：List 含义：返回的近似商品
    new_dict = {
        "keyword": req,
        "catLeafName": "",
        "fetchSize": FETSIZE
    }
    res = requests.post(url='https://k8s-api-dev.fenxianglife.com/dev1/fenxiang-ai/search/item', json=new_dict)
    user_dict = json.loads(res.text)
    if "data" in user_dict.keys():
        request_items = user_dict["data"]['items']  # 查询到的商品信息JSON
        top_category = user_dict["data"]['topCategories']
        return request_items,top_category
    else:
        return []
    
def search_with_api(requirements,categery):
    #函数：调用搜索引擎，这里调用的粉象api
    #入参 attachments 类型：dict 含义：message携带的信息
    #出参 request_items 类型：List 含义：搜索得到的商品
    #出参 chat_answer 类型：str 含义：表示回答客户时附加的信息（测试时使用）
    
    
    # requirements = attachments["requirements"]
    # all_req = requirements + " " + attachments["category"]
    # request_items,top_category = Search_Engines(all_req)#这里调用搜索引擎
    request_items = []
    all_req_list = requirements.split(" ")#需求字符串转换为list
    count = 0 #记录减少需求的次数
    
    while len(request_items)<FETSIZE and len(all_req_list)>0:
        if count:#非第一次搜索
            all_req_list.pop(0)#删除第一个需求
        all_req = (" ").join(all_req_list)#需求list转换为字符串
        if categery not in all_req_list:
            all_req = all_req + " " + categery
        now_request_items,top_category = Search_Engines(all_req)#这里调用搜索引擎
        request_items = merge_list(request_items,now_request_items)
        count +=1
    new_top = []
    for category in top_category:
        if "其他" in category or "其它" in category:
            continue
        else:
            new_top.append(category)    
    if len(request_items)>FETSIZE:
        request_items = request_items[:FETSIZE]       
    return request_items,new_top



def response_to_string(response):
    all = ""
    for data in response:
        all += data.choices[0]['delta'].get('content') if data.choices[0]['delta'].get('content') else ''
    return all
    
    
    
if __name__ == '__main__':
    str = "hello 123 hello"
    x = get_content_between_a_b("hello1","hello1",str)
