"""Loading and validating JSON-based test data."""

from __future__ import annotations

import json
import re
from pathlib import Path

from mini_npu.models import FilterSet, PatternCase
from mini_npu.normalizer import normalize_label
from mini_npu.validator import validate_square_matrix

SIZE_PATTERN = re.compile(r"^size_(\d+)$")
CASE_PATTERN = re.compile(r"^size_(\d+)_(\d+)$")


def load_json_data(path: str) -> dict:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def _convert_matrix(raw_matrix) -> list[list[float]]:
    return [[float(value) for value in row] for row in raw_matrix]


def get_filter_payloads(raw_data: dict) -> dict:
    filters_block = raw_data.get("filters")
    if not isinstance(filters_block, dict):
        raise ValueError("data.json의 filters 필드가 누락되었거나 객체가 아닙니다.")
    return filters_block


def build_filter_set(key: str, value: dict) -> tuple[int, FilterSet]:
    match = SIZE_PATTERN.match(key)
    if not match:
        raise ValueError(f"필터 키 형식 오류: {key}")

    size = int(match.group(1))
    cross_matrix = None
    x_matrix = None

    if not isinstance(value, dict):
        raise ValueError(f"{key} 필터 정의가 객체 형식이 아닙니다.")

    for filter_name, matrix in value.items():
        normalized_name = normalize_label(filter_name)
        normalized_matrix = _convert_matrix(matrix)
        validate_square_matrix(normalized_matrix, size)
        if normalized_name == "Cross":
            cross_matrix = normalized_matrix
        elif normalized_name == "X":
            x_matrix = normalized_matrix

    if cross_matrix is None or x_matrix is None:
        raise ValueError(f"{key}에는 cross와 x 필터가 모두 필요합니다.")

    return size, FilterSet(size=size, cross=cross_matrix, x=x_matrix)


def get_pattern_payloads(raw_data: dict) -> dict:
    patterns_block = raw_data.get("patterns")
    if not isinstance(patterns_block, dict):
        raise ValueError("data.json의 patterns 필드가 누락되었거나 객체가 아닙니다.")
    return patterns_block


def build_pattern_case(case_id: str, payload: dict) -> PatternCase:
    match = CASE_PATTERN.match(case_id)
    if not match:
        raise ValueError(f"패턴 키 형식 오류: {case_id}")
    size = int(match.group(1))
    if not isinstance(payload, dict):
        raise ValueError(f"{case_id} 패턴 정의가 객체 형식이 아닙니다.")
    if "input" not in payload or "expected" not in payload:
        raise ValueError(f"{case_id} 패턴에 input 또는 expected 필드가 없습니다.")

    matrix = _convert_matrix(payload["input"])
    validate_square_matrix(matrix, size)
    expected = normalize_label(str(payload["expected"]))
    return PatternCase(case_id=case_id, size=size, pattern=matrix, expected=expected)
