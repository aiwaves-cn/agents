from .ToolComponent import ToolComponent
import json
from utils import flatten_dict,get_embedding,matching_category,search_with_api,limit_keys,limit_values
import os


class CategoryRequirementsComponent(ToolComponent):
    def __init__(self, information_path):
        super().__init__()
        self.information_dataset = []
        self.leaf_name = []
        for toy_path in information_path:
            with open(toy_path, encoding="utf-8") as json_file:
                data = json.load(json_file)
            for d in data:
                if "/" in d["cat_leaf_name"]:
                    leaf_names = d["cat_leaf_name"].split("/") + [d["cat_leaf_name"]]
                else:
                    leaf_names = [d["cat_leaf_name"]]
                for name in leaf_names:
                    self.leaf_name.append(name)
                    new_d = d.copy()
                    new_d["cat_leaf_name"] = name
                    new_d["information"] = flatten_dict(new_d["information"])
                    self.information_dataset.append(new_d)

        self.target_embbeding = get_embedding(
            self.leaf_name
        )

    def search_information(self, category, information_dataset):
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

    def func(self, agent):
        prompt = ""
        messages = agent.long_term_memory
        outputdict = {}
        functions = [
            {
                "name": "search_information",
                "description": "根据用户所需要购买商品的种类跟用户的需求去寻找用户所需要的商品",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "用户现在所需要的商品类别，比如纸尿布，笔记本电脑等，注意，只能有一个",
                        },
                        "requirements": {
                            "type": "string",
                            "description": "用户现在的需求，比如说便宜，安踏品牌等等，可以有多个需求，中间以“ ”分隔",
                        },
                    },
                    "required": ["category", "requirements"],
                },
            }
        ]
        
        response = agent.LLM.get_response(
            messages,
            None,
            None,
            functions=functions,
            stream=False,
            function_call={"name": "search_information"},
        )
        response_message = json.loads(response["function_call"]["arguments"])
        category = (
            response_message["category"] if response_message["category"] else None
        )
        requirements = (
            response_message["requirements"]
            if response_message["requirements"]
            else category
        )
        if not (category or requirements):
            return {}

        topk_result = matching_category(
            category, self.leaf_name, None, self.target_embbeding, top_k=3
        )

        top1_score = topk_result[1][0]
        request_items, top_category = search_with_api(requirements, category)
        

        MIN_CATEGORY_SIM = eval(os.environ["MIN_CATEGORY_SIM"]
                                ) if "MIN_CATEGORY_SIM" in os.environ else 0.7

        if top1_score > MIN_CATEGORY_SIM:
            agent.environment.shared_memory["category"] = topk_result[0][0]
            category = topk_result[0][0]
            information = self.search_information(
                topk_result[0][0], self.information_dataset
            )
            information = limit_keys(information, 3)
            information = limit_values(information, 2)
            prompt += f"""你需要知道的是：用户目前选择的商品是{category}，该商品信息为{information}。你需要根据这些商品信息来详细介绍商品，比如详细介绍商品有哪些品牌，有哪些分类等等，并且询问用户是否有更多的需求。"""
            if category in top_category:
                top_category.remove(category)

            recommend = "\n经过搜索后，推荐商品如下：\n"
            prompt += "筛选出的商品如下：\n"
            for i, request_item in enumerate(request_items):
                itemTitle = request_item["itemTitle"]
                itemPrice = request_item["itemPrice"]
                itemPicUrl = request_item["itemPicUrl"]
                recommend += f"[{i}.商品名称：{itemTitle},商品价格:{float(itemPrice)/100}]({itemPicUrl})\n"
                prompt += f"[{i}.商品名称：{itemTitle},商品价格:{float(itemPrice)/100}]\n"
            print(recommend)
        else:
            prompt += f"""你需要知道的是：用户目前选择的商品是{category}，而我们店里没有这类商品，但是我们店里有一些近似商品，如{top_category},{topk_result[0][0]}，你需要对这些近似商品进行介绍，并引导用户购买"""
        outputdict["prompt"] = prompt
        return outputdict

