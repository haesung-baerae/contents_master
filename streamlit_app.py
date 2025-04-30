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
        max-width: none;  /* 최대 너비 해제 */
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
    .header {
        width: auto;
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        margin: 0 auto 20px auto;
        padding: 10px 20px;
        background-color: #111;
        color: white;
        border-radius: 5px;
        overflow: visible;
        white-space: normal;
    }
    .subheader {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
    }
    .subject-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1,
        'recommended_videos': [],
        'selected_video': None,
        'video_transcript': "",
        'generated_content': "",
        'target_audience': "",
        'tone_style': "일반",
        'goal': "정보전달",
        'word_count': "500자내외"
    })

# 모의 함수들 (실제 함수로 교체)
# ... (생략: 이전과 동일)

def get_youtube_recommendations(keyword):
    return [
        {"title": f"{keyword}에 대한 분석", "thumbnail": "https://via.placeholder.com/320x180.png?text=Video+1", "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        {"title": f"{keyword} 심층탐구", "thumbnail": "https://via.placeholder.com/320x180.png?text=Video+2", "link": "https://www.youtube.com/watch?v=xvFZjo5PgG0"},
        {"title": f"{keyword} 완벽 가이드", "thumbnail": "https://via.placeholder.com/320x180.png?text=Video+3", "link": "https://www.youtube.com/watch?v=jNQXAC9IVRw"}
    ]

def get_video_transcript(video_link):
    return f"선택된 영상 링크: {video_link}\n이 영상의 예시 트랜스크립트입니다."

def regenerate_content(video_transcript, target_audience, tone_style, goal, word_count):
    return f"""[재구성된 콘텐츠]\n\n타겟층: {target_audience}\n톤/스타일: {tone_style}\n목표: {goal}\n글자수: {word_count}\n\n원본 기반 AI 콘텐츠입니다.\n"""

# UI 로직
if st.session_state.step == 1:
    st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)
    st.markdown("<div class='subheader'>주제 입력</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='subject-container'>", unsafe_allow_html=True)
        keyword = st.text_input("키워드 입력", placeholder="예: AI 마케팅", key="keyword_input")
        st.markdown("</div>", unsafe_allow_html=True)

    search_click = st.button("콘텐츠 검색", use_container_width=True, key="search_btn")
    if search_click:
        if not keyword:
            st.warning("키워드를 입력해주세요.")
        else:
            st.session_state.recommended_videos = get_youtube_recommendations(keyword)
            st.session_state.step = 1  # remain
        st.experimental_rerun()

    if st.session_state.recommended_videos:
        st.markdown("<div class='subheader'>인기 콘텐츠 TOP3</div>", unsafe_allow_html=True)
        for i, video in enumerate(st.session_state.recommended_videos):
            col1, col2 = st.columns([1,4])
            with col1:
                st.image(video['thumbnail'], use_column_width=True)
            with col2:
                st.write(f"**{i+1}. {video['title']}**")
                st.write(f"[영상 보기]({video['link']})")
                select_click = st.button(f"선택 {i+1}", key=f"select_{i}")
                if select_click:
                    st.session_state.selected_video = video
                    st.experimental_rerun()

    if st.session_state.selected_video:
        st.success(f"선택된 콘텐츠: {st.session_state.selected_video['title']}")
        yes_click = st.button("진행하기", key="yes_btn")
        no_click = st.button("다시 선택", key="no_btn")
        if yes_click:
            st.session_state.step = 2
            st.session_state.video_transcript = get_video_transcript(st.session_state.selected_video['link'])
            st.experimental_rerun()
        if no_click:
            for var in ['selected_video','recommended_videos']:
                st.session_state.pop(var, None)
            st.experimental_rerun()

elif st.session_state.step == 2:
    st.markdown("<div class='header'>콘텐츠 만들기</div>", unsafe_allow_html=True)
    st.write(f"**선택된 영상:** {st.session_state.selected_video['title']}")
    st.write(f"[영상 링크]({st.session_state.selected_video['link']})")

    st.markdown("<div class='subheader'>트랜스크립트</div>", unsafe_allow_html=True)
    st.text_area("", st.session_state.video_transcript, height=150, key="transcript_area")

    st.markdown("<div class='subheader'>파라미터 설정</div>", unsafe_allow_html=True)
    tgt = st.text_input("타겟층", value=st.session_state.target_audience, key="audience_input")
    tone = st.radio("톤/스타일", ["일반","정중함","감성"], index=["일반","정중함","감성"].index(st.session_state.tone_style), horizontal=True)
    goal = st.radio("목표", ["정보전달","설득력","구매유도"], index=["정보전달","설득력","구매유도"].index(st.session_state.goal), horizontal=True)
    wc = st.radio("글자수", ["500자내외","1000자내외","1500자내외"], index=["500자내외","1000자내외","1500자내외"].index(st.session_state.word_count), horizontal=True)

    gen_click = st.button("콘텐츠 생성", use_container_width=True, key="gen_btn")
    if gen_click:
        st.session_state.target_audience = tgt
        st.session_state.tone_style = tone
        st.session_state.goal = goal
        st.session_state.word_count = wc
        st.session_state.generated_content = regenerate_content(
            st.session_state.video_transcript, tgt, tone, goal, wc
        )
        st.session_state.step = 3
        st.experimental_rerun()

elif st.session_state.step == 3:
    st.markdown("<div class='header'>생성된 콘텐츠</div>", unsafe_allow_html=True)
    st.markdown(st.session_state.generated_content)
    reset_click = st.button("처음으로 돌아가기", use_container_width=True, key="reset_btn")
    if reset_click:
        for var in ['step','recommended_videos','selected_video','video_transcript','generated_content']:
            st.session_state.pop(var, None)
        st.experimental_rerun()
