import streamlit as st
import time
import json
import streamlit.components.v1 as components
import youtube_handler as yt
import script_handler as sc
import textwrap   # ← 4칸 들여쓰기 제거용


# --------------------------------------------------------------------
# 스트림릿 페이지 설정 ― 반드시 **최초** 명령으로 실행되어야 합니다!
# --------------------------------------------------------------------
st.set_page_config(
    page_title="콘텐츠 마스터",
    layout="centered",  # centered 레이아웃 유지
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------------------------
# 향상된 전역 CSS 스타일 - 더 컴팩트하게 조정
# --------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* 전체 페이지 스타일 */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* 컨테이너 너비 조정 - 더 좁게 */
        .block-container {
            max-width: 600px !important;
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        
        /* 헤더 스타일 - 더 컴팩트하게 */
        .header {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            margin: 12px 0;
            padding: 20px;
            background: linear-gradient(135deg, #2c3e50, #4c6ef5);
            color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* 서브헤더 스타일 - 더 컴팩트하게 */
        .subheader {
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin: 10px 0 8px 0;
            color: #2c3e50;
            border-bottom: 2px solid #4c6ef5;
            padding-bottom: 5px;
        }
        
        /* 텍스트 입력 스타일 */
        .stTextInput input {
            border-radius: 6px;
            border: 1px solid #e0e5ec;
            padding: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* 텍스트 영역 스타일 */
        .stTextArea textarea {
            background: #fff;
            color: #333;
            border: 1px solid #e0e5ec;
            border-radius: 6px;
            padding: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            font-size: 14px;
        }
        
        /* 버튼 스타일 - 더 작게 */
        .stButton button {
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
            font-size: 14px;
        }
        
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 3px 6px rgba(0,0,0,0.15);
        }
        
        /* 카드 스타일 - 더 컴팩트하게 */
        .content-card {
            border: none;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            background: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        
        .content-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        /* 단계 표시기 - 더 작게 */
        .step-indicator {
            display: flex;
            justify-content: center;
            margin: 15px 0;
        }
        
        .step {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #e0e5ec;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 15px;
            font-weight: bold;
            position: relative;
            font-size: 14px;
        }
        
        .step.active {
            background: #4c6ef5;
            color: white;
            box-shadow: 0 3px 6px rgba(76, 110, 245, 0.3);
        }
        
        .step-line {
            height: 3px;
            background: #e0e5ec;
            flex-grow: 1;
            position: relative;
            top: 15px;
        }
        
        .step-line.active {
            background: #4c6ef5;
        }
        
        /* 메시지 스타일 - 더 컴팩트하게 */
        .info-box {
            background-color: #e3f2fd;
            color: #0d47a1;
            padding: 10px;
            border-radius: 6px;
            border-left: 4px solid #2196f3;
            margin: 10px 0;
            font-size: 14px;
        }
        
        .success-box {
            background-color: #e8f5e9;
            color: #1b5e20;
            padding: 10px;
            border-radius: 6px;
            border-left: 4px solid #4caf50;
            margin: 10px 0;
            font-size: 14px;
        }
        
        /* 옵션 버튼 스타일 */
        .option-button-active {
            background: #4c6ef5 !important;
            color: white !important;
        }
        
        .option-button {
            background: #f8f9fa;
            border: 1px solid #e0e5ec !important;
            color: #555 !important;
        }
        
        /* 전체 간격 조정 */
        .row-widget {
            margin-bottom: 6px !important;
        }
        
        /* 요약 카드 스타일 - 더 컴팩트하게 */
        .summary-card {
            background: #f8f9fa;
            padding: 8px;
            border-radius: 6px;
            margin-bottom: 6px;
            border-left: 3px solid #4c6ef5;
            font-size: 13px;
        }
        
        /* 복사 버튼 컨테이너 높이 조정 */
        .copy-button-container {
            height: 45px !important;
        }
        
        /* 경고 메시지 스타일 */
        .stAlert {
            padding: 8px !important;
            font-size: 14px !important;
        }
        
        /* 이미지 인디케이터 숫자 크기 */
        .number-indicator {
            width: 24px;
            height: 24px;
            font-size: 13px;
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
# 복사 버튼 컴포넌트 - 더 컴팩트하게 높이 조정
# --------------------------------------------------------------------

def copy_button(text: str):
    js_literal = json.dumps(text)
    html = f"""
        <button onclick='navigator.clipboard.writeText({js_literal});alert("클립보드에 복사되었습니다!");' 
                style='width:100%;padding:8px;background:linear-gradient(135deg, #4CAF50, #2E7D32);
                color:white;border:none;border-radius:6px;cursor:pointer;font-weight:600;
                box-shadow:0 2px 8px rgba(46,125,50,0.3);transition:all 0.3s;font-size:14px;'>
            📋 클립보드에 복사하기
        </button>
    """
    components.html(html, height=45)

# --------------------------------------------------------------------
# STEP 1 ─ 콘텐츠 마스터 (주제 입력 & 영상 선택)
# --------------------------------------------------------------------

def step_1():
    st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)
    render_step_indicator(st.session_state.step)
    start = "2024-12-01"
    end = "2025-04-29"
    lang = "ko"          # "ko" 이면 한국어 자막 우선
    # ─── 주제 입력 ─── 
    st.markdown("<div class='subheader'>주제 키워드 입력</div>", unsafe_allow_html=True)
    
    # 4:1 비율로 변경하여 검색 버튼 더 컴팩트하게
    col1, col2 = st.columns([4, 1])
    with col1:
        keyword = st.text_input("주제 키워드", key="keyword_input", label_visibility="collapsed", 
                              placeholder="분석하고 싶은 주제나 키워드를 입력하세요...")
    
    with col2:
        if st.button("🔍 검색", use_container_width=True, type="primary"):
            if keyword:
                with st.spinner("검색중..."):
                    #st.session_state.recommended_videos = get_youtube_recommendations(keyword)
                    st.session_state.recommended_videos = yt.top3_videos(keyword, start, end, lang)
                st.rerun()
            else:
                st.warning("키워드를 입력해주세요!")

    # ─── 추천 목록 ─── 
    if st.session_state.recommended_videos:
        st.markdown("<div class='subheader'>추천 인기 콘텐츠 TOP3</div>", unsafe_allow_html=True)
        
    # 추천 영상 정보를 표시하는 코드
    for i, v in enumerate(st.session_state.recommended_videos):
        dur_min = v['duration_sec'] // 60
        
        # 각 비디오마다 새로운 컨테이너 생성
        with st.container():
            col1, col2 = st.columns([4, 1])  # 비율을 4:1로 조정하여 카드에 더 많은 공간 할당
            
            # ───────── 카드(왼쪽) ─────────
            with col1:
                html = textwrap.dedent(f"""
                <div class='content-card' style='padding:10px;border:1px solid #e6e6e6;border-radius:5px;margin-bottom:10px;background-color:#f9f9f9;'>
                  <div style='display:flex;align-items:flex-start'>
                    <div class='number-indicator'
                         style='background:#4c6ef5;color:white;width:28px;height:28px;border-radius:50%;
                                display:flex;align-items:center;justify-content:center;margin-right:12px;font-weight:bold;flex-shrink:0;'>
                         {i+1}
                    </div>
                    <div style='flex-grow:1;overflow:hidden;'>
                      <h3 style='margin:0 0 5px 0;font-size:16px;color:#333;font-weight:600;'>{v['title']}</h3>
                      <div style='display:flex;align-items:center;margin-bottom:5px;'>
                        <a href='{v['url']}' target='_blank'
                           style='color:#4c6ef5;text-decoration:none;font-size:13px;display:inline-flex;align-items:center;'>
                           <span style='margin-right:4px;'>🎬</span>영상 보기
                        </a>
                      </div>
                      <p style='margin:0;font-size:12px;color:#555;'>
                        <span style='margin-right:8px;'>👁️ 조회수 {v['views']:,}</span>
                        <span style='margin-right:8px;'>📅 업로드 {v['upload_date']}</span>
                        <span>⏱️ 길이 {dur_min}분 {v['duration_sec']%60}초</span>
                      </p>
                    </div>
                  </div>
                </div>
                """)
                st.markdown(html, unsafe_allow_html=True)
            
            # ───────── 선택 버튼(오른쪽) ─────────
            with col2:
                button_html = f"""
                <style>
                .custom-button-{i} {{
                    background-color: #4c6ef5;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 0;
                    width: 100%;
                    font-weight: 600;
                    font-size: 14px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                    text-align: center;
                    display: inline-block;
                    margin-top: 10px;
                }}
                .custom-button-{i}:hover {{
                    background-color: #364fc7;
                }}
                </style>
                """
                st.markdown(button_html, unsafe_allow_html=True)
                
                if st.button("선택", key=f"sel_{i}", use_container_width=True, 
                            help=f"이 영상을 선택합니다: {v['title']}"):
                    st.session_state.selected_video = v
                    st.rerun()
        
        # 비디오 사이에 약간의 간격 추가
        st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

    # ─── 선택 확인 ───
    if st.session_state.selected_video:
        st.markdown(
            f"""
            <div class="success-box">
                <b>✅ 선택:</b> {st.session_state.selected_video['title']}
            </div>
            """,
            unsafe_allow_html=True
        )
        col1, col2 = st.columns(2)
        if col2.button("다음 →", type="primary", use_container_width=True):            
            t_path = save_transcript(v['id'], v['title'], lang)
            if t_path:
                st.success(f"저장 완료 ✔\n→ {t_path}")
            else:
                st.error("저장 실패 또는 자막 없음 😥")
            next_step()
        if col1.button("🔄 다시", use_container_width=True):
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
        <div class="info-box">
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
    if col1.button("← 이전", use_container_width=True):
        prev_step()
    if col2.button("✨ 생성", type="primary", use_container_width=True):
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
            <h3 style="margin-top:0;font-size:16px;">✅ 콘텐츠가 생성되었습니다</h3>
            <p style="margin-bottom:0;font-size:13px;">아래 콘텐츠를 확인하고 복사하여 사용하세요.</p>
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
    
    # 4열로 더 컴팩트하게 배치
    cols = st.columns([1, 1, 1, 1])
    for i, (k, v) in enumerate(summary_data.items()):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div class="summary-card">
                    <div style="color:#666;font-size:12px">{k}</div>
                    <div style="font-weight:600;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{v}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 콘텐츠 영역
    st.markdown("<div class='subheader'>생성된 콘텐츠</div>", unsafe_allow_html=True)
    st.text_area("생성된 콘텐츠", st.session_state.generated_content, height=200, label_visibility="hidden")

    # 복사 버튼
    copy_button(st.session_state.generated_content)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    if col1.button("← 옵션 수정", use_container_width=True):
        prev_step()
    if col2.button("🔄 처음으로", use_container_width=True):
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
