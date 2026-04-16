"""Simulator class for the Mini NPU simulator.

이 파일은 MiniNPUSimulator 클래스를 중심으로 전체 실행 흐름을 담당한다.
사용자 입력, JSON 분석, 패턴 자동 생성, 결과 출력, 성능 분석을 모두 이 클래스가 조립한다.
따라서 시스템은 Pattern, Filter, MiniNPUSimulator 세 클래스로 이해할 수 있다.
"""

import json
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Tuple

from mini_npu.filter import Filter, STANDARD_CROSS, STANDARD_X, UNDECIDED
from mini_npu.pattern import Matrix, Pattern, PerformanceResult, TestResult


class MiniNPUSimulator:
    """사용자 입력, JSON 분석, 자동 생성 모드의 전체 실행 흐름을 관리한다."""

    epsilon = 1e-9
    repeat = 10
    supported_sizes = (3, 5, 13, 25)
    score_precision = 10

    #region 입력 처리 관련
    def prompt_matrix(self, size: int, title: str) -> Matrix:
        while True:
            print(f"{title} ({size}줄 입력, 공백 구분)")
            rows = []
            try:
                for row_index in range(size):
                    line = input(f"{row_index + 1}> ")
                    rows.append(self.parse_numeric_row(line, size))
                return rows
            except ValueError as error:
                print(error)
                print("처음부터 다시 입력해 주세요.")

    def prompt_pattern_type(self) -> str:
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

    def prompt_size(self) -> int:
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

    def parse_numeric_row(self, line: str, expected_size: int) -> List[float]:
        parts = line.strip().split()
        if len(parts) != expected_size:
            raise ValueError(
                f"입력 형식 오류: 각 줄에 {expected_size}개의 숫자를 공백으로 구분해 입력하세요."
            )
        try:
            return [float(value) for value in parts]
        except ValueError as exc:
            raise ValueError("입력 형식 오류: 숫자만 입력할 수 있습니다.") from exc

    def print_matrix(self, title: str, matrix: Matrix) -> None:
        print(title)
        for row in matrix:
            print(" ".join(f"{value:.0f}" for value in row))
    #endregion

    def judge_scores(self, cross_score: float, x_score: float) -> str:
        if abs(cross_score - x_score) < self.epsilon:
            return UNDECIDED
        if cross_score > x_score:
            return STANDARD_CROSS
        return STANDARD_X

    def evaluate_pattern(
        self, pattern: Pattern, cross_filter: Filter, x_filter: Filter
    ) -> Tuple[float, float, str]:
        cross_score = cross_filter.score(pattern)
        x_score = x_filter.score(pattern)
        predicted = self.judge_scores(cross_score, x_score)
        return cross_score, x_score, predicted

    #region 성능 분석 관련
    def measure_average_ms(self, func) -> float:
        start = perf_counter()
        for _ in range(self.repeat):
            func()
        end = perf_counter()
        return (end - start) * 1000.0 / self.repeat

    def analyze_performance(
        self, pattern: Pattern, cross_filter: Filter, x_filter: Filter
    ) -> List[PerformanceResult]:
        avg_2d = self.measure_average_ms(
            lambda: (cross_filter.score(pattern), x_filter.score(pattern))
        )
        avg_1d = self.measure_average_ms(
            lambda: (cross_filter.score_flat(pattern), x_filter.score_flat(pattern))
        )
        operation_count = pattern.size * pattern.size
        return [
            PerformanceResult(pattern.size, avg_2d, operation_count, self.repeat, "2D"),
            PerformanceResult(
                pattern.size, avg_1d, operation_count, self.repeat, "1D(flat)"
            ),
        ]
    #endregion

    #region 결과 출력 관련
    def format_test_result(self, result: TestResult) -> str:
        if result.cross_score is None or result.x_score is None:
            return f"{result.case_id}: FAIL ({result.reason})"

        base = (
            f"{result.case_id}: Cross 점수={result.cross_score:.{self.score_precision}f}, "
            f"X 점수={result.x_score:.{self.score_precision}f}, 판정={result.predicted}, "
            f"expected={result.expected}"
        )
        if result.passed:
            return f"{base}, PASS"
        if result.reason:
            return f"{base}, FAIL ({result.reason})"
        return f"{base}, FAIL"

    def summarize_results(self, results: List[TestResult]) -> str:
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

    def format_performance_table(self, items: List[PerformanceResult]) -> str:
        lines = [
            "크기 | 방식 | 평균 시간(ms) | 연산 횟수(N^2) | 반복 횟수",
            "--- | --- | ---: | ---: | ---:",
        ]
        for item in items:
            lines.append(
                f"{item.size}x{item.size} | {item.mode_name} | {item.avg_ms:.6f} | "
                f"{item.operation_count} | {item.repeat}"
            )
        return "\n".join(lines)

    def print_analysis(
        self,
        pattern: Pattern,
        cross_filter: Filter,
        x_filter: Filter,
        mode_label: str,
    ) -> None:
        cross_score, x_score, predicted = self.evaluate_pattern(
            pattern, cross_filter, x_filter
        )
        performance_rows = self.analyze_performance(pattern, cross_filter, x_filter)

        print(f"\n[3] MAC 결과 - {mode_label}")
        print(f"A 점수: {cross_score:.{self.score_precision}f}")
        print(f"B 점수: {x_score:.{self.score_precision}f}")
        print(f"연산 시간(평균/{self.repeat}회): {performance_rows[0].avg_ms:.6f} ms")
        if predicted == UNDECIDED:
            print(f"판정: 판정 불가 (|A-B| < {self.epsilon})")
        elif predicted == STANDARD_CROSS:
            print("판정: A")
        else:
            print("판정: B")

        print("\n[4] 성능 분석")
        print(self.format_performance_table(performance_rows))
    #endregion

    def build_generated_filters(self, size: int) -> Tuple[Filter, Filter]:
        return Filter.generate_cross(size), Filter.generate_x(size)

    #region JSON 처리 관련
    def convert_matrix(self, raw_matrix: Any) -> Matrix:
        return [[float(value) for value in row] for row in raw_matrix]

    def load_json_data(self, path: str) -> Dict[str, Any]:
        with Path(path).open("r", encoding="utf-8") as file:
            return json.load(file)

    def build_filter_map(self, key: str, value: Dict[str, Any]) -> Tuple[int, Dict[str, Filter]]:
        parts = key.split("_")
        if len(parts) != 2 or parts[0] != "size" or not parts[1].isdigit():
            raise ValueError(f"필터 키 형식 오류: {key}")

        size = int(parts[1])
        if not isinstance(value, dict):
            raise ValueError(f"{key} 필터 정의가 객체 형식이 아닙니다.")

        filters: Dict[str, Filter] = {}
        for filter_name, matrix in value.items():
            # expected('+', 'x')와 filter 키('cross', 'x')가 프로그램 내부에서
            # 표준 라벨(Cross/X)로 정규화되어 비교
            normalized_name = Filter.normalize_label(filter_name)
            filter_obj = Filter(normalized_name, self.convert_matrix(matrix))
            filter_obj.validate_square(size)
            filters[normalized_name] = filter_obj

        if STANDARD_CROSS not in filters or STANDARD_X not in filters:
            raise ValueError(f"{key}에는 cross와 x 필터가 모두 필요합니다.")
        return size, filters

    def build_pattern(self, case_id: str, payload: Dict[str, Any]) -> Pattern:
        # 패턴 키(size_{N}_{idx})에서 N을 읽어 올바른 필터를 선택하기 위해 N을 추출한다.
        parts = case_id.split("_")
        if (
            len(parts) != 3
            or parts[0] != "size"
            or not parts[1].isdigit()
            or not parts[2].isdigit()
        ):
            raise ValueError(f"패턴 키 형식 오류: {case_id}")

        size = int(parts[1])
        if not isinstance(payload, dict):
            raise ValueError(f"{case_id} 패턴 정의가 객체 형식이 아닙니다.")
        if "input" not in payload or "expected" not in payload:
            raise ValueError(f"{case_id} 패턴에 input 또는 expected 필드가 없습니다.")

        pattern = Pattern(
            values=self.convert_matrix(payload["input"]),
            # expected('+', 'x')와 filter 키('cross', 'x')가 프로그램 내부에서
            # 표준 라벨(Cross/X)로 정규화되어 비교
            expected=Filter.normalize_label(str(payload["expected"])),
            case_id=case_id,
        )
        pattern.validate_square(size)
        return pattern
    #endregion

    def run_manual_mode(self) -> None:
        print("\n[1] 필터 입력")
        cross_filter = Filter(STANDARD_CROSS, self.prompt_matrix(3, "필터 A"))
        x_filter = Filter(STANDARD_X, self.prompt_matrix(3, "필터 B"))
        print("저장 확인: 필터 A, B 입력 완료")

        print("\n[2] 패턴 입력")
        pattern = Pattern.from_rows(self.prompt_matrix(3, "패턴"))

        self.print_analysis(pattern, cross_filter, x_filter, "사용자 입력")

    def run_generated_mode(self) -> None:
        print("\n[1] 기준 필터 생성")
        size = self.prompt_size()
        cross_filter, x_filter = self.build_generated_filters(size)
        print("저장 확인: Cross/X 기준 필터 생성 완료")
        print("A 기준 필터 = Cross")
        self.print_matrix("A 필터:", cross_filter.values)
        print("B 기준 필터 = X")
        self.print_matrix("B 필터:", x_filter.values)

        print("\n[2] 패턴 자동 생성")
        pattern_type = self.prompt_pattern_type()
        if pattern_type == STANDARD_CROSS:
            pattern = Pattern.from_rows(Filter.generate_cross(size).values)
        else:
            pattern = Pattern.from_rows(Filter.generate_x(size).values)

        self.print_matrix("생성된 패턴:", pattern.values)
        self.print_analysis(pattern, cross_filter, x_filter, "패턴 자동 생성")

    def run_json_mode(self, data_path: str) -> None:
        # data.json의 filters/patterns를 로드
        data = self.load_json_data(data_path)
        filter_payloads = data.get("filters", {})
        pattern_payloads = data.get("patterns", {})

        filters_by_size: Dict[int, Dict[str, Filter]] = {}
        filter_errors: Dict[str, str] = {}
        for key, payload in filter_payloads.items():
            try:
                size, filter_map = self.build_filter_map(key, payload)
                filters_by_size[size] = filter_map
            except Exception as error:
                filter_errors[key] = str(error)

        print("\n[1] 필터 로드")
        for key, payload in filter_payloads.items():
            try:
                size, _ = self.build_filter_map(key, payload)
                print(f"size_{size} 필터 로드 완료 (Cross, X)")
            except Exception as error:
                print(f"{key} 필터 로드 실패: {error}")

        print("\n[2] 패턴 분석")
        results: List[TestResult] = []
        for case_id, payload in pattern_payloads.items():
            try:
                # 패턴 키(size_{N}_{idx})에서 N을 추출해 올바른 필터를 선택
                pattern = self.build_pattern(case_id, payload)                
                filter_map = filters_by_size.get(pattern.size)
                if filter_map is None:
                    key = f"size_{pattern.size}"
                    raise ValueError(filter_errors.get(key, f"{key} 필터가 없습니다."))

                cross_filter = filter_map[STANDARD_CROSS]
                x_filter = filter_map[STANDARD_X]
                cross_score, x_score, predicted = self.evaluate_pattern(
                    pattern, cross_filter, x_filter
                )
                passed = predicted == pattern.expected
                reason = None
                if not passed and predicted == UNDECIDED:
                    reason = "동점 규칙으로 UNDECIDED 판정"

                result = TestResult(
                    case_id=pattern.case_id,
                    size=pattern.size,
                    expected=pattern.expected,
                    predicted=predicted,
                    passed=passed,
                    reason=reason,
                    cross_score=cross_score,
                    x_score=x_score,
                )
            except Exception as error:
                result = TestResult(
                    case_id=case_id,
                    size=0,
                    expected=None,
                    predicted=None,
                    passed=False,
                    reason=str(error),
                )
            results.append(result)
            print(self.format_test_result(result))

        print("\n[3] 성능 분석")
        performance_items: List[PerformanceResult] = []
        for size in self.supported_sizes:
            filter_map = filters_by_size.get(size)
            if filter_map is None:
                cross_filter, x_filter = self.build_generated_filters(size)
            else:
                cross_filter = filter_map[STANDARD_CROSS]
                x_filter = filter_map[STANDARD_X]
            pattern = Pattern.from_rows(Filter.generate_cross(size).values)
            performance_items.extend(
                self.analyze_performance(pattern, cross_filter, x_filter)
            )
        print(self.format_performance_table(performance_items))

        print()
        print(self.summarize_results(results))

    def run(self) -> None:
        print("=== Mini NPU Simulator ===")
        print("\n[모드 선택]")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        print("3. 패턴 자동 생성")
        selection = input("선택: ").strip()

        if selection == "1":
            self.run_manual_mode()
            return
        if selection == "2":
            self.run_json_mode(str(Path(__file__).resolve().parent.parent / "data.json"))
            return
        if selection == "3":
            self.run_generated_mode()
            return
        print("지원하지 않는 선택입니다. 1, 2 또는 3을 입력하세요.")
