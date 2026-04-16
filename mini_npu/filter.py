"""Filter-related classes for the Mini NPU simulator.

이 파일은 비교 기준이 되는 필터를 Filter 클래스로 표현한다.
필터가 자신의 라벨, 행렬 값, 점수 계산 책임을 가지게 해
시스템을 설명할 때 "비교 기준 객체"로 이해하기 쉽게 정리했다.
"""

from dataclasses import dataclass, field
from typing import List

from mini_npu.pattern import Matrix, Pattern

STANDARD_CROSS = "Cross"
STANDARD_X = "X"
UNDECIDED = "UNDECIDED"


@dataclass(frozen=True)
class Filter:
    """Cross 또는 X 기준 필터를 표현한다."""

    label: str
    values: Matrix
    # 객체 생성 시점에 1회만 계산된 1차원 데이터를 보관한다.
    flat: List[float] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        # frozen=True 이므로 object.__setattr__로 초기화한다.
        object.__setattr__(
            self, "flat", [value for row in self.values for value in row]
        )

    @property
    def size(self) -> int:
        return len(self.values)

    def flatten(self) -> List[float]:
        # 이미 생성 시점에 변환된 캐시를 반환한다.
        return self.flat

    def validate_square(self, expected_size: int) -> None:
        if len(self.values) != expected_size:
            raise ValueError(f"행 수 오류: {expected_size}개의 행이 필요합니다.")
        for row in self.values:
            if len(row) != expected_size:
                raise ValueError(
                    f"열 수 오류: 각 행은 {expected_size}개의 원소를 가져야 합니다."
                )

    def score(self, pattern: Pattern) -> float:
        self.validate_matching_size(pattern)
        score = 0.0
        for row_index in range(pattern.size):
            for col_index in range(pattern.size):
                # 위치별 곱셈: 같은 위치의 패턴 값과 필터 값을 곱한다.
                score += pattern.values[row_index][col_index] * self.values[row_index][col_index]
                # 누적 합산: 위치별 곱셈 결과를 score에 계속 더한다.
        # 점수 반환: 최종 누적합을 MAC 점수로 반환한다.
        return score

    def score_flat(self, pattern: Pattern) -> float:
        if len(pattern.flat) != len(self.flat):
            raise ValueError("평탄화된 패턴과 필터의 길이가 일치하지 않습니다.")
        score = 0.0
        for index in range(len(pattern.flat)):
            # 순수 MAC: 이미 사전 변환된 1차원 데이터를 그대로 사용한다.
            score += pattern.flat[index] * self.flat[index]
            # 누적 합산: 각 위치의 곱셈 결과를 score에 더한다.
        # 점수 반환: 1차원 방식으로 계산한 최종 MAC 점수를 반환한다.
        return score

    def validate_matching_size(self, pattern: Pattern) -> None:
        if pattern.size != self.size:
            raise ValueError("패턴과 필터의 크기가 일치하지 않습니다.")
        for pattern_row, filter_row in zip(pattern.values, self.values):
            if len(pattern_row) != len(filter_row):
                raise ValueError("패턴과 필터의 크기가 일치하지 않습니다.")

    @classmethod
    def normalize_label(cls, raw: str) -> str:
        value = raw.strip().lower()
        if value in {"+", "cross"}:
            return STANDARD_CROSS
        if value == "x":
            return STANDARD_X
        raise ValueError(f"지원하지 않는 라벨입니다: {raw}")

    @classmethod
    def generate_cross(cls, size: int) -> "Filter":
        if size < 3:
            raise ValueError("패턴 크기는 3 이상이어야 합니다.")
        center = size // 2
        values = [
            [1.0 if row == center or col == center else 0.0 for col in range(size)]
            for row in range(size)
        ]
        return cls(label=STANDARD_CROSS, values=values)

    @classmethod
    def generate_x(cls, size: int) -> "Filter":
        if size < 3:
            raise ValueError("패턴 크기는 3 이상이어야 합니다.")
        last = size - 1
        values = [
            [1.0 if row == col or row + col == last else 0.0 for col in range(size)]
            for row in range(size)
        ]
        return cls(label=STANDARD_X, values=values)
