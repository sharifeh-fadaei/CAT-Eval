from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .config import get_settings


class RunManager:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.settings.run_root.mkdir(parents=True, exist_ok=True)

    def create_run(self, metadata: Dict[str, Any]) -> str:
        run_id = self._make_run_id(metadata)
        run_dir = self._run_dir(run_id)
        run_dir.mkdir(parents=True, exist_ok=True)

        metadata_with_state = {
            **metadata,
            "run_id": run_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        self._write_json(run_dir / "metadata.json", metadata_with_state)
        return run_id

    def update_status(self, run_id: str, status: str, extra: Dict[str, Any] | None = None) -> None:
        run_dir = self._run_dir(run_id)
        metadata = self._read_json(run_dir / "metadata.json")
        metadata["status"] = status
        if extra:
            metadata.update(extra)
        self._write_json(run_dir / "metadata.json", metadata)

    def get_metadata(self, run_id: str) -> Dict[str, Any]:
        return self._read_json(self._run_dir(run_id) / "metadata.json")

    # -----------------------------
    # Run-id / directory naming
    # -----------------------------
    def _make_run_id(self, metadata: Dict[str, Any]) -> str:
        sample_names = self._infer_sample_names(metadata)
        model_keys = self._infer_model_keys(metadata)

        sample_part = self._sample_part(sample_names)
        models_part = self._models_part(model_keys)

        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        run_id_raw = f"{sample_part}__{models_part}__{ts}"
        return self._slug(run_id_raw, max_len=160)

    def _infer_sample_names(self, metadata: Dict[str, Any]) -> List[str]:
        # Prefer explicit lists if present
        candidates = (
            metadata.get("sample_names"),
            metadata.get("samples"),
        )
        for c in candidates:
            names = self._as_list_of_str(c)
            if names:
                return [self._slug(x, max_len=60) for x in names]

        # Single-sample fallbacks
        for key in ("sample_name", "sample"):
            v = metadata.get(key)
            if isinstance(v, str) and v.strip():
                return [self._slug(v.strip(), max_len=60)]

        # Sometimes you only have test_number
        tn = metadata.get("test_number")
        if tn is not None and str(tn).strip():
            return [self._slug(f"Test_{tn}", max_len=60)]

        return []

    def _infer_model_keys(self, metadata: Dict[str, Any]) -> List[str]:
        # Prefer explicit lists
        candidates = (
            metadata.get("models"),
            metadata.get("model_keys"),
        )
        for c in candidates:
            keys = self._as_list_of_str(c)
            if keys:
                return [self._to_model_key(x) for x in keys]

        # Single-model fallbacks
        for key in ("model_key", "model"):
            v = metadata.get(key)
            keys = self._as_list_of_str(v)
            if keys:
                return [self._to_model_key(x) for x in keys]

        return []

    def _to_model_key(self, s: str) -> str:
        """
        Convert provider ids like 'openai/gpt-5.1' -> 'GPT-5.1'
        and keep simple keys like 'GPT-5.1' unchanged.
        """
        s = s.strip()
        # If it looks like "provider/model", keep tail
        if "/" in s:
            s = s.split("/")[-1]
        return self._slug(s, max_len=60)

    def _sample_part(self, sample_names: List[str]) -> str:
        if not sample_names:
            return "unknown-samples"
        if len(sample_names) == 1:
            return sample_names[0]
        return f"{sample_names[0]}-{sample_names[-1]}"

    def _models_part(self, models: List[str]) -> str:
        if not models:
            return "unknown-models"
        models_sorted = sorted(models)
        joined = "+".join(models_sorted)
        return self._slug(joined, max_len=90)

    def _as_list_of_str(self, v: Any) -> List[str]:
        if v is None:
            return []
        if isinstance(v, list):
            out = []
            for x in v:
                sx = str(x).strip()
                if sx:
                    out.append(sx)
            return out
        if isinstance(v, str):
            # allow comma-separated strings
            parts = [p.strip() for p in v.split(",")]
            return [p for p in parts if p]
        return [str(v).strip()] if str(v).strip() else []

    def _slug(self, s: str, max_len: int = 160) -> str:
        s = s.strip()
        s = re.sub(r"\s+", "-", s)
        # prevent path separators
        s = s.replace("/", "-").replace("\\", "-")
        # keep safe filename chars
        s = re.sub(r"[^A-Za-z0-9._+\-]+", "", s)
        return s[:max_len] if len(s) > max_len else s

    # -----------------------------
    # I/O
    # -----------------------------
    def _run_dir(self, run_id: str) -> Path:
        return self.settings.run_root / run_id

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _read_json(self, path: Path) -> Dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))


run_manager = RunManager()
