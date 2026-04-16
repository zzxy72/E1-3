"""Pattern and filter generators for supported sizes."""

from mini_npu.models import Matrix


def generate_cross_pattern(size: int) -> Matrix:
    if size < 3:
        raise ValueError("패턴 크기는 3 이상이어야 합니다.")
    center = size // 2
    return [
        [1.0 if row == center or col == center else 0.0 for col in range(size)]
        for row in range(size)
    ]


def generate_x_pattern(size: int) -> Matrix:
    if size < 3:
        raise ValueError("패턴 크기는 3 이상이어야 합니다.")
    last = size - 1
    return [
        [1.0 if row == col or row + col == last else 0.0 for col in range(size)]
        for row in range(size)
    ]

