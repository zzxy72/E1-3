"""Validation and parsing utilities."""

from mini_npu.models import Matrix


def parse_numeric_row(line: str, expected_size: int) -> list[float]:
    parts = line.strip().split()
    if len(parts) != expected_size:
        raise ValueError(
            f"입력 형식 오류: 각 줄에 {expected_size}개의 숫자를 공백으로 구분해 입력하세요."
        )

    try:
        return [float(value) for value in parts]
    except ValueError as exc:
        raise ValueError("입력 형식 오류: 숫자만 입력할 수 있습니다.") from exc


def validate_square_matrix(matrix: Matrix, expected_size: int) -> None:
    if len(matrix) != expected_size:
        raise ValueError(f"행 수 오류: {expected_size}개의 행이 필요합니다.")

    for row in matrix:
        if len(row) != expected_size:
            raise ValueError(
                f"열 수 오류: 각 행은 {expected_size}개의 원소를 가져야 합니다."
            )


def validate_matching_sizes(pattern: Matrix, filt: Matrix) -> None:
    if len(pattern) != len(filt):
        raise ValueError("패턴과 필터의 크기가 일치하지 않습니다.")
    for pattern_row, filter_row in zip(pattern, filt):
        if len(pattern_row) != len(filter_row):
            raise ValueError("패턴과 필터의 크기가 일치하지 않습니다.")

