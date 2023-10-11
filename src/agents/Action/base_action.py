from ..Memory import Memory
from ..utils import extract
import os
class Action:
    """
    The basic action unit of agent
    """
    def __init__(self,**kwargs):
        self.response = None
        self.is_user = False
        self.res_dict = {}
        self.name = ""
        self.role = ""
        for key,value in kwargs.items():
            setattr(self,key,value)
    
    
    def process(self):
        """
        processing action
        Rerutn : memory(Memory)
        """
        response = self.response
        send_name = self.name
        send_role = self.role
        all = ""
        for res in response:
            all += res
        parse = f"{send_name}:"
        
        # 将里面对话的第三人称删了
        # The third person in the dialogue was deleted.
        while parse in all:
            index = all.index(parse) + len(parse)
            all = all[index:]
        
        if not self.is_user:
            print(f"{send_name}({send_role}):{all}")
                # for software
        if "<title>" in all:
            title = extract(all,"title")
            title = "main.py" if title == "" else title
            python = extract(all,"python")
            os.makedirs("output_code", exist_ok=True)
            file_name = "output_code/" + title
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(python)
        memory = Memory(send_role, send_name, all)
        return memory
    
    
