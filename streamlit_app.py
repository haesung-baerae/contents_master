import streamlit as st
import time

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
        background-color: #222;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        border: 1px solid #444;
    }
    .stSelectbox > div > div > div {
        background-color: #f0f0f0;
    }
    .header {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        padding: 10px 0;
        background-color: #111;
        color: white;
        border-radius: 5px;
    }
    .subheader {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
for var, val in {
    "step": 1,
    "recommended_videos": [],
    "selected_video": None,
    "generated_content": "",
    "target_audience": "",
    "tone_style": "일반",
    "goal": "정보전달",
    "word_count": "500자내외",
}.items():
    if var not in st.session_state:
        st.session_state[var] = val

# 모의 함수들
def get_youtube_recommendations(keyword):
    mock_data = [
        {
            "title": f"{keyword}에 대한 분석",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=Video+1",
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        },
        {
            "title": f"{keyword} 심층탐구",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=Video+2",
            "link": "https://www.youtube.com/watch?v=xvFZjo5PgG0"
        },
        {
            "title": f"{keyword} 완벽 가이드",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=Video+3",
            "link": "https://www.youtube.com/watch?v=jNQXAC9IVRw"
        }
    ]
    time.sleep(1)
    return mock_data

def get_video_transcript(video_link):
    return f"선택된 영상 링크: {video_link}\n이 영상의 예시 트랜스크립트입니다."

def regenerate_content(video_transcript, target_audience, tone_style, goal, word_count):
    return f"""[재구성된 콘텐츠]

타겟층: {target_audience}
톤/스타일: {tone_style}
목표: {goal}
글자수: {word_count}

원본 기반 AI 콘텐츠입니다.
"""


# 단계 1
if st.session_state.step == 1:
    st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)
    st.markdown("<div class='subheader'>주제입력</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        keyword = st.text_input("키워드 입력", key="keyword_input", label_visibility="collapsed")

    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        if st.button("콘텐츠 검색", use_container_width=True) and keyword:
            st.session_state.recommended_videos = get_youtube_recommendations(keyword)
            st.experimental_rerun()

    if st.session_state.recommended_videos:
        st.markdown("<div class='subheader'>인기 콘텐츠 TOP3</div>", unsafe_allow_html=True)
        for i, video in enumerate(st.session_state.recommended_videos):
            st.markdown(f"""
            <div style='padding: 10px; border:1px solid #ccc; margin-bottom: 10px;'>
                <strong>{i+1}. 제목:</strong> {video['title']}<br>
                <a href="{video['link']}" target="_blank">영상 보기</a>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"선택 {i+1}", key=f"select_{i}"):
                st.session_state.selected_video = video
                st.experimental_rerun()

    if st.session_state.selected_video:
        st.markdown(f"""<div style='padding: 10px; background-color: #eef;'>선택한 콘텐츠: 
        {st.session_state.selected_video['title']}<br>진행하시겠습니까?</div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("YES"):
                st.session_state.step = 2
                st.experimental_rerun()
        with col2:
            if st.button("다시 선택"):
                st.session_state.selected_video = None
                st.experimental_rerun()

# 단계 2
elif st.session_state.step == 2:
    st.markdown("<div class='header'>콘텐츠 만들기</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"<b>선택된 영상:</b> {st.session_state.selected_video['title']}", unsafe_allow_html=True)
        st.markdown(f"<a href='{st.session_state.selected_video['link']}' target='_blank'>영상 링크</a>", unsafe_allow_html=True)

        st.markdown("<div class='subheader'>타겟층</div>", unsafe_allow_html=True)
        st.session_state.target_audience = st.text_input("", key="target_audience_input", value=st.session_state.target_audience, label_visibility="collapsed")

        st.markdown("<div class='subheader'>톤/스타일</div>", unsafe_allow_html=True)
        st.session_state.tone_style = st.radio("톤 선택", ["일반", "정중함", "감성"], horizontal=True, index=["일반", "정중함", "감성"].index(st.session_state.tone_style))

        st.markdown("<div class='subheader'>목표</div>", unsafe_allow_html=True)
        st.session_state.goal = st.radio("목표 선택", ["정보전달", "설득력", "구매유도"], horizontal=True, index=["정보전달", "설득력", "구매유도"].index(st.session_state.goal))

        st.markdown("<div class='subheader'>글자수</div>", unsafe_allow_html=True)
        st.session_state.word_count = st.radio("글자수 선택", ["500자내외", "1000자내외", "1500자내외"]()
