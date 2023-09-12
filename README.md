# <p align="center"><img src='./assets/agents-logo.png'  width=300> </p>
## <p align="center" style="display:inline-block;"><font  face="Calisto MT"><font  size="4">An Open-source Framework for Autonomous Language Agents</font></font></p>

<p align="center"><a href="https://arxiv.org/pdf/2305.13304.pdf">[📄 Paper]</a>
<a href="http://www.aiwaves-agents.com/home">[🌐 Website]</a>
<a href="http://www.aiwaves-agents.com/agents">[🤖️ Demos]</a> </p>
<hr>
  

## Overview

**Agents** is an open-source library/framework for building autonomous language agents. The library is carefully engineered to support important features including **long-short term memory**, **tool usage**, **web navigation**, **multi-agent communication**, and brand new features including **human-agent interaction** and **symbolic control**. With **Agents**, one can customize a language agent or a multi-agent system by simply filling in a config file in natural language and deploy the language agents in a terminal, a Gradio interface, or a backend service.

One major difference between **Agents** and other existing frameworks for language agents is that our framework allows users to provide fine-grained control and guidance to language agents via an **SOP (Standard Operation Process)**. An SOP defines subgoals/subtasks for the overall task and allows users to customize a fine-grained workflow for the language agents.

<p align="center"><img src='./assets/agents-cover.png'  width=800></p>

## 📢 Updates

- [x] Support LLM-based SOP generation
- [x] 2023.9.12 Offical Release

## 💡 Highlights

- **Long-short Term Memory**: Language agents in the library are equipped with both long-term memory implemented via VectorDB + Semantic Search and short-term memory (working memory) maintained and updated by an LLM.
- **Tool Usage**: Language agents in the library can use any external tools via [function-calling](https://platform.openai.com/docs/guides/gpt/function-calling) and developers can add customized tools/APIs [here](https://github.com/aiwaves-cn/agents/blob/master/src/agents/Component/ToolComponent.py).
- **Web Navigation**: Language agents in the library can use search engines to navigate the web and get useful information.
- **Multi-agent Communication**: In addition to single language agents, the library supports building multi-agent systems in which language agents can communicate with other language agents and the environment. Different from most existing frameworks for multi-agent systems that use pre-defined rules to control the order for agents' action, **Agents** includes a *controller* function that dynamically decides which agent will perform the next action using an LLM by considering the previous actions, the environment, and the target of the current states. This makes multi-agent communication more flexible.
- **Human-Agent interaction**: In addition to letting language agents communicate with each other in an environment, our framework seamlessly supports human users to play the role of the agent by himself/herself and input his/her own actions, and interact with other language agents in the environment.
- **Symbolic Control**: Different from existing frameworks for language agents that only use a simple task description to control the entire multi-agent system over the whole task completion process, **Agents** allows users to use an **SOP (Standard Operation Process)** that defines subgoals/subtasks for the overall task to customize fine-grained workflows for the language agents.


## 🛠 Installation

#### Option 1.  Build from source

    ```
    git clone https://github.com/aiwaves-cn/agents.git
    cd agents
    pip install -e . 
    ```

#### Option 2.  Install via PyPI

    ```
    pip install agents
    ```

##  📦 Usage
### 🛠️ Generate the config file

#### Option 1.  Fill in the config template manually
TBD


#### Option 2.  Try our WebUI for customizing the config file.

TBD

### 🤖️ The Agent Hub
We encourage you to submit PRs or send us your own config files via [email](mailto:contact@aiwaves.cn), and we will share your examples.

A WebUI for automatic uploading of your customized agents will be available soon!


## 📷 Examples and Demos

We have provided exemplar config files, code, and demos for both single-agent and multi-agent systems [here](https://github.com/aiwaves-cn/agents/tree/master/examples).


## 📚 Documentation


Please check our [documentation](https://ai-waves.feishu.cn/wiki/KZb6whkDTiM1cUkLqqOcnUNNnuh?from=from_copylink) for detailed documentation of the framework.

## 😄 Getting Started with Fun

Try  our demo in your terminal!

#### 1. Open your terminal 🖥️
#### 2. Get the Repository 📦
```
git clone https://github.com/aiwaves-cn/agents.git
```
#### 3. Install the requirements 🛠️
```
pip install -r requirements.txt
```
#### 4. Set the config 🛠️
Modify `example/{Muti|Single_Agent}/{target_agent}/config.json`

```JSON
{  // e.g. for shopping assistant
    MIN_CATEGORY_SIM  =  "0.7"  ##Threshold for category matching
    TOY_INFO_PATH  = "[\"your_path1\",\"your_path2_\"......]" #Path to the product database
    FETSIZE  =  "5" #Number of recommended products at a time
    
    #for all agents
    API_KEY  =  #Your API KEY
    PROXY  =  #Your proxy
    MAX_CHAT_HISTORY  =  "8" #Longest History
    User_Names = "[\"{user_name}\"]" # the name of agents which you want to play  
}
```

Note that if you want to use `WebSearchComponent`, you also need set the config!

```JSON
 "WebSearchComponent": {
                        "engine_name": "bing",
                        "api": {
                            "google": {
                                "cse_id": "Your cse_id",
                                "api_key": "Your api_key"
                            },
                            "bing": "Your bing key"
                        }
                    }
```

#### Haven't figured out how to write the JSON file yet? Check out [documentation](https://ai-waves.feishu.cn/wiki/NIjrw8FR7inGTMkfS5yc5wcvnlg?from=from_copylink)!



