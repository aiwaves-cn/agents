import logging
from typing import List

from .optimizer import OptimizerConfig, Optimizer
from ..agents.llm import LLMConfig, OpenAILLM
from ..evaluation import Case
from ..task import Solution
from ..agents.toolkit import Toolkit


class ToolkitOptimizerConfig(OptimizerConfig):
    def __init__(self, config_path_or_dict):
        super().__init__(config_path_or_dict)

        self.max_actions_per_step = self.config_dict.get("max_actions_per_step", 3)
        self.LLM_config = self.config_dict.get("LLM_config", None)


class ToolkitOptimizer(Optimizer):
    def __init__(self, config: ToolkitOptimizerConfig, logger_name: str = None):
        super().__init__(config)
        self.config = config
        self.max_actions_per_step = self.config.max_actions_per_step
        LLM_config = (
            LLMConfig(self.config.LLM_config) if self.config.LLM_config else None
        )
        self.LLM = OpenAILLM(LLM_config) if LLM_config else None

        self._best_score = -1

        # logger
        self.logger = (
            logging.getLogger(logger_name)
            if logger_name
            else logging.getLogger(__name__)
        )

    def optimize(self, case_list: List[Case], solution: Solution):
        shared_tookit: Toolkit = solution.agent_team.environment.shared_toolkit
        if not shared_tookit:
            return solution

        scores = [case.dataset_eval.score for case in case_list]
        avg_score = sum(scores) / len(scores)

        if avg_score > self._best_score:
            self._best_score = avg_score
            # TODO: implement the optimization
