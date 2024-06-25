import os
from agents import SolutionConfig, Solution
import litellm

litellm.set_verbose = True
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_URL"] = ""

solution = Solution(config=SolutionConfig("examples/chatbot/config.json"))
solution.run()
