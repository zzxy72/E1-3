"""Core MAC implementations."""

from mini_npu.models import FlatMatrix, Matrix
from mini_npu.validator import validate_matching_sizes


def compute_mac(pattern: Matrix, filt: Matrix) -> float:
    validate_matching_sizes(pattern, filt)
    score = 0.0
    for row_index in range(len(pattern)):
        for col_index in range(len(pattern[row_index])):
            score += pattern[row_index][col_index] * filt[row_index][col_index]
    return score


def flatten_matrix(matrix: Matrix) -> FlatMatrix:
    return [value for row in matrix for value in row]


def compute_mac_flat(pattern: FlatMatrix, filt: FlatMatrix) -> float:
    if len(pattern) != len(filt):
        raise ValueError("평탄화된 패턴과 필터의 길이가 일치하지 않습니다.")
    score = 0.0
    for index in range(len(pattern)):
        score += pattern[index] * filt[index]
    return score

