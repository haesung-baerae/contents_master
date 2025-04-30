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
    .block-container { padding: 2rem 3rem; max-width: none; }
    .header { font-size: 32px; font-weight: bold; text-align: center; padding: 20px; background-color: #111; color: white; border-radius: 8px; margin-bottom: 1.5rem; }
    .subheader { font-size: 20px; font-weight: 600; text-align: center; margin: 1rem 0; }
    .stTextInput > div > div > input { background-color: #222; color: #fff; padding: 0.75rem; border-radius: 6px; border: 1px solid #444; width: 100%; }
    .stButton button { background-color: #f8f8f8; border: 1px solid #ccc; color: #333; padding: 0.75rem; border-radius: 6px; font-size: 16px; }
    .dummy-box { background: #333; color: #eee; padding: 1rem; border-radius: 6px; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# 세션 초기화
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.recommended_videos = []
    st.session_state.selected_video = None
    st.session_state.generated_content = ""

# 더미 데이터 함수

def get_dummy_recommendations():
    return [
        {"title": "AI 콘텐츠 전략 완벽 가이드", "link": "#"},
        {"title": "2025년 마케팅 트렌드 분석", "link": "#"},
        {"title": "브랜드 스토리텔링 작성법", "link": "#"}
    ]

def get_youtube_recommendations(keyword):
    time.sleep(0.5)
    return get_dummy_recommendations()

def get_video_transcript(link):
    # 더미 트랜스크립트 예시
    return (
        "안녕하세요, 이 영상은 AI 콘텐츠 자동 생성 툴을 소개합니다."
        " 주요 기능으로 인기 콘텐츠 분석, 트랜스크립트 생성, 키워드 기반 요약이 있습니다."
    )

def regenerate_content(transcript, audience, tone, goal, wc):
    # 더미 생성 문구 예시
    return (
        "안녕하세요!\n"
        f"타겟층: {audience}\n"
        f"톤/스타일: {tone}\n"
        f"목표: {goal}\n"
        f"분량: {wc}\n\n"
        "이 콘텐츠는 AI 자동 생성 예시입니다. 실제 연동 시 OpenAI API를 사용하여"
        " 트랜스크립트를 기반으로 최적화된 문장을 제공합니다."
    )

# UI 구현
st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)

if st.session_state.step == 1:
    st.markdown("<div class='subheader'>주제 입력 (더미 예시 가능)</div>", unsafe_allow_html=True)
    keyword = st.text_input("키워드 입력", placeholder="예: AI 마케팅")
    if st.button("콘텐츠 검색"):
        st.session_state.recommended_videos = get_youtube_recommendations(keyword or "")

    if not st.session_state.recommended_videos:
        st.info("동작 테스트용 더미 콘텐츠가 표시됩니다.")
    for idx, vid in enumerate(st.session_state.recommended_videos or get_dummy_recommendations(), 1):
        st.markdown(f"<div class='dummy-box'><strong>{idx}. {vid['title']}</strong> <a href='{vid['link']}'>[보기]</a></div>", unsafe_allow_html=True)
        if st.button(f"선택 {idx}", key=f"sel{idx}"):
            st.session_state.selected_video = vid
            st.session_state.step = 2

elif st.session_state.step == 2:
    vid = st.session_state.selected_video or get_dummy_recommendations()[0]
    st.markdown("<div class='subheader'>콘텐츠 만들기</div>", unsafe_allow_html=True)
    st.text_area("트랜스크립트 확인", get_video_transcript(vid['link']), height=120)
    audience = st.text_input("타겟층 (예: 직장인 30대)")
    tone = st.selectbox("톤/스타일", ["일반", "정중함", "감성"])
    goal = st.selectbox("목표", ["정보전달", "설득력", "구매유도"])
    wc = st.selectbox("글자수", ["500자내외", "1000자내외", "1500자내외"])
    if st.button("더미 콘텐츠 생성"):
        st.session_state.generated_content = regenerate_content(None, audience or "30대 직장인", tone, goal, wc)
        st.session_state.step = 3

elif st.session_state.step == 3:
    st.markdown("<div class='subheader'>생성된 콘텐츠 (더미)</div>", unsafe_allow_html=True)
    st.write(st.session_state.generated_content)
    if st.button("처음으로"):
        for key in ['step', 'recommended_videos', 'selected_video', 'generated_content']:
            st.session_state.pop(key, None)
        st.session_state.step = 1
