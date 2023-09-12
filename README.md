
  

# <p align="center"><img src='./assets/logo.png'  width=300></p>

  

## <p align="center"><font  face="Calisto MT"><font  size="4">An Open-source Framework for Autonomous Language Agents</font></font></p>

<p align="center"><a href="https://arxiv.org/pdf/2305.13304.pdf">[📄 Paper]</a> </p>
<hr>
  

## **Overview**

**Agents** is an open-source library/framework for building autonomous language agents. The library is carefully engineered to support important features including **long-short term memory**, **tool usage**, **web navigation**, **multi-agent communication**, and brand new features including **human-agent interaction** and **symbolic control**. With **Agents**, one can customize a language agent or a multi-agent system by simply filling in a config file in natural language and deploy the language agents in a terminal, a Gradio interface, or a backend service.

One major different between our **Agents** framework and other existing frameworks for language agents is that our framework allows users to provide fine-grained control and guidance to language agents via an **SOP (Standard Operation Process)**. An SOP defines subgoals/subtasks for the overall task and allows users to customize a fine-grained workflow for the language agents 

With our Agent module, all you need to do is generate and modify particular prompts with the help of **🧩Component** module . Sequently, as aforementioned, those stylized prompts, graved in **✨States**, will define your agent's status, styles, etc. Numerous sorts of States altogether formed our **📋Standard Operation Process(SOP) System**, which helps run your agents under sophisticated circumstances.


## **Updates and ToDos**

[] Support LLM-based SOP generation
[x] 2023.9.12 Offical Release

## **Highlights**
  

- 


## Installation and Usage

### Install the package
[x] Option 1.  Build from source

    ```
    git clone https://github.com/aiwaves-cn/agents.git
    cd agents
    pip install -e . 
    ```

[] Option 2.  Install via PyPI

    ```
    pip install agents
    ```

### Generate the config file

[x] Option 1.  Fill in the config template manually

TBD

[x] Option 2.  Try our WebUI for customizing the config file.

TBD



## Examples and Demos

We have provided exemplar config files, code, and demos for both single-agent and multi-agent systems [here](https://github.com/aiwaves-cn/agents/tree/master/examples).


## **Documentation**


Please check our [documentation](https://ai-waves.feishu.cn/wiki/KZb6whkDTiM1cUkLqqOcnUNNnuh?from=from_copylink) for detailed documentation of the framework.





