## 😄 Getting Started with Fun


### 1. Install the package
- [x] Option 1.  Build from source
<br>To install using this method,you need to change 'from agents.XXX import XXX' to 'from XXX import XXX' in either run.py or run_gradio.py.
    ```bash
    git clone https://github.com/aiwaves-cn/agents.git
    cd agents
    pip install ai-agents
    ```

- [x] Option 2.  Install via PyPI
<br>It is recommended to install in this way, and every code update will require reinstallation afterwards
    ```bash
    pip install ai-agents
    ```
 ### 2. Single Agent🤖️   
#### Set  config firstly(examples/Single_Agent/{target_agent}/config.json)
```
{  // e.g. for shopping assistant（due to change the search engine，it maybe not work now）
    MIN_CATEGORY_SIM  =  "0.7"  ##Threshold for category matching
    TOY_INFO_PATH  = "[\"your_path1\",\"your_path2_\"......]" #Path to the product database
    FETSIZE  =  "5" #Number of recommended products at a time
    SHOPPING_SEARCH = "Your url"  # Your search engine
    
    #for all agents
    API_KEY  =  #Your API KEY
    PROXY  =  #Your proxy
    API_BASE  = # Your api_base
    MAX_CHAT_HISTORY  =  "8" #Longest History
    User_Names = "[\"{user_name}\"]" # the name of agents which you want to play  
}
```


Note that if you want to use `WebSearchComponent`, you also need set the config!

```
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
- [x] Option 1.  Run on your terminal

    ```bash
    cd examples
    python run.py --agent Single_Agent/{target_agent}/config.json
    ```

- [x] Option 2. Run on gradio
	
    ```bash
   cd examples
   # `run_gradio.py` depends on `gradio_backend.py`.
   python Single_Agent/run_gradio.py --agent Single_Agent/{target_agent}/config.json
   ```
- [ ] Option 3. Run on fast api
    ```bash
   cd examples
   python run_backend.py --agent Single_Agent/{target_agent}/config.json
   ```


 ### 3. Multi Agent🤖️🤖️   
- [x] Option 1.  Run on your terminal
      
	Modify the config.json

	For example, if you want to play the agent named "Mike" and "Mary"(Support all Agent)
	```
	{ 
	    #for all agents
	    API_KEY  =  #Your API KEY
	    PROXY  =  #Your proxy
	    MAX_CHAT_HISTORY  =  "8" #Longest History
	    User_Names = "[\"Mike\",\"Mary\"]" # the name of agents which you want to play  
	}
	```

    ```bash
    cd examples
    python run.py --agent Multi_Agent/{target_agent}/config.json
    ```

- [x] Option 2. Run on gradio
	
    ```bash
   cd examples/Multi_Agent/{target_agent}
   # `run_gradio.py` depends on `gradio_backend.py`.
   python run_gradio.py
   ```
   Choose the agent you want to perform in the gradio UI.

   **Note:**
   You need to set environment variables first, if you want to run Fiction-Studio demo on gradio.
   ```
   export PROXY="xxx"
   export API_KEY="sk-xxxxxxx"
   ```
   And then
    ```bash
   cd examples/Multi_Agent/novel
   python run_gradio.py
   ```
   
- [ ] Option 3. Run on fast api
    ```bash
   cd examples
   python run_backend.py --agent Multi_Agent/{target_agent}/config.json
   ```

 ### 4. Start with your own Agent🤖️🤖️🤖️  
 #### 1.Write your config.json according to [template.py](https://github.com/aiwaves-cn/agents/blob/master/src/agents/template.py)(more details refer to the [doc](https://ai-waves.feishu.cn/wiki/NIjrw8FR7inGTMkfS5yc5wcvnlg))
 
 #### 2.Run your config.json 

- [x] Option 1.  Run on your terminal

    ```bash
    cd examples
    python run.py --agent config.json
    ```


- [x] Option 2. Run on gradio
	
    ```bash
   cd examples
   # `run_gradio.py` depends on `gradio_backend.py`.
   python run_gradio.py --agent your_config.json
   ```
    
- [ ] Option 3. Run on fast api
    ```bash
   cd examples
   python run_backend.py --agent config.json
   ```

 ### 5. Change your LLM
 refer src/agents/LLM/base_LLM.py
 ```python
def init_LLM(default_log_path,**kwargs):
    LLM_type = kwargs["LLM_type"] if "LLM_type" in kwargs else "OpenAI"
    log_path = kwargs["log_path"].replace("/",os.sep) if "log_path" in kwargs else default_log_path
    if LLM_type == "OpenAI":
        LLM = (
            OpenAILLM(**kwargs["LLM"])
            if "LLM" in kwargs
            else OpenAILLM(model = "gpt-3.5-turbo-16k-0613",temperature=0.3,log_path=log_path)
        )
        return LLM
```
You can change this method to deploy your own LLM.
For example:
 ```python
def init_LLM(default_log_path,**kwargs):
	LLM = Your_LLM()
	return LLM
```
Also, ensure that your LLM's input and output parameters remain consistent with the original LLM, and keep the method name as 'get_response'.
For example:
 ```python
class Your_LLM(LLM):
	def __init__(self,**kwargs) -> None:
		super().__init__()

	def get_response(self,
                    chat_history,
                    system_prompt,
                    last_prompt=None,
                    stream=False,
                    functions=None,
                    function_call="auto",
                    WAIT_TIME=20,
                    **kwargs):
		return chatglm(**kwargs)
```
Please note that it is essential to ensure consistency in streaming output. For instance, when 'stream=True' is set, the function should return a generator, and when 'stream=False,' it should return a string.


 ### 6. SOP generation
 - [x] Option 1.  Single agent🤖️

#### Set  config firstly(examples/sop_generation/gen_single_agent/run.py)

```python
    API_KEY = "API_KEY" # change to your api-key,delete it if you do not need it
    PROXY = "PROXY" # change to your proxy,delete it if you do not need it
    API_BASE = "API_BASE" # change to your api_base,delete it if you do not need it
    target = """a shopping assistant help customer to buy the commodity""" # change to your target
    os.environ["API_KEY"] = API_KEY
    os.environ["PROXY"] = PROXY
    sop["config"]["API_KEY"] = API_KEY
    sop["config"]["PROXY"] = PROXY
```
#### Run the code
```bash
    cd examples/sop_generation/gen_single_agent
    python run.py
```


- [x] Option 2. Multi agent🤖️🤖️🤖️
	
#### Set  config firstly(examples/sop_generation/gen_multi_agent/run.py)
```python
    API_KEY = "API_KEY" # change to your api-key,delete it if you do not need it
    PROXY = "PROXY" # change to your proxy,delete it if you do not need it
    API_BASE = "API_BASE" # change to your api_base,delete it if you do not need it
    target = """a shopping assistant help customer to buy the commodity""" # change to your target
    need_coder = True # True if the scene need output code
    os.environ["API_KEY"] = API_KEY
    os.environ["PROXY"] = PROXY
    sop["config"]["API_KEY"] = API_KEY
    sop["config"]["PROXY"] = PROXY
```
#### Run the code
```bash
    cd examples/sop_generation/gen_multi_agent
    python run.py
```
    
### 🤖️ The Agent Hub

We provide an **AgentHub**, where you can search for interesting Agents shared by us or other developers, try them out or use them as the starting point to customize your own agent. We encourage you to share your customized agents to help others build their own agents more easily! You can share your customized agents by submitting PRs that adds configs and customized codes [here](https://github.com/aiwaves-cn/agents/tree/master/examples/Community_Agent). You can also send us your own config files and codes for customized agents by [email](mailto:contact@aiwaves.cn), and we will share your examples and acknowledge your contribution in future updates!

A WebUI for automatically uploading of your customized agents will be available soon!
 
