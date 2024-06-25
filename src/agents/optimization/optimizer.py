# coding=utf-8
# Copyright 2024 The AIWaves Inc. team.

#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from ..utils.config import Config


class OptimizerConfig(Config):
    class TaskSetting:
        """
        The TaskSetting class is used to hold the task settings for the optimizer.
        """

        def __init__(self, **kwargs):
            """
            Initializes the TaskSetting object.

            Args:
                **kwargs: Arbitrary keyword arguments for initializing the task settings.
            """
            self.has_ground_truth = kwargs.get("has_ground_truth", False)
            self.has_result = kwargs.get("has_result", False)

    def __init__(self, config_path_or_dict):
        """
        Initializes the OptimizerConfig object.

        Args:
            config_path_or_dict (str or dict): The path to the configuration file or the configuration dictionary.
        """
        super().__init__(config_path_or_dict)  # The parent class reads the JSON file to get self.config_dict

        self.task_setting = self.TaskSetting(**self.config_dict.get("task_setting", {}))
        self.evaluator_llm_config = self.config_dict.get("evaluator_llm_config", None)

        # The configuration for prompt, node, and SOP optimizers, and loss settings are kept as dictionaries,
        # as the classes parsing these fields are not here, and these are just passed along.
        self.prompt_optimizer_setting_dict: dict = self.config_dict.get("prompt_optimizer")
        self.node_optimizer_setting_dict: dict = self.config_dict.get("node_optimizer")
        self.sop_optimizer_setting_dict: dict = self.config_dict.get("sop_optimizer")
        self.loss_setting_dict: dict = self.config_dict["loss"]

        self.toolkit_optimizer_setting_dict: dict = self.config_dict.get("toolkit_optimizer")


class Optimizer:
    """
    The Optimizer class is used to perform optimization tasks based on the configuration.
    """
    def __init__(self, config: OptimizerConfig):
        """
        Initializes the Optimizer object.

        Args:
            config (OptimizerConfig): The optimizer configuration.
        """
        # Parse the fields in the config that are not related to prompt, node, or SOP optimizers
        self.config = config

        # task_setting
        self.task_setting = self.config.task_setting
        self.has_ground_truth = self.config.task_setting.has_ground_truth
        self.has_result = self.config.task_setting.has_result
