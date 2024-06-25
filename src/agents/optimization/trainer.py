import copy
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
import random

import wandb

from agents.optimization.loss import LossCalculator, LossConfig
from agents.optimization.prompt_optimizer import PromptOptimizer, PromptOptimizerConfig
from agents.optimization.node_optimizer import NodeOptimizer, NodeOptimizerConfig
from agents.optimization.sop_optimizer import SOPOptimizer, SOPOptimizerConfig
from agents.optimization.toolkit_optimizer import (
    ToolkitOptimizerConfig,
    ToolkitOptimizer,
)
from agents.evaluation.case import Case
from agents.optimization.utils import OptimUtils
from agents.datasets import BaseDataset
from .. import Solution, SolutionConfig

from ..utils.config import Config


class TrainerConfig(Config):
    def __init__(self, config_path_or_dict):
        super().__init__(config_path_or_dict)

        # optim_setting
        self.batch_size: int = self.config_dict["batch_size"]
        self.max_step = self.config_dict["max_step"]
        self.parallel: bool = self.config_dict.get("parallel", True)
        self.parallel_max_num = self.config_dict.get("parallel_max_num", 1)
        self.optim_order = self.config_dict["optim_order"]
        self.optimizers = self.config_dict["optimizers"]
        self.additional_info = self.config_dict.get("additional_info", {})

        # initial solution and optimizer config
        self.initial_solution_path = self.config_dict["initial_solution_path"]
        self.optimizer_config_path = self.config_dict["optimizer_config_path"]

        # dataset sample
        self.sample_kind: str = self.config_dict.get("sample_kind", "order")
        self.allow_duplicate_samples: bool = self.config_dict.get("allow_duplicate_samples", False)

        # task setting
        self.has_ground_truth = self.config_dict.get("has_ground_truth", False)
        self.has_eval_score = self.config_dict.get("has_eval_score", False)

        # early stop
        self.early_stop_threshold: float = self.config_dict.get("early_stop_threshold", 0.9)
        self.max_exceed_threshold_count = self.config_dict.get("max_exceed_threshold_count", 3)
        self.max_score_decline_count = self.config_dict.get("max_score_decline_count", 3)
        self.use_early_stop_threshold: bool = self.config_dict.get("use_early_stop_threshold", False)
        self.use_early_stop_score_decline: bool = self.config_dict.get("use_early_stop_score_decline", False)

        # roll back
        self.use_roll_back = self.config_dict.get("use_roll_back", False)
        self.log_path = self.config_dict["log_path"]

        # check the config
        if self.optim_order not in ["order", "up_to_down", "down_to_up", "random"]:
            self.optim_order = "order"

        # wandb_config
        self.wandb_config = self.config_dict.get("wandb_config", {})

        assert len(self.optimizers) > 0, "The number of optimizers that need to be used cannot be 0"
        for optimizer in self.optimizers:
            if optimizer not in ["prompt", "node", "sop", "toolkit"]:
                self.optimizers.remove(optimizer)
                print(f"optimizer {optimizer} can not in the options, it has been removed")


class Trainer:
    def __init__(self, config: TrainerConfig, dataset: BaseDataset):
        """
        Init the trainer

        Args:
            config (TrainerConfig): The TrainerConfig used to initialize the Trainer
            dataset (BaseDataset): The dataset to be used for training, the actual type should be a subclass of BaseDataset
        """
        self.config = config

        self.log_path = Path(config.log_path)
        self.batch_size = config.batch_size
        self.max_step = config.max_step
        self.optimizer_config_path = config.optimizer_config_path
        self.optimizers = config.optimizers
        self.optim_order = config.optim_order

        # logger
        self.logger, self.time_path = setup_logging(self.log_path)
        self.logger.info(f"Logs are saved in{self.log_path / self.time_path}")
        self.config.dump(self.log_path / self.time_path / "trainer.json")

        # dataset
        self.dataset: BaseDataset = dataset
        self.sample_kind: str = config.sample_kind
        self.allow_duplicate_samples: bool = config.allow_duplicate_samples
        self.sampled_idx_set = set()

        # task setting
        self.has_ground_truth = config.has_ground_truth
        self.has_eval_score = config.has_eval_score

        # early stop
        self.use_early_stop_threshold: bool = config.use_early_stop_threshold
        self.use_early_stop_score_decline: bool = config.use_early_stop_score_decline
        self.early_stop_threshold: float = config.early_stop_threshold
        self.max_exceed_threshold_count = config.max_exceed_threshold_count
        self.max_score_decline_count = config.max_score_decline_count

        # roll back
        self.use_roll_back = config.use_roll_back

        # parallel
        self.parallel: bool = config.parallel
        self.parallel_max_num: int = config.parallel_max_num

        # wandb
        self.wandb_config = config.wandb_config
        wandb.init(**self.wandb_config, config=self.config.to_dict())

        # The three optimizers and loss calculators
        with open(self.optimizer_config_path, encoding="utf-8") as f:
            optim_json_config = json.load(f)
        self.prompt_optimizer = (
            PromptOptimizer(
                PromptOptimizerConfig(optim_json_config),
                logger_name="global_logger_for_training",
            )
            if "prompt_optimizer" in optim_json_config
            else None
        )
        self.node_optimizer = (
            NodeOptimizer(NodeOptimizerConfig(optim_json_config), logger_name="global_logger_for_training")
            if "node_optimizer" in optim_json_config
            else None
        )
        self.sop_optimizer = (
            SOPOptimizer(SOPOptimizerConfig(optim_json_config), logger_name="global_logger_for_training")
            if "sop_optimizer" in optim_json_config
            else None
        )
        self.loss_calculator = (
            LossCalculator(
                LossConfig(optim_json_config),
                has_ground_truth=self.has_ground_truth,
                has_eval_score=self.has_eval_score,
                logger_name="global_logger_for_training"
            )
            if "loss" in optim_json_config
            else None
        )
        self.additional_info = config.additional_info

        self.toolkit_optimizer = (
            ToolkitOptimizer(
                ToolkitOptimizerConfig(optim_json_config),
                logger_name="global_logger_for_training",
            )
            if "toolkit_optimizer" in optim_json_config
            else None
        )

        # others
        self.initial_solution_path = config.initial_solution_path
        self.exceed_threshold_times = 0

    def get_step_optim_order(self, last_optim_order: list[str]) -> list[str]:
        """
        Get the optimizer to call for the current step

        There are four choices for the order of optimizers: order, random, up_to_down, and down_to_up. The default is order.
        - order means following the sequence of sop, node, prompt.
        - random means randomly selecting an optimizer. In both cases, only one optimizer is called per step.
        - up_to_down means calling all optimizers in the sequence of sop, node, prompt within a single step.
        - down_to_up means calling all optimizers in the sequence of prompt, node, sop within a single step.

        Args:
            last_optim_order (list[str]): List of optimizers used in the previous step.

        Returns:
            list[str]: List of optimizers to be used in the current step.
        """
        if len(last_optim_order) == 0:
            return [self.optimizers[0]]

        assert len(self.optimizers) > 0, "The length of the ignore_optimizer cannot exceed 2"
        optim_dict = {
            0: "sop",
            1: "node",
            2: "prompt",
            3: "toolkit",
            "sop": 0,
            "node": 1,
            "prompt": 2,
            "toolkit": 3,
        }
        optimizer_num = len(optim_dict) / 2
        if self.optim_order == "order":
            new_optim_id = (optim_dict[last_optim_order[0]] + 1) % optimizer_num
            while optim_dict[new_optim_id] not in self.optimizers:
                new_optim_id = (new_optim_id + 1) % optimizer_num
            return [optim_dict[new_optim_id]]

        elif self.optim_order == "random":
            return [random.choice(self.optimizers)]

        elif self.optim_order == "up_to_down":
            return [
                optimizer_name
                for optimizer_name in ["sop", "node", "prompt", "toolkit"]
                if optimizer_name in self.optimizers
            ]

        elif self.optim_order == "down_to_up":
            return [
                optimizer_name
                for optimizer_name in ["toolkit", "prompt", "node", "sop"]
                if optimizer_name in self.optimizers
            ]

    def train(self):
        """
        Train solution.json

        Returns:
            None: This function does not return any value.

        """
        self.exceed_threshold_times = 0
        last_solution = None

        step_optim_order = []
        case_count = 0
        step_cost_time = []
        ave_score_list = []
        sample_from_idx = random.randint(0, len(self.dataset) - self.batch_size * self.max_step) \
            if len(self.dataset) > self.batch_size * self.max_step else 0
        op_status = False

        solution = Solution(config=SolutionConfig(self.initial_solution_path))
        for step in range(1, self.max_step + 1):
            step_start_time = time.time()
            save_step_path = self.log_path / self.time_path / f"step_{step}"
            save_step_path.mkdir(exist_ok=True, parents=True)

            step_optim_order = self.get_step_optim_order(step_optim_order)
            self.logger.info(f"start step: {step}, optim_order is: {step_optim_order}")

            case_list = self.sample_case_list(self.sample_kind, sample_from_idx)

            raw_case_list = [copy.deepcopy(case) for case in case_list]
            sample_from_idx += self.batch_size

            # forward the case_list
            if self.parallel:
                OptimUtils.parallel_case_forward(
                    case_list, solution, self.parallel_max_num, save_step_path / "raw",
                    self.dataset.evaluate, self.logger, )
            else:
                for case in case_list:
                    OptimUtils.case_forward(
                        case, solution, save_step_path / "raw" / f"{case.case_id}.json", self.dataset.evaluate)

            # get the score of the forward result
            scores = [case.dataset_eval.score for case in case_list]
            ave_score_list.append(sum(scores) / len(scores))

            # log the forward result
            self.logger.info(f"step{step}, finish forward, aver_score: {ave_score_list[-1]:.2f}, scores: {scores}")

            # early stop
            if self.early_stop(ave_score_list, step):
                break

            # roll back and save the last solution (solution before optim) for roll back
            if op_status and self.use_roll_back:
                solution, case_list = self.roll_back(solution, ave_score_list, last_solution, raw_case_list, case_list)
            last_solution = solution

            # use the optimizer to optimize the solution
            for optimizer_name in step_optim_order:
                # loss calculation
                self.loss_calculator.parallel_calculate_loss(
                    case_list, self.parallel_max_num, self.additional_info.get("loss", None),
                    save_step_path / "case_after_loss")

                if optimizer_name == "prompt":
                    solution, op_status = self.prompt_optimizer.optimize(
                        case_list, solution, save_step_path, self.parallel_max_num)

                elif optimizer_name == "node":
                    solution, op_status = self.node_optimizer.optimize(
                        case_list, solution, save_step_path, self.parallel_max_num)

                elif optimizer_name == "sop":
                    solution, op_status = self.sop_optimizer.optimize(
                        case_list, solution, save_step_path, self.parallel_max_num)

                elif optimizer_name == "toolkit":
                    # TODO: toolkit optimizer
                    solution = self.toolkit_optimizer.optimize(
                        case_list, solution, save_step_path
                    )

            # record some information
            self.logger.info(f"step {step} optim status: {op_status}")
            case_count += self.batch_size
            step_cost_time.append(time.time() - step_start_time)
            self.logger.info(f"step {step} cost time: {step_cost_time[-1] / 60:.1f}min")

            # log the result of this step to wandb
            wandb.log({
                "step": step,
                "score_before_optim": ave_score_list[-1],
                "scores": scores,
                "cost_time": step_cost_time[-1],
                "case_count": case_count,
                "optim_status": op_status,
            })

        self.logger.info(
            f"Training completed. Total time spent: {sum(step_cost_time) / 60:.1f} minutes. There were {case_count} cases and {step} steps.")

        wandb.finish()

    def sample_case_list(self, sample_kind: str, from_idx: int):
        """
        Extract self.batch_size cases from the dataset.

        Args:
            sample_kind (str): The method for extracting cases from the dataset, which can be either 'order' or 'random'.
            from_idx (int): If 'order', the position to start extracting from; if 'random', this parameter is invalid.

        Returns:
            list[Case]: A list of elements, each being a case, representing randomly selected samples.
        """
        assert sample_kind in ["order", "random"], "sample_kind can only be order or random, passed in" + sample_kind
        case_list = []
        if sample_kind == "order":
            if from_idx + self.batch_size > len(self.dataset):
                print("The dataset has been traversed and started over")
                from_idx = 0
            case_list = [
                Case(self.dataset.get_case_dict(i))
                for i in range(from_idx, from_idx + self.batch_size)
            ]
        elif sample_kind == "random":
            if len(self.sampled_idx_set) + self.batch_size > len(self.dataset):
                self.sampled_idx_set.clear()
                print("The dataset has been traversed and started over")
            for _ in range(self.batch_size):
                idx = -1
                while idx in self.sampled_idx_set or idx < 0:
                    idx = random.randint(0, len(self.dataset) - 1)
                self.sampled_idx_set.add(idx)
                case_list.append(Case(self.dataset.get_case_dict(idx)))
            # If repeated sampling is allowed, the sampled_idx_set is cleared,
            # which can ensure that samples of one step will not be repeated
            if self.allow_duplicate_samples:
                self.sampled_idx_set.clear()
        return case_list

    def early_stop(self, ave_score_list: list[float], step: int):
        """
        Achieved early stop in training

        Args:
            ave_score_list (list[float]): The score obtained for each case of the current step
            step (int): The step during training

        Returns:
            bool: Whether the training needs to be stopped early
        """
        if self.use_early_stop_threshold:
            # if the average score is higher than the threshold for max_exceed_threshold_count times, stop the training
            if ave_score_list[-1] > self.early_stop_threshold:
                self.exceed_threshold_times += 1
                self.logger.info(
                    f"At step {step}, the score has reached {self.early_stop_threshold} for {self.exceed_threshold_times} consecutive times."
                )
                if self.exceed_threshold_times >= self.max_exceed_threshold_count:
                    # stop the training
                    self.logger.info(
                        f"At step {step}, the score has reached {self.early_stop_threshold} for {self.max_exceed_threshold_count} consecutive times, ending the training early."
                    )
                    return True
            else:
                self.exceed_threshold_times = 0

        # if the average score has not been improved for max_score_decline_count times, stop the training
        if self.use_early_stop_score_decline:
            if len(ave_score_list) <= self.max_score_decline_count:
                return False

            for i in range(1, self.max_score_decline_count + 1):
                if ave_score_list[-i] > ave_score_list[-i - 1]:
                    return False
            self.logger.info(
                f"The score has not been improved for {self.max_score_decline_count} consecutive times, ending the training early."
            )
            return True

        # default return False
        return False

    def roll_back(
            self,
            solution: Solution,
            ave_score_list: list[float],
            last_solution: Solution,
            raw_case_list: list[Case],
            finished_case_list: list[Case]
    ):
        """
        roll back to the last solution if the new solution is worse than the last solution

        If the score of the new solution on the current step is lower than that of the previous solution on the previous step,
        and lower than the score of the previous solution on the current step, roll back to the previous solution.

        Args:
            solution (Solution): new Solution
            ave_score_list (list[float]): The score obtained for each case of the current step
            last_solution (Solution): Solution of last step
            raw_case_list (list[Case]):  Cases in which forward() has not been executed
            finished_case_list (list[Case]): Cases in which forward() has been executed using the Solution of the current step

        Returns:
            Solution: the Solution to be adopted
            list[Case]: The list of cases corresponding to the Solution to be adopted
        """
        if not self.use_roll_back or len(ave_score_list) < 2:
            return solution, finished_case_list

        # new solution score on current score is worse than the last solution score on the previous step
        if ave_score_list[-1] < ave_score_list[-2]:
            # self.logger.debug("in roll_back(), new solution is worse than the last solution on the previous step")
            OptimUtils.parallel_case_forward(
                raw_case_list,
                last_solution,
                self.parallel_max_num,
                self.log_path / self.time_path / "roll_back_check",
                self.dataset.evaluate,
                self.logger,
            )
            scores = [case.dataset_eval.score for case in raw_case_list]
            ave_score_of_pre_solution = sum(scores) / len(scores)

            # if the new solution is worse than the old one on current step case, rollback
            if ave_score_of_pre_solution > ave_score_list[-1]:
                self.logger.info(
                    f"roll back to last solution, new solution score: {ave_score_list[-1]:.2f}, last solution score: {ave_score_of_pre_solution:.2f}"
                )
                return last_solution, raw_case_list
            else:
                self.logger.debug(
                    f"no need to roll back, after validation, new solution score: {ave_score_list[-1]:.2f}, last solution score: {ave_score_of_pre_solution:.2f}"
                )
                return solution, finished_case_list

        self.logger.debug("no need to roll back")
        return solution, finished_case_list


def setup_logging(save_log_path: Path):
    """
    Initialize the logging configuration.

    This function sets up logging to both a file and the console.
    Log messages are saved to a file with a timestamped directory name.
    The logger captures all log levels (DEBUG and above).

    Args:
        save_log_path (Path): The directory path where log files should be saved.

    Returns:
        Logger: Configured logger instance.
        Path: Path to the directory where log files are saved.
    """
    time_path = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(save_log_path / time_path, exist_ok=True)

    # Create a logger with a specified name and set its level to DEBUG
    logger = logging.getLogger("global_logger_for_training")
    logger.setLevel(logging.DEBUG)

    # Create a file handler, set its level to DEBUG, and add it to the logger
    file_handler = logging.FileHandler(
        save_log_path / time_path / "app.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Create a console handler, set its level to DEBUG, and add it to the logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Return the configured logger and the path to the log directory
    return logger, time_path
