import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ReportConfig:
    """
    Configuration holder for evaluation report generation.
    """

    def __init__(self, config_dict: Optional[dict] = None):
        cfg = config_dict or {}
        self.enable: bool = cfg.get("enable", False)
        self.sample_size: int = cfg.get("sample_size", 8)
        self.eval_indices: Optional[List[int]] = cfg.get("eval_indices", None)
        self.success_threshold: Optional[float] = cfg.get("success_threshold", None)
        self.top_k_reflections: int = cfg.get("top_k_reflections", 5)
        self.report_name: str = cfg.get("report_name", "report.json")
        # optional fixed baseline solution; fall back to initial solution
        self.baseline_solution_path: Optional[str] = cfg.get("baseline_solution_path", None)


class EvaluationReporter:
    """
    Utility class to aggregate evaluation results and emit a compact report.
    """

    def __init__(self, report_config: ReportConfig):
        self.report_config = report_config

    def _load_cases_from_dir(self, case_dir: Path) -> List[Dict[str, Any]]:
        if not case_dir.exists():
            return []
        case_dicts: List[Dict[str, Any]] = []
        for file in case_dir.iterdir():
            if file.suffix != ".json":
                continue
            with open(file, "r", encoding="utf-8") as f:
                try:
                    case_dicts.append(json.load(f))
                except json.JSONDecodeError:
                    continue
        return case_dicts

    def _summarize_cases(self, case_dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        scores: List[float] = []
        loss_scores: List[float] = []
        for case in case_dicts:
            dataset_eval = case.get("dataset_eval", {})
            score = dataset_eval.get("score")
            if isinstance(score, (int, float)):
                scores.append(float(score))

            loss_score = case.get("loss", {}).get("score")
            if isinstance(loss_score, (int, float)):
                loss_scores.append(float(loss_score))

        avg_score = sum(scores) / len(scores) if scores else None
        avg_loss = sum(loss_scores) / len(loss_scores) if loss_scores else None

        success_rate = None
        if scores:
            if self.report_config.success_threshold is not None:
                success_rate = sum(1 for s in scores if s >= self.report_config.success_threshold) / len(scores)
            elif all(s in (0, 1) for s in scores):
                success_rate = sum(scores) / len(scores)

        return {
            "num_cases": len(case_dicts),
            "average_score": avg_score,
            "average_loss": avg_loss,
            "success_rate": success_rate,
        }

    def extract_reflections(self, case_dicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get top reflection snippets from loss / sop suggestions.
        """
        reflections: List[Dict[str, Any]] = []
        for case in case_dicts:
            loss_info = case.get("loss", {})
            requirement = loss_info.get("requirement_for_previous")
            if requirement:
                reflections.append(
                    {
                        "case_id": case.get("case_id"),
                        "dataset_score": case.get("dataset_eval", {}).get("score"),
                        "loss_score": loss_info.get("score"),
                        "requirement_for_previous": requirement,
                    }
                )
        reflections.sort(
            key=lambda x: (
                x.get("dataset_score") if isinstance(x.get("dataset_score"), (int, float)) else -1,
                x.get("loss_score") if isinstance(x.get("loss_score"), (int, float)) else -1,
            )
        )
        return reflections[: self.report_config.top_k_reflections]

    def build_report(
            self,
            baseline_summary: Optional[Dict[str, Any]],
            final_summary: Dict[str, Any],
            training_curve: List[Dict[str, Any]],
            reflections: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        delta_score = None
        if baseline_summary and baseline_summary.get("average_score") is not None and final_summary.get("average_score") is not None:
            delta_score = final_summary["average_score"] - baseline_summary["average_score"]

        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "baseline": baseline_summary,
            "final": final_summary,
            "delta_average_score": delta_score,
            "training_curve": training_curve,
            "top_reflections": reflections,
        }

    def summarize_dir(self, case_dir: Path) -> Dict[str, Any]:
        case_dicts = self._load_cases_from_dir(case_dir)
        summary = self._summarize_cases(case_dicts)
        summary["case_dir"] = str(case_dir)
        return summary

    def collect_reflections_from_dir(self, case_dir: Path) -> List[Dict[str, Any]]:
        case_dicts = self._load_cases_from_dir(case_dir)
        return self.extract_reflections(case_dicts)

    @staticmethod
    def save_report(report: Dict[str, Any], save_path: Path):
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=4)

