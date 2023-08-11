# 主题
'''
min-width: 0px; 
max-width: 600px;
border-radius: 20px 0px 20px 20px;
'''
CSS = """
#chatbot1 .user {
    background-color:white;
    border-color:white;
}
#chatbot1 .bot {
    background-color:white;
    border-color:white;
}
"""

# 身份
ID = ["USER","AGENT","SYSTEM"]

# 有哪些具体的角色
OBJECT_INFO = {
    # 主要是user/agent/system
    "User":{
        # https://img-blog.csdnimg.cn/img_convert/7c20bc39ac69b6972a22e18762d02db3.jpeg
        "head_url": "file/7c20bc39ac69b6972a22e18762d02db3.jpeg",
        "bubble_color": "#95EC69",
        "text_color": "#000000",
        "font_size": 0,
        "id": "USER"
    },
    "吴家隆":{
        # https://img-blog.csdnimg.cn/img_convert/6b0284aedf3b1570d7699319bf159b40.png
        "head_url": "file/6b0284aedf3b1570d7699319bf159b40.png",
        "bubble_color": "#b2dbbf",
        "text_color": "#000000",
        "font_size": 0,
        "id": "AGENT"
    },
    "John":{
        # https://img-blog.csdnimg.cn/img_convert/475bcaebf8fec50aeee697a7edac8260.png
        "head_url": "file/475bcaebf8fec50aeee697a7edac8260.png",
        "bubble_color": "#BAC0C2",
        "text_color": "#000000",
        "font_size": 0,
        "id": "AGENT"
    },
    "system":{
        # https://img-blog.csdnimg.cn/img_convert/e7e5887cfff67df8c2205c2ef0e5e7fa.png
        "head_url": "file/e7e5887cfff67df8c2205c2ef0e5e7fa.png",
        "bubble_color": "#7F7F7F",
        "text_color": "#FFFFFF",
        "font_size": 0,
        "id": "SYSTEM"
    },
}

# BUBBLE模板
BUBBLE_CSS = {
    # 背景颜色 名字 字体颜色 字体大小 内容 图片地址
    "USER": """
<div style="display: flex; align-items: flex-start; justify-content: flex-end;">
    <div style="background-color: {}; border-radius: 20px 0px 20px 20px; padding: 15px; min-width: 100px; max-width: 300px;">
        <p style="margin: 0; padding: 0; font-weight: bold; font-size: 18px;">{}</p>
        <p style="margin: 0; padding: 0; color: {}; font-size: {}px;">{}</p>
    </div>
    <img src="{}" alt="USER" style="width: 50px; height: 50px; border-radius: 50%; margin-left: 10px;">
</div>
    """,
    
    # 图片地址 背景颜色 名字 字体颜色 字体大小 内容
    "AGENT":"""
<div style="display: flex; align-items: flex-start;">
    <img src="{}" alt="AGENT" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px;">
    <div style="background-color: {}; border-radius: 0px 20px 20px 20px; padding: 15px; min-width: 100px; max-width: 600px;">
        <p style="margin: 0; padding: 0; font-weight: bold; font-size: 18px;">{}</p>
        <p style="margin: 0; padding: 0; color: {}; font-size: {}px;">{}</p>
    </div>
</div>
    """,
    
    # 背景颜色 字体大小 字体颜色 名字 内容
    "SYSTEM": """
<div style="display: flex; align-items: center; justify-content: center;">
    <div style="background-color: {}; border-radius: 20px; padding: 1px; min-width: 200px; max-width: 600px;">
        <p style="margin: 0; padding: 0; text-align: center; font-size: {}px; font-weight: bold; font-family: '微软雅黑', sans-serif; color: {};">{}:{}</p>
    </div>
</div>
    """
}

def init():
    """主要是设置字体大小"""
    for usr_name in OBJECT_INFO:
        if OBJECT_INFO[usr_name]["id"] == "SYSTEM":
            OBJECT_INFO[usr_name]["font_size"] = 12
        elif OBJECT_INFO[usr_name]["id"] in ["USER","AGENT"]:
            OBJECT_INFO[usr_name]["font_size"] = 16
        else:
            assert False
