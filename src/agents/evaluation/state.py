import copy

from .. import AgentConfig, ActionConfig
from ..agents import Agent, Action, Environment
from ..task.node import Node, NodeConfig


class State:
    def __init__(
            self,
            node: Node,
            agent: Agent,
            action: Action,
            environment: Environment,
    ):
        """
        Initializes a State object.

        Args:
            node (Node): The node associated with this state.
            agent (Agent): The agent associated with this state. A deep copy is made.
            action (Action): The action taken in this state.
            environment (Environment): The environment associated with this state. A deep copy is made.
        """
        self.node = node
        self.agent: Agent = copy.deepcopy(agent)  # 这里需要深拷贝，而且是仅仅一个agent
        self.action: Action = action
        self.environment: Environment = copy.deepcopy(environment)
        self.node_eval = NodeEval(node.node_name, "", "", "", "")
        self.backward: StateBackward = StateBackward()
        self.node_backward: StateBackward = StateBackward()

    def to_dict(self):
        """
        Returns a dictionary representation of the State object.

        Returns:
            dict: A dictionary containing the state information.
        """
        return {
            "node": self.node.to_dict(),
            "action": self.action.to_dict(),
            "prompt_backward": self.backward.to_dict(),
            "node_backward": self.node_backward.to_dict(),  # Records node's backward information, such as suggestions
            "node_eval": self.node_eval.to_dict(),  # Evaluation results for each node during SOP optimization
            "agent": self.agent.to_dict(self.node.node_name),
            # "environment": self.environment.to_dict(),
        }

    def get_dict_for_trainer(self, keys: list):
        """
        Gets the information needed for the trainer.

        Allowed keys:
        - prompt_template: Components used to generate the last prompt, excluding default components, only those in padding.
        - prompt_components: Components used to generate the last prompt, including default components.
        - response: The generated response.
        - suggestion: Suggestions for optimizing the prompt for this state.
        - last_prompt: The prompt from the previous state.
        - index: The index of this state in the trajectory.
        - prompts_order: The order of the prompts.
        - needed_optim_component: Components needed for optimization.

        Args:
            keys (list): The keys of the information needed.

        Returns:
            dict: A dictionary containing the requested information.
        """
        allowed_keys = {"prompt_template", "index", "response", "suggestion", "prompt_components", "last_prompt_str",
                        "prompts_order", "needed_optim_component"}

        for key in keys:
            if key not in allowed_keys:
                print(f"keys must be in {allowed_keys}, 传入了{keys}")

        ret_dict = {}
        if "prompt_template" in keys:
            ret_dict["prompt_template"] = self.action.used_prompt_templates
        if "response" in keys:
            # This is content, not response. Response is the direct return object from the large model.
            ret_dict["response"] = self.action.content
        if "suggestion" in keys:
            ret_dict["suggestion"] = self.backward.suggestion
        if "last_prompt_str" in keys:
            ret_dict["last_prompt"] = self.action.last_prompt
        if "prompt_components" in keys:
            role_name = self.action.agent_role
            ret_dict["prompt_components"] = {**self.action.used_prompt_templates,
                                             **self.node.node_primary_prompts[role_name]}
        if "prompts_order" in keys:
            ret_dict["prompts_order"] = self.action.prompts_order
        return ret_dict

    @classmethod
    def load_from_json(cls, state_json):
        """
        Loads a State object from a JSON dictionary.

        Args:
            state_json (dict): The JSON dictionary containing the state data.

        Returns:
            State: A State object.
        """
        # FIXME: Environment load from json error
        return cls(
            Node(NodeConfig(state_json["node"])),
            Agent(AgentConfig(state_json["agent"])),
            Action(ActionConfig(state_json["action"])),
            Environment.load_from_json(state_json["environment"])
        )


class StateBackward:
    """
    The StateBackward class is used to record the backward information of a state.
    """
    def __init__(self, **kwargs):
        """
        Initializes the StateBackward object.

        Args:
            **kwargs: Arbitrary keyword arguments for initializing the backward information.
        """
        self.prompt = kwargs.get("prompt", "")
        self.analyse = kwargs.get("analyse", "")
        self.response = kwargs.get("response", "")
        self.suggestion = kwargs.get("suggestion", "")
        self.requirement_for_previous = kwargs.get("requirement_for_previous", "")

    def update(self, **kwargs):
        """
        Updates the backward information.

        Args:
            **kwargs: Arbitrary keyword arguments for updating the backward information.
        """
        self.prompt = kwargs.get("prompt", self.prompt)
        self.response = kwargs.get("response", self.response)
        self.suggestion = kwargs.get("suggestion", self.suggestion)
        self.requirement_for_previous = kwargs.get(
            "requirement_for_previous", self.requirement_for_previous
        )
        self.analyse = kwargs.get("analyse", self.analyse)

    def to_dict(self):
        """
        Returns a dictionary representation of the StateBackward object.

        Returns:
            dict: A dictionary containing the backward information.
        """
        return {
            "prompt": self.prompt,
            "response": self.response,
            "suggestion": self.suggestion,
            "requirement_for_previous": self.requirement_for_previous,
            "analyse": self.analyse,
        }


class NodeEval:
    """
    The NodeEval class is used to record the evaluation information of a node.
    """
    def __init__(self, node_name, prompt, content, summary, evaluation):
        """
        Initializes the NodeEval object.

        Args:
            node_name (str): The name of the node.
            prompt (str): The prompt used for the node.
            content (str): The content of the node.
            summary (str): The summary of the node.
            evaluation (str): The evaluation of the node.
        """
        self.node_name = node_name
        self.prompt = prompt
        self.content = content
        self.summary = summary
        self.evaluation = evaluation

    def to_dict(self):
        """
        Returns a dictionary representation of the NodeEval object.

        Returns:
            dict: A dictionary containing the node evaluation information.
        """
        return {
            "node_name": self.node_name,
            "prompt": self.prompt,
            "content": self.content,
            "evaluation": self.evaluation,
        }

    def update(self, prompt, content, summary, evaluation):
        """
        Updates the node evaluation information.

        Args:
            prompt (str): The prompt used for the node.
            content (str): The content of the node.
            summary (str): The summary of the node.
            evaluation (str): The evaluation of the node.
        """
        self.prompt = prompt if prompt else self.prompt
        self.content = content if content else self.content
        self.summary = summary if summary else self.summary
        self.evaluation = evaluation if evaluation else self.evaluation
