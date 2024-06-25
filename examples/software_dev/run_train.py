import os

from agents import SoftwareDevDataset
import litellm
from agents.optimization.trainer import Trainer, TrainerConfig

os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_URL"] = ""

litellm.set_verbose = False

if __name__ == "__main__":
    # 准备数据
    dataset = SoftwareDevDataset()

    # Trainer训练
    trainer_config_path = "examples/software_dev/configs/trainer_config.json"
    trainer = Trainer(config=TrainerConfig(trainer_config_path), dataset=dataset)
    trainer.train()
