"""Performance measurement helpers."""

from time import perf_counter

from mini_npu.mac import compute_mac, compute_mac_flat, flatten_matrix
from mini_npu.models import FilterSet, Matrix, PerformanceResult


def measure_average_ms(func, repeat: int = 10) -> float:
    start = perf_counter()
    for _ in range(repeat):
        func()
    end = perf_counter()
    return (end - start) * 1000.0 / repeat


def analyze_mac_performance(
    pattern: Matrix, filters: FilterSet, repeat: int = 10
) -> PerformanceResult:
    avg_ms = measure_average_ms(
        lambda: (compute_mac(pattern, filters.cross), compute_mac(pattern, filters.x)),
        repeat=repeat,
    )
    size = filters.size
    return PerformanceResult(
        size=size,
        avg_ms=avg_ms,
        operation_count=size * size,
        repeat=repeat,
        mode_name="2D",
    )


def analyze_flat_performance(
    pattern: Matrix, filters: FilterSet, repeat: int = 10
) -> PerformanceResult:
    flat_pattern = flatten_matrix(pattern)
    flat_cross = flatten_matrix(filters.cross)
    flat_x = flatten_matrix(filters.x)
    avg_ms = measure_average_ms(
        lambda: (
            compute_mac_flat(flat_pattern, flat_cross),
            compute_mac_flat(flat_pattern, flat_x),
        ),
        repeat=repeat,
    )
    size = filters.size
    return PerformanceResult(
        size=size,
        avg_ms=avg_ms,
        operation_count=size * size,
        repeat=repeat,
        mode_name="1D(flat)",
    )

