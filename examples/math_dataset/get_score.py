import json
import os


def get_score():
    """
    case跑完了之后加载保存下来的case获取分数，会获取路径下所有的case的分数，然后计算加权平均分数
    Returns:

    """
    save_result_path = "eval/final_result.json"
    dir_list = [
        r"eval\test_algebra",
        r"eval\test_counting_and_probability",
        r"eval\test_intermediate_algebra",
        r"eval\test_number_theory",
        r"eval\test_prealgebra",
        r"eval\test_precalculus"
    ]

    scores = []
    count = 0
    for dir in dir_list:
        print(f"\n\nthe dir is: {dir}")
        files_and_folders = os.listdir(dir)
        files = [f for f in files_and_folders if os.path.isfile(
            os.path.join(dir, f))]
        for file_name in files:
            if file_name == "result.json":
                continue
            with open(f"{dir}/{file_name}", "r", encoding='utf-8') as f:
                result = json.load(f)
                count += 1
                print(f"file_{count} path is: {dir}/{file_name}")
                scores.append(result["dataset_eval"]["score"])

    save_info = {
        "average_score": sum(scores) / len(scores),
        "scores": scores,
    }
    print("\n\nfinal result is: ")
    print(save_info)
    with open(save_result_path, "w", encoding='utf-8') as f:
        json.dump(save_info, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    get_score()
