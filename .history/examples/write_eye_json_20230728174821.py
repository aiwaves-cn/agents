import json
data = {}
node_judge_intent = {
        "name":"node_judge_chat",
        "node_type":"judge",
        "extract_word":"意图",
        "done":False,
        "root":True,
        "components":
            {"style":
                {"agent":"眼科医院的客服","style":"严谨专业"},
            "task":
                {"task":"需要做的是判断用户目前是回答了你的问题还是在另外提问。"},
            "knowledge":None,
            "rule":
                {"rule":"""根据用户的回答，分析其与之前对话的关系，判断其是否为回答你的问题，还是另外进行了提问。
如果用户回答了你的问题并且同意了你的请求，输出<意图>1</意图>
如果用户回答了你的问题但是拒绝了你的请求，输出<意图>2</意图>
如果用户没有回答你的问题而且提出了新的问题，输出<意图>3</意图>"""},
            "demonstration":None,
            "input":True,
            "tool":None,
            "output":{"output":"意图"}
            }
        }

node_judge_intent_invite = {
        "name":"node_judge_chat",
        "node_type":"judge",
        "extract_word":"意图",
        "done":False,
        "root":True,
        "components":
            {"style":
                {"agent":"眼科医院的客服","style":"严谨专业"},
            "task":
                {"task":"需要做的是判断用户目前是回答了你的问题还是在另外提问。"},
            "knowledge":None,
            "rule":
                {"rule":"""根据用户的回答，分析其与之前对话的关系，判断其是否为回答你的问题，还是另外进行了提问。
如果用户回答了你的问题并且同意了你的请求，输出<意图>1</意图>
如果用户回答了你的问题但是拒绝了你的请求，输出<意图>2</意图>
如果用户没有回答你的问题而且提出了新的问题，输出<意图>3</意图>"""},
            "demonstration":None,
            "input":True,
            "tool":None,
            "output":{"output":"意图"}
            }
        }

node_judge_intent_book_card = {
        "name":"node_judge_chat",
        "node_type":"judge",
        "extract_word":"意图",
        "done":False,
        "root":True,
        "components":
            {"style":
                {"agent":"眼科医院的客服","style":"严谨专业"},
            "task":
                {"task":"需要做的是判断用户目前是回答了你的问题还是在另外提问。"},
            "knowledge":None,
            "rule":
                {"rule":"""根据用户的回答，分析其与之前对话的关系，判断其是否为回答你的问题，还是另外进行了提问。
如果用户回答了你的问题并且同意了你的请求，输出<意图>1</意图>
如果用户回答了你的问题但是拒绝了你的请求，输出<意图>2</意图>
如果用户没有回答你的问题而且提出了新的问题，输出<意图>3</意图>"""},
            "demonstration":None,
            "input":True,
            "tool":None,
            "output":{"output":"意图"}
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

node_knowleage_response_invite = {
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

node_knowleage_response_book_card = {
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
    "name":"node_end",
    "output":"""我会帮您预约好名额，请您合理安排好时间。届时我会在二迷眼科分诊台等您。""",
    "done":True
    }

node_no_invite = {
    "tool_name":"StaticNode",
    "name":"node_no_invite",
    "output":"""你还有其他关于眼科的的问题吗？""",
    "done":True
    }

node_second_invite = {
    "tool_name":"StaticNode",
    "name":"node_second_invite",
    "output":"""建议您可以到院和医院详聊哦。""",
    "done":True
    }

node_no_book_card = {
    "tool_name":"StaticNode",
    "name":"node_no_book_card",
    "output":"""您是否还有其他顾虑？""",
    "done":True
    }

node_second_book_card = {
    "tool_name":"StaticNode",
    "name":"node_no_agree_invite",
    "output":"""建议您可以到院和医院详聊哦。""",
    "done":True
    }


data["gpt_nodes"] = {"node_judge_intent":node_judge_intent,
                     "node_judge_intent_invite":node_judge_intent_invite,
                     "node_judge_intent_book_card":node_judge_intent_book_card,
                     "node_knowleage_response":node_knowleage_response,
                     "node_knowleage_response_invite":node_knowleage_response_invite,
                    "node_knowleage_response_book_card":node_knowleage_response_book_card}

data["tool_nodes"] = {"node_invite":node_invite,
                      "node_no_invite":node_no_invite,
                      "node_second_invite":node_second_invite,
                      "node_book_card":node_book_card,
                      "node_no_book_card":node_no_book_card,
                      "node_second_book_card":node_second_book_card,
                      "node_end":node_end}

data["relation"] = {
    "node_knowleage_response":{"0","node_invite"},
    "node_invite":{"0":"node_judge_intent_invite"},
    "node_judge_intent_invite":{"0":"node_book_card","1":"node_no_invite","2":"node_knowleage_response_invite"},
    "node_no_invite":{"0":"node_knowleage_response"},

    "node_book_card":{"0":"node_judge_intent_book_card"},
    "node_judge_intent_book_card":{"0":"node_end","1":"node_no_book_card","2":"node_knowleage_response_book_card"},
    "node_knoleadge_response_book_card":{"0":"node_invite"},
    "node_no_book_card":{"0":"node_knowleage_response_book_card"},
    }
print(type(data))
with open("eye.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)