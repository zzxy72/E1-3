"""Dataclasses used across the simulator."""

from dataclasses import dataclass


Matrix = list[list[float]]
FlatMatrix = list[float]


@dataclass(frozen=True)
class FilterSet:
    size: int
    cross: Matrix
    x: Matrix


@dataclass(frozen=True)
class PatternCase:
    case_id: str
    size: int
    pattern: Matrix
    expected: str


@dataclass(frozen=True)
class JudgeResult:
    cross_score: float
    x_score: float
    predicted: str
    epsilon_used: float


@dataclass(frozen=True)
class TestResult:
    case_id: str
    size: int
    expected: str | None
    predicted: str | None
    passed: bool
    reason: str | None
    cross_score: float | None = None
    x_score: float | None = None


@dataclass(frozen=True)
class PerformanceResult:
    size: int
    avg_ms: float
    operation_count: int
    repeat: int
    mode_name: str = "2D"

