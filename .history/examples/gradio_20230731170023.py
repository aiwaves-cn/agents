import random
import gradio as gr

def random_response(message, history):
    return random.choice(["Yes", "No"])

demo = gr.ChatInterface(random_response)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0",server_port=18870,share=True,
                    show_api=False))
