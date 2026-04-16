"""Console UI helpers."""

from mini_npu.constants import (
    DEFAULT_REPEAT,
    EPSILON,
    SCORE_PRECISION,
    STANDARD_CROSS,
    STANDARD_X,
    UNDECIDED,
)
from mini_npu.generator import generate_cross_pattern, generate_x_pattern
from mini_npu.judge import evaluate_pattern
from mini_npu.models import FilterSet, Matrix
from mini_npu.performance import analyze_flat_performance, analyze_mac_performance
from mini_npu.report import format_performance_table
from mini_npu.validator import parse_numeric_row


def prompt_matrix(size: int, title: str) -> Matrix:
    while True:
        print(f"{title} ({size}줄 입력, 공백 구분)")
        rows: Matrix = []
        try:
            for row_index in range(size):
                line = input(f"{row_index + 1}> ")
                rows.append(parse_numeric_row(line, size))
            return rows
        except ValueError as error:
            print(error)
            print("처음부터 다시 입력해 주세요.")


def prompt_pattern_type() -> str:
    while True:
        print("패턴 종류를 선택하세요.")
        print("1. Cross")
        print("2. X")
        selection = input("선택: ").strip()
        if selection == "1":
            return STANDARD_CROSS
        if selection == "2":
            return STANDARD_X
        print("지원하지 않는 선택입니다. 1 또는 2를 입력하세요.")


def prompt_size() -> int:
    while True:
        raw = input("크기 N 입력(3 이상): ").strip()
        try:
            size = int(raw)
        except ValueError:
            print("입력 형식 오류: 크기 N은 정수여야 합니다.")
            continue
        if size < 3:
            print("입력 형식 오류: 크기 N은 3 이상이어야 합니다.")
            continue
        return size


def display_generated_pattern(title: str, pattern: Matrix) -> None:
    print(title)
    for row in pattern:
        print(" ".join(f"{value:.0f}" for value in row))


def display_analysis(pattern: Matrix, filters: FilterSet, mode_label: str) -> None:
    result = evaluate_pattern(pattern, filters, EPSILON)

    performance_rows = [
        analyze_mac_performance(pattern, filters, DEFAULT_REPEAT),
        analyze_flat_performance(pattern, filters, DEFAULT_REPEAT),
    ]

    print(f"\n[3] MAC 결과 - {mode_label}")
    print(f"A 점수: {result.cross_score:.{SCORE_PRECISION}f}")
    print(f"B 점수: {result.x_score:.{SCORE_PRECISION}f}")
    print(f"연산 시간(평균/{DEFAULT_REPEAT}회): {performance_rows[0].avg_ms:.6f} ms")
    if result.predicted == UNDECIDED:
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    elif result.predicted == STANDARD_CROSS:
        print("판정: A")
    else:
        print("판정: B")

    print("\n[4] 성능 분석")
    print(format_performance_table(performance_rows))


def run_manual_mode() -> None:
    print("\n[1] 필터 입력")
    filter_a = prompt_matrix(3, "필터 A")
    filter_b = prompt_matrix(3, "필터 B")
    print("저장 확인: 필터 A, B 입력 완료")

    print("\n[2] 패턴 입력")
    pattern = prompt_matrix(3, "패턴")

    filters = FilterSet(size=3, cross=filter_a, x=filter_b)
    display_analysis(pattern, filters, "사용자 입력")


def run_generated_mode() -> None:
    print("\n[1] 기준 필터 생성")
    size = prompt_size()
    filters = FilterSet(
        size=size,
        cross=generate_cross_pattern(size),
        x=generate_x_pattern(size),
    )
    print("저장 확인: Cross/X 기준 필터 생성 완료")
    print("A 기준 필터 = Cross")
    display_generated_pattern("A 필터:", filters.cross)
    print("B 기준 필터 = X")
    display_generated_pattern("B 필터:", filters.x)

    print("\n[2] 패턴 자동 생성")
    pattern_type = prompt_pattern_type()
    if pattern_type == STANDARD_CROSS:
        pattern = generate_cross_pattern(size)
    else:
        pattern = generate_x_pattern(size)

    display_generated_pattern("생성된 패턴:", pattern)
    display_analysis(pattern, filters, "패턴 자동 생성")
