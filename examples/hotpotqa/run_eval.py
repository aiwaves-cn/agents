import json
import os
from datetime import datetime

from agents import HotpotQADataset, Solution, SolutionConfig
import litellm

from agents.evaluation import Case
from agents.optimization.utils import OptimUtils

litellm.set_verbose = False

os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_URL"] = ""

split = "hard"
time_path = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_path = f"eval/{time_path}_hotpotqa_{split}"


def run_eval():
    # !需要根据情况配置split
    dataset = HotpotQADataset(split)

    # !需要根据情况配置
    solution_config_path = "eval/accepted_solution/solution.json"
    solution = Solution(SolutionConfig(solution_config_path))

    case_list = []
    for i in range(len(dataset)):
        case_list.append(Case(dataset.get_case_dict(i)))

    OptimUtils.parallel_case_forward(
        case_list, solution, 8, save_path, dataset.evaluate)

    ems = []
    f1s = []
    for case in case_list:
        ems.append(1 if case.dataset_eval.standard_eval_result["em"] else 0)
        f1s.append(case.dataset_eval.standard_eval_result["f1"])

    result = {
        "EM": sum(ems) / len(ems),
        "F1": sum(f1s) / len(f1s)
    }
    print(result)

    with open(f"{save_path}/result.json", "w", encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    for case in case_list:
        print(f"case_id: {case.case_id}, f1: {case.dataset_eval.standard_eval_result['f1']}, ground_truth: {
              case.ground_truth}, prediction: {case.result}")


if __name__ == "__main__":
    run_eval()
