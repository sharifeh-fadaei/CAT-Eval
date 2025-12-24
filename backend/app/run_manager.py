from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .config import get_settings


class RunManager:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.settings.run_root.mkdir(parents=True, exist_ok=True)

    def create_run(self, metadata: Dict[str, Any]) -> str:
        run_id = uuid.uuid4().hex
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

    def _run_dir(self, run_id: str) -> Path:
        return self.settings.run_root / run_id

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _read_json(self, path: Path) -> Dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))


run_manager = RunManager()
