# Event-Data-Pipeline
이 프로젝트는 이벤트 생성 -> 저장 -> 분석 -> 시각화까지 이어지는 End-to-End 데이터 파이프라인 구축하는것을 목표로 합니다.

# 프로젝트 목표
- 실시간 이벤트 데이터 생성 및 수집
- 데이터 흐름을 고려한 구조 설계
- 분석 및 시각화

# 실행 방법
- 프로젝트 루트인 `liveklass`에서 `docker compose up`으로 앱과 DB를 함께 실행할 수 있습니다.
- 실행 시 FastAPI, Streamlit, PostgreSQL이 함께 기동되며, 백엔드가 초기 이벤트 데이터를 자동 생성하고 저장합니다.

# Docker 설정 안내
- `docker-compose.yml`에 포함된 PostgreSQL 계정, 비밀번호, 포트는 과제 제출 및 로컬 재현을 위한 예제 실행값입니다.
- 이 값들은 채점자가 별도 환경 설정 없이 바로 `docker compose up`으로 실행할 수 있도록 문서화된 기본값입니다.
- 실제 운영 환경에서는 동일한 방식을 사용하지 않고, `.env` 또는 별도 secret 관리 방식으로 분리하는 것이 적절합니다.
