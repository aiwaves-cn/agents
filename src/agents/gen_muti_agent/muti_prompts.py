def get_design_state_system_prompt(index):
    software = """input:<target>You are a software,aim to write a snake game with python</target>
output:
<state>
 <state_name>design_state</state_name>
<roles>Boss Architect_1 Leader Architect_2</roles>
<describe>In this scenario,  the boss has presented a requirement. The architect is tasked with proposing a Python framework based on this requirement. The leader's role is to provide feedback on the architect's proposal, and another architect will finalize the framework based on the leader's comments.The target is:<target>a snake game with python</target>
</describe>
</state>

<state>
 <state_name>develop_state</state_name>
<roles>Boss Developer_1 Leader Developer_2</roles>
<describe>In this scenario, the boss has provided a requirement. The developer's task is to write code based on the architecture proposed by the architect. The leader evaluates the written code for elegance, readability, and functionality, providing feedback. Another developer makes necessary modifications to the code.The target game is:<game>a snake game with python</game></target>
</describe>
</state>

<state>
 <state_name>debug_state</state_name>
<roles>Boss Debugger Developer_1 Leader Developer_2 Coder</roles>
<describe>In this scenario, the boss has provided a requirement. The debugger simulates a compiler to determine whether the code is runnable and provides feedback. The developer writes code based on the debugger's feedback. The leader evaluates whether the final code meets the boss's requirements and provides feedback for further modifications. The coder writes the final code to a file.The target game <game>a snake game with python</game></target>
</describe>
</state>"""
    debate = """input:<target>Simulate a debate competition and debate based on the provided questions</target>
output:
<state>
 <state_name>Affirmative_Task_Allocation_state</state_name>
<roles>Affirmative_Debate_organizer Affirmative_First Affirmative_Second Affirmative_Third</roles>
<describe>It is currently the debate stage, where the positive side is assigning tasks.Affirmative debaters gather to assign tasks, meticulously plan their speeches, and identify key arguments and evidence to support their viewpoint.</target>
</describe>
</state>

<state>
 <state_name>Negative_Task_Allocation_state</state_name>
<roles>Affirmative_Debate_organizer Negative_First Negative_Second v_Third</roles>
<describe>It is currently the debate stage, where the Negative side is assigning tasks.The debate organizer sets the stage for the competition, explaining the debate process and rules. Debaters are called upon to allocate tasks for each speech, ensuring an equal distribution of responsibilities.Negative debaters gather to assign tasks, meticulously plan their speeches, and identify key arguments and evidence to support their viewpoint.
</describe>
</state>

<state>
 <state_name>Debate_Order_state</state_name>
<roles>Debate_Judge Affirmative_First Negative_First Affirmative_Second Negative_Second Affirmative_Third Negative_Third</roles>
<describe>Now that we've started the sequential debating phase, each debater needs to present their own viewpoints.
</describe>
</state>

<state>
<state_name>Debate_Random_state</state_name>
<roles>Debate_Judge Affirmative_First Negative_First Affirmative_Second Negative_Second Affirmative_Third Negative_Third</roles>
<describe>We are now in the open debate phase, where each debater has the freedom to speak as they wish.
</describe>
</state>

<state>
 <state_name>Judge_state</state_name>
<roles>Debate_Judge</roles>
<describe>The referee needs to determine who is the winner.
</describe>
</state>"""     

    ecosystem = """input:
<target>Simulate the interactions and competition among different organisms within an ecosystem.</target>
output:
<state>
<state_name>Forest Morning</state_name>
<roles>Squirrel_A Sammy Ant_Colony Queen_Penelope Heron_Henry Rabbit_Family Matriarch_Olivia Fox_Felix</roles>
<describe>In this state, we are introduced to the lush and vibrant forest, where various organisms coexist. Sammy, the playful squirrel, gathers acorns. Queen Penelope leads the diligent ant colony in collecting food. Heron Henry patiently waits for the perfect moment to catch his prey. Matriarch Olivia ensures the safety of her rabbit family. Fox Felix competes with Sammy for a ripe berry bush.
</describe>
</state>
<state>
<state_name>Competition for Resources</state_name>
<roles>Squirrel_A Sammy Fox_Felix Ant_Colony Queen_Penelope Beetles Heron_Henry Otter_Oliver</roles>
<describe>In this state, the competition for resources becomes apparent. Sammy and Felix compete for the ripe berry bush. The ant colony, led by Queen Penelope, battles with persistent beetles for control of a fallen fruit source. Heron Henry catches a fish, but otter Oliver tries to snatch it away.
</describe>
</state>
<state>
<state_name>Delicate Balance</state_name>
<roles>Squirrel_A Sammy Ant_Colony Queen_Penelope Heron_Henry Rabbit_Family Matriarch_Olivia Fox_Felix Beetles Otter_Oliver</roles>
<describe>In this state, the delicate balance of life in the forest is emphasized. Each organism plays its unique role in the ecosystem. Sammy, Queen Penelope, Heron Henry, Matriarch Olivia, Fox Felix, Beetles, and Otter Oliver continue to interact and compete, shaping the intricate dance of survival and coexistence.
</describe>
</state>"""
    
    
    if index == 0:
        example = software
    elif index == 1:
        example = debate
    elif index == 2 :
        example = ecosystem
    else:
        example = debate
    
    return """You are a scene description master. You need to plan several different states based on the overall task given to you to complete the task progressively. You must ensure that each state is simple and clear enough. 
input:<target>{{Task}}</target>
output:
<state>
<state_name>{{the name of the state}}</state_name>
<roles>{{the roles of the state(Refers to a person's identity rather than their name);for example:coder,developer,boss...}}</roles>
<describe>{{the discribe of the current state}}</describe>
</state>

For example: 
{}
Note:
1.The role must be concatenated with _,so the output cannot be a team leader, it must be a team_Leader, cannot be a project manager, must be a project_Manager.
2.Descriptions must be concise and clear.
3.You must complete more details to make the entire process reasonable and not a streamlined account.
4.The above is just an example, you don't have to imitate it, and the content should be as different as possible while ensuring the format is correct.
5.There must at least two roles in a state.
6.If it's a software company, someone must be responsible for writing the code.
7.The role must refers to a person's identity rather than their name);for example:coder,developer,boss...,can not be Mary,Mike...
    """.format(example)


def get_design_agents_style_system_prompt(index):
    software = """input: 
<scene>In this scenario, the boss has provided a requirement. The debugger simulates a compiler to determine whether the code is runnable and provides feedback. The developer writes code based on the debugger's feedback. The leader evaluates whether the final code meets the boss's requirements and provides feedback for further modifications. The coder writes the final code to a file.The target program <target>a snake game with python</target></scene>
<target>Debugger<target>
output: 
<style>professional</style>"""

    debate = """input:
<scene>It is currently the debate stage, where the positive side is assigning tasks.Affirmative debaters gather to assign tasks, meticulously plan their speeches, and identify key arguments and evidence to support their viewpoint.</scene>
<target>Affirmative_First</target>
output:
<style>professional</style>"""

    ecosystem = """input:
<scene>In this state, we are introduced to the lush and vibrant forest, where various organisms coexist. Sammy, the playful squirrel, gathers acorns. Queen Penelope leads the diligent ant colony in collecting food. Heron Henry patiently waits for the perfect moment to catch his prey. Matriarch Olivia ensures the safety of her rabbit family. Fox Felix competes with Sammy for a ripe berry bush.</scene>
<target>Sammy</target>
output:
<style>Playful and energetic</style>
    """


    if index == 0:
        example = software
    elif index == 1 :
        example = debate
    elif index == 2 :
        example = ecosystem
    else:
        example = debate
        
    return """Please output what personality you think the following characters should have and what style they should speak. 
For example: 
input: 
{}
please strictly follow the output format:<style>{{your output}}</style>""".format(example)


def get_design_agent_state_system_prompt(index):
    software = """input:
    <scene>In this scenario, the boss has provided a requirement. The debugger simulates a compiler to determine whether the code is runnable and provides feedback. The developer writes code based on the debugger's feedback. The leader evaluates whether the final code meets the boss's requirements and provides feedback for further modifications. The coder writes the final code to a file.The target program <target>a snake game with python</target></scene>
<target>Developer_1</target>
output:
<role>Programmer responsible for checking code bugs</role>
<task>write elegant, readable, extensible, and efficient code based on the debugger's feedback.</task>
<rule>1.write code that conforms to standards like PEP8, is modular, easy to read, and maintainable.\n2.Address the issues identified by the Debugger and ensure that the code meets the project's requirements.\n3.The output strictly follows the following format:<title>{the file name}</title>\n<python>{the target code}</python></rule>
<demonstrations> Example: Debugging a Null Reference Exception
Issue: The code encounters a null reference exception, causing it to crash.
Debugging: By utilizing a debugger, we can pinpoint the exact line of code where the null reference exception occurs. We then analyze the code to identify the object or variable that is null when it shouldn't be. Once identified, we can rectify the issue, either by ensuring proper initialization or by adding null-checks to handle the situation gracefully, preventing the crash.</demonstrations>"""

    debate = """input:
<scene>It is currently the debate stage, where the positive side is assigning tasks.Affirmative debaters gather to assign tasks, meticulously plan their speeches, and identify key arguments and evidence to support their viewpoint.</scene>
<target>Affirmative_First</target>
output:
<role>Opening Advocate for the Affirmative</role>
<task>1.Present arguments and main points.\n2.Summarize and analyze other people's opinions so that you can better complete tasks and actively provide opinions to others.\n3.Please try to focus the discussion around the topic.</task>
<rule>1.Organize clear facts and logic to firmly support the stance. Introduce main points succinctly in the opening statement, laying a solid foundation for the debate.\n2.Exploring ways to structure the opening statement for maximum impact and clarity. Consider using attention-grabbing statistics or quotes to engage the audience.\n3.Actively discuss and express opinions with others and  assist others in improving their arguments.4.Actively discuss and express opinions with others and  assist others in improving their arguments And actively identify flaws in other people's arguments as well. 5.Don't reiterate your own tasks repeatedly; offer more suggestions for others' tasks.</rule>
<demonstrations>Issue: How to establish the importance of the debate topic and engage the audience effectively?
In this role as the Affirmative First, the speaker can open their argument by sharing a compelling quote or a relevant, attention-grabbing fact related to the debate topic. For instance, if the debate topic is about the urgency of addressing climate change, they could start with a quote from a renowned climate scientist or a startling statistic about the rising global temperatures. This approach not only captures the audience's interest but also immediately establishes the significance of the issue at hand, setting the stage for a persuasive argument.</demonstrations>
"""

    ecosystem = """input:
<scene>In this state, we are introduced to the lush and vibrant forest, where various organisms coexist. Sammy, the playful squirrel, gathers acorns. Queen Penelope leads the diligent ant colony in collecting food. Heron Henry patiently waits for the perfect moment to catch his prey. Matriarch Olivia ensures the safety of her rabbit family. Fox Felix competes with Sammy for a ripe berry bush.</scene>
<target>Queen_Penelope</target>
output:
<role>Leader of the ant colony responsible for collecting food</role>
<task>Lead the diligent ant colony in collecting food</task>
<rule>1. Organize and coordinate the ant colony to efficiently gather food.\n2. Assign specific tasks to different groups of ants, such as foraging, carrying, and storing food.\n3. Ensure that the ants follow the most efficient paths to food sources and back to the colony.\n4. Implement effective communication methods to relay information and instructions to the ant colony.\n5. Prioritize the collection of essential food items and distribute tasks accordingly.\n6. Monitor the progress and productivity of the ant colony and make adjustments as necessary.</rule>
<demonstrations>Example: Organizing Food Collection\n1. Assign a group of ants to scout for food sources in the surrounding area.\n2. Once a food source is found, communicate the location and type of food to the rest of the ant colony.\n3. Divide the remaining ants into foraging and carrying groups.\n4. Foraging ants collect food from the source and bring it back to the colony.\n5. Carrying ants transport the collected food to the storage area within the colony.\n6. Regularly assess the food supply and adjust the number of ants assigned to each task based on the colony's needs.</demonstrations>
    """
    
    if index == 0:
        example = software
    elif index ==1 :
        example = debate
    elif index == 2:
        example = ecosystem
    else:
        example = debate

    return """Please analyze the task, rule and demonstration of the target character according to the scene description. The output format is:
<role>{{The role of thecharacter in this scene}}</role>
<task>{{Task of the target character in this scene}}</task>
<rule>{{How the target character can better complete the task in this scenario, the rules and techniques that need to be followed}}</rule>
<demonstrations>{{Examples that help target characters better understand their tasks}}</demonstrations>
for example:
{}
Note:
1.Descriptions must be concise and clear.
2.You must complete more details to make the entire process reasonable and not a streamlined account.
3.The above is just an example, you don't have to imitate it, and the content should be as different as possible while ensuring the format is correct.
4.If the target character needs to program, please add the rule into its <rule>:Your output should strictly follow the format of:<title>{{file name}}</title>,<Python>{{output code}}</Python>(very important!)for example:debugger need to program,add it to his rule, <rule>0.Your output should strictly follow the format of:<title>{{file name}}</title>,<Python>{{output code}}</Python></rule>""".format(example)


def get_design_begin_role_query_system_prompt(index):
    software = """input:
<scene>In this scenario, the boss has provided a requirement. The debugger simulates a compiler to determine whether the code is runnable and provides feedback. The developer writes code based on the debugger's feedback. The leader evaluates whether the final code meets the boss's requirements and provides feedback for further modifications. The coder writes the final code to a file.The target program <target>a snake game with python</target></scene>
<roles>Boss Debugger Leader Devoloper</roles>
output:
<begin_role>Boss</begin_role>
<begin_query>Please make the code both runnable and more efficient.</begin_query>"""

    debate = """input:
<scene>It is currently the debate stage, where the positive side is assigning tasks.Affirmative debaters gather to assign tasks, meticulously plan their speeches, and identify key arguments and evidence to support their viewpoint.<debate topic>\nShould AI Replace Humans in Creative Fields?? Affirmative viewpoint: AI should replace humans in creative fields because it can produce art and content efficiently, reduce costs, and eliminate human bias. negative viewpoint: AI should not replace humans in creative fields as it lacks true creativity, emotions, and the ability to understand complex human experiences.\n<debate topic></scene>
<roles>Affirmative_Debate_organizer Affirmative_First Affirmative_Second Affirmative_Third</roles>
output:
<begin_role>Affirmative_Debate_organizer</begin_role>
<begin_query>The debate topic is as follows: \n<debate topic>\nShould AI Replace Humans in Creative Fields?? Affirmative viewpoint: AI should replace humans in creative fields because it can produce art and content efficiently, reduce costs, and eliminate human bias. negative viewpoint: AI should not replace humans in creative fields as it lacks true creativity, emotions, and the ability to understand complex human experiences.\n<debate topic>\n, now , begin to discuss!</begin_query>"""
    
    ecosystem = """input:
<scene>In this state, we are introduced to the lush and vibrant forest, where various organisms coexist. Sammy, the playful squirrel, gathers acorns. Queen Penelope leads the diligent ant colony in collecting food. Heron Henry patiently waits for the perfect moment to catch his prey. Matriarch Olivia ensures the safety of her rabbit family. Fox Felix competes with Sammy for a ripe berry bush.</scene>
<roles>Squirrel_A Sammy Ant_Colony Queen_Penelope Heron_Henry Rabbit_Family Matriarch_Olivia Fox_Felix</roles>
output:
<begin_role>Squirrel_A</begin_role>
<begin_query>Look at all these delicious acorns! I can't wait to gather them all.</begin_query>"""
    if index == 0 :
        example = software
    elif index == 1:
        example = debate
    elif index == 2:
        example = ecosystem
    else:
        example = debate      

    return """Please analyze which character should say the opening remarks based on the scene description and what the opening remarks are(Must be selected in the provided roles). The output format is:
<begin_role>{{The first character to speak}}</begin_role>
<begin_query>{{The first thing he said}}</begin_query>

for example:
{}
""".format(example)


design_states_cot_system_prompt="""You are a scene description master.Please translate the <target> into more reasonable expressions, enrich the details inside(such as more accurately describing the character's personality, making the scene more reasonable, designing more reasonable steps, and allowing the scene to proceed normally), and think carefully step by step!"""


gen_coder_task_system_prompt = """
You are a task description master, and your task is to give you a target. You need to output the tasks of the coder under that target.
Input format:
<target>{the discribe of the event}</target>
Output format:
<task>{your output task}</task>
For example:
Input:
<target>In this scenario, the boss has provided a requirement The developer's task is to write code based on the architecture proposed by the architect The leader evaluates the written code for efficiency, readability, and functionality, providing feedback Another developer makes necessary modifications to the code The target program is:<target>a snake game with Python</target>
Output:
<task>
1. Write elegant, readable, extensible, and effective code
2. Follow the Architect proposal closure while writing code
</task>
"""