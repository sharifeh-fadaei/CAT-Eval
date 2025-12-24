from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict


class JsonParser:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def parse(self) -> List[Dict]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "samples" in data:
            return list(data["samples"])
        if isinstance(data, list):
            return list(data)
        raise ValueError("JSON file must be a list of samples or contain a 'samples' array")
