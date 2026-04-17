"""Pattern-related classes for the Mini NPU simulator.

이 파일은 입력 패턴 데이터를 표현하는 Pattern 클래스를 중심으로 구성된다.
패턴 자체가 자신의 크기, 1차원 변환, 검증 책임을 함께 가지도록 만들어
시스템을 설명할 때 "입력 데이터 객체"로 이해하기 쉽게 정리했다.
"""

from dataclasses import dataclass, field
from typing import List

from typing import Any, Dict, List

Matrix = List[List[float]]


@dataclass(frozen=True)
class JsonData:
    """data.json의 구조를 그대로 담는 데이터 객체"""
    filters: Dict[str, Any]
    patterns: Dict[str, Any]



@dataclass(frozen=True)
class Pattern:
    """입력 패턴 데이터를 표현한다."""

    values: Matrix
    expected: str = ""
    case_id: str = ""
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

    @classmethod
    def from_rows(
        cls, rows: Matrix, expected: str = "", case_id: str = ""
    ) -> "Pattern":
        return cls(values=rows, expected=expected, case_id=case_id)


@dataclass(frozen=True)
class TestResult:
    """패턴 하나에 대한 판정 결과를 표현한다."""

    case_id: str
    size: int
    expected: str
    predicted: str
    passed: bool
    reason: str = ""
    scores: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class PerformanceResult:
    """성능 측정 결과 한 줄을 표현한다."""

    size: int
    avg_ms: float
    operation_count: int
    repeat: int
    mode_name: str
