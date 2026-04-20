# Event-Data-Pipeline

이 프로젝트는 이벤트 생성 -> 저장 -> 분석 -> 시각화까지 이어지는 End-to-End 데이터 파이프라인 구축을 목표로 합니다.

## 프로젝트 목표
- 실시간 이벤트 데이터 생성 및 저장
- PostgreSQL 기반 집계 분석
- 차트 이미지 파일 생성 자동화

## 프로젝트 구성
- `gen_event`: 이벤트 생성 API, 저장 로직, 테스트
- `visual`: SQL 집계 결과를 PNG로 저장하는 시각화 코드
- 루트 `docker-compose.yml`: 앱, DB, 시각화 컨테이너를 함께 실행하는 진입점

## 실행 방법

### 필요한 도구:
- Docker
- Docker Compose

### 실행 명령어:

```powershell
docker compose up --build -d
```

### 실행 후 동작:
- PostgreSQL, FastAPI, Streamlit이 함께 기동됩니다.
- 백엔드는 시작 시 초기 이벤트 50건을 자동 생성하고 PostgreSQL에 저장합니다.
- 프론트엔드는 화면만 띄우고, 실제 데이터 적재는 백엔드가 담당합니다.
- `visual` 컨테이너가 PostgreSQL 집계 결과를 읽어 차트 PNG 파일을 자동 생성합니다.

### 접속 주소:
- FastAPI: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Streamlit: [http://127.0.0.1:8501](http://127.0.0.1:8501)
- PostgreSQL(host): `127.0.0.1:55432`

### 생성 파일:
- `visual/output/product_performance.png`

    컨텐츠 별 구매 전환율 시각화
- `visual/output/referrer_conversion_rate.png`

    마케팅 성과 측정을 위한 유입 별 전환율 시각화
- `visual/output/hourly_event_distribution.png`

    시간대별 이벤트 발생 분포 시각화

세부 구현 설명과 이벤트 필드 정의는 [`gen_event/README.md`]에서 확인할 수 있습니다.

## PostgreSQL 포트 안내
Docker Compose 기준 PostgreSQL은 컨테이너 내부에서는 `5432`, 호스트에서는 `55432`를 사용합니다.

- 컨테이너 내부 서비스 간 통신: `5432`
- Windows/Linux 호스트에서 직접 접속할 때: `55432`

`docker compose up`만으로 실행할 때는 별도 포트 설정이 필요하지 않습니다. 아래 예시는 로컬에서 `python -m visual.generate_charts` 같은 스크립트를 직접 실행할 때만 사용합니다.

## Windows

```powershell
$env:POSTGRES_PORT='55432'
python -m visual.generate_charts
```

## Linux

```bash
export POSTGRES_PORT=55432
python -m visual.generate_charts
```

## 분석 쿼리 실행
아래 명령은 `docker compose up` 이후 PostgreSQL 컨테이너에서 바로 실행할 수 있는 집계 쿼리입니다.

### Windows

#### 1. 상품별 조회수 / 구매수 / 전환율

```powershell
docker exec gen-event-postgres psql -U commerce_admin -d commerce_events -c "
WITH latest_product_names AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        product_name
    FROM event_logs
    ORDER BY product_id, event_time DESC, id DESC
),
page_views AS (
    SELECT product_id, COUNT(*) AS page_view_count
    FROM event_logs
    WHERE event_type = 'page_view'
    GROUP BY product_id
),
purchases AS (
    SELECT product_id, COUNT(*) AS purchase_count
    FROM event_logs
    WHERE event_type = 'purchase'
    GROUP BY product_id
)
SELECT
    COALESCE(pv.product_id, p.product_id) AS product_id,
    lpn.product_name,
    COALESCE(pv.page_view_count, 0) AS page_view_count,
    COALESCE(p.purchase_count, 0) AS purchase_count,
    ROUND(
        COALESCE(p.purchase_count, 0)::numeric
        / NULLIF(COALESCE(pv.page_view_count, 0), 0) * 100,
        2
    ) AS conversion_rate_percent
FROM page_views pv
FULL OUTER JOIN purchases p
    ON pv.product_id = p.product_id
LEFT JOIN latest_product_names lpn
    ON lpn.product_id = COALESCE(pv.product_id, p.product_id)
ORDER BY conversion_rate_percent DESC NULLS LAST, page_view_count DESC;
"
```

#### 2. 유입 경로별 조회수 / 구매수 / 전환율

```powershell
docker exec gen-event-postgres psql -U commerce_admin -d commerce_events -c "
WITH purchase_source AS (
    SELECT DISTINCT ON (p.id)
        p.id AS purchase_id,
        pv.referrer
    FROM event_logs p
    JOIN event_logs pv
      ON p.user_id = pv.user_id
     AND p.session_id = pv.session_id
     AND p.product_id = pv.product_id
    WHERE p.event_type = 'purchase'
      AND pv.event_type = 'page_view'
      AND pv.referrer IS NOT NULL
      AND pv.event_time <= p.event_time
    ORDER BY p.id, pv.event_time DESC, pv.id DESC
),
page_views AS (
    SELECT referrer, COUNT(*) AS page_view_count
    FROM event_logs
    WHERE event_type = 'page_view'
      AND referrer IS NOT NULL
    GROUP BY referrer
),
purchases AS (
    SELECT referrer, COUNT(*) AS purchase_count
    FROM purchase_source
    GROUP BY referrer
)
SELECT
    pv.referrer,
    pv.page_view_count,
    COALESCE(p.purchase_count, 0) AS purchase_count,
    ROUND(
        COALESCE(p.purchase_count, 0)::numeric
        / NULLIF(pv.page_view_count, 0) * 100,
        2
    ) AS conversion_rate_percent
FROM page_views pv
LEFT JOIN purchases p
  ON pv.referrer = p.referrer
ORDER BY conversion_rate_percent DESC, pv.page_view_count DESC;
"
```

#### 3. 시간대별 이벤트 분포

```powershell
docker exec gen-event-postgres psql -U commerce_admin -d commerce_events -c "
SELECT
    EXTRACT(HOUR FROM event_time)::int AS event_hour,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE event_type = 'page_view') AS page_view_count,
    COUNT(*) FILTER (WHERE event_type = 'purchase') AS purchase_count
FROM event_logs
GROUP BY EXTRACT(HOUR FROM event_time)
ORDER BY event_hour;
"
```

### Linux

#### 1. 상품별 조회수 / 구매수 / 전환율

```bash
docker exec -i gen-event-postgres psql -U commerce_admin -d commerce_events <<'SQL'
WITH latest_product_names AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        product_name
    FROM event_logs
    ORDER BY product_id, event_time DESC, id DESC
),
page_views AS (
    SELECT product_id, COUNT(*) AS page_view_count
    FROM event_logs
    WHERE event_type = 'page_view'
    GROUP BY product_id
),
purchases AS (
    SELECT product_id, COUNT(*) AS purchase_count
    FROM event_logs
    WHERE event_type = 'purchase'
    GROUP BY product_id
)
SELECT
    COALESCE(pv.product_id, p.product_id) AS product_id,
    lpn.product_name,
    COALESCE(pv.page_view_count, 0) AS page_view_count,
    COALESCE(p.purchase_count, 0) AS purchase_count,
    ROUND(
        COALESCE(p.purchase_count, 0)::numeric
        / NULLIF(COALESCE(pv.page_view_count, 0), 0) * 100,
        2
    ) AS conversion_rate_percent
FROM page_views pv
FULL OUTER JOIN purchases p
    ON pv.product_id = p.product_id
LEFT JOIN latest_product_names lpn
    ON lpn.product_id = COALESCE(pv.product_id, p.product_id)
ORDER BY conversion_rate_percent DESC NULLS LAST, page_view_count DESC;
SQL
```

#### 2. 유입 경로별 조회수 / 구매수 / 전환율

```bash
docker exec -i gen-event-postgres psql -U commerce_admin -d commerce_events <<'SQL'
WITH purchase_source AS (
    SELECT DISTINCT ON (p.id)
        p.id AS purchase_id,
        pv.referrer
    FROM event_logs p
    JOIN event_logs pv
      ON p.user_id = pv.user_id
     AND p.session_id = pv.session_id
     AND p.product_id = pv.product_id
    WHERE p.event_type = 'purchase'
      AND pv.event_type = 'page_view'
      AND pv.referrer IS NOT NULL
      AND pv.event_time <= p.event_time
    ORDER BY p.id, pv.event_time DESC, pv.id DESC
),
page_views AS (
    SELECT referrer, COUNT(*) AS page_view_count
    FROM event_logs
    WHERE event_type = 'page_view'
      AND referrer IS NOT NULL
    GROUP BY referrer
),
purchases AS (
    SELECT referrer, COUNT(*) AS purchase_count
    FROM purchase_source
    GROUP BY referrer
)
SELECT
    pv.referrer,
    pv.page_view_count,
    COALESCE(p.purchase_count, 0) AS purchase_count,
    ROUND(
        COALESCE(p.purchase_count, 0)::numeric
        / NULLIF(pv.page_view_count, 0) * 100,
        2
    ) AS conversion_rate_percent
FROM page_views pv
LEFT JOIN purchases p
  ON pv.referrer = p.referrer
ORDER BY conversion_rate_percent DESC, pv.page_view_count DESC;
SQL
```

#### 3. 시간대별 이벤트 분포

```bash
docker exec -i gen-event-postgres psql -U commerce_admin -d commerce_events <<'SQL'
SELECT
    EXTRACT(HOUR FROM event_time)::int AS event_hour,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE event_type = 'page_view') AS page_view_count,
    COUNT(*) FILTER (WHERE event_type = 'purchase') AS purchase_count
FROM event_logs
GROUP BY EXTRACT(HOUR FROM event_time)
ORDER BY event_hour;
SQL
```

## Docker 설정 안내
- `docker-compose.yml`에 포함된 PostgreSQL 계정, 비밀번호, 포트는 과제 제출 및 로컬 재현을 위한 예제 실행값입니다.
- 이 값들은 채점자가 별도 환경 설정 없이 바로 `docker compose up`으로 실행할 수 있도록 문서화된 기본값입니다.
- 실제 운영 환경에서는 `.env` 또는 별도 secret 관리 방식으로 분리하는 것이 적절합니다.

## 스키마 설명
이 프로젝트는 `event_logs` 단일 테이블에 `page_view`와 `purchase` 이벤트를 함께 저장합니다. 공통 필드는 컬럼으로 고정하고, 이벤트별 값은 nullable 컬럼으로 분리해 JSON 통저장 없이 바로 SQL 집계가 가능하도록 설계했습니다.

주요 컬럼:
- `event_id`, `event_type`, `event_time`
- `user_id`, `session_id`, `page_url`
- `product_id`, `product_name`
- `referrer`, `device_type`
- `quantity`, `price`, `currency`, `payment_method`

## 구현하면서 고민한 점
- 제출 환경에서 재현성이 가장 중요하다고 판단해, 루트에서 `docker compose up`만으로 앱, DB, 시드 데이터, 시각화 파일이 모두 준비되도록 구성했습니다.
- 분석 결과가 실행 시점마다 흔들리지 않도록 백엔드 시작 시 초기 50건만 적재하고 이후에는 자동 누적하지 않도록 했습니다.
- 저장 구조는 구현 복잡도와 분석 편의성의 균형을 고려해 PostgreSQL 단일 테이블을 선택했습니다.
