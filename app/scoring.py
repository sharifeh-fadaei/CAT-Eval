from __future__ import annotations

from typing import Dict, List, Tuple

# Canonical rubric: MUST match hqcat_v1 prompt exactly. :contentReference[oaicite:1]{index=1}
ORDERED_FACTORS: List[str] = [
    "D1 – Factual Accuracy",
    "D1 – Completeness & Key Insights",
    "D1 – Context Alignment",
    "D2 – Conciseness & Brevity",
    "D2 – Language Quality & Tone",
    "D2 – Imaginability & Visual Detail",
]

FACTOR_WEIGHTS: Dict[str, float] = {
    "D1 – Factual Accuracy": 0.25,
    "D1 – Completeness & Key Insights": 0.25,
    "D1 – Context Alignment": 0.20,
    "D2 – Conciseness & Brevity": 0.10,
    "D2 – Language Quality & Tone": 0.10,
    "D2 – Imaginability & Visual Detail": 0.10,
}


class EvaluationValidationError(Exception):
    pass


def validate_evaluation_table(table: List[Dict]) -> None:
    if len(table) != len(ORDERED_FACTORS):
        raise EvaluationValidationError(
            f"Evaluation table must contain exactly {len(ORDERED_FACTORS)} factors."
        )

    # validate factor set + duplicates + expected order (prevents LLM shuffling)
    seen = set()
    for i, row in enumerate(table):
        factor = row.get("factor")
        if factor not in FACTOR_WEIGHTS:
            raise EvaluationValidationError(f"Unknown factor: {factor}")
        if factor in seen:
            raise EvaluationValidationError(f"Duplicate factor: {factor}")
        expected = ORDERED_FACTORS[i]
        if factor != expected:
            raise EvaluationValidationError(
                f"Invalid factor order at row {i+1}: got '{factor}' but expected '{expected}'"
            )
        seen.add(factor)

    # weights must sum to 1.00 exactly (within float tolerance)
    total_w = sum(FACTOR_WEIGHTS.values())
    if abs(total_w - 1.0) > 1e-9:
        raise EvaluationValidationError(f"Factor weights must sum to 1.0 (got {total_w}).")


def compute_scores(table: List[Dict]) -> Tuple[float, List[Dict]]:
    validate_evaluation_table(table)

    weighted_total = 0.0
    for row in table:
        factor = row["factor"]
        weight = FACTOR_WEIGHTS[factor]
        score = float(row.get("score_1_to_10", 0))
        weighted_total += weight * score

    # Severe factual accuracy cap (as specified in the prompt). :contentReference[oaicite:2]{index=2}
    if any(
        row.get("factor") == "D1 – Factual Accuracy" and row.get("error_severity") == "Severe"
        for row in table
    ):
        weighted_total = min(weighted_total, 5.0)

    return weighted_total, table
