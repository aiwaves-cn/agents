from component import *
from extra_component import *

class State:
    def __init__(
        self,
        **kwargs
    ):
        
        self.next_states = {}
        self.name = kwargs["name"]
        self.environment_prompt = kwargs["environment_prompt"] if "environment_prompt" in kwargs else ""
        self.begin_role = kwargs["begin_role"] if "begin_role" in kwargs else self.agents_name[0]
        self.begin_query = kwargs["begin_query"] if "begin_query" in kwargs else ""
        self.summary_prompt = kwargs["summary_prompt"] if "summary_prompt" in kwargs else None
        self.current_role = self.begin_role
        self.roles = kwargs["roles"]
        self.components = self.init_components(kwargs["agent_states"])
        self.current_role = self.begin_role
        self.is_begin = True
        
        
    def init_components(self,agent_states_dict: dict):
        agent_states = {}
        for role, components in agent_states_dict.items():
            component_dict = {}
            for component, component_args in components.items():
                if component:
                    # "role" "style"
                    if component == "style":
                        component_dict["style"] = StyleComponent(
                            component_args["role"],
                            component_args["style"],
                        )

                        # "task"
                    elif component == "task":
                        component_dict["task"] = TaskComponent(component_args["task"])

                        # "rule"
                    elif component == "rule":
                        component_dict["rule"] = RuleComponent(component_args["rule"])

                        # "demonstration"
                    elif component == "demonstrations":
                        component_dict["demonstrations"] = DemonstrationComponent(
                            component_args["demonstrations"]
                        )

                    # "output"
                    elif component == "output":
                        component_dict["output"] = OutputComponent(
                            component_args["output"]
                        )

                    elif component == "last":
                        component_dict["last"] = LastComponent(
                            component_args["last_prompt"]
                        )

                    # "demonstrations"
                    elif component == "cot":
                        component_dict["cot"] = CoTComponent(
                            component_args["demonstrations"]
                        )
                    elif component == "CustomizeComponent":
                        component["CustomizeComponent"] = CustomizeComponent(
                            component_args["template"], component_args["keywords"]
                        )

                    # =================================================================================#

                    # "output"
                    elif component == "StaticComponent":
                        component_dict["StaticComponent"] = StaticComponent(
                            component_args["output"]
                        )

                    # "top_k"  "type" "knowledge_base" "system_prompt" "last_prompt"
                    elif component == "KnowledgeBaseComponent":
                        component_dict["tool"] = KnowledgeBaseComponent(
                            component_args["top_k"],
                            component_args["type"],
                            component_args["knowledge_path"],
                        )

                    elif component == "CategoryRequirementsComponent":
                        component_dict[
                            "CategoryRequirementsComponent"
                        ] = CategoryRequirementsComponent(
                            component_args["information_path"]
                        )

                    # "short_memory_extract_words"  "long_memory_extract_words" "system_prompt" "last_prompt"
                    elif component == "ExtractComponent":
                        component_dict["ExtractComponent"] = ExtractComponent(
                            component_args["long_memory_extract_words"],
                            component_args["short_memory_extract_words"],
                            component_args["system_prompt"],
                            component_args["last_prompt"],
                        )
                    elif component == "WebSearchComponent":
                        component_dict["WebSearchComponent"] = WebSearchComponent(
                            component_args["engine_name"], component_args["api"]
                        )
                    elif component == "WebCrawlComponent":
                        component_dict["WebCrawlComponent"] = WebCrawlComponent(
                            component_args["name"]
                        )

                    # ====================================================
                    else:
                        continue

            agent_states[role] = component_dict

        return agent_states

