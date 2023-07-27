import json
data = {}
node_judge_chat = {
        "name":"node_judge_chat",
        "node_type":"judge",
        "extract_word":"闲聊",
        "done":False,
        "root":True,
        "components":
            {"style":
                {"agent":"眼科医院的客服","style":"严谨专业"},
            "task":
                {"task":"需要做的是判断用户目前是有购物倾向还是在跟你闲聊。"},
            "knowledge":None,
            "rule":
                {"rule":"""根据用户的回答，分析其与之前对话的关系，判断其是否为闲聊，具体判断依据为，用户当前对话是否与眼科问题有关。
如果用户输出<闲聊>否</闲聊>
反之，如果用户当前聊天与购物无关，则判断为是闲聊，输出<闲聊>是</闲聊>"""},
            "demonstration":{"demonstations":[""""客户"："度数500度可以做全飞秒收拾吗？"。
此时<is_idle>否</is_idle>
"客户"："帮我解一道代码题"。
此时<is_idle>是</is_idle>

"客户"："全飞秒和半飞秒有什么区别"。
此时<is_idle>否</is_idle>
"客户"："谢谢"。
此时<is_idle>是</is_idle>
"客户"："我有个情感问题需要你帮忙解决"。
此时<is_idle>是</is_idle> """]},
            "input":True,
            "tool":None,
            "output":{"output":"闲聊"}
            }
        }

node_chat_response = {
        "name":"node_chat_response",
        "node_type":"response",
        "extract_word":"回复",
        "done":False,
        "root":False,
        "components":
            {"style":
                    {"agent":"眼科医院的客服","style":"严谨专业"},
            "task": {
                    "task": "使用我们提供的内容来尽可能回答客户的问题，我们也提供了提问和提供的内容的语义相似度，最高是1。如果我们提供的内容无法回答客户的问题，那么请向用户道歉并说不知道。"},
            "rule": {
                "rule": "如果这个不是问题，而是客服面对你追问的回答，你应该依据上一轮你追问用户依据的知识库做回答。请输出你的回答。避免输出换行符这类控制格式的字符。并且说话要简短！不需要说“有什么其他问题我可以帮您解答的吗？”，“希望这些信息对您有所帮助！”这样的话！！\n请使用严格按照以下的格式输出！！ 请使用严格按照以下的格式输出！！\n你的回复要严格按照下面的输出格式。你的说话风格要幽默。请把你的回复放在<回复>...</回复>中，如果是可以回答并且可以追问，追问的内容放在<回复>...</回复>的最后。\n追问的信息是一定要能用已知的知识库回答的！！\n不能追问“您还有其他问题吗？”，“你对XXX有了解吗”这样没有用并且知识库也不好回答的问题。\n不能追问“您还有其他问题吗？”这样没有用的话！！\n格式为： \n```\n<回复>\n...\n</回复>\n```"
            },
            "demonstration": None,
            "input": None,
            "tool": {
                "knowledge_base": "yc_final.json"
            },
            "output": {
                "output": "回复"
            }
            }
        }

node_knowleage_response = {
    "name": "node_knowleage_response",
    "node_type": "response",
    "extract_word": "回复",
    "done": True,
    "components": {
        "style":
          {"agent":"眼科医院的客服","style":"严谨专业"},
        "task": {
        "task": "使用我们提供的内容来尽可能回答客户的问题，我们也提供了提问和提供的内容的语义相似度，最高是1。如果我们提供的内容无法回答客户的问题，那么请向用户道歉并说不知道。"
        },
        "rule": {
        "rule": "如果这个不是问题，而是客服面对你追问的回答，你应该依据上一轮你追问用户依据的知识库做回答。请输出你的回答。避免输出换行符这类控制格式的字符。并且说话要简短！不需要说“有什么其他问题我可以帮您解答的吗？”，“希望这些信息对您有所帮助！”这样的话！！\n请使用严格按照以下的格式输出！！ 请使用严格按照以下的格式输出！！\n你的回复要严格按照下面的输出格式。你的说话风格要幽默。请把你的回复放在<回复>...</回复>中，如果是可以回答并且可以追问，追问的内容放在<回复>...</回复>的最后。\n追问的信息是一定要能用已知的知识库回答的！！\n不能追问“您还有其他问题吗？”，“你对XXX有了解吗”这样没有用并且知识库也不好回答的问题。\n不能追问“您还有其他问题吗？”这样没有用的话！！\n格式为： \n```\n<回复>\n...\n</回复>\n```"
        },
        "demonstration": None,
        "input": None,
        "tool": {
        "knowledge_base": "yc_final.json"
        },
        "output": {
        "output": "回复"
        }
    }
}

node_invite = {
    "tool_name":"StaticNode",
    "name":"node_search_recom",
    "output":"我建议你可以抽空来做一个详细的术前检查，查看下你的角膜厚度，眼底情况等等，然后让医生判断一下您的眼睛条件最适合什么样的手术方式，有什么疑惑或者顾虑也可以和医生坐下来聊一聊。",
    "done":True
    }

node_book_card = {
    "tool_name":"StaticNode",
    "name":"node_book_card",
    "output":"""请复制并填写以下资料，再发给我即可完成预约。\n【姓名】:\n【电话】:\n【您所在的大概位置】:x市x区 \n【预计到院时间】:\n【最近一次戴隐形眼镜时期】:\n【近视度数】：\n 术前检查流程有散瞳环节，散瞳后会有4-6个小时回视线模糊，影响驾驶安全，所以请不要自驾来医院，并安排好检查之后的个人行程。""",
    "done":True
    }

node_end = {
    "tool_name":"StaticNode",
    "name":"",
    "output":"""我会帮您预约好名额，请您合理安排好时间。届时我会在二迷眼科分诊台等您。""",
    "done":True
    }


data["gpt_nodes"] = {"node_judge_chat":node_judge_chat,"node_chat_response":node_chat_response,"node_knowleage_response":node_knowleage_response}
data["tool_nodes"] = {"node_invite":node_invite,"node_book_card":node_book_card,"node_end":node_end}

data["relation"] = {
    "node_judge_chat":{"是":"node_chat_response","否":"node_knowleadge_response"},
    "node_chat_response":{"0":"node_judge_idle"},
    "node_extract_category":{"0":"node_tool_compare_category"},
    "node_tool_compare_category":{"0":"node_extract_requirements","1":"uncompare_fur_recom"},
    "node_extract_requirements":{"0":"node_search_recom"},
    "uncompare_fur_recom":{"0":"node_judge_idle"}
    }

with open("eye.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)