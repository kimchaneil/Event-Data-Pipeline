# Event-Data-Pipeline
이 프로젝트는 이벤트 생성 -> 저장 -> 분석 -> 시각화까지 이어지는 End-to-End 데이터 파이프라인 구축하는것을 목표로 합니다.

# 프로젝트 목표
- 실시간 이벤트 데이터 생성 및 수집
- 데이터 흐름을 고려한 구조 설계
- 분석 및 시각화

# 프로젝트 구성
- `gen_event`: 이벤트 생성, 저장, 분석용 SQL 기준 로직
- `visual`: PostgreSQL 집계 결과를 차트 이미지로 저장하는 시각화 코드
- 루트 `docker-compose.yml`: 앱과 DB를 함께 실행하는 진입점

# 실행 방법
필요한 도구:
- Docker Desktop

실행 명령어:

```powershell
docker compose up --build -d
```

실행 후 동작:
- PostgreSQL, FastAPI, Streamlit이 함께 기동됩니다.
- 백엔드는 시작 시 초기 이벤트 50건을 자동 생성하고 PostgreSQL에 저장합니다.
- 프론트엔드는 화면만 띄우고, 실제 데이터 적재는 백엔드가 담당합니다.
- 과제 환경에서는 초기 이벤트를 적재하여, 별도의 동작 없이 데이터를 적재합니다.
- `visual` 컨테이너가 PostgreSQL 집계 결과를 읽어 차트 PNG 파일을 자동 생성합니다.

접속 주소:
- FastAPI: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Streamlit: [http://127.0.0.1:8501](http://127.0.0.1:8501)
- PostgreSQL(host): `127.0.0.1:55432`

생성 파일:
- `visual/output/product_performance.png`

    컨텐츠 별 구매 전환율 시각화
- `visual/output/referrer_conversion_rate.png`

    마케팅 성과 측정을 위한 유입 별 전환율 시각화
- `visual/output/hourly_event_distribution.png`

    시간대 별 이벤트 발생 분포 시각화

# PostgreSQL 포트 안내
Docker Compose 기준 PostgreSQL은 컨테이너 내부에서는 `5432`를 사용하고, 호스트에서는 `55432`로 노출됩니다.

즉:
- 컨테이너 내부 서비스 간 통신: `5432`
- Windows/Linux 호스트에서 직접 접속할 때: `55432`

## Windows

`docker compose up`만으로 실행할 때는 아래 설정이 필요하지 않습니다. 

아래 예시는 로컬에서 `python -m visual.generate_charts` 같은 스크립트를 직접 실행할 때만 사용합니다.

현재 코드 기본값은 이미 `55432`를 사용하므로, 일반적인 로컬 실행에서는 별도 설정 없이 동작합니다.

PowerShell에서 다른 포트로 바꾸고 싶을 때만 아래처럼 설정합니다.

```powershell
$env:POSTGRES_PORT='55432'
```

예:

```powershell
$env:POSTGRES_PORT='55432'
python -m visual.generate_charts
```

## Linux

`docker compose up`만으로 실행할 때는 아래 설정이 필요하지 않습니다. 아래 예시는 로컬에서 `python -m visual.generate_charts` 같은 스크립트를 직접 실행할 때만 사용합니다.

bash/zsh에서도 기본적으로 추가 설정 없이 동작합니다.

다른 포트로 바꾸고 싶을 때만 아래처럼 설정합니다.

```bash
export POSTGRES_PORT=55432
```

예:

```bash
export POSTGRES_PORT=55432
python -m visual.generate_charts
```

# Docker 설정 안내
- `docker-compose.yml`에 포함된 PostgreSQL 계정, 비밀번호, 포트는 과제 제출 및 로컬 재현을 위한 예제 실행값입니다.
- 이 값들은 채점자가 별도 환경 설정 없이 바로 `docker compose up`으로 실행할 수 있도록 문서화된 기본값입니다.
- 실제 운영 환경에서는 동일한 방식을 사용하지 않고, `.env` 또는 별도 secret 관리 방식으로 분리하는 것이 적절합니다.

# 스키마 설명
이 프로젝트는 `event_logs` 단일 테이블에 `page_view`와 `purchase` 이벤트를 함께 저장합니다. 공통 필드는 컬럼으로 고정하고, 이벤트별로 필요한 값만 nullable 컬럼에 저장하는 방식으로 설계했습니다. 이렇게 하면 JSON 통저장 없이도 조회, 구매, 전환율, 시간대 분석 같은 집계를 SQL로 바로 수행할 수 있습니다.

주요 컬럼:
- `event_id`, `event_type`, `event_time`
- `user_id`, `session_id`, `page_url`
- `product_id`, `product_name`
- `referrer`, `device_type`
- `quantity`, `price`, `currency`, `payment_method`

# 구현하면서 고민한 점
- 실행 재현성을 우선했습니다. 과제 제출 환경에서는 채점자가 별도 설정 없이 실행할 수 있어야 하므로, 루트에서 `docker compose up`만으로 앱과 DB가 함께 올라오도록 구성했습니다.
- 이벤트 적재 방식은 반복 생성보다 초기 1회 적재를 선택했습니다. 분석 쿼리 결과가 실행 시점마다 바뀌면 검증이 어려워지기 때문에, 백엔드 시작 시 50건만 seed 하고 이후에는 데이터가 고정되도록 했습니다.
- 이벤트 저장은 PostgreSQL 단일 테이블 구조를 유지했습니다. `page_view`와 `purchase`를 별도 테이블로 나눌 수도 있었지만, 현재 과제 범위에서는 한 테이블이 구현 복잡도를 낮추면서도 상품별 전환율, 유입 경로 성과, 시간대 분포 분석을 수행하기에 충분하다고 판단했습니다.
- 시각화는 화면 출력보다 파일 저장을 선택했습니다. 요구사항이 차트 생성 후 이미지 파일 저장이므로, `matplotlib`를 사용해 PNG를 바로 남기도록 했고 `docker compose up`만으로 자동 생성되게 별도 `visual` 컨테이너를 추가했습니다.
