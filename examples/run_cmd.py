import argparse
import sys
sys.path.append("../src/agents")
from sop import SOP
from agent import Agent

parser = argparse.ArgumentParser(description='A demo of chatbot')
parser.add_argument('--agent', type=str, help='path to SOP json')
args = parser.parse_args()
agent = Agent(args.agent)
agent.run()