"""Mini NPU Simulator entry point."""

# 이 파일은 프로그램을 시작할 때 가장 먼저 실행되는 진입점이다.
# 실제 기능 로직을 여기저기 직접 작성하지 않고 MiniNPUSimulator 클래스에 위임해,
# main.py는 "프로그램 시작" 책임만 갖도록 단순하게 유지한다.

# 실행 제어 클래스인 MiniNPUSimulator를 직접 가져와 실행 책임을 위임한다.
from mini_npu.simulator import MiniNPUSimulator


def main() -> None:
    simulator = MiniNPUSimulator()
    simulator.run()


if __name__ == "__main__":
    main()
