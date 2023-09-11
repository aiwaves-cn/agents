import sys
sys.path.append("../cfg")

from gradio_example import SingleAgentUI

if __name__ == '__main__':
    # 启动client_server_file并自动传递消息
    ui = SingleAgentUI(
        # client_server_file="serving.py"
        client_cmd=["python", "run.py"]
    )
    # 构建映射关系
    # GradioConfig.add_agent(agents_name=ui.all_agents_name)
    # 搭建前端并建立监听事件
    ui.construct_ui()
    # 启动运行
    ui.run(share=True)
