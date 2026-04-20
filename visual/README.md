# Visual

이 디렉토리는 PostgreSQL에 저장된 이벤트 집계 결과를 차트 이미지로 저장하는 시각화 기능을 관리합니다.

## 역할

- SQL 집계 결과 조회
- 상품/유입 경로/시간대 기준 차트 생성
- PNG 이미지 파일 저장

## 디렉토리 구조

```text
visual/
├── output/
├── README.md
├── generate_charts.py
├── sql_queries.py
└── __init__.py
```

## 구성 파일

### `generate_charts.py`

시각화 실행 스크립트입니다.

하는 일:
- PostgreSQL 연결 대기
- 초기 이벤트 적재 완료 대기
- SQL 집계 쿼리 실행
- `matplotlib`로 차트 생성
- `visual/output` 아래에 PNG 파일 저장

### `sql_queries.py`

시각화에 사용하는 SQL 집계 쿼리를 모아둔 파일입니다.

포함된 분석 기준:
- 상품별 조회수 / 구매수 / 전환율
- 유입 경로별 조회수 / 구매수 / 전환율
- 시간대별 이벤트 분포

### `output/`

생성된 차트 이미지가 저장되는 디렉토리입니다.

기본 생성 파일:
- `product_performance.png`
- `referrer_conversion_rate.png`
- `hourly_event_distribution.png`

## 실행 방법

현재 시각화는 별도 수동 실행이 아니라 루트에서 Docker 전체 실행 시 자동으로 수행됩니다.

```powershell
docker compose up --build -d
```

실행 후 `visual` 컨테이너가 한 번 실행되고 종료되며, 차트 이미지를 파일로 남깁니다.

## 출력 파일

- `visual/output/product_performance.png`
- `visual/output/referrer_conversion_rate.png`
- `visual/output/hourly_event_distribution.png`

## 출력 차트 설명

### 1. Product Performance

상품별 `page_view`와 `purchase` 건수를 막대 차트로 비교합니다.

목적:
- 많이 조회된 상품 확인
- 실제 구매가 많이 발생한 상품 확인
- 조회 대비 구매 성과 비교

### 2. Referrer Conversion Rate

유입 경로별 구매 전환율을 막대 차트로 표현합니다.

목적:
- 어떤 유입 경로가 더 높은 전환율을 보이는지 확인
- 조회량과 별개로 효율이 높은 채널 파악

### 3. Hourly Event Distribution

시간대별 `page_view`와 `purchase` 분포를 선 그래프로 표현합니다.

목적:
- 이벤트가 집중되는 시간대 확인
- 조회와 구매 패턴 비교

## 참고 사항

- 시각화는 화면 출력이 아니라 파일 저장 방식입니다.
- 출력 이미지는 실행 시 같은 파일명으로 갱신됩니다.
- `docker compose up` 이후 `gen-event-visual` 컨테이너가 `Exited (0)` 상태면 정상적으로 생성이 끝난 것입니다.
