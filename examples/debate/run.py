import os
from agents import SolutionConfig, Solution
import litellm

litellm.set_verbose = True
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_URL"] = ""

if __name__ == "__main__":
    solution = Solution(config=SolutionConfig("generated_config.json"))
    solution.run()
