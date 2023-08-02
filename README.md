
# <p align="center"><font size="6">Agents</font><br />

## <p align="center"><font face="Calisto MT"><font size="4">A toolkit for building customized autonomous AI agents</font></font><br />  

<p align="center"><a href="https://arxiv.org/pdf/2305.13304.pdf">[📄 Paper]</a> | <a href="http://47.96.122.196:8098/boxingbot-chat/">[🤖 Demo - Customer Service Agent]</a> | <a href="https://front-dev.fenxianglife.com/h5-official/appPages/independent/AI-guide/index.html?appToken=0af0c773c04ca654f19514fbb51f4352&did=B4B88CE9-F39A-48A6-9DA9-9E2BE8D3CD27&uid=108#/">[🛍️ Demo - Shopping Guide Agent]</a> </p>
<hr>


## 🤖 AI Autonomous Agents

- **Brief Introduction**: AI Autonomous Agents are intelligent entities capable of perceiving their environment, making decisions, and taking actions without direct human intervention. As human society rapidly develops, AI Autonomous Agents find applications in diverse circumstances, as follows:

  - 💊 **Medical Use**:
    - The oculist agent acts as a consultant, providing professional advice and enabling online reservations for patients.

  - 🛍️ **Commercial Use**:
    - The shopping guide agent serves as an intelligent shopping assistant, offering diverse and customized shopping experiences.

- **Features**: AI Autonomous Agents offer several advantages over human assistants:

  - 🎯 **Precision**: They avoid human errors caused by fatigue, distractions, or emotions. Consistent execution of actions without performance decline.

  - ⚡ **Efficiency**: These agents process vast data and make decisions at incredible speeds, often surpassing human capabilities. Particularly in complex scenarios with extensive document volumes, AI Autonomous Agents tend to outperform human assistants.

  - 📈 **Scalability**: They easily scale for diverse requirements without extensive hiring or training. Explore our **Agents** toolkit to effortlessly develop your customized autonomous agents!


## 📋 Standard Operation Procedure (SOP)


A **Standard Operating Procedure (SOP)** is a reasoning graph that consists of a set of step-by-step instructions outlining how to execute a specific task or process. SOP serves as the core component within our autonomous agents, playing an essential role in orchestrating the operation of these agent systems.

### Example:
A typical SOP illustrates the complete operational process of our Agents. Taking the oculist agent as an example, the following SOP (shown below, in Chinese) delineates the entire workflow of the robot's customer service. This includes outlining the stages, steps, and criteria for each phase. By utilizing this SOP, we can comprehensively define the robot's functions and workflow, thereby generating customized agents tailored to specific requirements.
[SOP of the oculist agent](https://github.com/aiwaves-cn/agents/blob/master/examples/%E6%B5%81%E7%A8%8B%E5%9B%BE.jpg)

### Encoding:
To standardize SOPs of diverse kinds, we consistently employ **JSON files** for input. A JSON file, short for *JavaScript Object Notation*, is employed to store basic data structures and objects. It facilitates data interchange in web applications.
Here's an example JSON file: [JSON file of youcai agent](https://github.com/aiwaves-cn/agents/blob/master/examples/youcai_service.json)

### Keyword Extraction:
We've developed several functions to extract specific words from JSON files, facilitating the creation of various types of nodes. In essence, all that's required is meticulous input of your requirements and conversational attributes, and you'll obtain your personalized autonomous agent!


## ✨ Nodes

- **Definition**: As previously mentioned, we utilize SOP to operate the autonomous agent. Our SOP reasoning graph is composed of various **Nodes**, each derived from key words provided in the JSON file. These nodes play distinct roles, contributing to the entire system. We've developed a straightforward node, the **SIMPLIST** node, primarily based on GPT. The process is simple: input a prompt, obtain the response as output, and then utilize this response for various operations.

- **Classification**: We've established two parent node classes: "GPT Nodes" and "Tool Nodes". 
  - **GPT Nodes** consist of three different types: "judge", "response", and "extract", each serving a unique purpose:
    - 🧠 **Judge Node**: Determines certain sentences and returns a keyword to determine the next node.
    - 💬 **Response Node**: Responds to user's questions, typically relying on the knowledge base.
    - 🔍 **Extract Node**: Extracts specific keywords from user input and stores them for memory.
  - **Tool Nodes** are designed to fulfill specific tasks, such as searching for information in memory or matching keywords.

- **Examples**:
  - Basic codes for a GPT Node are as follows:
    ```python
    class GPTNode():
        def __init__(self, name: str = None, node_type: str = None, extract_words=None, done=False, user_input: str = "", components: dict = {}):
            # ... (attributes)
    ```
    Each attribute is described below:
    - `node_type` (str, optional): three types (response, extract, judge)
      - `response`: return a response
      - `extract`: return a keyword for memory
      - `judge`: return the keyword to determine which node is next
    - ... (other attributes)

  - Basic codes for a Tool Node are as follows:
    ```python
    class ToolNode:
        def __init__(self, name="", done=False):
            # ... (attributes)
        @abstractmethod
        def func(self, long_memory, temp_memory):
            pass
    ```
    The Static Node is a type of Tool Node, with the following code:
    ```python
    class StaticNode(ToolNode):
        def __init__(self, name="", output="", done=False):
            # ... (attributes)
        def func(self, long_memory, temp_memory):
            outputdict = {"response": self.output, "next_node_id": "0"}
            yield outputdict
    ```


## 🧩 Components

To facilitate modularized prompts for Nodes in an AI Autonomous Agent, we've introduced the **Components** module.

- **Classification**: We employ parent classes and subclasses to categorize different types of prompts. Two parent classes are available: "Component" and "KnowledgeComponent". Specific requirements, such as rules, styles, and output formats for autonomous agents, are inherited from these parent classes.

- **Examples**:
  - Codes for the "Component" class are as follows:
    ```python
    class Component():
        def __init__(self):
            self.prompt = ""
        @abstractmethod
        def get_prompt(self):
            pass
    ```
  - Codes for the "StyleComponent" class, a subclass, are as shown:
    ```python
    class StyleComponent(Component):
        def __init__(self, agent, style):
            super().__init__()
            self.agent = agent
            self.style = style
        def get_prompt(self):
            return f"Imagine you are simulating a {self.agent}. You are expected to adhere to the following output style: {self.style}."
    ```
[^1]: "Component" is the parent class, providing a modularized input form for diverse prompts.

[^2]: "StyleComponent" is a subclass designated to provide various "temperaments" for autonomous agents. These "temperaments" encompass customized chat templates and styles. We've developed numerous styles, including humorous and expert ones.


## 😄Getting Started with Fun 
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
