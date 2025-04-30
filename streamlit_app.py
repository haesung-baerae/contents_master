import streamlit as st
import time
import json
import streamlit.components.v1 as components

# --------------------------------------------------------------------
# 스트림릿 페이지 설정 ― 반드시 **최초** 명령으로 실행되어야 합니다!
# --------------------------------------------------------------------
st.set_page_config(
    page_title="콘텐츠 마스터",
    layout="centered",  # wide에서 centered로 변경
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------
# 향상된 전역 CSS 스타일  
# --------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* 전체 페이지 스타일 */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* 컨테이너 너비 조정 */
        .block-container {
            max-width: 800px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* 헤더 스타일 */
        .header {
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            padding: 30px;
            background: linear-gradient(135deg, #2c3e50, #4c6ef5);
            color: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* 서브헤더 스타일 */
        .subheader {
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin: 18px 0 12px 0;
            color: #2c3e50;
            border-bottom: 2px solid #4c6ef5;
            padding-bottom: 8px;
        }
        
        /* 텍스트 입력 스타일 */
        .stTextInput input {
            border-radius: 8px;
            border: 2px solid #e0e5ec;
            padding: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        
        /* 텍스트 영역 스타일 */
        .stTextArea textarea {
            background: #fff;
            color: #333;
            border: 2px solid #e0e5ec;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            font-size: 16px;
        }
        
        /* 버튼 스타일 */
        .stButton button {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        /* 카드 스타일 */
        .content-card {
            border: none;
            border-radius: 12px;
            padding: 16px;
            margin: 12px 0;
            background: #fff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .content-card:hover {
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
            transform: translateY(-3px);
        }
        
        /* 단계 표시기 */
        .step-indicator {
            display: flex;
            justify-content: center;
            margin: 24px 0;
        }
        
        .step {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e0e5ec;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 20px;
            font-weight: bold;
            position: relative;
        }
        
        .step.active {
            background: #4c6ef5;
            color: white;
            box-shadow: 0 4px 8px rgba(76, 110, 245, 0.3);
        }
        
        .step-line {
            height: 4px;
            background: #e0e5ec;
            flex-grow: 1;
            position: relative;
            top: 20px;
        }
        
        .step-line.active {
            background: #4c6ef5;
        }
        
        /* 메시지 스타일 */
        .info-box {
            background-color: #e3f2fd;
            color: #0d47a1;
            padding: 16px;
            border-radius: 8px;
            border-left: 5px solid #2196f3;
            margin: 16px 0;
        }
        
        .success-box {
            background-color: #e8f5e9;
            color: #1b5e20;
            padding: 16px;
            border-radius: 8px;
            border-left: 5px solid #4caf50;
            margin: 16px 0;
        }
        
        /* 옵션 버튼 스타일 */
        .option-button-active {
            background: #4c6ef5 !important;
            color: white !important;
        }
        
        .option-button {
            background: #f8f9fa;
            border: 2px solid #e0e5ec !important;
            color: #555 !important;
        }
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
# 단계 표시기 렌더링
# --------------------------------------------------------------------

def render_step_indicator(current_step, total_steps=3):
    step_html = '<div class="step-indicator">'
    
    for i in range(1, total_steps + 1):
        # 단계 원
        step_class = "active" if i <= current_step else ""
        step_html += f'<div class="step {step_class}">{i}</div>'
        
        # 연결선 (마지막 단계 제외)
        if i < total_steps:
            line_class = "active" if i < current_step else ""
            step_html += f'<div class="step-line {line_class}"></div>'
    
    step_html += '</div>'
    st.markdown(step_html, unsafe_allow_html=True)

# --------------------------------------------------------------------
# 복사 버튼 컴포넌트
# --------------------------------------------------------------------

def copy_button(text: str):
    js_literal = json.dumps(text)
    html = f"""
        <button onclick='navigator.clipboard.writeText({js_literal});alert("클립보드에 복사되었습니다!");' 
                style='width:100%;padding:12px;background:linear-gradient(135deg, #4CAF50, #2E7D32);
                color:white;border:none;border-radius:8px;cursor:pointer;font-weight:600;
                box-shadow:0 2px 10px rgba(46,125,50,0.3);transition:all 0.3s;'>
            📋 클립보드에 복사하기
        </button>
    """
    components.html(html, height=60)

# --------------------------------------------------------------------
# STEP 1 ─ 콘텐츠 마스터 (주제 입력 & 영상 선택)
# --------------------------------------------------------------------

def step_1():
    st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)
    render_step_indicator(st.session_state.step)
    
    # ─── 주제 입력 ─── 
    st.markdown("<div class='subheader'>주제 키워드 입력</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        keyword = st.text_input("주제 키워드", key="keyword_input", label_visibility="collapsed", 
                              placeholder="분석하고 싶은 주제나 키워드를 입력하세요...")
    
    with col2:
        if st.button("🔍 검색", use_container_width=True, type="primary"):
            if keyword:
                with st.spinner("관련 콘텐츠 검색중..."):
                    st.session_state.recommended_videos = get_youtube_recommendations(keyword)
                st.rerun()
            else:
                st.warning("키워드를 입력해주세요!")

    # ─── 추천 목록 ─── 
    if st.session_state.recommended_videos:
        st.markdown("<div class='subheader'>추천 인기 콘텐츠 TOP3</div>", unsafe_allow_html=True)
        
        for i, v in enumerate(st.session_state.recommended_videos):
            st.markdown(
                f"""
                <div class='content-card'>
                    <div style='display:flex;align-items:center'>
                        <div style='background:#4c6ef5;color:white;width:28px;height:28px;border-radius:50%;
                                    display:flex;align-items:center;justify-content:center;margin-right:12px;
                                    font-weight:bold;'>{i+1}</div>
                        <div>
                            <h3 style='margin:0;font-size:16px;color:#333'>{v['title']}</h3>
                            <a href='{v['link']}' target='_blank' style='color:#4c6ef5;text-decoration:none;font-size:14px;'>
                                🎬 영상 보기
                            </a>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("선택하기", key=f"sel_{i}", use_container_width=True):
                st.session_state.selected_video = v
                st.rerun()

    # ─── 선택 확인 ───
    if st.session_state.selected_video:
        st.markdown(
            f"""
            <div class="success-box">
                <b>✅ 선택한 영상:</b> {st.session_state.selected_video['title']}
            </div>
            """,
            unsafe_allow_html=True
        )
        col1, col2 = st.columns(2)
        if col2.button("다음 단계로 →", type="primary", use_container_width=True):
            next_step()
        if col1.button("🔄 다시 선택", use_container_width=True):
            st.session_state.selected_video = None
            st.rerun()

# --------------------------------------------------------------------
# 공용 선택 버튼 컴포넌트 (톤/목표/글자수)
# --------------------------------------------------------------------

def selectable(label, state_key, options):
    st.markdown(f"<div class='subheader'>{label}</div>", unsafe_allow_html=True)
    # 컨테이너 추가하여 옵션 버튼들 모아주기
    with st.container():
        cols = st.columns(len(options))
        for col, opt in zip(cols, options):
            with col:
                button_type = "option-button-active" if st.session_state[state_key] == opt else "option-button"
                if st.button(opt, key=f"{state_key}_{opt}", 
                            use_container_width=True, 
                            type="secondary" if button_type == "option-button" else "primary"):
                    st.session_state[state_key] = opt
                    st.rerun()

# --------------------------------------------------------------------
# STEP 2 ─ 콘텐츠 만들기 (옵션 설정)
# --------------------------------------------------------------------

def step_2():
    st.markdown("<div class='header'>콘텐츠 만들기</div>", unsafe_allow_html=True)
    render_step_indicator(st.session_state.step)
    
    st.markdown(
        f"""
        <div class="info-box" style="font-size:14px;">
            <b>📽️ 선택한 영상:</b> {st.session_state.selected_video['title']}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 옵션 영역을 컨테이너로 감싸기
    with st.container():
        st.markdown("<div class='subheader'>타겟층 설정</div>", unsafe_allow_html=True)
        st.session_state.target_audience = st.text_input("타겟층 입력", 
                                              value=st.session_state.target_audience, 
                                              placeholder="예: 20-30대 직장인, 대학생, 학부모 등...",
                                              label_visibility="collapsed")
    
        # 나머지 옵션들
        selectable("톤/스타일 선택", "tone_style", ["일반", "정중함", "감성"])
        selectable("콘텐츠 목표", "goal", ["정보전달", "설득력", "구매유도"])
        selectable("글자수 설정", "word_count", ["500자내외", "1000자내외", "1500자내외"])

    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    if col1.button("← 이전 단계", use_container_width=True):
        prev_step()
    if col2.button("✨ 콘텐츠 생성하기", type="primary", use_container_width=True):
        with st.spinner("콘텐츠 생성 중..."):
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
# STEP 3 ─ 결과 & 복사 버튼
# --------------------------------------------------------------------

def step_3():
    st.markdown("<div class='header'>콘텐츠 생성완료</div>", unsafe_allow_html=True)
    render_step_indicator(st.session_state.step)

    st.markdown(
        """
        <div class="success-box">
            <h3 style="margin-top:0;font-size:18px;">✅ 콘텐츠가 성공적으로 생성되었습니다!</h3>
            <p style="margin-bottom:0;font-size:14px;">아래 생성된 콘텐츠를 확인하고 복사하여 사용하세요.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # 선택 옵션 요약 - 카드 형태로
    st.markdown("<div class='subheader'>선택 옵션 요약</div>", unsafe_allow_html=True)
    
    summary_data = {
        "영상 제목": st.session_state.selected_video["title"],
        "타겟층": st.session_state.target_audience or "지정되지 않음",
        "톤/스타일": st.session_state.tone_style,
        "목표": st.session_state.goal,
        "글자수": st.session_state.word_count,
    }
    
    # 2열로 변경하여 좁은 화면에서 더 보기 좋게 표시
    cols = st.columns(2)
    for i, (k, v) in enumerate(summary_data.items()):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div style="background:#f8f9fa;padding:10px;border-radius:8px;margin-bottom:8px;border-left:3px solid #4c6ef5;">
                    <div style="color:#666;font-size:13px">{k}</div>
                    <div style="font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{v}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 콘텐츠 영역
    st.markdown("<div class='subheader'>생성된 콘텐츠</div>", unsafe_allow_html=True)
    st.text_area("생성된 콘텐츠", st.session_state.generated_content, height=300, label_visibility="hidden")

    # 복사 버튼
    copy_button(st.session_state.generated_content)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    if col1.button("← 옵션 다시 설정하기", use_container_width=True):
        prev_step()
    if col2.button("🔄 처음부터 다시하기", use_container_width=True):
        st.session_state.step = 1
        st.session_state.selected_video = None
        st.session_state.generated_content = ""
        st.rerun()

# --------------------------------------------------------------------
# 메인 라우터
# --------------------------------------------------------------------

if st.session_state.step == 1:
    step_1()
elif st.session_state.step == 2:
    step_2()
else:
    step_3()
