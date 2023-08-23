from component import ToolComponent,Component
import json
from utils import *


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

    def func(self, agent_dict):
        prompt = ""
        messages = agent_dict["long_memory"]["chat_history"]
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
        query = agent_dict["long_memory"]["chat_history"][-1] if len(agent_dict["long_memory"]["chat_history"])>0 else " "
        key_history = get_key_history(query,agent_dict["long_memory"]["chat_history"][:-1],agent_dict["long_memory"]["chat_embeddings"][:-1])
        response = get_response(
            messages,
            None,
            None,
            functions=functions,
            stream=False,
            function_call={"name": "search_information"},
            key_history = key_history
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
        if top1_score > MIN_CATEGORY_SIM:
            agent_dict["long_memory"]["category"] = topk_result[0][0]
            category = topk_result[0][0]
            information = self.search_information(
                topk_result[0][0], self.information_dataset
            )
            information = limit_keys(information, 3)
            information = limit_values(information, 2)
            prompt += f"""你需要知道的是：用户目前选择的商品是{category}，该商品信息为{information}。你需要根据这些商品信息来询问用户是否有更多的需求，如果没有商品信息则不需要推荐。例如：\n输入商品信息为：{{ \"品牌\": [\n        \"DIY\",\n        \"钓鱼\",\n      ],\n      \"发饰分类\": [\n        \"发箍\",\n        \"对夹\",\n        \"边夹\"\n      ],\n      \"风格\": [\n        \"甜美\",\n        \"复古/宫廷\",\n        \"日韩\",\n      ],\n      \"材质\": [\n        \"缎\",\n        \"布\",\n      ]}}\n输出：\n<回复>非常高兴您选择了我们的产品！关于您的选择，我有以下详细的推荐：\n品牌:\n**DIY**: DIY品牌的产品以其独特的个性化设计和高品质材料赢得了消费者的喜爱。如果你是手工艺品的热爱者，那么这个品牌绝对不容错过。\n**钓鱼**: 钓鱼品牌因其专注于创新和用户体验，受到了广大消费者的一致好评。\n发饰分类:\n**发箍**: 发箍非常适合运动或者是需要保持发型整洁的场合，它能有效地帮助你固定头发，避免头发散落影响视线。\n**对夹**: 对夹适合任何场合，尤其是需要快速简单地改变发型的时候，它是你的最佳选择。\n**边夹**: 边夹可以作为你日常打扮的点睛之笔，为你的发型增加一抹色彩。\n风格:\n**甜美**: 甜美风格的发饰通常以其温柔的色彩和繁复的设计受到年轻女孩的喜爱。\n**复古/宫廷**: 复古/宫廷风格则给人一种高贵而神秘的感觉，非常适合正式的场合。\n**日韩**: 日韩风格的发饰以其简约而精致的设计，给人留下深刻印象。\n材质:\n**缎**: 缎是一种光滑柔软的织物，常常被用于高档的头饰制作，其质地舒适，触感良好。\n**布**: 布材质的发饰以其轻便耐用，保养简单等特点，赢得了消费者的喜爱。\n希望这些建议能帮助您更好地理解每个选项，并为您的购买决策提供帮助。当然，您的个人喜好和需求是最重要的，这些都只是建议供您参考。</回复>"""
            if category in top_category:
                top_category.remove(category)

            recommend = "\n经过搜索后，推荐商品如下：\n"
            for i, request_item in enumerate(request_items):
                itemTitle = request_item["itemTitle"]
                itemPrice = request_item["itemPrice"]
                itemPicUrl = request_item["itemPicUrl"]
                recommend += f"[{i}.商品名称：{itemTitle},商品价格:{itemPrice}]({itemPicUrl})\n"
            print(recommend)
        else:
            prompt += f"""你需要知道的是：用户目前选择的商品是{category}，而我们店里没有这类商品，但是我们店里有一些近似商品，如{top_category},{topk_result[0][0]}，你需要对这些近似商品进行介绍，并引导用户购买"""
        outputdict["prompt"] = prompt
        return outputdict

