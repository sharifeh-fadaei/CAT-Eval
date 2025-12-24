from __future__ import annotations

from typing import Dict, List, Tuple


FACTOR_WEIGHTS: Dict[str, float] = {
    "D1 – Factual Accuracy": 0.25,
    "D2 – Visual Encoding Fidelity": 0.15,
    "D3 – Context and Purpose": 0.15,
    "D4 – Comparative Reasoning": 0.15,
    "D5 – Accessibility and Brevity": 0.15,
    "D6 – Terminology and Conventions": 0.15,
}


class EvaluationValidationError(Exception):
    pass


def validate_evaluation_table(table: List[Dict]) -> None:
    if len(table) != len(FACTOR_WEIGHTS):
        raise EvaluationValidationError("Evaluation table must contain exactly six factors.")
    seen = set()
    for row in table:
        factor = row.get("factor")
        if factor not in FACTOR_WEIGHTS:
            raise EvaluationValidationError(f"Unknown factor: {factor}")
        if factor in seen:
            raise EvaluationValidationError(f"Duplicate factor: {factor}")
        seen.add(factor)


def compute_scores(table: List[Dict]) -> Tuple[float, List[Dict]]:
    validate_evaluation_table(table)
    weighted_total = 0.0
    for row in table:
        weight = FACTOR_WEIGHTS[row["factor"]]
        score = float(row.get("score_1_to_10", 0))
        weighted_total += weight * score

    if any(
        row["factor"] == "D1 – Factual Accuracy" and row.get("error_severity") == "Severe"
        for row in table
    ):
        weighted_total = min(weighted_total, 5.0)
    return weighted_total, table
