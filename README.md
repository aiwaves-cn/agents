
# <p align="center"><font size="6">Agents</font><br />

## <p align="center"><font face="Calisto MT"><font size="4">A toolkit for building customized autonomous AI agents</font></font><br />  

<p align="center"><a href="https://arxiv.org/pdf/2305.13304.pdf">[📄 Paper]</a> | <a href="http://47.96.122.196:8098/boxingbot-chat/">[🤖 Demo - Customer Service Agent]</a> | <a href="https://front-dev.fenxianglife.com/h5-official/appPages/independent/AI-guide/index.html?appToken=0af0c773c04ca654f19514fbb51f4352&did=B4B88CE9-F39A-48A6-9DA9-9E2BE8D3CD27&uid=108#/">[🛍️ Demo - Shopping Guide Agent]</a> </p>
<hr>

## ✨AI Autonomous Agents
> - Brief introduction: AI Autonomous Agents are intelligent entities that can perceive their environment, make decisions, and take actions without direct human intervention. With the rapid development of human society, AI Autonomous Agents are designated to apply for diverse circumstances as folows:
>> - <font face="Consolas">for medical use:</font><br />
>>> - the oculist agent serves as a consultant, which can offer professional advice and online reserevation for patients.
>> - <font face="Consolas">for commercial use:</font><br />
>>> - the shopping guide agent is an intelligent shopping assistant that can provide a diverse and customized shopping service.
> - Features: AI Autonomous Agents has several advantages over human assistants.
> >- <font face="Consolas">Precision</font>: AI Autonomous Agents can avoid human errors  due to fatigue, distractions, or emotions. They can execute the same action repeatedly without a decline in performance.
> 
> >- <font face="Consolas">Efficiency</font>: AI Autonomous Agents can process vast amounts of data and make decisions at incredible speeds, often surpassing human capabilities. Especially under  sophisticated circumstances where large amounts of documents are given, AI Autonomous Agents are likely to perform better than human assistants.
> 
> >- <font face="Consolas">Scalability</font>: AI Autonomous Agents can be easily scaled to apply for different requirements, without the need for extensive hiring or training. **With our <u><font size="5">Agents</font></u> toolkit, you can easily develop your own customized autonomous agents!**

## Standard Operation Procedure (SOP)

## Nodes
>- Definition: Apparently, an autonomous agent is composed of numorous nodes, each contributing to the whole system. We have developed nearly the **simplist node** mainly based on GPT. All you need to do is __input the prompt__,and you could get the response as output. Afterwards, the response can be used for different operations.
>
>- Classification: We have created two kinds of parent node classes, namely "GPT Nodes" and "Tool Nodes". 
><br>GPT Nodes consists of three differnt types, namely "judge", "response" and "extract", with their functions as follows:
>>- <font face="Consolas">judge node</font>:  This type of node judges certain sentences and return the keyword to determine which node for next.
>
>>- <font face="Consolas">response node</font>: This type of node responds to user's questions, usually according to their knowledge base.
>
>>- <font face="Consolas">extract node</font>: This type of node extracts particular key words from user's input, and return the key word for memory.
><br>Tool Nodes are created to complete certain tasks, such as searching particular information in the memory base, or matching certain key words.
>- Examples:
>>- basic codes of a GPT Node is shown below:
>>> ```python
>>>     class  GPTNode():
>>>        def  __init__(self,
>>>            name:str = None,
>>>            node_type: str = None,
>>>            extract_words = None,
>>>            done=False,
>>>            user_input:str= "",
>>>            components:dict = {}):
>>>            self.prompt = ""
>>>            self.node_type = node_type
>>>            self.next_nodes = {}
>>>            self.components = components
>>>            self.extract_words = extract_words
>>>            self.done = done
>>>            self.name = name
>>Each of the attributes are shown below:
>>- `tool` (Tool, optional): _description_. Defaults to None.
>>- `node_type` (str, optional): three types (response, extract, judge)  
>>    - `response`: return a response
>>    - `extract`: return a keyword for memory
>>    - `judge`: return the keyword to determine which node is next
>>- `extract_words` (str, optional): _description_. Defaults to "".
>>- `next_nodes` (dict, optional): _description_. Defaults to {}.
>>- `done` (bool, optional): True: When the program runs to this node, it will be interrupted, allowing the user >>to input.
>>- `user_input` (str, optional): The content you want the agent to know. Defaults to "".
>>
>>- `components` (dict): Contains the definition of various components:
>>    - `style`: {"agent": "", "style": ""}
>>    - `task`: {"task": ""}
>>    - `rule`: {"rule": ""}
>>    - `knowledge` (str): ""
>>    - `demonstration`: {"demonstration": []}
>>    - `input`: true or false (whether the node has external inputs, usually the last input)
>>    - `tool`: {"tool_name": "", **args} (tool_name: the name of the tool, **args: the parameters of the tool)
>>    - `output`: {"output": ""} (the HTML wrap of the response)
>>- basic nodes of a Tool Node is shown below:
>>>```python
>>>    class  ToolNode:
>>>        def  __init__(self,name="",done=False):
>>>            self.next_nodes = {}
>>>            self.name = name
>>>            self.done = done
>>>            @abstractmethod
>>>        def  func(self,long_memory,temp_memory):
>>>            pass
>>Static Node is one type of Tool Nodes, the codes are shown below:
>>>``` python
>>>    class  StaticNode(ToolNode):
>>>        def  __init__(self, name="",output = "", done=False):
>>>            super().__init__(name, done)
>>>            self.output = output
>>>        def  func(self,long_memory,temp_memory):
>>>            outputdict = {"response":self.output,"next_node_id" : "0"}
>>>            yield  outputdict

## Components
> In order to provide <u>modularized prompts</u> of a Node in an AI Autonomous Agent, we established **Components** module.
> 
> - Classification:  We use parent classes and subclasses to classify diverse kinds of prompts. Two kinds of parent classes are provided,  namely "Component" and "KnowledgeComponent".  Specialized requirements, such as rules, styles and output forms of an autonomous agent, is inherited from one of the parent classes above.
> 
> - Examples:
> >- codes of "Component" [^1]class is shown below:
> >>```python
>>>    class Component():  
>>>        def __init__(self):  
>>>            self.prompt = ""  
>>>        @abstractmethod  
>>>        def get_prompt(self):  
>>>            pass
>>- codes of "StyleComponent"[^2] class is shown below:
> >>```python
>>>    class StyleComponent(Component):
>>>        def __init__(self, agent, style):
>>>            super().__init__()
>>>            self.agent = agent  
>>>            self.style = style
>>>        def get_prompt(self):  
>>>            return f"""现在你来模拟一个{self.agent}。你需要遵循以下的输出风格：  {self.style}。  """
>>>            pass
[^1]: "Component" is the parent class, providing a modularized input form for diverse prompts.

[^2]: "StyleComponent" is a subclass that is designated to provide various "temperaments" for autonomous agents. These "temperaments" include customized chatting templates and styles. We have developed numerous kinds of styles, such as humorous and expertised.

## Getting Started with Fun 😄
### Try  our demo in your terminal:point_down:
1. **Open your teminal**🖥️

3. **Get the Repository**📦
   ```bash
   git clone https://github.com/aiwaves-cn/agents.git
   ```
4. **Install the requirements**🛠️
      ```bash
   pip install -r requirements.txt
   ```
  4. **Set the config**🛠️
  >Modify sec/agents/config.py
  >Mainly modify API KEY and PROXY
   ```bash
   ##only used for shopping assistant
 MIN_CATEGORY_SIM  =  0.7  ##Threshold for category matching
TOY_INFO_PATH  = [your_path1,your_path2_......] #Path to the product database
FETSIZE  =  5 #Number of recommended products at a time

#for all agents
API_KEY  =  #Your API KEY
PROXY  =  #Your proxy
MAX_CHAT_HISTORY  =  8 #Longest History
   ```
5. **Run our demo in your teminal**🏃‍♂️
	
    4.1. **Shopping assistant**🛍️
      ```bash
   cd examples
   python run_cmd.py --agent shopping_assistant.json 
   ```
   4.2. **Oculist agent**👁️
     ```bash
   cd examples
   python run_cmd.py --agent eye.json 
   ```

## Deploy our demo on the backend:point_down:
 1. **Prepare your front-end webpage**🌐
 
2. **Deploy**🚀

    Please refer to serving.py for details
	We used flask to deploy🌶️
   ```bash
   cd examples
   python serving.py --agent shopping_assistant.json --port your_port --router your_api_router
   ```