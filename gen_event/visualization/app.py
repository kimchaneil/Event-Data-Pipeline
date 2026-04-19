"""Streamlit frontend for commerce event generation."""

from __future__ import annotations

import json
from urllib import error, request

import streamlit as st

from gen_event.config.settings import get_settings


def post_json(url: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload or {}).encode("utf-8")
    req = request.Request(
        url=url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    settings = get_settings()
    api_base_url = str(settings["api_base_url"]).rstrip("/")

    st.set_page_config(page_title="Commerce Event Generator", page_icon="🛒", layout="centered")
    st.title("Commerce Event Generator")
    st.write("커머스 데이터 파이프라인용 샘플 이벤트를 생성합니다.")

    st.subheader("구현 구조")
    st.write("- 백엔드: FastAPI")
    st.write("- 프론트엔드: Streamlit")
    st.write("- 저장소: PostgreSQL")
    st.write("- 자동 적재: 백엔드 시작 시 초기 이벤트 50건 생성 및 저장")

    batch_size = st.number_input(
        "수동 생성 건수",
        min_value=1,
        max_value=500,
        value=int(settings["random_batch_size"]),
        step=1,
    )

    col1, col2, col3 = st.columns(3)

    response_data: dict | None = None
    error_message: str | None = None

    try:
        with col1:
            if st.button("Page View 1건 생성", use_container_width=True):
                response_data = post_json(f"{api_base_url}/events/page-view")

        with col2:
            if st.button("Purchase 1건 생성", use_container_width=True):
                response_data = post_json(f"{api_base_url}/events/purchase")

        with col3:
            if st.button("랜덤 이벤트 생성", use_container_width=True):
                response_data = post_json(f"{api_base_url}/events/random", {"count": int(batch_size)})
    except error.URLError:
        error_message = "FastAPI 서버에 연결할 수 없습니다. 백엔드 컨테이너 상태를 먼저 확인하세요."

    if error_message:
        st.error(error_message)

    if response_data:
        st.success(response_data.get("message", "이벤트 생성 완료"))
        st.json(response_data)


if __name__ == "__main__":
    main()
