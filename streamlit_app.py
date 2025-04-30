import streamlit as st
import pandas as pd
from PIL import Image
import base64
import time
import re
import json

# 페이지 설정
st.set_page_config(
    page_title="콘텐츠 마스터",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS 스타일 추가
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton button {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        color: black;
        width: 100%;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;  /* 입력창 배경색 흰색으로 변경 */
        color: #000000;  /* 입력 텍스트 색상을 검정색으로 설정 */
        border: 1px solid #ddd;
        max-width: 100%;
    }
    .stSelectbox > div > div > div {
        background-color: #ffffff;  /* 선택 상자 배경색 흰색으로 변경 */
    }
    .custom-box {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .header {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        padding-top: 25px;  /* 패딩 더 증가 */
        padding-bottom: 25px;  /* 패딩 더 증가 */
        background-color: #111;
        color: white;
        border-radius: 5px;
        line-height: 2.0;  /* 줄 간격 추가 */
        min-height: 80px;  /* 최소 높이 설정 */
        display: flex;
        align-items: center;
        justify-content: center; /* 중앙 정렬 */
    }
    .subheader {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;  /* 모든 subheader를 가운데 정렬 */
    }
    .input-container {
        max-width: 600px;
        margin: 0 auto;
    }
    /* 텍스트 영역 스타일 개선 */
    .stTextArea textarea {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# 클립보드 복사를 위한 JS 생성 함수 (텍스트를 직접 넘겨 안전하게 복사)

def get_copy_button_js(text_to_copy: str) -> str:
    escaped = json.dumps(text_to_copy)  # JS 의 문자열 literal 로 안전하게 인코딩
    return f"""
    <script>
        function copyGeneratedContent() {{
            navigator.clipboard.writeText({escaped}).then(() => {{
                const note = document.createElement('div');
                note.textContent = '클립보드에 복사되었습니다!';
                note.style.position = 'fixed';
                note.style.bottom = '20px';
                note.style.left = '50%';
                note.style.transform = 'translateX(-50%)';
                note.style.backgroundColor = '#4CAF50';
                note.style.color = 'white';
                note.style.padding = '10px 20px';
                note.style.borderRadius = '5px';
                note.style.zIndex = '1000';
                document.body.appendChild(note);
                setTimeout(() => document.body.removeChild(note), 3000);
            }}).catch(err => alert('클립보드 복사에 실패했습니다.'));
        }}
    </script>
    <button onclick="copyGeneratedContent()" style="width: 100%; padding: 0.5rem; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">복사하기</button>
    """

# ------------------------------------------
# 테스트용 모의 함수(그대로 유지)
# ------------------------------------------

def get_youtube_recommendations(keyword):
    mock_data = [
        {
            "title": f"<자세히보기>(토큰) {keyword}에 대한 분석",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=Video+1",
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        },
        {
            "title": f"<자세히보기> {keyword} 심층탐구",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=Video+2",
            "link": "https://www.youtube.com/watch?v=xvFZjo5PgG0"
        },
        {
            "title": f"<자세히보기> {keyword} 완벽 가이드",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=Video+3",
            "link": "https://www.youtube.com/watch?v=jNQXAC9IVRw"
        }
    ]
    time.sleep(1)
    return mock_data

def get_video_transcript(video_link):
    return f"이것은 선택된 영상의 스크립트입니다. 실제 구현에서는 YouTube API를 통해 실제 트랜스크립트를 가져와야 합니다.\n선택된 영상 링크: {video_link}"

def regenerate_content(video_transcript, target_audience, tone_style, goal, word_count):
    return f"""재구성된 콘텐츠:\n\n타겟층: {target_audience}\n톤/스타일: {tone_style}\n목표: {goal}\n글자수: {word_count}\n\n원본 트랜스크립트를 기반으로 한 새로운 콘텐츠입니다. 이 부분은 실제 구현에서 AI 모델을 통해 생성된 콘텐츠로 대체될 것입니다."""

# ------------------------------------------
# 세션 상태 초기화
# ------------------------------------------

state_defaults = {
    "step": 1,
    "recommended_videos": [],
    "selected_video": None,
    "generated_content": "",
    "target_audience": "",
    "tone_style": "일반",
    "goal": "정보전달",
    "word_count": "500자내외"
}
for k, v in state_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------------------------------
# 네비게이션 함수
# ------------------------------------------

def go_to_next_step():
    st.session_state.step += 1
    st.rerun()

def go_to_previous_step():
    st.session_state.step -= 1
    st.rerun()

# ------------------------------------------
# STEP 1: 콘텐츠 마스터
# ------------------------------------------

def show_step_1():
    st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)

    st.markdown("<div class='subheader'>주제입력</div>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            keyword = st.text_input("", key="keyword_input", label_visibility="collapsed")

    with st.container():
        col1, col2, col3 = st.columns([3, 1, 3])
        with col2:
            search_button = st.button("콘텐츠 검색", use_container_width=True)

    if search_button and keyword:
        st.session_state.recommended_videos = get_youtube_recommendations(keyword)
        st.rerun()

    if st.session_state.recommended_videos:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown("<div class='subheader' style='text-align: center;'>인기 콘텐츠 TOP3</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; margin-bottom: 15px;'>원하시는 콘텐츠를 선택해주세요.</div>", unsafe_allow_html=True)
                for i, video in enumerate(st.session_state.recommended_videos):
                    st.markdown(f"""
                    <div style='border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin-bottom: 10px; background-color: #f8f9fa;'>
                        <div style='font-weight: bold;'>{i+1}.제목: {video['title']}</div>
                        <div style='margin: 5px 0;'><a href='{video['link']}' target='_blank'>영상 보기</a></div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("선택", key=f"select_btn_{i}", use_container_width=True):
                        st.session_state.selected_video = video
                        st.rerun()

    if st.session_state.selected_video:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown("<div class='subheader' style='text-align: center; margin-top: 20px;'>선택 확인</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='text-align: center; margin: 15px 0; padding: 15px; background-color: #f0f7ff; border-radius: 5px; border: 1px solid #c5d5e5;'>
                    선택한 콘텐츠로 진행하시겠습니까?<br><br>
                    <strong>선택된 영상:</strong> {st.session_state.selected_video['title']}
                </div>
                """, unsafe_allow_html=True)
                yes_col, no_col = st.columns(2)
                with yes_col:
                    if st.button("YES", use_container_width=True):
                        go_to_next_step()
                with no_col:
                    if st.button("다시 선택", use_container_width=True):
                        st.session_state.selected_video = None
                        st.rerun()

# ------------------------------------------
# STEP 2: 콘텐츠 만들기
# ------------------------------------------

def show_step_2():
    st.markdown("<div class='header'>콘텐츠 만들기</div>", unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("<div style='text-align: center;'>원하시는 스타일을 선택해주세요.</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; margin: 20px 0;'><strong>선택된 영상:</strong> {st.session_state.selected_video['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'><a href='{st.session_state.selected_video['link']}' target='_blank'>영상 링크</a></div>", unsafe_allow_html=True)

            # 타겟층 입력
            st.markdown("<div class='subheader' style='margin-top: 20px;'>타겟층</div>", unsafe_allow_html=True)
            st.session_state.target_audience = st.text_input("", key="target_audience_input", value=st.session_state.target_audience, label_visibility="collapsed")

            # 톤/스타일 라디오
            st.markdown("<div class='subheader'>톤/스타일</div>", unsafe_allow_html=True)
            tone_options = ["인풋말씀", "정중함", "감성"]
            st.session_state.tone_style = st.radio(
                label="tone_style_radio",
                options=tone_options,
                index=tone_options.index(st.session_state.tone_style),
                horizontal=True,
                label_visibility="collapsed"
            )

            # 목표 라디오
            st.markdown("<div class='subheader'>목표</div>", unsafe_allow_html=True)
            goal_options = ["정보전달", "설득력", "구매유도"]
            st.session_state.goal = st.radio(
                label="goal_radio",
                options=goal_options,
                index=goal_options.index(st.session_state.goal),
                horizontal=True,
                label_visibility="collapsed"
            )

            # 글자수 라디오
            st.markdown("<div class='subheader'>글자수</div>", unsafe_allow_html=True)
            count_options = ["500자내외", "1000자내외", "1500자내외"]
            st.session_state.word_count = st.radio(
                label="count_radio",
                options=count_options,
                index=count_options.index(st.session_state.word_count),
                horizontal=True,
                label_visibility="collapsed"
            )

            # 네비게이션 버튼
            back_col, generate_col = st.columns(2)
            with back_col:
                if st.button("이전으로", use_container_width=True):
                    go_to_previous_step()
            with generate_col:
                if st.button("콘텐츠만들기", use_container_width=True):
                    video_transcript = get_video_transcript(st.session_state.selected_video['link'])
                    st.session_state.generated_content = regenerate_content(
                        video_transcript,
                        st.session_state.target_audience,
                        st.session_state.tone_style,
                        st.session_state.goal,
                        st.session_state.word_count,
                    )
                    go_to_next_step()

# ------------------------------------------
# STEP 3: 콘텐츠 생성완료
# ------------------------------------------

def show_step_3():
    st.markdown("<div class='header'>콘텐츠 생성완료</div>", unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>선택된 옵션</h4>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>영상:</strong> {st.session_state.selected_video['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>타겟층:</strong> {st.session_state.target_audience}</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>톤/스타일:</strong> {st.session_state.tone_style}</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>목표:</strong> {st.session_state.goal}</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>글자수:</strong> {st.session_state.word_count}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<h4 style='text-align: center; margin: 20px 0;'>생성된 콘텐츠</h4>", unsafe_allow_html=True)
            st.text_area("", value=st.session_state.generated_content, height=300, label_visibility="collapsed")

            # 복사하기 버튼 + JS 삽입
            st.markdown(get_copy_button_js(st.session_state.generated_content), unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
            back_col, dummy = st.columns([1, 1])
            with back_col:
                if st.button("다시 설정하기", use_container_width=True):
                    go_to_previous_step()
            st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# 메인 라우팅
# ------------------------------------------

if st.session_state.step == 1:
    show_step_1()
elif st.session_state.step == 2:
    show_step_2()
else:
    show_step_3()
