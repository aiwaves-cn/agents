import os

current_path = os.path.abspath(__file__)
current_path = os.path.dirname(current_path)
MIN_CATEGORY_SIM = 0.7
TOY_INFO_PATH =[os.path.join(current_path,'../../examples/shopping_assistant/toy_info.json'),
                 os.path.join(current_path,'../../examples/shopping_assistant/bb_info.json')
] #子类目相关知识库的路径
API_KEY = "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"
PROXY = 'http://127.0.0.1:7000'
FETSIZE = 5
MAX_CHAT_HISTORY = 10