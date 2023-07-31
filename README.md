
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

## Components
> In order to provide <u>modularized prompts</u> of a Node in an AI Autonomous Agent, we established **Components** module.
> 
> - Classification:  We use parent classes and subclasses to classify diverse kinds of prompts. Two kinds of parent classes are provided,  namely "Component" and "KnowledgeComponent".  Specialized requirements, such as rules, styles and output forms of an autonomous agent, is inherited from one of the parent classes above.
> 
> - Examples:
> >- codes of "Component" [^1]class is shown below:
> >>```python
>>>class Component():  
>>>def __init__(self):  
>>>    self.prompt = ""  
>>>@abstractmethod  
>>>def get_prompt(self):  
>>>    pass
>>- codes of "StyleComponent"[^2] class is shown below:
> >>```python
>>>class StyleComponent(Component):
>>>def __init__(self, agent, style):
>>>    super().__init__()
>>>    self.agent = agent  
>>>    self.style = style
>>>def get_prompt(self):  
>>>    return f"""现在你来模拟一个{self.agent}。你需要遵循以下的输出风格：  {self.style}。  """
>>>    pass
> [^1]:"Component" is defined as parent class, providing modularized input form of diverse prompts.
> [^2]:"StyleComponent" is a sort of subclasses, which is designated to provide several kinds of "temper" of the autonomous agents. Those "temper" include customized chatting templates and styles. We have developed numorous kinds of styles, such as humorous and expertised.
## Usage
