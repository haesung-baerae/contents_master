import streamlit as st
import pandas as pd
from PIL import Image
import base64
import time
import re

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
        padding-top: 15px;  /* 패딩 증가 */
        padding-bottom: 15px;  /* 패딩 증가 */
        background-color: #111;
        color: white;
        border-radius: 5px;
        line-height: 1.5;  /* 줄 간격 추가 */
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

# 클립보드에 복사하는 자바스크립트 함수
def get_clipboard_js(text):
    return f"""
    <script>
    function copyToClipboard() {{
        const text = `{text}`;
        navigator.clipboard.writeText(text)
            .then(() => {{
                console.log('텍스트가 클립보드에 복사되었습니다.');
            }})
            .catch(err => {{
                console.error('클립보드 복사 실패:', err);
            }});
    }}
    </script>
    """

# 유튜브 영상 추천을 위한 모의 함수
def get_youtube_recommendations(keyword):
    # 실제 어플리케이션에서는 YouTube API 호출
    # 이것은 모의 구현입니다
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
    time.sleep(1)  # API 호출 지연 시뮬레이션
    return mock_data

# 비디오 트랜스크립트를 가져오는 모의 함수
def get_video_transcript(video_link):
    # 실제 어플리케이션에서는 실제 트랜스크립트를 가져옵니다
    return f"""이것은 선택된 영상의 스크립트입니다. 실제 구현에서는 YouTube API를 통해 
               실제 트랜스크립트를 가져와야 합니다. 이 텍스트는 임시로 사용되는 예시입니다. 
               선택된 영상 링크: {video_link}"""

# 콘텐츠를 재생성하는 모의 함수
def regenerate_content(video_transcript, target_audience, tone_style, goal, word_count):
    # 실제 어플리케이션에서는 GPT와 같은 AI 서비스를 호출할 수 있습니다
    return f"""재구성된 콘텐츠:
               
               타겟층: {target_audience}
               톤/스타일: {tone_style}
               목표: {goal}
               글자수: {word_count}
               
               원본 트랜스크립트를 기반으로 한 새로운 콘텐츠입니다.
               이 부분은 실제 구현에서 AI 모델을 통해 생성된 콘텐츠로 대체될 것입니다.
               """

# 세션 상태 변수 초기화
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: 콘텐츠 마스터, 2: 콘텐츠 만들기, 3: 콘텐츠 생성완료
    
if 'recommended_videos' not in st.session_state:
    st.session_state.recommended_videos = []
    
if 'selected_video' not in st.session_state:
    st.session_state.selected_video = None
    
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = ""
    
if 'target_audience' not in st.session_state:
    st.session_state.target_audience = ""
    
if 'tone_style' not in st.session_state:
    st.session_state.tone_style = "일반"  # 기본값
    
if 'goal' not in st.session_state:
    st.session_state.goal = "정보전달"  # 기본값
    
if 'word_count' not in st.session_state:
    st.session_state.word_count = "500자내외"  # 기본값

# 다음 단계로 이동하는 함수
def go_to_next_step():
    st.session_state.step += 1
    st.experimental_rerun()  # 상태 변경 후 즉시 페이지 리로드

# 이전 단계로 이동하는 함수
def go_to_previous_step():
    st.session_state.step -= 1
    st.experimental_rerun()  # 상태 변경 후 즉시 페이지 리로드

# 스텝 1: 콘텐츠 마스터 (키워드 입력 및 영상 선택)
def show_step_1():
    st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)
    
    # 주제입력
    st.markdown("<div class='subheader'>주제입력</div>", unsafe_allow_html=True)
    
    # 입력 폼을 적절한 너비로 제한
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            keyword = st.text_input("", key="keyword_input", label_visibility="collapsed")
    
    # 검색 버튼 가운데 정렬
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 3])
        with col2:
            search_button = st.button("콘텐츠 검색", use_container_width=True)
    
    # 검색 버튼 클릭 시 추천 영상 로드
    if search_button and keyword:
        st.session_state.recommended_videos = get_youtube_recommendations(keyword)
        st.experimental_rerun()  # 상태 변경 후 페이지 리로드
    
    # 인기 콘텐츠 TOP3 표시
    if st.session_state.recommended_videos:
        # 결과를 가운데 컨테이너에 표시
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown("<div class='subheader' style='text-align: center;'>인기 콘텐츠 TOP3</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; margin-bottom: 15px;'>원하시는 콘텐츠를 선택해주세요.</div>", unsafe_allow_html=True)
                
                # 비디오 목록을 카드 형식으로 표시
                for i, video in enumerate(st.session_state.recommended_videos):
                    st.markdown(f"""
                    <div style='
                        border: 1px solid #ddd; 
                        border-radius: 5px; 
                        padding: 10px; 
                        margin-bottom: 10px;
                        background-color: #f8f9fa;
                    '>
                        <div style='font-weight: bold;'>{i+1}.제목: {video['title']}</div>
                        <div style='margin: 5px 0;'><a href='{video['link']}' target='_blank'>영상 보기</a></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"선택", key=f"select_btn_{i}", use_container_width=True):
                        st.session_state.selected_video = video
                        st.experimental_rerun()  # 상태 변경 후 페이지 리로드
    
    # 선택한 비디오 확인
    if st.session_state.selected_video:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown("<div class='subheader' style='text-align: center; margin-top: 20px;'>선택 확인</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='
                    text-align: center; 
                    margin: 15px 0; 
                    padding: 15px; 
                    background-color: #f0f7ff; 
                    border-radius: 5px;
                    border: 1px solid #c5d5e5;
                '>
                    선택한 콘텐츠로 진행하시겠습니까?<br><br>
                    <strong>선택된 영상:</strong> {st.session_state.selected_video['title']}
                </div>
                """, unsafe_allow_html=True)
                
                # 버튼을 좀 더 예쁘게 배치
                yes_col, no_col = st.columns(2)
                with yes_col:
                    if st.button("YES", use_container_width=True, type="primary"):
                        go_to_next_step()
                with no_col:
                    if st.button("다시 선택", use_container_width=True):
                        st.session_state.selected_video = None
                        st.experimental_rerun()  # 상태 변경 후 페이지 리로드

# 스텝 2: 콘텐츠 만들기 (스타일, 타겟층 등 설정)
def show_step_2():
    st.markdown("<div class='header'>콘텐츠 만들기</div>", unsafe_allow_html=True)
    
    # 내용을 가운데로 정렬
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("<div style='text-align: center;'>원하시는 스타일로 선택해주세요.</div>", unsafe_allow_html=True)
            
            # 선택된 비디오 표시
            st.markdown(f"<div style='text-align: center; margin: 20px 0;'><strong>선택된 영상:</strong> {st.session_state.selected_video['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'><a href='{st.session_state.selected_video['link']}' target='_blank'>영상 링크</a></div>", unsafe_allow_html=True)
            
            # 타겟층
            st.markdown("<div class='subheader' style='margin-top: 20px;'>타겟층</div>", unsafe_allow_html=True)
            target_audience = st.text_input("", key="target_audience_input", value=st.session_state.target_audience, label_visibility="collapsed")
    st.session_state.target_audience = target_audience
    
    # 톤/스타일
    st.markdown("<div class='subheader'>톤/스타일</div>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        informal = st.button("인풋말씀", key="informal", 
                            use_container_width=True,
                            type="primary" if st.session_state.tone_style == "인풋말씀" else "secondary")
        if informal:
            st.session_state.tone_style = "인풋말씀"
            st.experimental_rerun()  # 상태 변경 후 페이지 리로드
            
    with col_btn2:
        formal = st.button("정중함", key="formal", 
                          use_container_width=True,
                          type="primary" if st.session_state.tone_style == "정중함" else "secondary")
        if formal:
            st.session_state.tone_style = "정중함"
            st.experimental_rerun()  # 상태 변경 후 페이지 리로드
            
    with col_btn3:
        friendly = st.button("감성", key="friendly", 
                            use_container_width=True,
                            type="primary" if st.session_state.tone_style == "감성" else "secondary")
        if friendly:
            st.session_state.tone_style = "감성"
            st.experimental_rerun()  # 상태 변경 후 페이지 리로드
    
    # 목표
    st.markdown("<div class='subheader'>목표</div>", unsafe_allow_html=True)
    col_goal1, col_goal2, col_goal3 = st.columns(3)
    
    with col_goal1:
        inform = st.button("정보전달", key="inform", 
                          use_container_width=True,
                          type="primary" if st.session_state.goal == "정보전달" else "secondary")
        if inform:
            st.session_state.goal = "정보전달"
            st.experimental_rerun()  # 상태 변경 후 페이지 리로드
            
    with col_goal2:
        persuade = st.button("설득력", key="persuade", 
                            use_container_width=True,
                            type="primary" if st.session_state.goal == "설득력" else "secondary")
        if persuade:
            st.session_state.goal = "설득력"
            st.experimental_rerun()  # 상태 변경 후 페이지 리로드
            
    with col_goal3:
        educate = st.button("구매유도", key="educate", 
                            use_container_width=True,
                            type="primary" if st.session_state.goal == "구매유도" else "secondary")
        if educate:
            st.session_state.goal = "구매유도"
            st.experimental_rerun()  # 상태 변경 후 페이지 리로드
    
    # 글자수
    st.markdown("<div class='subheader'>글자수</div>", unsafe_allow_html=True)
    col_count1, col_count2, col_count3 = st.columns(3)
    
    with col_count1:
        count_500 = st.button("500자내외", key="count_500", 
                             use_container_width=True,
                             type="primary" if st.session_state.word_count == "500자내외" else "secondary")
        if count_500:
            st.session_state.word_count = "500자내외"
            st.experimental_rerun()  # 상태 변경 후 페이지 리로드
            
    with col_count2:
        count_1000 = st.button("1000자내외", key="count_1000", 
                              use_container_width=True,
                              type="primary" if st.session_state.word_count == "1000자내외" else "secondary")
        if count_1000:
            st.session_state.word_count = "1000자내외"
            st.experimental_rerun()  # 상태 변경 후 페이지 리로드
            
    with col_count3:
        count_1500 = st.button("1500자내외", key="count_1500", 
                              use_container_width=True,
                              type="primary" if st.session_state.word_count == "1500자내외" else "secondary")
        if count_1500:
            st.session_state.word_count = "1500자내외"
            st.experimental_rerun()  # 상태 변경 후 페이지 리로드
    
    # 네비게이션 버튼
    back_col, generate_col = st.columns(2)
    
    with back_col:
        if st.button("이전으로", use_container_width=True):
            go_to_previous_step()
            
    with generate_col:
        if st.button("콘텐츠만들기", use_container_width=True):
            # 비디오 트랜스크립트 가져오기
            video_transcript = get_video_transcript(st.session_state.selected_video['link'])
            # 콘텐츠 생성
            st.session_state.generated_content = regenerate_content(
                video_transcript, 
                st.session_state.target_audience,
                st.session_state.tone_style,
                st.session_state.goal, 
                st.session_state.word_count
            )
            go_to_next_step()

# 스텝 3: 콘텐츠 생성완료 (결과 표시)
def show_step_3():
    st.markdown("<div class='header'>콘텐츠 생성완료</div>", unsafe_allow_html=True)
    
    # 내용을 가운데 정렬
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # 선택된 비디오 및 설정 요약
            st.markdown("<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>선택된 옵션</h4>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>영상:</strong> {st.session_state.selected_video['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>타겟층:</strong> {st.session_state.target_audience}</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>톤/스타일:</strong> {st.session_state.tone_style}</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>목표:</strong> {st.session_state.goal}</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>글자수:</strong> {st.session_state.word_count}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 생성된 콘텐츠 표시
            st.markdown("<h4 style='text-align: center; margin: 20px 0;'>생성된 콘텐츠</h4>", unsafe_allow_html=True)
            content_area = st.text_area("", value=st.session_state.generated_content, height=300, label_visibility="collapsed")
            
            # 자바스크립트로 클립보드 복사 기능 추가
            copy_js = get_clipboard_js(st.session_state.generated_content.replace('"', '\\"').replace('\n', '\\n'))
            st.markdown(copy_js, unsafe_allow_html=True)
            
            # 버튼 - 중앙 정렬 및 여백 추가
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            back_col, copy_col = st.columns(2)
            
            with back_col:
                if st.button("다시 설정하기", use_container_width=True):
                    go_to_previous_step()
                    
            with copy_col:
                # 자바스크립트 함수를 호출하는 버튼
                st.markdown(
                    f"""<button
                        style="width: 100%; padding: 0.5rem; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;"
                        onclick="copyToClipboard()">
                        복사하기
                    </button>""",
                    unsafe_allow_html=True
                )
                # 복사 성공 메시지를 표시하기 위한 빈 공간
                st.empty()

# 현재 단계에 따라 올바른 화면 표시
if st.session_state.step == 1:
    show_step_1()
elif st.session_state.step == 2:
    show_step_2()
else:
    show_step_3()
