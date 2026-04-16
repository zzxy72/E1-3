"""Mini NPU Simulator entry point."""

from __future__ import annotations

from pathlib import Path

from mini_npu.constants import DEFAULT_REPEAT, EPSILON, SUPPORTED_SIZES
from mini_npu.console import run_generated_mode, run_manual_mode
from mini_npu.generator import generate_cross_pattern, generate_x_pattern
from mini_npu.judge import evaluate_pattern
from mini_npu.json_loader import (
    build_filter_set,
    build_pattern_case,
    get_filter_payloads,
    get_pattern_payloads,
    load_json_data,
)
from mini_npu.models import FilterSet, TestResult
from mini_npu.performance import analyze_flat_performance, analyze_mac_performance
from mini_npu.report import format_performance_table, format_test_result, summarize_results
from mini_npu.validator import validate_matching_sizes


def build_generated_filter(size: int) -> FilterSet:
    return FilterSet(
        size=size,
        cross=generate_cross_pattern(size),
        x=generate_x_pattern(size),
    )


def run_json_mode(data_path: str = "data.json") -> None:
    data = load_json_data(data_path)
    filter_payloads = get_filter_payloads(data)
    filters: dict[int, FilterSet] = {}
    filter_errors: dict[str, str] = {}
    for key, payload in filter_payloads.items():
        try:
            size, filter_set = build_filter_set(key, payload)
            filters[size] = filter_set
        except Exception as error:
            filter_errors[key] = str(error)
    pattern_payloads = get_pattern_payloads(data)

    print("\n[1] 필터 로드")
    for key, payload in filter_payloads.items():
        try:
            size, _ = build_filter_set(key, payload)
            print(f"size_{size} 필터 로드 완료 (Cross, X)")
        except Exception as error:
            print(f"{key} 필터 로드 실패: {error}")

    print("\n[2] 패턴 분석")
    results: list[TestResult] = []
    for case_id, payload in pattern_payloads.items():
        try:
            case = build_pattern_case(case_id, payload)
            filter_set = filters.get(case.size)
            if filter_set is None:
                key = f"size_{case.size}"
                reason = filter_errors.get(key, f"{key} 필터가 없습니다.")
                raise ValueError(reason)
            validate_matching_sizes(case.pattern, filter_set.cross)
            validate_matching_sizes(case.pattern, filter_set.x)
            judge_result = evaluate_pattern(case.pattern, filter_set, EPSILON)
            passed = judge_result.predicted == case.expected
            if not passed and judge_result.predicted == "UNDECIDED":
                reason = "동점 규칙으로 UNDECIDED 판정"
            elif not passed:
                reason = None
            else:
                reason = None

            test_result = TestResult(
                case_id=case.case_id,
                size=case.size,
                expected=case.expected,
                predicted=judge_result.predicted,
                passed=passed,
                reason=reason,
                cross_score=judge_result.cross_score,
                x_score=judge_result.x_score,
            )
        except Exception as error:
            test_result = TestResult(
                case_id=case_id,
                size=0,
                expected=None,
                predicted=None,
                passed=False,
                reason=str(error),
            )

        results.append(test_result)
        print(format_test_result(test_result))

    print("\n[3] 성능 분석")
    performance_items = []
    for size in SUPPORTED_SIZES:
        benchmark_filters = filters.get(size) or build_generated_filter(size)
        benchmark_pattern = generate_cross_pattern(size)
        performance_items.append(
            analyze_mac_performance(benchmark_pattern, benchmark_filters, DEFAULT_REPEAT)
        )
        performance_items.append(
            analyze_flat_performance(benchmark_pattern, benchmark_filters, DEFAULT_REPEAT)
        )
    print(format_performance_table(performance_items))

    print()
    print(summarize_results(results))


def main() -> None:
    print("=== Mini NPU Simulator ===")
    print("\n[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("3. 패턴 자동 생성")
    selection = input("선택: ").strip()

    if selection == "1":
        run_manual_mode()
        return

    if selection == "2":
        data_path = Path(__file__).with_name("data.json")
        run_json_mode(str(data_path))
        return

    if selection == "3":
        run_generated_mode()
        return

    print("지원하지 않는 선택입니다. 1, 2 또는 3을 입력하세요.")


if __name__ == "__main__":
    main()
