import copy
import os
from myagent import Node, MyAgent, ask_gpt, Client
from typing import List, Tuple
from PROMPT import NOVEL_PROMPT
from myutils import print_log, new_parse
import json

class FirstNode(Node):
    def __init__(
        self,
        name: str,
        agents: List[MyAgent],
        start_agent_name: str,
        start_agent_query: str,
        summary_agent: MyAgent = None,
        save: bool=True,
        stream_output: bool=True,
        output_func=None,
    ):
        super(FirstNode, self).__init__(agents, summary_agent, save)
        self.name = name
        self.output_func = output_func
        self.stream_output = stream_output
        self.start_agent_name = start_agent_name
        self.start_agent_query = start_agent_query
        if self.stream_output:
            print_log("stream output ......")
        assert self.start_agent_name in self.agents, \
            f"invalid agent name `{self.start_agent_name}`"

    def start(self):
        self.agents[self.start_agent_name].prepare_message(
            self.start_agent_query+"\n"+self.agents[self.start_agent_name].query
        )
        self.agents[self.start_agent_name].output_message(
            recorder=self.recorder, stream=self.stream_output, output_func=self.output_func,
            node_name=self.name
        )
        # if self.stream_output:
        #     print(f"【{self.start_agent_name}】 ", end="")
        #     for chunk in self.agents[self.start_agent_name].send_message(recorder=self.recorder, stream=self.stream_output):
        #         if chunk is not None:
        #             print(chunk, end="")
        #     print()
        # else:
        #     self.agents[self.start_agent_name].send_message(recorder=self.recorder, stream=self.stream_output)
        #     self.print(agent_name=self.start_agent_name)

    def communicate(self):
        for turn in range(2):
            for agent_name in ["Zoe", "Abby", "Elmo"]:
                history = self.recorder.prepare(
                    agent_name=agent_name,
                    agents=self.agents,
                    return_dict=False
                )
                query = self.agents[agent_name].query
                if isinstance(history, str):
                    history = f"The following are the conversations of others, with what someone says wrapped in `<name>...</name>`: \n{history}\n{query}"
                elif isinstance(history, list):
                    history.append({"role": "user", "content": query})
                self.agents[agent_name].prepare_message(
                    history
                )
                self.agents[agent_name].output_message(
                    recorder=self.recorder, stream=self.stream_output,
                    output_func=self.output_func, node_name=self.name
                )
                # if not self.stream_output:
                #     self.agents[agent_name].send_message(
                #         recorder=self.recorder, stream=self.stream_output)
                #     self.print(agent_name=agent_name)
                # else:
                #     print(f"【{agent_name}】 ", end="")
                #     for chunk in self.agents[agent_name].send_message(
                #         recorder=self.recorder, stream=self.stream_output):
                #         if chunk is not None:
                #             print(chunk, end="")
                #     print()

    def end(self):
        temperature_copy = MyAgent.TEMPERATURE
        MyAgent.TEMPERATURE = 0
        message: str = self.summary_agent.query.format(
            self.recorder.prepare(agent_name="all", agents=self.agents, return_dict=False)
        )
        self.summary_agent.prepare_message(message)
        self.summary_agent.output_message(
            recorder=self.recorder, stream=self.stream_output,
            output_func=self.output_func, node_name=self.name
        )
        # if not self.stream_output:
        #     self.summary_agent.send_message(recorder=self.recorder, stream=self.stream_output)
        #     print(f"【summary】{self.summary_agent.get_message(index=-1)}")
        # else:
        #     print("【summary】 ", end="")
        #     for
        MyAgent.TEMPERATURE = temperature_copy
        content = self.summary_agent.get_message(index=-1)
        # start to parse ====================================================
        data_dict = new_parse(content, labels=[], return_dict=True)
        # 1. parse character
        characters_card: dict = {}
        for key in data_dict['CHARACTERS']:
            """default success"""
            if 'CHARACTER' in key:
                characters_card[
                    data_dict['CHARACTERS'][key]['NAME']
                ] = {
                    "role_name": data_dict['CHARACTERS'][key]['NAME'],
                    "gender": data_dict['CHARACTERS'][key]['GENDER'],
                    "age": data_dict['CHARACTERS'][key]['AGE'],
                    "occupation": data_dict['CHARACTERS'][key]['WORK'],
                    "personality": data_dict['CHARACTERS'][key]['PERSONALITY'],
                    "speaking_style": data_dict['CHARACTERS'][key]['SPEECH STYLE'],
                    "relation_with_others": data_dict['CHARACTERS'][key]['RELATION'],
                    "background": data_dict['CHARACTERS'][key]['BACKGROUND']
                }
        # file_name = "character_settings.json"
        try:
            os.mkdir("novel_outline")
        except:
            pass
        file_name = "./novel_outline/character_settings.json"
        with open(file_name, "w") as json_file:
            json.dump(characters_card, json_file, ensure_ascii=False)
            print("Save Successfully")
        # 2. converted to markdown
        return_content = "<CHARACTERS>\n# Character\n> There are a total of {} characters\n\n".format(
            data_dict['CHARACTERS']['TOTAL NUMBER'],
        )
        cnt = 1
        for key in data_dict['CHARACTERS']:
            """default success"""
            if 'CHARACTER' in key:
                return_content += "## Character{}\n- Gender: {}\n- Name: {}\n- Age: {}\n- Work: {}\n- Personality: {}\n- Speaking Style: {}\n- Relation with Others: {}\n- Background: {}\n\n".format(
                    cnt, data_dict['CHARACTERS'][key]['GENDER'], data_dict['CHARACTERS'][key]['NAME'],
                    data_dict['CHARACTERS'][key]['AGE'],
                    data_dict['CHARACTERS'][key]['WORK'],
                    data_dict['CHARACTERS'][key]['PERSONALITY'], data_dict['CHARACTERS'][key]['SPEECH STYLE'],
                    data_dict['CHARACTERS'][key]['RELATION'],
                    data_dict['CHARACTERS'][key]['BACKGROUND']
                )
                cnt += 1
        return_content += "</CHARACTERS>\n\n<OUTLINE>\n# outline\n> There are a total of {} chapters\n\n".format(
            data_dict['OUTLINE']['TOTAL NUMBER']
        )
        cnt = 1
        for key in data_dict['OUTLINE']:
            if 'SECTION' in key:
                return_content += "## Chapter {} {}\n- Characters Involved: {}\n- Story Summary: {}\n\n".format(
                    cnt, data_dict['OUTLINE'][key]['TITLE'], data_dict['OUTLINE'][key]['CHARACTER INVOLVED'],
                    data_dict['OUTLINE'][key]['ABSTRACT']
                )
                cnt += 1
        return_content += "</OUTLINE>"
        return return_content

    def print(self, agent_name):
        print(f"【{agent_name}】{self.agents[agent_name].get_message(index=-1)}")

class SecondNode(Node):
    def __init__(
        self,
        name: str,
        agents: List[MyAgent],
        start_agent_name: str,
        start_agent_query: str,
        summary_agent: MyAgent = None,
        save: bool=True,
        stream_output:bool=True,
        output_func=None
    ):
        super(SecondNode, self).__init__(agents, summary_agent, save)
        self.name = name
        self.stream_output = stream_output
        self.start_agent_name = start_agent_name
        self.start_agent_query = start_agent_query
        self.output_func = output_func
        assert self.start_agent_name in self.agents, \
            f"invalid agent name `{self.start_agent_name}`"
        self.temperature = [0.3, 0.3, 0.3]
        if self.stream_output:
            print("streaming output ......")

    def start(self):
        MyAgent.TEMPERATURE = self.temperature[0]
        self.agents[self.start_agent_name].prepare_message(
            self.start_agent_query+"\n"+self.agents[self.start_agent_name].query
        )
        self.agents[self.start_agent_name].output_message(
            recorder=self.recorder, stream=self.stream_output, output_func=self.output_func,
            node_name=self.name
        )
        # self.agents[self.start_agent_name].send_message(recorder=self.recorder)
        # print(f"【{self.start_agent_name}】{self.agents[self.start_agent_name].get_message(index=-1)}")
        # self.print(agent_name=self.start_agent_name)

    def communicate(self):
        MyAgent.TEMPERATURE = self.temperature[1]
        """to store output，e.g. Chapter i"""
        self.output_memory = []
        for turn in range(2):
            for agent_name in ["Oscar", "Bert", "Ernie"]:
                if agent_name == "Bert":
                    MyAgent.TEMPERATURE = 0.3
                else:
                    MyAgent.TEMPERATURE = turn*0.1 + 0.5
                history = self.recorder.prepare(
                    agent_name=agent_name,
                    agents=self.agents,
                    return_dict=False
                )

                # print(f"===========START {agent_name}==========")
                # print(history)
                # print("================END===============")
                query = self.agents[agent_name].query
                if isinstance(history, str):
                    history = f"The following are the conversations of others, with what someone says wrapped in `<name>...</name>`: \n{history}\n{query}"
                elif isinstance(history, list):
                    history.append({"role": "user", "content": query})
                self.agents[agent_name].prepare_message(
                    history
                )
                self.agents[agent_name].output_message(
                    recorder=self.recorder, stream=self.stream_output,
                    output_func=self.output_func, node_name=self.name
                )
                # self.agents[agent_name].send_message(recorder=self.recorder)
                # self.print(agent_name=agent_name)

    def end(self):
        MyAgent.TEMPERATURE = self.temperature[2]

        content = self.agents["Bert"].get_message(-1)
        index = -1
        while "none" in content.lower():
            index -= 1
            content = self.agents["Bert"].get_message(index)
        try:
            def save(data: dict):
                for idx, (key, value) in enumerate(data.items()):
                    # file_name = f"{self.name.replace(' ', '')}-plot-{idx+1}.json"
                    try:
                        os.mkdir("novel_outline")
                    except:
                        pass
                    file_name = f"./novel_outline/{self.name.replace(' ', '')}-plot-{idx+1}.json"
                    _characters:str = value["CHARACTER INVOLVED"]
                    characters = ask_gpt(
                        system_prompt="You are very good at structuring text, please make sure you structure your output as follows, with no other extra chars, in addition, extract from the given text as much as possible, rather than summarizing.",
                        input=f"""Here is a sentence: "{_characters}"\n What are the names of the people in the sentence above? Please use a semicolon to separate the names, e.g. "name 1; name 2", taking care not to add any words before or after."""
                    ).split(";")
                    characters = [c.strip() for c in characters]
                    print("mike",characters)
                    output = {
                        "plot": value["DESCRIPTION"],
                        "characters": characters #value["CHARACTER INVOLVED"]
                    }
                    with open(file_name, "w") as json_file:
                        json.dump(output, json_file, ensure_ascii=False)
                        # json_file.writelines(output)
            # data_dict = parse(copy.deepcopy(content), labels=["CONTENT"], return_dict=True)["CONTENT"]
            data_dict = new_parse(content, labels=["CONTENT"], return_dict=True)["CONTENT"]
            if len(data_dict) == 0 or data_dict is None:
                assert False
            save(data_dict)
            data_str = new_parse(content, labels=["CONTENT"], return_dict=False)
            if len(data_str) == 0:
                assert False
            print_log("Save successfully")
            print(data_str)

            if self.output_func:
                self.output_func(0, "Recorder", data_str[0], self.name)
                self.output_func(21, "Recorder", data_str[1:], self.name)
            return data_str
        except Exception as e:
            raise e


    def print(self, agent_name):
        print(f"【{agent_name}】{self.agents[agent_name].get_message(index=-1)}")

def generate_first_agents(task_prompt:str=None) -> Tuple[List[MyAgent], MyAgent]:
    prompts_set = NOVEL_PROMPT["Node 1"]
    if task_prompt is not None:
        print_log("The default task prompt has been replaced!")
        NOVEL_PROMPT["Node 1"]["task"] = task_prompt
    prompts_task = prompts_set["task"]
    prompts_agents = prompts_set["agents"]
    agents_list = []
    for agent_name in prompts_agents:
        agents_list.append(
            MyAgent(
                name=agent_name,
                SYSTEM_PROMPT=prompts_agents[agent_name]["system"].format(
                    prompts_task, prompts_agents[agent_name]["output"]
                ),
                query=prompts_agents[agent_name]["query"].format(
                    prompts_agents[agent_name]["output"]
                )
            )
        )
    summary_agent = MyAgent(
        name="summary",
        SYSTEM_PROMPT=prompts_set["summary"]["system"].format(
            prompts_task, prompts_set["summary"]["output"]
        ),
        query=prompts_set["summary"]["query"]
    )

    return agents_list, summary_agent

def generate_second_agents() -> Tuple[List[MyAgent], MyAgent]:
    prompts_set = NOVEL_PROMPT["Node 2"]
    prompts_task = prompts_set["task"]  # .format(outline, other)
    prompts_agents = prompts_set["agents"]
    agents_list = []
    for agent_name in prompts_agents:
        agents_list.append(
            MyAgent(
                name=agent_name,
                SYSTEM_PROMPT=prompts_agents[agent_name]["system"].format(
                    prompts_task, prompts_agents[agent_name]["output"]
                ),
                query=prompts_agents[agent_name]["query"].format(
                    prompts_agents[agent_name]["output"]
                )
            )
        )
    summary_agent = MyAgent(
        name="summary",
        SYSTEM_PROMPT=prompts_set["summary"]["system"].format(
            prompts_task, prompts_set["summary"]["output"]
        ),
        query=prompts_set["summary"]["query"]
    )

    return agents_list, summary_agent

def run_node_1(stream_output:bool=False, output_func=None,
               start_agent_name:str="Elmo", start_agent_query:str="Let's start by writing a first draft of the character settings.",
               task_prompt=None):
    print("node 1 start ...")
    first_agents, first_summary = generate_first_agents(task_prompt=task_prompt)
    first_node = FirstNode(
        name="Node 1",
        agents=first_agents,
        summary_agent=first_summary,
        save=True,
        start_agent_name=start_agent_name,
        start_agent_query=start_agent_query,
        stream_output=stream_output,
        output_func=output_func,
    )
    output = first_node.run()
    print("node 1 done ...")
    return output

def run_node_2(outline, node_start_index=2, stream_output:bool=False, output_func=None):
    num2cn = ["ONE","TWO","THREE","FOUR","FIVE","SIX","SEVEN","EIGHT","NINE","TEN","ELEVEN","TWELVE"]
    def generate_task_end_prompt(memory: list) -> str:
        if len(memory) == 0:
            return "\nThere are 5 chapters in total, please enrich the plot of the first chapter according to the outline above, taking care to be storytelling, logical, mainly in third person point of view, not involving description of dialogues, and without empty words. The plot of the first chapter is at least 800 words."
        else:
            start_prompt = f"\nThe following are the contents of chapter {', '.join(num2cn[0:len(memory)])}, which have been expanded: \n<EXPANDED>\n"
            for i in range(len(memory)):
                start_prompt = f"\n{start_prompt}<CHAPTER {i+1}>\n{memory[i]}\n</CHAPTER {i+1}>"
            start_prompt += "\n</EXPANDED>\n"
            end_prompt = f"\nPlease, based on the outline above and the content of chapter {', '.join(num2cn[0:len(memory)])}, which have been expanded, to enrich the plot of chapter {num2cn[len(memory)]}, " \
                         f"Content is noted to be storytelling, logical, and in the third person point of view, not involving descriptions of dialog, and without empty words. The plot of chapter {num2cn[len(memory)]} is at least 800 words."
            return start_prompt + end_prompt

    output_memory = []      
    start_agent_names = ["Ernie", "Ernie", "Ernie", "Ernie", "Ernie"]
    start_agent_queries = [f"Let's start by expanding on chapter {num2cn[i]} as required" for i in range(5)] 
    ORIGIN_TASK_PROMPT = NOVEL_PROMPT["Node 2"]["task"]
    ORIGIN_QUERY_PROMPT = {}
    ORIGIN_SUMMARY_PROMPT = NOVEL_PROMPT["Node 2"]["summary"]["query"]
    for idx in range(3):
        node_idx = idx + node_start_index

        NOVEL_PROMPT["Node 2"]["task"] = ORIGIN_TASK_PROMPT.format(
            outline,
            generate_task_end_prompt(output_memory)
        )

        for agent_name in NOVEL_PROMPT["Node 2"]["agents"]:
            if agent_name not in ORIGIN_QUERY_PROMPT:
                ORIGIN_QUERY_PROMPT[agent_name] = NOVEL_PROMPT["Node 2"]["agents"][agent_name]["query"]
            NOVEL_PROMPT["Node 2"]["agents"][agent_name]["query"] = ORIGIN_QUERY_PROMPT[agent_name].format(
                num2cn[idx], "{}"
            )
        NOVEL_PROMPT["Node 2"]["summary"]["query"] = ORIGIN_SUMMARY_PROMPT.format(num2cn[idx], num2cn[idx], "{}")   
        start_agent_name = start_agent_names[idx]
        start_agent_query = start_agent_queries[idx]
        
        print(f"node {node_idx} starting ......")
        second_agents, second_summary = generate_second_agents()
        second_node = SecondNode(
            name=f"Node {node_idx}",
            agents=second_agents,
            summary_agent=second_summary,
            save=True,
            start_agent_name=start_agent_name,
            start_agent_query=start_agent_query, 
            stream_output=stream_output,
            output_func=output_func
        )
        
        output_memory.append(
            second_node.run()
        )
       

def show_in_gradio(state, name, chunk, node_name):

    if state == 30:
        Client.server.send(str([state, name, chunk, node_name])+"<SELFDEFINESEP>")
        return

    if name.lower() in ["summary", "recorder"]:
        """It is recorder"""
        name = "Recorder"
        if state == 0:
            state = 22
        else:
            state = 21
    else:
        if Client.current_node != node_name and state == 0:
            state = 12
            Client.current_node = node_name
        elif Client.current_node != node_name and state != 0:
            assert False
        else:
            state = 10 + state
    Client.server.send(str([state, name, chunk, node_name])+"<SELFDEFINESEP>")


if __name__ == '__main__':

    MyAgent.SIMULATION = False
    MyAgent.TEMPERATURE = 1.0
    stream_output = True
    output_func = show_in_gradio
    output_func = None

    if output_func is not None:
        global client
        client = Client()

        client.listening_for_start()
        Client.server = client.start_server()
        next(Client.server)

        outline = run_node_1(
            stream_output=stream_output,
            output_func=output_func,
            start_agent_name=Client.cache["start_agent_name"],
            start_agent_query=Client.cache["start_agent_query"],
            task_prompt=Client.cache["task"]
        )
    else:
        outline = run_node_1(
            stream_output=stream_output,
            output_func=output_func
        )
    print(outline)
    # assert False
    run_node_2(outline, stream_output=stream_output, output_func=output_func)
    print("done")
