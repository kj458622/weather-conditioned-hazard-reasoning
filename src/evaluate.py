"""Simple evaluation for structured hazard reasoning outputs."""

from __future__ import annotations

from typing import Any, Dict, List

from utils import mean, rouge_l_f1


HAZARD_NORMALIZATION = {
    "front vehicle": "front_vehicle",
    "front_vehicle": "front_vehicle",
    "vehicle": "vehicle",
    "pedestrian": "pedestrian",
    "pedestrians": "pedestrian",
    "cyclist": "cyclist",
    "bicyclist": "cyclist",
    "bicycle": "cyclist",
    "two wheeler": "two_wheeler",
    "two-wheeler": "two_wheeler",
    "two_wheeler": "two_wheeler",
    "rider": "two_wheeler",
    "scooter rider": "two_wheeler",
    "unknown object": "unknown_object",
    "unknown_object": "unknown_object",
    "lane boundary": "lane_boundary",
    "lane_boundary": "lane_boundary",
}


def normalize_hazard_label(value: str) -> str:
    normalized = str(value).strip().lower().replace("-", " ").replace("_", " ")
    normalized = " ".join(normalized.split())
    return HAZARD_NORMALIZATION.get(normalized, normalized.replace(" ", "_"))


def evaluate_predictions(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute lightweight metrics for prototype validation."""
    total = len(records)
    if total == 0:
        return {
            "num_samples": 0,
            "json_parse_success_rate": 0.0,
            "hazard_object_accuracy": 0.0,
            "risk_level_accuracy": 0.0,
            "rouge_l_f1": 0.0,
        }

    json_success = 0
    hazard_correct = 0
    risk_correct = 0
    rouge_scores = []

    for record in records:
        prediction = record.get("prediction", {})
        target = record.get("target", {})
        if prediction.get("_parse_ok", False):
            json_success += 1

        pred_hazard = normalize_hazard_label(prediction.get("hazard_object", ""))
        tgt_hazard = normalize_hazard_label(target.get("hazard_object", ""))
        if pred_hazard and tgt_hazard and pred_hazard == tgt_hazard:
            hazard_correct += 1

        pred_risk = str(prediction.get("risk_level", "")).strip().lower()
        tgt_risk = str(target.get("risk_level", "")).strip().lower()
        if pred_risk and tgt_risk and pred_risk == tgt_risk:
            risk_correct += 1

        pred_explanation = str(prediction.get("explanation", "")).strip()
        tgt_explanation = str(target.get("explanation_ko", "")).strip()
        if pred_explanation and tgt_explanation:
            rouge_scores.append(rouge_l_f1(tgt_explanation, pred_explanation))

    return {
        "num_samples": total,
        "json_parse_success_rate": json_success / total,
        "hazard_object_accuracy": hazard_correct / total,
        "risk_level_accuracy": risk_correct / total,
        "rouge_l_f1": mean(rouge_scores),
    }
