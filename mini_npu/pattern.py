"""Pattern-related classes for the Mini NPU simulator.

이 파일은 입력 패턴 데이터를 표현하는 Pattern 클래스를 중심으로 구성된다.
패턴 자체가 자신의 크기, 1차원 변환, 검증 책임을 함께 가지도록 만들어
시스템을 설명할 때 "입력 데이터 객체"로 이해하기 쉽게 정리했다.
"""

from dataclasses import dataclass
from typing import List, Optional

Matrix = List[List[float]]


@dataclass(frozen=True)
class Pattern:
    """입력 패턴 데이터를 표현한다."""

    values: Matrix
    expected: Optional[str] = None
    case_id: str = ""

    @property
    def size(self) -> int:
        return len(self.values)

    def flatten(self) -> List[float]:
        return [value for row in self.values for value in row]

    def validate_square(self, expected_size: int) -> None:
        if len(self.values) != expected_size:
            raise ValueError(f"행 수 오류: {expected_size}개의 행이 필요합니다.")
        for row in self.values:
            if len(row) != expected_size:
                raise ValueError(
                    f"열 수 오류: 각 행은 {expected_size}개의 원소를 가져야 합니다."
                )

    @classmethod
    def from_rows(
        cls, rows: Matrix, expected: Optional[str] = None, case_id: str = ""
    ) -> "Pattern":
        return cls(values=rows, expected=expected, case_id=case_id)


@dataclass(frozen=True)
class TestResult:
    """패턴 하나에 대한 판정 결과를 표현한다."""

    case_id: str
    size: int
    expected: Optional[str]
    predicted: Optional[str]
    passed: bool
    reason: Optional[str]
    cross_score: Optional[float] = None
    x_score: Optional[float] = None


@dataclass(frozen=True)
class PerformanceResult:
    """성능 측정 결과 한 줄을 표현한다."""

    size: int
    avg_ms: float
    operation_count: int
    repeat: int
    mode_name: str
