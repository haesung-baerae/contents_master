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
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton button {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        color: black;
        width: 100%;
    }
    .stTextInput > div > div > input {
        background-color: #f0f0f0;
    }
    .stSelectbox > div > div > div {
        background-color: #f0f0f0;
    }
    .custom-box {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .header {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .subheader {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

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

# 이전 단계로 이동하는 함수
def go_to_previous_step():
    st.session_state.step -= 1

# 스텝 1: 콘텐츠 마스터 (키워드 입력 및 영상 선택)
def show_step_1():
    st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)
    
    # 주제입력
    st.markdown("<div class='subheader'>주제입력</div>", unsafe_allow_html=True)
    keyword = st.text_input("", key="keyword_input", label_visibility="collapsed")
    
    col_search, _ = st.columns([1, 3])
    with col_search:
        search_button = st.button("콘텐츠 검색", use_container_width=True)
    
    # 검색 버튼 클릭 시 추천 영상 로드
    if search_button and keyword:
        st.session_state.recommended_videos = get_youtube_recommendations(keyword)
    
    # 인기 콘텐츠 TOP3 표시
    if st.session_state.recommended_videos:
        st.markdown("<div class='subheader'>인기 콘텐츠 TOP3</div>", unsafe_allow_html=True)
        st.markdown("원하시는 콘텐츠를 선택해주세요.", unsafe_allow_html=True)
        
        for i, video in enumerate(st.session_state.recommended_videos):
            col_vid, col_btn = st.columns([3, 1])
            with col_vid:
                st.markdown(f"{i+1}.제목: {video['title']}")
                st.markdown(f"[영상 보기]({video['link']})", unsafe_allow_html=True)
            with col_btn:
                if st.button(f"선택", key=f"select_btn_{i}"):
                    st.session_state.selected_video = video
                    st.session_state.confirmed_selection = False
    
    # 선택한 비디오 확인
    if st.session_state.selected_video:
        st.markdown("<div class='subheader'>2.제목</div>", unsafe_allow_html=True)
        st.markdown(f"선택한 콘텐츠로 진행하시겠습니까?", unsafe_allow_html=True)
        st.markdown(f"**선택된 영상:** {st.session_state.selected_video['title']}")
        
        yes_col, no_col = st.columns(2)
        with yes_col:
            if st.button("YES", use_container_width=True):
                go_to_next_step()
        with no_col:
            if st.button("다시 선택", use_container_width=True):
                st.session_state.selected_video = None

# 스텝 2: 콘텐츠 만들기 (스타일, 타겟층 등 설정)
def show_step_2():
    st.markdown("<div class='header'>콘텐츠 만들기</div>", unsafe_allow_html=True)
    st.markdown("원하시는 스타일로 선택해주세요.", unsafe_allow_html=True)
    
    # 선택된 비디오 표시
    st.markdown(f"**선택된 영상:** {st.session_state.selected_video['title']}")
    st.markdown(f"[영상 링크]({st.session_state.selected_video['link']})")
    
    # 타겟층
    st.markdown("<div class='subheader'>타겟층</div>", unsafe_allow_html=True)
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
            
    with col_btn2:
        formal = st.button("정중함", key="formal", 
                          use_container_width=True,
                          type="primary" if st.session_state.tone_style == "정중함" else "secondary")
        if formal:
            st.session_state.tone_style = "정중함"
            
    with col_btn3:
        friendly = st.button("감성", key="friendly", 
                            use_container_width=True,
                            type="primary" if st.session_state.tone_style == "감성" else "secondary")
        if friendly:
            st.session_state.tone_style = "감성"
    
    # 목표
    st.markdown("<div class='subheader'>목표</div>", unsafe_allow_html=True)
    col_goal1, col_goal2, col_goal3 = st.columns(3)
    
    with col_goal1:
        inform = st.button("정보전달", key="inform", 
                          use_container_width=True,
                          type="primary" if st.session_state.goal == "정보전달" else "secondary")
        if inform:
            st.session_state.goal = "정보전달"
            
    with col_goal2:
        persuade = st.button("설득력", key="persuade", 
                            use_container_width=True,
                            type="primary" if st.session_state.goal == "설득력" else "secondary")
        if persuade:
            st.session_state.goal = "설득력"
            
    with col_goal3:
        educate = st.button("구매유도", key="educate", 
                            use_container_width=True,
                            type="primary" if st.session_state.goal == "구매유도" else "secondary")
        if educate:
            st.session_state.goal = "구매유도"
    
    # 글자수
    st.markdown("<div class='subheader'>글자수</div>", unsafe_allow_html=True)
    col_count1, col_count2, col_count3 = st.columns(3)
    
    with col_count1:
        count_500 = st.button("500자내외", key="count_500", 
                             use_container_width=True,
                             type="primary" if st.session_state.word_count == "500자내외" else "secondary")
        if count_500:
            st.session_state.word_count = "500자내외"
            
    with col_count2:
        count_1000 = st.button("1000자내외", key="count_1000", 
                              use_container_width=True,
                              type="primary" if st.session_state.word_count == "1000자내외" else "secondary")
        if count_1000:
            st.session_state.word_count = "1000자내외"
            
    with col_count3:
        count_1500 = st.button("1500자내외", key="count_1500", 
                              use_container_width=True,
                              type="primary" if st.session_state.word_count == "1500자내외" else "secondary")
        if count_1500:
            st.session_state.word_count = "1500자내외"
    
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
    
    # 선택된 비디오 및 설정 요약
    st.markdown("### 선택된 옵션:")
    st.markdown(f"**영상:** {st.session_state.selected_video['title']}")
    st.markdown(f"**타겟층:** {st.session_state.target_audience}")
    st.markdown(f"**톤/스타일:** {st.session_state.tone_style}")
    st.markdown(f"**목표:** {st.session_state.goal}")
    st.markdown(f"**글자수:** {st.session_state.word_count}")
    
    # 생성된 콘텐츠 표시
    st.markdown("### 생성된 콘텐츠:")
    content_area = st.text_area("", value=st.session_state.generated_content, height=300, label_visibility="collapsed")
    
    # 버튼
    back_col, copy_col = st.columns(2)
    
    with back_col:
        if st.button("다시 설정하기", use_container_width=True):
            go_to_previous_step()
            
    with copy_col:
        if st.button("복사하기", use_container_width=True):
            st.success("콘텐츠가 클립보드에 복사되었습니다!")

# 현재 단계에 따라 올바른 화면 표시
if st.session_state.step == 1:
    show_step_1()
elif st.session_state.step == 2:
    show_step_2()
else:
    show_step_3()
