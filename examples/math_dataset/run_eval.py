import json
import os
from datetime import datetime

from agents import HotpotQADataset, Solution, SolutionConfig, MATHDataset
import litellm

from agents.evaluation import Case
from agents.optimization.utils import OptimUtils


parallel_num = 24
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_URL"] = ""


solution_config_path = r"examples/math_dataset/solution_config/solution.json"

split = "test"
math_type = "prealgebra"

save_path = f"examples/math_dataset/eval/{split}_{math_type}"


def run_eval():
    # !需要根据情况配置split和solution的地址
    dataset = MATHDataset(split=split, math_type=math_type)

    solution = Solution(SolutionConfig(solution_config_path))
    case_list = []
    for i in range(len(dataset)):
        if os.path.exists(f"{save_path}/{dataset.get_case_dict(i).get('case_id')}.json"):
            continue
        print(f"case_id: {dataset.get_case_dict(i).get('case_id')}")
        case_list.append(Case(dataset.get_case_dict(i)))
    print(f"total case num: {len(dataset)}, case_list len: {len(case_list)}")
    # exit()

    OptimUtils.parallel_case_forward(case_list, solution, parallel_num, save_path, dataset.evaluate)

    scores = []
    for case in case_list:
        scores.append(case.dataset_eval.standard_eval_result["score"])
    # 输出并保存最终结果
    result = {"average_score": sum(scores) / len(scores), }
    print(result)
    with open(f"{save_path}/result.json", "w", encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    run_eval()
