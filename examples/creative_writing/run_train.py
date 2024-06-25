import os

from agents import CreativeWritingDataset
import litellm
from agents.optimization.trainer import Trainer, TrainerConfig

os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_URL"] = ""

litellm.set_verbose = False

if __name__ == "__main__":
    # 准备数据
    dataset = CreativeWritingDataset(split="train")

    # Trainer训练
    trainer_config_path = "examples/creative_writing/configs/trainer_config.json"
    trainer = Trainer(config=TrainerConfig(trainer_config_path), dataset=dataset)
    trainer.train()


