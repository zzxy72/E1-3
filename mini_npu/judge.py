"""Score comparison and case evaluation."""

from mini_npu.constants import EPSILON, STANDARD_CROSS, STANDARD_X, UNDECIDED
from mini_npu.mac import compute_mac
from mini_npu.models import FilterSet, JudgeResult, Matrix


def judge_scores(cross_score: float, x_score: float, epsilon: float = EPSILON) -> str:
    if abs(cross_score - x_score) < epsilon:
        return UNDECIDED
    if cross_score > x_score:
        return STANDARD_CROSS
    return STANDARD_X


def evaluate_pattern(
    pattern: Matrix, filters: FilterSet, epsilon: float = EPSILON
) -> JudgeResult:
    cross_score = compute_mac(pattern, filters.cross)
    x_score = compute_mac(pattern, filters.x)
    predicted = judge_scores(cross_score, x_score, epsilon)
    return JudgeResult(
        cross_score=cross_score,
        x_score=x_score,
        predicted=predicted,
        epsilon_used=epsilon,
    )

