import json
from PIL import Image
import requests

def color_for_img(url):
    """传入图片的链接，返回字体颜色和背景颜色"""
    def get_main_color(image):
        image = image.convert("RGB")
        width, height = image.size
        pixels = image.getcolors(width * height)
        most_common_pixel = max(pixels, key=lambda item: item[0])
        return most_common_pixel[1]

    def is_dark_color(rgb_color):
        r, g, b = rgb_color
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5

    def download_image(url):
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            with open('image.jpg', 'wb') as f:
                f.write(response.content)

    def rgb_to_hex(color):
        return "#{:02X}{:02X}{:02X}".format(color[0], color[1], color[2])

    def get_color(image_url):
        # 请替换为您的图片链接
        download_image(image_url)

        # 通过URL或者本地路径打开图片
        image = Image.open("image.jpg")
        main_color = get_main_color(image)
        is_dark = is_dark_color(main_color)

        if is_dark:
            font_color = "#FFFFFF"
        else:
            font_color = "#000000"

        return rgb_to_hex(main_color), font_color

    return get_color(url)

ROLE_2_NAME = {}

# 主题
AGENT_HEAD_URL = [
    "https://img.touxiangwu.com/zb_users/upload/2023/06/202306241687579617434043.jpg",
    "https://img.touxiangwu.com/zb_users/upload/2023/06/202306241687592097408547.jpg",
    "https://img.touxiangwu.com/zb_users/upload/2023/06/202306141686726561699613.jpg",
    "https://img.touxiangwu.com/zb_users/upload/2023/06/202306141686726561275758.jpg",
    "https://img.touxiangwu.com/uploads/allimg/2021090300/ry5k31wt33c.jpg",
    "https://img.touxiangwu.com/uploads/allimg/2021090300/0ls2gmwhrf5.jpg",
    "https://img.touxiangwu.com/zb_users/upload/2023/02/202302281677545695326193.jpg",
    "https://img.touxiangwu.com/zb_users/upload/2023/03/202303271679886128550253.jpg",
    "https://img.touxiangwu.com/zb_users/upload/2023/06/202306141686711344407060.jpg",
    "https://img.touxiangwu.com/zb_users/upload/2023/06/202306141686711345834296.jpg",
    "https://img.touxiangwu.com/zb_users/upload/2023/05/202305171684311194291520.jpg",
    "https://img.touxiangwu.com/zb_users/upload/2023/05/202305171684311196958993.jpg"
]
USER_HEAD_URL = "https://img.touxiangwu.com/zb_users/upload/2023/05/202305301685407468585486.jpg"
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
        "head_url": USER_HEAD_URL,
        "bubble_color": "#95EC69",
        "text_color": "#000000",
        "font_size": 0,
        "id": "USER"
    },
    
    "System":{
        # https://img-blog.csdnimg.cn/img_convert/e7e5887cfff67df8c2205c2ef0e5e7fa.png
        "head_url": "https://img.touxiangwu.com/zb_users/upload/2023/03/202303141678768524747045.jpg",
        "bubble_color": "#7F7F7F",
        "text_color": "#FFFFFF",
        "font_size": 0,
        "id": "SYSTEM"
    },
    
    "wait":{
        "head_url": "https://img.touxiangwu.com/zb_users/upload/2022/12/202212011669881536145501.jpg",
        "bubble_color": "#E7CBA6",
        "text_color": "#000000",
        "font_size": 0,
        "id": "AGENT"
    }
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

def init(JSON):
    """加载人物"""
    with open(JSON) as f:
        sop = json.load(f)
    cnt = 0
    for node_name in sop['nodes']:
        node_info = sop['nodes'][node_name]
        agent_states = node_info['agent_states']
        for agent_role in agent_states:
            name = agent_states[agent_role]['style']['name']
            ROLE_2_NAME[agent_role] = name
            bubble_color, text_color = color_for_img(AGENT_HEAD_URL[cnt])
            OBJECT_INFO[name] = {
                "head_url": f"{AGENT_HEAD_URL[cnt]}",
                "bubble_color": bubble_color,
                "text_color": text_color,
                "font_size": 0,
                "id": "AGENT"
            }
            cnt += 1
    print(OBJECT_INFO)
    """主要是设置字体大小"""
    for usr_name in OBJECT_INFO:
        if OBJECT_INFO[usr_name]["id"] == "SYSTEM":
            OBJECT_INFO[usr_name]["font_size"] = 12
        elif OBJECT_INFO[usr_name]["id"] in ["USER","AGENT"]:
            OBJECT_INFO[usr_name]["font_size"] = 16
        else:
            assert False

if __name__ == '__main__':
    init("game.json")