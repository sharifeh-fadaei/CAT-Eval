from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def write_batch_json(run_dir: Path, run_id: str, model_key: str, batch_index: int, records: List[Dict[str, Any]]) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    output_path = run_dir / f"batch_{batch_index}_{model_key}.json"
    output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return output_path


def write_single_json(run_dir: Path, run_id: str, record: Dict[str, Any]) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    output_path = run_dir / f"single_{run_id}.json"
    output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return output_path
