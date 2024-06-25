# 计算loss的逻辑
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents import LLMConfig, OpenAILLM
from agents.optimization.optimizer import OptimizerConfig, Optimizer
from agents.evaluation.case import Case
from agents.optimization.prompt_formatter import formulate_prompt, get_config_needed_variables
from agents.optimization.utils import OptimUtils


class LossConfig(OptimizerConfig):
    """
    The LossConfig class is used to configure the loss settings. It extends the OptimizerConfig class.
    """

    def __init__(self, config_path):
        """
        Initializes the LossConfig object.

        Args:
            config_path (str): The path to the configuration file.
        """
        super().__init__(config_path)

        # The parent class parses the common fields, here we only parse the private fields of loss
        self.llm_config: dict = self.loss_setting_dict.get("llm_config")
        self.meta_prompt: dict = self.loss_setting_dict.get("meta_prompt")


class LossCalculator(Optimizer):
    """
    The LossCalculator class is used to calculate the loss for a given case.
    """

    def __init__(self, config: LossConfig, has_ground_truth=False, has_eval_score=False, logger_name=None):
        """
        Initializes the LossCalculator object.

        Args:
            config (LossConfig): The loss configuration.
            has_ground_truth (bool): Indicates whether ground truth is available.
            has_eval_score (bool): Indicates whether evaluation score is available.
            logger_name (str): The name of the logger.
        """

        super().__init__(config)
        self.config = config

        # llm
        llm_config = LLMConfig(config.llm_config)
        self.llm = OpenAILLM(llm_config) if llm_config else None

        # task info (ground_truth and dataset eval score)
        self.has_ground_truth = has_ground_truth
        self.has_eval_score = has_eval_score

        # meta_loss and set the order according to "has_eval_score" and "has_eval_score"
        self.meta_loss = config.meta_prompt["loss"]
        self.meta_loss["order"] = self.get_prompt_config_order()
        self.meta_loss["extract_key"].append("score") if not self.has_eval_score else None

        # logger
        self.logger = (
            logging.getLogger(logger_name)
            if logger_name
            else logging.getLogger(__name__)
        )

        self.logger.info(f"has_ground_truth: {self.has_ground_truth}, has_eval_score: {self.has_eval_score}")
        self.logger.info(f"meta_loss[\"order\"]: {self.meta_loss['order']}")

    def calculate_loss(self, case: Case, additional_info=None, save_path=None):
        """
        Calculates the loss for a given case.

        Args:
            case (Case): The case for which the loss is to be calculated.
            additional_info (str, optional): Additional information for optimization. Defaults to None.
            save_path (str, optional): The path to save the case. Defaults to None.
        """
        # Steps for calculating loss: 1. Construct prompt; 2. Call large model; 3. Extract result; 4. Save result
        # Use get_needed_variables(self.meta_loss) to get the variables needed in the prompt,
        # as they vary depending on the availability of ground_truth
        case_data = case.get_dict_for_loss_calculation(get_config_needed_variables(self.meta_loss))
        eval_result_prompt = formulate_prompt(self.meta_loss, case_data)

        # 允许输入额外的优化信息
        if additional_info:
            eval_result_prompt = eval_result_prompt + additional_info

        _, content = self.llm.get_response(
            chat_messages=None,
            system_prompt="",
            last_prompt=eval_result_prompt,
            stream=False,
        )

        assert "requirement_for_previous" in self.meta_loss[
            "extract_key"], "meta_loss must contain requirement_for_previous field"
        loss_data_dict = OptimUtils.extract_data_from_response(content, self.meta_loss["extract_key"], self.logger)
        assert "requirement_for_previous" in loss_data_dict.keys(), "requirement_for_previous field must be in the extracted data"

        loss_data_dict["response"] = content
        loss_data_dict["prompt"] = eval_result_prompt
        loss_data_dict["score_info"] = case_data["score_info"]
        if "score" not in loss_data_dict.keys() and "score" in case_data:
            loss_data_dict["score"] = case_data["score"]

        case.loss.update(**loss_data_dict)

        if save_path:
            case.dump(save_path / f"{case.case_id}.json")

    def parallel_calculate_loss(
            self, case_list, parallel_max_num=8, additional_info="", save_path=None
    ):
        """
        Calculates the loss for a list of cases in parallel.

        Args:
            case_list (list): The list of cases.
            parallel_max_num (int): The maximum number of parallel calculations. Defaults to 8.
            additional_info (str, optional): Additional information for optimization. Defaults to "".
            save_path (str, optional): The path to save the cases. Defaults to None.
        """

        with ThreadPoolExecutor(max_workers=parallel_max_num) as executor:
            futures = [
                executor.submit(self.calculate_loss, case, additional_info, save_path)
                for case in case_list
            ]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(
                        f"in loss calculation, error processing case: {e}"
                    )

    def get_prompt_config_order(self):
        """
        Gets the order of the prompt configuration based on the availability of ground truth and evaluation score.

        Returns:
            list: The order of the prompt configuration.
        """
        if self.has_ground_truth and self.has_eval_score:
            return ["part1_with_gt_and_score", "task_description", "model_output", "ground_truth", "score",
                    "note_not_output_score"]
        if self.has_ground_truth and not self.has_eval_score:
            return ["part1_with_gt_no_score", "task_description", "model_output", "ground_truth", "note_output_score"]
        if not self.has_ground_truth and self.has_eval_score:
            return ["part1_no_gt_with_score", "task_description", "model_output", "score", "note_not_output_score"]
        if not self.has_ground_truth and not self.has_eval_score:
            return ["part1_no_gt_no_score", "task_description", "model_output", "note_output_score"]


if __name__ == "__main__":
    loss_with_ground_truth_and_score_cn = """
你是一个大语言模型精调师，我会给你一个模型的输出结果和期望的正确结果，你需要对其进行评价，并对模型的输出提出修改意见，请使用<requirement_for_previous></requirement_for_previous>包裹。

如下是模型输出的结果:
<result>{result}</result>；

我们期望得到的结果是:
<ground_truth>{ground_truth}</ground_truth>

如下是对此模型的评分，你的目标是优化这个得分:
<score>{score}</score>

这个得分的相关信息如下：
<evaluation_info>{score_info}</evaluation_info>


注意：
1.请务必保证<requirement_for_previous></requirement_for_previous>存在且存在一次。
2.如果模型输出效果很好，可以输出<requirement_for_previous>效果很好，没有额外的需求</requirement_for_previous>。
3.输出的结果应该在保证正确的情况下尽量与期望的结果一致，比如期望的结果是“BUST”时，模型的输出是“The women's lifestyle magazine  is "BUST" magazine.”，即便这个回答是对的，你也应该提醒模型输出应精简。
"""

    loss_with_ground_truth_and_score = """
You are a large language model fine-tuner. I will provide you with a model's output and the expected correct result. 
You need to evaluate it and suggest modifications to the model's output. Please use `<requirement_for_previous></requirement_for_previous>` to enclose your feedback.

The description of this task is as follows:
<task_description>{task_description}</task_description>

Below is the model's output:
<result>{result}</result>

The expected result is:
<ground_truth>{ground_truth}</ground_truth>

Here is the evaluation score for the model. Your goal is to optimize this score:
<score>{score}</score>

The relevant information about this score is as follows:
<evaluation_info>{score_info}</evaluation_info>

Please Note:
1. Ensure that `<requirement_for_previous></requirement_for_previous>` exists and appears once.
2. If the model's output is satisfactory, you can output <requirement_for_previous>The output is satisfactory, no additional requirements</requirement_for_previous>.
3. The output should be as close to the expected result as possible while ensuring correctness. For example, if the expected result is "BUST" and the model's output is "The women's lifestyle magazine is 'BUST' magazine.", even though this answer is correct, you should remind the model to be concise.
"""

    # same with loss_with_ground_truth_and_score, but there is no ground truth
    loss_without_ground_truth_with_score = """
You are a large language model fine-tuner. I will provide you with a model's output and the evaluation score. 
You need to evaluate it and suggest modifications to the model's output. Please use `<requirement_for_previous></requirement_for_previous>` to enclose your feedback.

The description of this task is as follows:
<task_description>{task_description}</task_description>

Below is the model's output:
<result>{result}</result>

Here is the evaluation score for the model. Your goal is to optimize this score:
<score>{score}</score>

The relevant information about this score is as follows:
<evaluation_info>{score_info}</evaluation_info>

Please Note:
1. Ensure that `<requirement_for_previous></requirement_for_previous>` exists and appears once.
2. If the model's output is satisfactory, you can output <requirement_for_previous>The output is satisfactory, no additional requirements</requirement_for_previous>.
3. The output should be as close to the expected result as possible while ensuring correctness. For example, if the expected result is "BUST" and the model's output is "The women's lifestyle magazine is 'BUST' magazine.", even though this answer is correct, you should remind the model to be concise.
"""

    # below don't have score, the beginning part of the prompt is different
    loss_with_ground_truth_without_score_en = """
You are a fine-tuner of a large model. I will provide you with some output results from the model and the expected correct results. 
You need to evaluate these data and provide a score out of 10, please wrap the score using <score></score>. Additionally, please provide some suggestions for modifying the model's output, using <requirement_for_previous></requirement_for_previous> to wrap your suggestions.

The description of this task is as follows:
<task_description>{task_description}</task_description>

Here is the model's output:
<result>{result}</result>;

The expected result is:
<ground_truth>{ground_truth}</ground_truth>

Please note:
1. Ensure that the output is wrapped with <score></score> and <requirement_for_previous></requirement_for_previous> respectively.
2. The output should be as consistent as possible with the expected result while being correct. For example, if the expected result is “BUST”, and the model's output is “The women's lifestyle magazine is 'BUST' magazine.”, even though the answer is correct, you should advise the model to be more concise.
3. The standard for a score of 10 is that the model's output is exactly the same as the expected result in a case-insensitive manner, and without any unnecessary content. Even if the model's output is semantically correct, if it includes superfluous content, points should be deducted.
"""

    loss_without_ground_truth_without_score = """
You are a fine-tuner of a large model. I will provide you with some output results from the model and the task description it is trying to solve.
You need to evaluate these data and provide a score out of 10, please wrap the score using <score></score>. Additionally, please provide some suggestions for modifying the model's output, using <requirement_for_previous></requirement_for_previous> to wrap your suggestions.

The description of this task is as follows:
<task_description>{task_description}</task_description>

Here is the model's output:
<result>{result}</result>;

Please note:
1. Ensure that the output is wrapped with <score></score> and <requirement_for_previous></requirement_for_previous> respectively.
2. The output should be as consistent as possible with the expected result while being correct. For example, if the expected result is “BUST”, and the model's output is “The women's lifestyle magazine is 'BUST' magazine.”, even though the answer is correct, you should advise the model to be more concise.
3. The standard for a score of 10 is that the model's output is exactly the same as the expected result in a case-insensitive manner, and without any unnecessary content. Even if the model's output is semantically correct, if it includes superfluous content, points should be deducted.
"""
