from __future__ import annotations

from typing import List, Set


class SampleSelectorError(Exception):
    pass


def parse_selector(selector: str) -> List[str]:
    selector = selector.strip()
    if not selector:
        raise SampleSelectorError("Sample selector cannot be empty.")

    parts = [part.strip() for part in selector.split(",") if part.strip()]
    samples: Set[str] = set()
    for part in parts:
        if "-" in part:
            start, end = part.split("-", 1)
            prefix = start.rstrip("0123456789")
            try:
                start_num = int(start[len(prefix) :])
                end_num = int(end[len(prefix) :])
            except ValueError:
                raise SampleSelectorError(f"Invalid range component: {part}")
            if end_num < start_num:
                raise SampleSelectorError(f"Range end before start: {part}")
            for num in range(start_num, end_num + 1):
                samples.add(f"{prefix}{num}")
        else:
            samples.add(part)
    return sorted(samples)


def validate_samples(requested: List[str], available: List[str]) -> List[str]:
    missing = [name for name in requested if name not in available]
    if missing:
        raise SampleSelectorError(f"Samples not found: {', '.join(missing)}")
    return requested
