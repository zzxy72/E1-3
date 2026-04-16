# 요구사항 체크리스트 점검표

이 문서는 [요구사항/readme.md](/home/keytest/openclaw/E1-3/요구사항/readme.md)를 기준으로 현재 구현 상태를 점검한 결과다.  
체크 기준은 "기능 존재 여부", "실행 확인 여부", "문서 반영 여부" 세 가지다.

## 1. 데이터 구조

- [x] `n x n` 2차원 패턴/필터 저장 가능
- [x] 특정 위치 값을 `matrix[row][col]` 형태로 읽고 사용
- [x] 3x3, 5x5, 13x13, 25x25 처리 가능

근거:

- 구현: [mini_npu/models.py](/home/keytest/openclaw/E1-3/mini_npu/models.py)
- 검증: [mini_npu/validator.py](/home/keytest/openclaw/E1-3/mini_npu/validator.py)

## 2. 모드 1 입력 처리

- [x] 3x3 필터 2개(A, B)를 한 줄씩 입력받음
- [x] 3x3 패턴을 동일 방식으로 입력받음
- [x] 행/열 수 불일치 시 재입력 유도
- [x] 숫자 파싱 실패 시 재입력 유도
- [x] 필터 입력 후 저장 확인 메시지 출력
- [x] 두 필터 점수, 평균 연산 시간, 판정 결과(A/B/판정 불가) 출력

근거:

- 구현: [mini_npu/console.py](/home/keytest/openclaw/E1-3/mini_npu/console.py)
- 실행 확인: `printf '1\n...' | python3 main.py`

## 3. 모드 2 JSON 로드 및 스키마 검증

- [x] `filters.size_5`, `filters.size_13`, `filters.size_25` 구조 읽기
- [x] `patterns.size_{N}_{idx}` 키 규칙 읽기
- [x] 패턴 키에서 `N` 추출 후 대응 필터 선택
- [x] 필터와 패턴 크기 일치 검증
- [x] 크기 불일치 시 케이스 단위 FAIL 처리
- [x] 잘못된 필터 정의도 전체 중단 없이 관련 케이스 FAIL 처리

근거:

- 구현: [mini_npu/json_loader.py](/home/keytest/openclaw/E1-3/mini_npu/json_loader.py), [main.py](/home/keytest/openclaw/E1-3/main.py)
- 실행 확인:
  - 정상 데이터: `printf '2\n' | python3 main.py`
  - 오류 데이터: 임시 JSON로 크기 오류 및 필터 오류 테스트 수행

## 4. 라벨 정규화

- [x] 내부 표준 라벨 `Cross`, `X` 사용
- [x] `expected` 값 `+ -> Cross`, `x -> X` 처리
- [x] 필터 키 `cross -> Cross`, `x -> X` 처리
- [x] 콘솔 출력 및 PASS/FAIL 비교를 표준 라벨 기준으로 수행

근거:

- 구현: [mini_npu/normalizer.py](/home/keytest/openclaw/E1-3/mini_npu/normalizer.py)

## 5. MAC 연산

- [x] 위치별 곱셈 후 누적합 계산
- [x] 외부 라이브러리 미사용
- [x] 반복문 기반 직접 구현
- [x] 점수 `float` 반환

근거:

- 구현: [mini_npu/mac.py](/home/keytest/openclaw/E1-3/mini_npu/mac.py)

## 6. 점수 비교 정책

- [x] epsilon 기반 비교 정책 적용
- [x] `abs(score_a - score_b) < 1e-9` 동점 처리
- [x] 사용자 입력 모드에서 `A/B/판정 불가` 출력
- [x] JSON 모드에서 `Cross/X/UNDECIDED`와 `PASS/FAIL` 출력
- [x] 기본 `data.json`에 `UNDECIDED FAIL`과 일반 오답 `FAIL` 검증 케이스 포함

근거:

- 구현: [mini_npu/judge.py](/home/keytest/openclaw/E1-3/mini_npu/judge.py), [mini_npu/console.py](/home/keytest/openclaw/E1-3/mini_npu/console.py), [mini_npu/report.py](/home/keytest/openclaw/E1-3/mini_npu/report.py)

## 7. 성능 분석

- [x] 크기별 MAC 연산 시간 ms 단위 측정
- [x] 10회 반복 측정 후 평균 출력
- [x] I/O 제외 함수 호출 구간 중심 측정
- [x] 표에 크기, 평균 시간, 연산 횟수(N^2) 포함
- [x] 3x3, 5x5, 13x13, 25x25 출력

근거:

- 구현: [mini_npu/performance.py](/home/keytest/openclaw/E1-3/mini_npu/performance.py), [main.py](/home/keytest/openclaw/E1-3/main.py)

## 8. 결과 리포트

- [x] data.json 모드에서 총 테스트 수 출력
- [x] data.json 모드에서 통과 수 출력
- [x] data.json 모드에서 실패 수 출력
- [x] 실패 케이스가 있으면 식별자와 실패 사유 출력
- [x] README에 실패 원인 분석 포함
- [x] README에 시간 복잡도 분석 포함
- [x] 실패가 0개일 때 왜 0 FAIL인지 설명 포함

근거:

- 구현: [mini_npu/report.py](/home/keytest/openclaw/E1-3/mini_npu/report.py)
- 문서: [README.md](/home/keytest/openclaw/E1-3/README.md)

## 9. 실행 흐름

- [x] 모드 선택 후 사용자 입력 또는 JSON 분석으로 분기
- [x] 사용자 입력 모드 흐름이 요구사항 순서와 일치
- [x] JSON 분석 모드 흐름이 요구사항 순서와 일치
- [x] 패턴 자동 생성 모드에서 생성된 패턴을 즉시 판정/성능 분석에 재사용

근거:

- 구현: [main.py](/home/keytest/openclaw/E1-3/main.py), [mini_npu/console.py](/home/keytest/openclaw/E1-3/mini_npu/console.py)

## 10. 보너스 과제

- [x] 2차원 배열을 1차원 배열로 변환하는 최적화 구현
- [x] 최적화 전/후 성능 비교 표 출력
- [x] 크기 N 입력 기반 Cross/X 패턴 생성기 구현
- [x] 생성기 결과를 모드 1 예시와 성능 분석에 재활용

근거:

- 구현: [mini_npu/mac.py](/home/keytest/openclaw/E1-3/mini_npu/mac.py), [mini_npu/generator.py](/home/keytest/openclaw/E1-3/mini_npu/generator.py), [mini_npu/performance.py](/home/keytest/openclaw/E1-3/mini_npu/performance.py)

## 11. 최종 점검 결론

- 현재 구현은 요구사항의 필수 체크리스트를 충족한다.
- 구현 중 보완한 핵심 항목은 아래와 같다.
  - 사용자 입력 모드의 판정 표기를 `Cross/X`에서 `A/B`로 수정
  - 필터 입력 후 저장 확인 메시지 추가
  - 필터 스키마 오류가 있어도 프로그램이 전체 종료되지 않도록 수정
  - 보너스 패턴 생성기 예시 출력을 제거하고 실제 사용 가능한 자동 생성 모드로 대체
  - 문서와 실제 콘솔 출력 형식을 다시 일치시킴
- 향후 추가 개선 후보는 자동 테스트 스크립트 추가와 측정값 기록 자동화다.
