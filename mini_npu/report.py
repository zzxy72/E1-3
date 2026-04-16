"""Formatting console reports."""

from mini_npu.constants import SCORE_PRECISION, UNDECIDED
from mini_npu.models import PerformanceResult, TestResult


def format_test_result(result: TestResult) -> str:
    if result.passed:
        return (
            f"{result.case_id}: Cross 점수={result.cross_score:.{SCORE_PRECISION}f}, "
            f"X 점수={result.x_score:.{SCORE_PRECISION}f}, 판정={result.predicted}, "
            f"expected={result.expected}, PASS"
        )
    if result.reason and result.cross_score is None and result.x_score is None:
        return f"{result.case_id}: FAIL ({result.reason})"
    base = (
        f"{result.case_id}: Cross 점수={result.cross_score:.{SCORE_PRECISION}f}, "
        f"X 점수={result.x_score:.{SCORE_PRECISION}f}, 판정={result.predicted}, "
        f"expected={result.expected}, FAIL"
    )
    if result.reason:
        return f"{base} ({result.reason})"
    return base


def summarize_results(results: list[TestResult]) -> str:
    total = len(results)
    passed = sum(1 for result in results if result.passed)
    failed_results = [result for result in results if not result.passed]

    lines = [
        "[결과 요약]",
        f"총 테스트 수: {total}",
        f"통과 수: {passed}",
        f"실패 수: {len(failed_results)}",
    ]
    if failed_results:
        lines.append("실패 케이스:")
        for result in failed_results:
            reason = result.reason or (
                f"expected={result.expected}, predicted={result.predicted or UNDECIDED}"
            )
            lines.append(f"- {result.case_id}: {reason}")
    return "\n".join(lines)


def format_performance_table(items: list[PerformanceResult]) -> str:
    lines = ["크기 | 방식 | 평균 시간(ms) | 연산 횟수(N^2) | 반복 횟수", "--- | --- | ---: | ---: | ---:"]
    for item in items:
        lines.append(
            f"{item.size}x{item.size} | {item.mode_name} | {item.avg_ms:.6f} | "
            f"{item.operation_count} | {item.repeat}"
        )
    return "\n".join(lines)
