Components
==========

To facilitate modularized prompts for Nodes in an AI Autonomous Agent, we've introduced the Components module. Basic codes of the Component class are as follows:

.. code-block:: python

   class Component:
       def __init__(self):
           pass

The Component class is the fundamental class of all components, which plays an important role in storing and modifying various sorts of prompts. We employ parent classes and subclasses to categorize different types of prompts. Two parent classes are available: Prompt Component and Tool Component. Specific requirements, such as rules, styles, and output formats for autonomous agents, are inherited from these parent classes.

Prompt Component: Versatility Redefined
----------------------------------------

Under the PromptComponent class, we've crafted nine distinctive subclasses, each playing an important role in shaping interactions. Basic codes of the PromptComponent class are shown as follows:

.. code-block:: python

   class PromptComponent:
       def __init__(self):
           pass

       @abstractmethod
       def get_prompt(self, agent_dict):
           pass

Apparently, the PromptComponent class serves as a container of all kinds of prompt-components. Different types are created for various sorts of prompts.

1. Demonstration Component:
   Showcases several examples under diverse circumstances, enabling agents to mimic its own style. Basic nodes of the Demonstration Component class are shown as follows:

.. code-block:: python

   class DemonstrationComponent(PromptComponent):
       """
       input a list, the example of the answer.
       """

       def __init__(self, demonstrations):
           super().__init__()
           self.demonstrations = demonstrations

       def add_demonstration(self, demonstration):
           self.demonstrations.append(demonstration)

       def get_prompt(self, agent_dict):
           prompt = "Here are demonstrations you can refer to:\n<demonstrations>"
           for demonstration in self.demonstrations:
               prompt += "\n" + demonstration
           prompt += "</demonstrations>\n"
           return prompt

2. CoT Component:
   Encompasses algebraic procedures, tailor-made for mathematical problems. Basic nodes of the CoT Component class are shown as follows:

.. code-block:: python

   class CoTComponent(PromptComponent):
       """
       input a list, the example of the answer.
       """

       def __init__(self, demonstrations):
           super().__init__()
           self.demonstrations = demonstrations

       def add_demonstration(self, demonstration):
           self.demonstrations.append(demonstration)

       def get_prompt(self, agent_dict):
           prompt = "You need to think in detail before outputting, the thinking case is as follows:\n<demonstrations>"
           for demonstration in self.demonstrations:
               prompt += "\n" + demonstration
           prompt += "</demonstrations>\n"
           return prompt

Seemingly, the codes of the two classes above are absolutely the same. However, the CoT Component class is relatively more complicated. The examples given should contain reasoning steps, including algebraic procedure and logical thinking. By analyzing the examples, your agent will be able to respond with its own thinking steps.

3. Output Component:
   Extracts responses in particular signs, thus enabling Nodes to start its functions. Basic nodes of the Output Component class are shown as follows:

.. code-block:: python

   class OutputComponent(PromptComponent):
       def __init__(self, output):
           super().__init__()
           self.output = output

       def get_prompt(self, agent_dict):
           return f"""Please contact the above to extract <{self.output}> and </{self.output}>, \
               do not perform additional output, please output in strict accordance with the above format!\n"""

4. Rule Component:
   Hosts a spectrum of node-specific settings, intimately tied to contextual tasks. Basic nodes of the Rule Component class are shown as follows:

.. code-block:: python

   class RuleComponent(PromptComponent):
       def __init__(self, rule):
           super().__init__()
           self.rule = rule

       def get_prompt(self, agent_dict):
           return f"""The rule you need to follow is:\n<rule>{self.rule}</rule>.\n"""

5. Task Component:
   Illuminates a node's purpose, defining its role within the agent's architecture. Basic nodes of the Task Component class are shown as follows:

.. code-block:: python

   class TaskComponent(PromptComponent):
       def __init__(self, task):
           super().__init__()
           self.task = task

       def get_prompt(self, agent_dict):
           return f"""The task you need to execute is: <task>{self.task}</task>.\n"""

6. Style Component:
   Illuminates a node's purpose, defining its role within the agent's architecture. Basic nodes of the Style Component class are shown as follows:

.. code-block:: python

   class StyleComponent(PromptComponent):
       def __init__(self, role):
           super().__init__()
           self.role = role

       def get_prompt(self, agent_dict):
           name = agent_dict["name"]
           style = agent_dict["style"]
           return f"""Now your role is:\n<role>{self.role}</role>, your name is:\n<name>{name}</name>. \
               You need to follow the output style:\n<style>{style}</style>.\n"""

7. Last Component:
   Serves as another system prompt which lies at the end of the prompts. Extraordinarily significant requirements or background information is recommended to highlight in this component type. Basic nodes of the Last Component class are shown as follows:

.. code-block:: python

   class LastComponent(PromptComponent):
       def __init__(self, last_prompt):
           super().__init__()
           self.last_prompt = last_prompt

       def get_prompt(self, agent_dict):
           return self.last_prompt

8. Input Component:
   Provide background information for a particular LLM agent. Extraordinarily useful while applied for chatting bots of different statuses. Basic nodes of the Input Component class are shown as follows:

.. code-block:: python

   class InputComponent(PromptComponent):
       def __init__(self):
           super().__init__()

       def get_prompt(self, agent_dict):
           information = agent_dict["information"]
           return f"The information you need to know:\n<information>{information}</information>\n"

9. Customize Component:
   Generate a customized template for a certain agent. Basic nodes of the Customize Component class are shown as follows:

.. code-block:: python

   class CustomizeComponent(PromptComponent):
       def __init__(self, template, keywords) -> None:
           super().__init__()
           self.template = template
           self.keywords = keywords

       def get_prompt(self, agent_dict):
           template_keyword = []
           for keyword in self.keywords:
               current_keyword = agent_dict[keyword]
               template_keyword.append(current_keyword)

           return self.template.format(*template_keyword)

Tool Component: Empowering Functionality
----------------------------------------

The ToolComponent family provides specialized functions crucial for the agent's performance:

1. Extract Component:
   Surgically extracts vital keywords from user input, strategically storing them for reference. Basic codes of the Extract Component class are as follows:

.. code-block:: python

   class ExtractComponent(ToolComponent):
       def __init__(
           self,
           extract_words,
           system_prompt,
           last_prompt=None,
       ):
           super().__init__()
           self.extract_words = extract_words
           self.system_prompt = system_prompt
           self.last_prompt = last_prompt if last_prompt else f"Please strictly adhere to the following format for outputting: <{self.extract_words}>{{the content you need to extract}}</{self.extract_words}>"

       def func(self, agent_dict):
           response = agent_dict["LLM"].get_response(
               agent_dict["long_term_memory"],
               self.system_prompt,
               self.last_prompt,
               agent_dict=agent_dict,
               stream=False,
           )
           for extract_word in self.extract_words:
               key = extract(response, extract_word)
               key = key if key else response
               agent_dict[extract_word] = key

           return {}

2. KnowledgeBase Component:
   Masterfully rephrases user queries, leveraging top answers from the knowledge base using advanced similarity matching, ensuring accurate responses. Basic codes of the Knowledge Component class are as follows:

.. code-block:: python

   class KnowledgeBaseComponent(ToolComponent):
       def __init__(self, top_k, type, knowledge_base):
           super().__init__()
           self.top_k = top_k
           self.type = type
           self.knowledge_base = knowledge_base

           if self.type == "QA":
               (
                   self.kb_embeddings,
                   self.kb_questions,
                   self.kb_answers,
                   self.kb_chunks,
               ) = load_knowledge_base_qa(self.knowledge_base)
           else:
               self.kb_embeddings, self.kb_chunks = load_knowledge_base_UnstructuredFile(
                   self.knowledge_base
               )

       def func(self, agent_dict):
           query = (
               agent_dict["long_term_memory"][-1]
               if len(agent_dict["long_term_memory"]) > 0
               else ""
           )
           knowledge = ""
           query = (
               "Generate a representation for this sentence for retrieving related articles:"
               + query
           )
           query_embedding = get_embedding(query)
           hits = semantic_search(query_embedding, self.kb_embeddings, top_k=50)
           hits = hits[0]
           temp = []
           if self.type == "QA":
               for hit in hits:
                   matching_idx = hit["corpus_id"]
                   if self.kb_chunks[matching_idx] in temp:
                       pass
                   else:
                       knowledge = (
                           knowledge
                           + f"question:{self.kb_questions[matching_idx]},answer:{self.kb_answers[matching_idx]}\n\n"
                       )
                       temp.append(self.kb_answers[matching_idx])
                       if len(temp) == 1:
                           break
               print(hits[0]["score"])
               score = hits[0]["score"]
               if score < 0.5:
                   return {"prompt": "No matching knowledge base"}
               else:
                   return {"prompt": "The relevant content is: " + knowledge + "\n"}
           else:
               for hit in hits:
                   matching_idx = hit["corpus_id"]
                   if self.kb_chunks[matching_idx] in temp:
                       pass
                   else:
                       knowledge = knowledge + f"{self.kb_answers[matching_idx]}\n\n"
                       temp.append(self.kb_answers[matching_idx])
                       if len(temp) == self.top_k:
                           break
               print(hits[0]["score"])
               score = hits[0]["score"]
               if score < 0.5:
                   return {"prompt": "No matching knowledge base"}
               else:
                   print(knowledge)
                   return {"prompt": "The relevant content is: " + knowledge + "\n"}

3. WebSearch Component:
   Establish connections to several Web search engines and acquire information based on the WEB. One of the core components in Tool components part, the highlight of the whole project. Basic codes of the WebSearch Component class are as follows:

.. code-block:: python

   class WebSearchComponent(ToolComponent):
       """search engines"""

       __ENGINE_NAME__: List = ["google", "bing"]

       def __init__(self, engine_name: str, api: Dict):
           """
           :param engine_name: The name of the search engine used
           :param api: Pass in a dictionary, such as {"bing": "key1", "google": "key2", ...}, of course, each value can also be a list, or more complicated
           """
           super(WebSearchComponent, self).__init__()
           """Determine whether the key and engine_name of the api are legal"""

           assert engine_name in WebSearchComponent.__ENGINE_NAME__
           for api_name in api:
               assert api_name in WebSearchComponent.__ENGINE_NAME__

           self.api = api
           self.engine_name = engine_name

           self.search: Dict = {"bing": self._bing_search, "google": self._google_search}

       def _bing_search(self, query: str, **kwargs):
           """Initialize search hyperparameters"""
           subscription_key = self.api["bing"]
           search_url = "https://api.bing.microsoft.com/v7.0/search"
           headers = {"Ocp-Apim-Subscription-Key": subscription_key}
           params = {
               "q": query,
               "textDecorations": True,
               "textFormat": "HTML",
               "count": 10,
           }
           """start searching"""
           response = requests.get(search_url, headers=headers, params=params)
           response.raise_for_status()
           results = response.json()["webPages"]["value"]
           """execute"""
           metadata_results = []
           for result in results:
               metadata_result = {
                   "snippet": result["snippet"],
                   "title": result["name"],
                   "link": result["url"],
               }
               metadata_results.append(metadata_result)
           return {"meta data": metadata_results}

       def _google_search(self, query: str, **kwargs):
           """Initialize search hyperparameters"""
           api_key = self.api[self.engine_name]["api_key"]
           cse_id = self.api[self.engine_name]["cse_id"]
           service = build("customsearch", "v1", developerKey=api_key)
           """start searching"""
           results = (
               service.cse().list(q=query, cx=cse_id, num=10, **kwargs).execute()["items"]
           )
           """execute"""
           metadata_results = []
           for result in results:
               metadata_result = {
                   "snippet": result["snippet"],
                   "title": result["title"],
                   "link": result["link"],
               }
               metadata_results.append(metadata_result)
           return {"meta data": metadata_results}

       def func(self, agent_dict: Dict, **kwargs) -> Dict:
           query = (
               agent_dict["long_term_memory"][-2]["content"]
               if len(agent_dict["long_term_memory"]) > 0
               else " "
           )
           search_results = self.search[self.engine_name](query=query, **kwargs)
           information = ""
           for i in search_results["meta data"][:2]:
               information += i["snippet"]
           return {
               "prompt": "You can refer to the following information to reply:\n"
               + information
           }

       def convert_search_engine_to(self, engine_name):
           assert engine_name in WebSearchComponent.__ENGINE_NAME__
           self.engine_name = engine_name

4. WebCrawl Component:
   Open a single webpage and crawl contents on a certain URL. Basic codes of the WebCrawl Component class are as follows:

.. code-block:: python

   class WebCrawlComponent(ToolComponent):
       """Open a single web page for crawling"""

       def __init__(self):
           super(WebCrawlComponent, self).__init__()

       def func(self, agent_dict: Dict) -> Dict:
           url = agent_dict["url"]
           print(f"crawling {url} ......")
           content = ""
           """Crawling content from URL may need to be carried out according to different websites, such as wiki, Baidu, Zhihu, etc."""
           driver = webdriver.Chrome()
           try:
               """Open URL"""
               driver.get(url)

               """Wait 20 seconds"""
               wait = WebDriverWait(driver, 20)
               wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

               """Crawl code"""
               page_source = driver.page_source

               """Parse"""
               soup = BeautifulSoup(page_source, "html.parser")

               """Concatenate"""
               for paragraph in soup.find_all("p"):
                   content = f"{content}\n{paragraph.get_text()}"
           except Exception as e:
               print("Error:", e)
           finally:
               """Quit"""
               driver.quit()
           return {"content": content.strip()}

5. API Component:
   Start and utilize certain kinds of APIs. Basic codes of the API Component class are as follows:

.. code-block:: python

   class APIComponent(ToolComponent):
       def __init__(self):
           super(APIComponent, self).__init__()

       def func(self, agent_dict: Dict) -> Dict:
           pass

6. Static Component:
   Create a special type of component for states. Static components only operate under given requirements and don't have to generate its own intelligence based on LLM. Basic codes of the Static Component class are as follows:

.. code-block:: python

   class StaticComponent(ToolComponent):
       def __init__(self, output):
           super().__init__()
           self.output = output

       def func(self, agent_dict):
           outputdict = {"response": self.output}
           return outputdict

7. Function Component:
   Utilize the 'function call' method and store particular args of the particular Agent. Basic codes of the Function Component class are as follows:

.. code-block:: python

   class FunctionComponent(ToolComponent):
       def __init__(
           self,
           functions,
           function_call="auto",
           response_type="response",
           your_function=None,
       ):
           super().__init__()
           self.functions = functions
           self.function_call = function_call
           self.parameters = {}
           self.available_functions = {}
           self.response_type = response_type
           if your_function:
               function_name = your_function["name"]
               function_content = your_function["content"]
               exec(function_content)
               self.available_functions[function_name] = eval(function_name)

           for function in self.functions:
               self.parameters[function["name"]] = list(
                   function["parameters"]["properties"].keys()
               )
               self.available_functions[function["name"]] = eval(function["name"])

       def func(self, agent_dict):
           messages = agent_dict["long_term_memory"]
           outputdict = {}
           query = (
               agent_dict["long_term_memory"][-1]
               if len(agent_dict["long_term_memory"]) > 0
               else " "
           )
           key_history = get_key_history(
               query,
               agent_dict["long_term_memory"][:-1],
               agent_dict["chat_embeddings"][:-1],
           )
           response = agent_dict["LLM"].get_response(
               messages,
               None,
               functions=self.functions,
               stream=False,
               function_call=self.function_call,
               key_history=key_history,
           )
           response_message = response
           if response_message.get("function_call"):
               function_name = response_message["function_call"]["name"]
               fuction_to_call = self.available_functions[function_name]
               function_args = json.loads(response_message["function_call"]["arguments"])
               input_args = {}
               for args_name in self.parameters[function_name]:
                   input_args[args_name] = function_args.get(args_name)
               function_response = fuction_to_call(**input_args)
               if self.response_type == "response":
                   outputdict["response"] = function_response
               elif self.response_type == "prompt":
                   outputdict["prompt"] = function_response

           return outputdict

(The above material is from prompt master jlwu & prompt noob stephen_qs)
