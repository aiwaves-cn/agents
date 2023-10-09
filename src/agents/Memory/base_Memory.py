from agents.Prompt import *
class Memory:
    def __init__(self,role,name,content) -> None:
        self.send_role = role
        self.send_name = name
        self.content = content
    
    def get_gpt_message(self,role):
        return {"role":role,"content":self.content}
    
    @classmethod
    def get_chat_history(self,messages,agent_name =None):
        """
        Splice a memory list into a sentence
        input : 
        messages(list) : list of memory(Memory)
        Return :
        chat_history(str) : One sentence after integration
        """
        chat_history = ""
        for message in messages:
            name,role,content = message.send_name,message.send_role,message.content
            if agent_name and agent_name==name:
                name = "you"
            chat_history += eval(Single_message)
        chat_history = eval(Chat_total_message)
        return chat_history
    
    def get_query(self):
        "Return : query(str):last sentence"
        name,role,content = self.send_name,self.send_role,self.content
        return eval(Single_message)