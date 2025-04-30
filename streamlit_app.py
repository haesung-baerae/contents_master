import streamlit as st
import time
import json
import streamlit.components.v1 as components

# --------------------------------------------------------------------
# 스트림릿 페이지 설정 ― 반드시 **최초** 명령으로 실행되어야 합니다!
# --------------------------------------------------------------------
st.set_page_config(
    page_title="콘텐츠 마스터",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------
# 전역 CSS (심플 버전)  
# --------------------------------------------------------------------
st.markdown(
    """
    <style>
        .header {font-size:28px;font-weight:bold;text-align:center;margin:20px 0;padding:25px;background:#111;color:#fff;border-radius:6px;}
        .subheader {font-size:18px;font-weight:bold;text-align:center;margin:12px 0;}
        .stTextArea textarea {background:#fff;color:#000;border:1px solid #ddd;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------
# 테스트용 모의 함수 (원형 유지)
# --------------------------------------------------------------------

def get_youtube_recommendations(keyword):
    mock = [
        {"title": f"<자세히보기>(토큰) {keyword} 분석", "link": "https://youtu.be/dQw4w9WgXcQ"},
        {"title": f"<자세히보기> {keyword} 심층탐구", "link": "https://youtu.be/xvFZjo5PgG0"},
        {"title": f"<자세히보기> {keyword} 가이드", "link": "https://youtu.be/jNQXAC9IVRw"},
    ]
    time.sleep(1)
    return mock

def get_video_transcript(link):
    return f"선택 영상({link})의 예시 스크립트입니다. 실제 구현에서는 YouTube API 호출 필요."

def regenerate_content(transcript, audience, tone, goal, words):
    return (
        "재구성된 콘텐츠\n\n"
        f"타겟층: {audience}\n톤/스타일: {tone}\n목표: {goal}\n글자수: {words}\n\n"
        "원본 스크립트를 기반으로 한 새 콘텐츠 예시입니다."
    )

# --------------------------------------------------------------------
# 세션 상태 기본값
# --------------------------------------------------------------------

defaults = {
    "step": 1,
    "recommended_videos": [],
    "selected_video": None,
    "generated_content": "",
    "target_audience": "",
    "tone_style": "일반",
    "goal": "정보전달",
    "word_count": "500자내외",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# --------------------------------------------------------------------
# 헬퍼 함수
# --------------------------------------------------------------------

def next_step():
    st.session_state.step += 1
    st.rerun()

def prev_step():
    st.session_state.step -= 1
    st.rerun()

# --------------------------------------------------------------------
# STEP 1 ─ 콘텐츠 마스터 (주제 입력 & 영상 선택)
# --------------------------------------------------------------------

def step_1():
    st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)

    # ─── 주제 입력 ───
    st.markdown("<div class='subheader'>주제 입력</div>", unsafe_allow_html=True)
    keyword = st.text_input("주제 키워드", key="keyword_input", label_visibility="collapsed")

    if st.button("콘텐츠 검색", use_container_width=True):
        if keyword:
            st.session_state.recommended_videos = get_youtube_recommendations(keyword)
            st.rerun()

    # ─── 추천 목록 ───
    if st.session_state.recommended_videos:
        st.markdown("<div class='subheader'>인기 콘텐츠 TOP3</div>", unsafe_allow_html=True)
        for i, v in enumerate(st.session_state.recommended_videos):
            st.markdown(
                f"<div style='border:1px solid #ddd;border-radius:5px;padding:10px;margin:8px 0;background:#f8f9fa;'>"
                f"<b>{i+1}. {v['title']}</b><br>"
                f"<a href='{v['link']}' target='_blank'>영상 보기</a></div>",
                unsafe_allow_html=True,
            )
            if st.button("선택", key=f"sel_{i}", use_container_width=True):
                st.session_state.selected_video = v
                st.rerun()

    # ─── 선택 확인 ───
    if st.session_state.selected_video:
        st.success(f"선택된 영상: {st.session_state.selected_video['title']}")
        if st.button("다음", type="primary"):
            next_step()
        if st.button("다시 선택"):
            st.session_state.selected_video = None
            st.rerun()

# --------------------------------------------------------------------
# 공용 선택 버튼 컴포넌트 (톤/목표/글자수)
# --------------------------------------------------------------------

def selectable(label, state_key, options):
    st.markdown(f"<div class='subheader'>{label}</div>", unsafe_allow_html=True)
    cols = st.columns(len(options))
    for col, opt in zip(cols, options):
        with col:
            if st.button(opt, key=f"{state_key}_{opt}", type="primary" if st.session_state[state_key] == opt else "secondary", use_container_width=True):
                st.session_state[state_key] = opt
                st.experimental_rerun()

# --------------------------------------------------------------------
# STEP 2 ─ 콘텐츠 만들기 (옵션 설정)
# --------------------------------------------------------------------

def step_2():
    st.markdown("<div class='header'>콘텐츠 만들기</div>", unsafe_allow_html=True)
    st.info(f"선택된 영상: {st.session_state.selected_video['title']}")

    st.session_state.target_audience = st.text_input("타겟층 입력", value=st.session_state.target_audience, label_visibility="collapsed")

    selectable("톤/스타일", "tone_style", ["인풋말씀", "정중함", "감성"])
    selectable("목표", "goal", ["정보전달", "설득력", "구매유도"])
    selectable("글자수", "word_count", ["500자내외", "1000자내외", "1500자내외"])

    col1, col2 = st.columns(2)
    if col1.button("이전"):
        prev_step()
    if col2.button("콘텐츠 만들기", type="primary"):
        transcript = get_video_transcript(st.session_state.selected_video["link"])
        st.session_state.generated_content = regenerate_content(
            transcript,
            st.session_state.target_audience,
            st.session_state.tone_style,
            st.session_state.goal,
            st.session_state.word_count,
        )
        next_step()

# --------------------------------------------------------------------
# STEP 3 ─ 결과 & 복사 버튼
# --------------------------------------------------------------------

def copy_button(text: str):
    js_literal = json.dumps(text)
    html = f"""
        <button onclick='navigator.clipboard.writeText({js_literal});alert("클립보드에 복사되었습니다!");' 
                style='width:100%;padding:0.6rem;background:#4CAF50;color:white;border:none;border-radius:4px;cursor:pointer;'>복사하기</button>
    """
    components.html(html, height=60)


def step_3():
    st.markdown("<div class='header'>콘텐츠 생성완료</div>", unsafe_allow_html=True)

    st.markdown("**선택 옵션 요약**")
    st.write({
        "영상": st.session_state.selected_video["title"],
        "타겟층": st.session_state.target_audience,
        "톤/스타일": st.session_state.tone_style,
        "목표": st.session_state.goal,
        "글자수": st.session_state.word_count,
    })

    st.text_area("생성된 콘텐츠", st.session_state.generated_content, height=300, label_visibility="hidden")

    copy_button(st.session_state.generated_content)

    if st.button("다시 설정하기"):
        prev_step()

# --------------------------------------------------------------------
# 메인 라우터
# --------------------------------------------------------------------

if st.session_state.step == 1:
    step_1()
elif st.session_state.step == 2:
    step_2()
else:
    step_3()
