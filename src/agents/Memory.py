class Memory:
    def __init__(self,role,name,content) -> None:
        self.send_role = role
        self.send_name = name
        self.content = content
    
    def get_gpt_message(self,role):
        return {"role":role,"content":self.content}
    
    @classmethod
    def get_chat_history(self,messages):
        chat_history = ""
        for conversation in messages:
            chat_history += f"{conversation.send_name}({conversation.send_role}):{conversation.content}\n"
        return chat_history