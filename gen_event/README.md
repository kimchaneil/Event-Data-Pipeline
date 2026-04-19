# Gen Event

이 프로젝트는 커머스 서비스에서 사용할 수 있는 이벤트 생성 기능만 따로 분리해 관리하는 하위 프로젝트입니다.

현재 구현 범위는 이벤트 생성 페이지입니다. FastAPI 백엔드에서 페이지 조회 이벤트와 구매 이벤트를 랜덤하게 생성하고, Streamlit 프론트엔드에서 이를 호출합니다.

## 현재 기능

- FastAPI 기반 이벤트 생성 API
- Streamlit 기반 이벤트 생성 UI
- `page_view` 이벤트 생성
- `purchase` 이벤트 생성
- 랜덤 이벤트 배치 생성
- 생성된 이벤트를 JSONL 파일로 저장

## 이벤트 시나리오

커머스 회사 기준으로 아래 두 이벤트를 우선 구현합니다.

1. `page_view`
상품 상세 페이지를 조회한 상황을 표현합니다.

2. `purchase`
상품을 실제로 결제한 상황을 표현합니다.

## 이벤트 필드 구성

### 공통 필드

- `event_id`: 이벤트 고유 ID
- `event_type`: 이벤트 종류
- `event_time`: 이벤트 발생 시각
- `user_id`: 사용자 ID
- `session_id`: 세션 ID
- `page_url`: 페이지 URL

### page_view 추가 필드

- `product_id`: 상품 ID
- `product_name`: 상품명
- `referrer`: 유입 경로
- `device_type`: 디바이스 유형

### purchase 추가 필드

- `product_id`: 상품 ID
- `product_name`: 상품명
- `quantity`: 구매 수량
- `price`: 상품 단가
- `currency`: 통화
- `payment_method`: 결제 수단

## 디렉토리 구조

```text
gen_event/
├── config/
├── producer/
├── visualization/
├── scripts/
├── tests/
├── .env.example
├── README.md
└── requirements.txt
```

## 실행 방법

### 1. 가상환경 생성

```powershell
cd "C:\Users\diabl\Desktop\김찬일(ChanIl Kim) f313db8811114d9d902ca7fb23904849\liveklass"
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. 패키지 설치

```powershell
pip install -r gen_event/requirements.txt
```

### 3. 환경 변수 파일 준비

```powershell
Copy-Item gen_event/.env.example gen_event/.env
```

### 4. FastAPI 실행

```powershell
python -m gen_event.scripts.run_api
```

백엔드는 기본적으로 [http://127.0.0.1:8000](http://127.0.0.1:8000) 에서 실행됩니다.

### 5. Streamlit 실행

새 터미널에서 아래 명령을 실행합니다.

```powershell
.venv\Scripts\Activate.ps1
python -m gen_event.scripts.run_streamlit
```

프론트엔드는 기본적으로 [http://127.0.0.1:8501](http://127.0.0.1:8501) 에서 실행됩니다.

### 6. 화면 사용

- `Page View 1건 생성`
- `Purchase 1건 생성`
- `랜덤 이벤트 생성`

## 랜덤 생성 규칙

- `page_view`는 단건 생성 가능
- `purchase`는 단건 생성 가능
- 랜덤 배치 생성은 기본 10건
- 배치 생성 시 `page_view`가 `purchase`보다 더 자주 나오도록 구성

## 저장 방식

생성된 이벤트는 `gen_event/data/events.jsonl` 파일에 한 줄당 하나의 JSON 형태로 저장됩니다.

## 테스트 실행

```powershell
python -m unittest gen_event.tests.test_event_service
```

# 설계 의도
### 이벤트 설계 의도

퓨쳐스콜레(라이브클래스)와 같은 지식 커머스 서비스의 실제 사용자 행동 흐름을 반영하여 이벤트를 설계하였습니다.

지식 커머스는 일반 상품과 달리 “강의/콘텐츠를 탐색 → 비교 → 구매”로 이어지는 의사결정 과정이 긴 서비스이기 때문에, 단순 구매 데이터보다 사용자의 탐색 과정을 함께 수집하는 것이 중요합니다.

이에 따라 사용자 행동을 가장 기본적인 흐름으로 단순화하여 다음 두 가지 핵심 이벤트를 정의하였습니다.

### **page_view** 설계 의도
지식 커머스에서는 사용자가 강의를 바로 구매하기보다는 **강의 커리큘럼, 강사 정보, 가격 비교, 후기탐색**의 과정을 거치기 때문에, 조회 데이터는 구매 이전의 핵심 신호가 됩니다.

따라서, 아래와 같은 목적을 가지고 설계하였습니다.

- 어떤 강의가 많이 조회되는지 (인기 컨텐츠)
- 어떤 유입 경로가 효과적인지 (마케팅 성과 측정)
- 디바이스에 따른 사용자 행동 분석 차이 비교
- 조회 대비 구매율 계산을 위한 데이터 확보

### **purchase** 설계 의도
purchase는 고객이 실제 강의를 구매한 행동을 의미합니다.

서비스의 최종 목표인 매출 발생 지점이며, 모든 사용자 행동 분석의 기준점이 되는 이벤트입니다.

다음과 같은 분석을 가능하기 위해 설계하였습니다.

- 강의별 매출 및 판매량 분석
- 가격 및 수량 기반 수익 구조 분석
- 결제 수단 선호도 분석
- 특정 강의의 조회 대비 구매 전환율 분석

특히 **page_view**와 같이 분석하였을 때,

**특정 유입 경로를 통한 결제**,**조회는 많지만 구매가 낮은 강의**와 같은 비지니스 인사이트 도출을 가능하게 하도록 설계하였습니다.

### 랜덤 생성 규칙 설계 이유
랜덤 이벤트 생성 시 page_view가 purchase보다 많이 발생되도록 설계한 이유는 실제 서비스에서도 조회 대비 구매 비율이 낮은 것이 일반적이기 때문입니다.