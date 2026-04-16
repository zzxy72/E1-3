"""Helpers for standardizing labels."""

from mini_npu.constants import STANDARD_CROSS, STANDARD_X


def normalize_label(raw: str) -> str:
    """Convert supported raw labels to standard internal labels."""
    value = raw.strip().lower()
    if value in {"+", "cross"}:
        return STANDARD_CROSS
    if value == "x":
        return STANDARD_X
    raise ValueError(f"지원하지 않는 라벨입니다: {raw}")

