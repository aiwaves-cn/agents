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

import json
from PIL import Image
import requests
from typing import List, Tuple

class GradioConfig:
    # How many avatars are currently registered
    POINTER = 0
    
    # Avatar image. You can add or replace.
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
        "https://img.touxiangwu.com/zb_users/upload/2023/05/202305171684311196958993.jpg",
        "https://img.touxiangwu.com/uploads/allimg/2021082612/vr0bkov0dwl.jpg",
        "https://img.touxiangwu.com/uploads/allimg/2021082612/auqx5zfsv5g.jpg",
        "https://img.touxiangwu.com/uploads/allimg/2021082612/llofpivtwls.jpg",
        "https://img.touxiangwu.com/uploads/allimg/2021082612/3j2sdot3ye0.jpg",
        "https://img.touxiangwu.com/2020/3/nQfYf2.jpg",
        "https://img.touxiangwu.com/zb_users/upload/2023/08/202308131691918068774532.jpg",
        "https://img.touxiangwu.com/zb_users/upload/2023/08/202308131691918068289945.jpg",
        "https://img.touxiangwu.com/zb_users/upload/2023/08/202308131691918069785183.jpg",
        "https://img.touxiangwu.com/zb_users/upload/2023/06/202306141686726561292003.jpg",
        "https://img.touxiangwu.com/zb_users/upload/2023/06/202306141686726561578616.jpg",
        "https://img.touxiangwu.com/zb_users/upload/2023/06/202306141686726564597524.jpg"
    ]
    USER_HEAD_URL = "https://img.touxiangwu.com/zb_users/upload/2023/05/202305301685407468585486.jpg"
    
    # The css style of gradio.Chatbot
    CSS = """
    #chatbot1 .user {
        background-color:transparent;
        border-color:transparent;
    }
    #chatbot1 .bot {
        background-color:transparent;
        border-color:transparent;
    }
    """
 
    ID = ["USER", "AGENT", "SYSTEM"]
    
    # Bubble template
    BUBBLE_CSS = {
        # 背景颜色 名字颜色 名字 字体颜色 字体大小 内容 图片地址
        "USER": """
    <div style="display: flex; align-items: flex-start; justify-content: flex-end;">
        <div style="background-color: {}; border-radius: 20px 0px 20px 20px; padding: 15px; min-width: 100px; max-width: 300px;">
            <p style="margin: 0; padding: 0; color: {}; font-weight: bold; font-size: 18px;">{}</p>
            <p style="margin: 0; padding: 0; color: {}; font-size: {}px;">{}</p>
        </div>
        <img src="{}" alt="USER" style="width: 50px; height: 50px; border-radius: 50%; margin-left: 10px;">
    </div>
        """,

        # 图片地址 背景颜色 名字颜色 名字 字体颜色 字体大小 内容
        "AGENT": """
    <div style="display: flex; align-items: flex-start;">
        <img src="{}" alt="AGENT" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px;">
        <div style="background-color: {}; border-radius: 0px 20px 20px 20px; padding: 15px; min-width: 100px; max-width: 600px;">
            <p style="margin: 0; padding: 0; color: {}; font-weight: bold; font-size: 18px;">{}</p>
            <p style="margin: 0; padding: 0; color: {}; font-size: {}px;">{}</p>
        </div>
    </div>
        """,

        # 背景颜色 字体大小 字体颜色 名字 内容
        "SYSTEM": """
    <div style="display: flex; align-items: center; justify-content: center;">
        <div style="background-color: {}; border-radius: 20px; padding: 1px; min-width: 200px; max-width: 1000px;">
            <p style="margin: 0; padding: 0; text-align: center; font-size: {}px; font-weight: bold; font-family: '微软雅黑', sans-serif; color: {};">{}:{}</p>
        </div>
    </div>
        """
    }

    ROLE_2_NAME = {}
    
    OBJECT_INFO = {
        # 主要是user/agent/system
        "User": {
            # https://img-blog.csdnimg.cn/img_convert/7c20bc39ac69b6972a22e18762d02db3.jpeg
            "head_url": USER_HEAD_URL,
            "bubble_color": "#95EC69",
            "text_color": "#000000",
            "font_size": 0,
            "id": "USER"
        },

        "System": {
            # https://img-blog.csdnimg.cn/img_convert/e7e5887cfff67df8c2205c2ef0e5e7fa.png
            "head_url": "https://img.touxiangwu.com/zb_users/upload/2023/03/202303141678768524747045.jpg",
            "bubble_color": "#7F7F7F",  ##FFFFFF
            "text_color": "#FFFFFF",  ##000000
            "font_size": 0,
            "id": "SYSTEM"
        },

        "wait": {
            "head_url": "https://img.touxiangwu.com/zb_users/upload/2022/12/202212011669881536145501.jpg",
            "bubble_color": "#E7CBA6",
            "text_color": "#000000",
            "font_size": 0,
            "id": "AGENT"
        },

        "Recorder": {
            "head_url": "https://img.touxiangwu.com/zb_users/upload/2023/02/202302281677545695326193.jpg",
            "bubble_color": "#F7F7F7",
            "text_color": "#000000",
            "font_size": 0,
            "id": "AGENT"
        }
    }

    @classmethod
    def color_for_img(cls, url):
        """
        Extract the main colors from the picture and set them as the background color, 
        then determine the corresponding text color.
        """

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
            print(f"binding: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                with open('image.jpg', 'wb') as f:
                    f.write(response.content)

        def rgb_to_hex(color):
            return "#{:02X}{:02X}{:02X}".format(color[0], color[1], color[2])

        def get_color(image_url):
            download_image(image_url)

            image = Image.open("image.jpg")
            main_color = get_main_color(image)
            is_dark = is_dark_color(main_color)

            if is_dark:
                font_color = "#FFFFFF"
            else:
                font_color = "#000000"

            return rgb_to_hex(main_color), font_color

        return get_color(url)

    @classmethod
    def init(cls, JSON):
        # Deprecated
        with open(JSON) as f:
            sop = json.load(f)
        cnt = 0
        FISRT_NODE = True
        fisrt_node_roles = []
        for node_name in sop['nodes']:
            node_info = sop['nodes'][node_name]
            agent_states = node_info['agent_states']
            for agent_role in agent_states:
                name = agent_states[agent_role]['style']['name']
                cls.ROLE_2_NAME[agent_role] = name
                if FISRT_NODE:
                    fisrt_node_roles.append(agent_role)
                bubble_color, text_color = cls.color_for_img(cls.AGENT_HEAD_URL[cnt])
                cls.OBJECT_INFO[name] = {
                    "head_url": f"{cls.AGENT_HEAD_URL[cnt]}",
                    "bubble_color": bubble_color,
                    "text_color": text_color,
                    "font_size": 0,
                    "id": "AGENT"
                }
                cnt += 1
            if FISRT_NODE:
                FISRT_NODE = False
        print(cls.OBJECT_INFO)
        for usr_name in cls.OBJECT_INFO:
            if cls.OBJECT_INFO[usr_name]["id"] == "SYSTEM":
                cls.OBJECT_INFO[usr_name]["font_size"] = 12
            elif cls.OBJECT_INFO[usr_name]["id"] in ["USER", "AGENT"]:
                cls.OBJECT_INFO[usr_name]["font_size"] = 16
            else:
                assert False
        return fisrt_node_roles

    @classmethod
    def add_agent(cls, agents_name:List):
        for name in agents_name:
            bubble_color, text_color = cls.color_for_img(cls.AGENT_HEAD_URL[cls.POINTER])
            cls.OBJECT_INFO[name] = {
                "head_url": f"{cls.AGENT_HEAD_URL[cls.POINTER]}",
                "bubble_color": bubble_color,
                "text_color": text_color,
                "font_size": 0,
                "id": "AGENT"
            }
            cls.POINTER += 1
        for usr_name in cls.OBJECT_INFO:
            if cls.OBJECT_INFO[usr_name]["id"] == "SYSTEM":
                cls.OBJECT_INFO[usr_name]["font_size"] = 12
            elif cls.OBJECT_INFO[usr_name]["id"] in ["USER", "AGENT"]:
                cls.OBJECT_INFO[usr_name]["font_size"] = 16
            else:
                assert False


class StateConfig:
    """UI configuration for the step progress bar (indicating the current node)"""
    
    CSS = """
:root {
        --gradient-start: 100%;
        --gradient-end: 0%;
 }
.container.progress-bar-container {
  position: relative;
  display: flex;
  align-items: flex-end; /* 将内容底部对齐 */
  width: 100%;
  overflow-x: auto;
  padding-bottom: 30px;
  padding-top: 20px
}
.container.progress-bar-container::-webkit-scrollbar {
  width: 8px;
  background-color: transparent;
}

.container.progress-bar-container::-webkit-scrollbar-thumb {
  background-color: transparent;
}

.progress-bar-container .progressbar {
  counter-reset: step;
  white-space: nowrap;
}
.progress-bar-container .progressbar li {
  list-style: none;
  display: inline-block;
  width: 200px;
  position: relative;
  text-align: center;
  cursor: pointer;
  white-space: normal;
}
.progress-bar-container .progressbar li:before {
  content: counter(step);
  counter-increment: step;
  width: 30px;
  height: 30px;
  line-height: 30px;
  border: 1px solid #ddd;
  border-radius: 100%;
  display: block;
  text-align: center;
  margin: 0 auto 10px auto;
  background-color: #ffffff;
}
.progress-bar-container .progressbar li:after {
  content: attr(data-content);
  position: absolute;
  width: 87%;
  height: 2px;
  background-color: #dddddd;
  top: 15px;
  left: -45%;
}
.progress-bar-container .progressbar li:first-child:after {
  content: none;
}
.progress-bar-container .progressbar li.active {
  color: green;
}
.progress-bar-container .progressbar li.active:before {
  border-color: green;
  background-color: green;
  color: white;
}
.progress-bar-container .progressbar li.active + li:after {
  background: linear-gradient(to right, green var(--gradient-start), lightgray var(--gradient-end));
}
.progress-bar-container .small-element {
  transform: scale(0.8);
}
.progress-bar-container .progressbar li span {
  position: absolute;
  top: 40px;
  left: 0;
  width: 100%;
  text-align: center;
}
.progress-bar-container .progressbar li .data-content {
  position: absolute;
  width: 100%;
  top: -10px;
  left: -100px;
  text-align: center;
}
"""
    
    FORMAT = """
<html>
    <head>
        <style>
            {}
        </style>
    </head>
    <body>
        <br>
        <center>
            <div class="container progress-bar-container">
                <ul class="progressbar">
                    {}
                </ul>
            </div>
        </center>
    </body>
</html>
"""
    
    STATES_NAME:List[str] = None
    
    @classmethod
    def _generate_template(cls, types:str)->str:
        # normal: A state with no execution.
        # active-show-up: Active state, and content displayed above the horizontal line.
        # active-show-down: Active state, and content displayed below the horizontal line.
        # active-show-both: Active state, and content displayed both above and below the horizontal line.
        # active-show-none: Active state, with no content displayed above the horizontal line.
        
        assert types.lower() in ["normal","active-show-up", "active-show-down", "active-show-both", "active", "active-show-none"]
        both_templates = """<li class="active" style="--gradient-start: {}%; --gradient-end: {}%;">
	<div class="data-content">
		<center>
            <p style="line-height: 1px;"></p>
			{}
			<p>
				{}
			</p>
		</center>
	</div>
	<span>{}</span>
</li>"""

        if types.lower() == "normal":
            templates = "<li><span>{}</span></li>"
        elif types.lower() == "active":
            templates = """<li class="active"><span>{}</span></li>"""
        elif types.lower() == "active-show-up":
            templates = both_templates.format("{}","{}", "{}", "", "{}")
        elif types.lower() == "active-show-down":
            templates = both_templates.format("{}","{}", "", "{}", "{}")
        elif types.lower() == "active-show-both":
            templates = both_templates
        elif types.lower() == "active-show-none":
            templates = """<li class="active" style="--gradient-start: {}%; --gradient-end: {}%;">
	<span>{}</span>
</li>"""
        else:
            assert False
        return templates
            
    @classmethod
    def update_states(cls, current_states:List[int], current_templates:List[str], show_content:List[Tuple[str]])->str:
        assert len(current_states) == len(current_templates)
        # You can dynamically change the number of states.
        # assert len(current_states) == len(cls.STATES_NAME)
        css_code = []
        for idx in range(len(current_states)):
            if idx == 0:
                if current_states[idx] != 0:
                    css_code = [f"{cls._generate_template('active').format(cls.STATES_NAME[idx])}"]
                else:
                    css_code = [f"{cls._generate_template('normal').format(cls.STATES_NAME[idx])}"]
                continue
            if current_states[idx-1] == 0:
                # new_code = f"{cls._generate_template('normal').format(*(show_content[idx]))}"
                new_code = f"{cls._generate_template('normal').format(cls.STATES_NAME[idx])}"
            else:
                new_code = f"{cls._generate_template(current_templates[idx]).format(current_states[idx-1], 100-current_states[idx-1],*(show_content[idx-1]), cls.STATES_NAME[idx])}"
            if current_states[idx-1] != 100 or (current_states[idx]==0 and current_states[idx-1]==100):
                new_code = new_code.replace("""li class="active" ""","""li """)
            css_code.append(new_code)
        return "\n".join(css_code)
    
    @classmethod
    def create_states(cls, states_name:List[str], manual_create_end_nodes:bool=False):
        # Create states
        if manual_create_end_nodes:
            states_name.append("Done")
        css_code = ""
        cls.STATES_NAME: List[str] = states_name
        for name in states_name:
            css_code = f"{css_code}\n{cls._generate_template('normal').format(name)}"
        return css_code
    

if __name__ == '__main__':
    pass
