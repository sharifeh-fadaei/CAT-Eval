from __future__ import annotations

from pathlib import Path
from typing import List, Dict

from docx import Document


class DocxParser:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def parse(self) -> List[Dict]:
        document = Document(self.path)
        samples: List[Dict] = []
        current: Dict[str, str] = {}
        for para in document.paragraphs:
            line = para.text.strip()
            if not line:
                continue
            if line.lower().startswith("sample_name"):
                if current:
                    samples.append(current)
                    current = {}
                current["sample_name"] = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("alt_text"):
                current["alt_text"] = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("caption"):
                current["caption"] = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("local_text"):
                current["local_text"] = line.split(":", 1)[-1].strip()
        if current:
            samples.append(current)
        return samples
