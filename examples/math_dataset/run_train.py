import litellm
import os

from agents import HotpotQADataset, LLMConfig, OpenAILLM, Solution, SolutionConfig, MATHDataset
from agents.optimization.trainer import Trainer, TrainerConfig
from agents.optimization.utils import OptimUtils

os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_URL"] = ""

litellm.set_verbose = False

if __name__ == "__main__":
    # 准备数据
    dataset = MATHDataset(split="train")

    # Trainer训练
    trainer_config_path = "configs/trainer_config.json"
    trainer = Trainer(config=TrainerConfig(
        trainer_config_path), dataset=dataset)
    trainer.train()
