import streamlit as st
import pandas as pd
from PIL import Image
import base64
import time
import re

# Set page configuration
st.set_page_config(
    page_title="콘텐츠 마스터",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add custom CSS to make the UI more like the mockup
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

# Mocked function to get YouTube video recommendations
def get_youtube_recommendations(keyword):
    # In a real application, this would call YouTube API
    # This is just a mock implementation
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
    time.sleep(1)  # Simulate API call delay
    return mock_data

# Mocked function to get video transcript
def get_video_transcript(video_link):
    # In a real application, this would get the actual transcript
    return f"""이것은 선택된 영상의 스크립트입니다. 실제 구현에서는 YouTube API를 통해 
               실제 트랜스크립트를 가져와야 합니다. 이 텍스트는 임시로 사용되는 예시입니다. 
               선택된 영상 링크: {video_link}"""

# Mocked function to regenerate content
def regenerate_content(video_transcript, target_audience, tone_style, goal, word_count):
    # In a real application, this might call an AI service like GPT
    return f"""재구성된 콘텐츠:
               
               타겟층: {target_audience}
               톤/스타일: {tone_style}
               목표: {goal}
               글자수: {word_count}
               
               원본 트랜스크립트를 기반으로 한 새로운 콘텐츠입니다.
               이 부분은 실제 구현에서 AI 모델을 통해 생성된 콘텐츠로 대체될 것입니다.
               """

# Function to create three columns with equal width
def create_three_panels():
    col1, col2, col3 = st.columns(3)
    return col1, col2, col3

# Initialize session state variables if they don't exist
if 'recommended_videos' not in st.session_state:
    st.session_state.recommended_videos = []
    
if 'selected_video' not in st.session_state:
    st.session_state.selected_video = None
    
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = ""

# Create the three main panels
col1, col2, col3 = create_three_panels()

# Panel 1: 콘텐츠 마스터 (Content Master)
with col1:
    st.markdown("<div class='header'>콘텐츠 마스터</div>", unsafe_allow_html=True)
    
    # 주제입력 (Enter topic/keyword)
    st.markdown("<div class='subheader'>주제입력</div>", unsafe_allow_html=True)
    keyword = st.text_input("", key="keyword_input", label_visibility="collapsed")
    
    # 인기 콘텐츠 TOP3 (Popular content TOP3)
    st.markdown("<div class='subheader'>인기 콘텐츠 TOP3</div>", unsafe_allow_html=True)
    st.markdown("원하시는 콘텐츠를 선택해주세요.", unsafe_allow_html=True)
    
    # Display recommendations if available
    if st.session_state.recommended_videos:
        for i, video in enumerate(st.session_state.recommended_videos):
            col_vid, col_btn = st.columns([3, 1])
            with col_vid:
                st.markdown(f"{i+1}.제목: {video['title']}")
                st.markdown(f"[영상 보기]({video['link']})", unsafe_allow_html=True)
            with col_btn:
                if st.button(f"선택", key=f"select_btn_{i}"):
                    st.session_state.selected_video = video
    
    # Button to get recommendations
    if st.button("콘텐츠 검색"):
        if keyword:
            st.session_state.recommended_videos = get_youtube_recommendations(keyword)
    
    # Display selected video confirmation
    if st.session_state.selected_video:
        st.markdown("<div class='subheader'>2.제목</div>", unsafe_allow_html=True)
        st.markdown(f"선택한 콘텐츠로 진행하시겠습니까?", unsafe_allow_html=True)
        if st.button("YES"):
            st.success("선택 완료! 오른쪽 패널에서 설정을 진행해주세요.")

# Panel 2: 콘텐츠 만들기 (Content Creation)
with col2:
    st.markdown("<div class='header'>콘텐츠 만들기</div>", unsafe_allow_html=True)
    st.markdown("원하시는 스타일로 선택해주세요.", unsafe_allow_html=True)
    
    # 타겟층 (Target Audience)
    st.markdown("<div class='subheader'>타겟층</div>", unsafe_allow_html=True)
    target_audience = st.text_input("", key="target_audience", label_visibility="collapsed")
    
    # 톤/스타일 (Tone/Style)
    st.markdown("<div class='subheader'>톤/스타일</div>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        informal = st.button("인풋말씀", key="informal")
    with col_btn2:
        formal = st.button("정중함", key="formal")
    with col_btn3:
        friendly = st.button("감성", key="friendly")
        
    tone_style = "일반" # Default value
    if informal:
        tone_style = "인풋말씀"
    elif formal:
        tone_style = "정중함"
    elif friendly:
        tone_style = "감성"
    
    # 목표 (Goal)
    st.markdown("<div class='subheader'>목표</div>", unsafe_allow_html=True)
    col_goal1, col_goal2, col_goal3 = st.columns(3)
    
    with col_goal1:
        inform = st.button("정보전달", key="inform")
    with col_goal2:
        persuade = st.button("설득력", key="persuade")
    with col_goal3:
        educate = st.button("구매유도", key="educate")
        
    goal = "정보전달" # Default value
    if inform:
        goal = "정보전달"
    elif persuade:
        goal = "설득력"
    elif educate:
        goal = "구매유도"
    
    # 글자수 (Word Count)
    st.markdown("<div class='subheader'>글자수</div>", unsafe_allow_html=True)
    col_count1, col_count2, col_count3 = st.columns(3)
    
    with col_count1:
        count_500 = st.button("500자내외", key="count_500")
    with col_count2:
        count_1000 = st.button("1000자내외", key="count_1000")
    with col_count3:
        count_1500 = st.button("1500자내외", key="count_1500")
        
    word_count = "500자내외" # Default value
    if count_500:
        word_count = "500자내외"
    elif count_1000:
        word_count = "1000자내외"
    elif count_1500:
        word_count = "1500자내외"
    
    # Generate Content button
    if st.button("콘텐츠만들기"):
        if st.session_state.selected_video:
            video_transcript = get_video_transcript(st.session_state.selected_video['link'])
            st.session_state.generated_content = regenerate_content(
                video_transcript, target_audience, tone_style, goal, word_count
            )
            st.success("콘텐츠가 생성되었습니다!")
        else:
            st.error("먼저 왼쪽 패널에서 영상을 선택해주세요!")

# Panel 3: 콘텐츠 생성완료 (Content Preview)
with col3:
    st.markdown("<div class='header'>콘텐츠 생성완료</div>", unsafe_allow_html=True)
    
    content_box = st.empty()
    if st.session_state.generated_content:
        content_box.text_area("", value=st.session_state.generated_content, height=400, label_visibility="collapsed")
    else:
        content_box.markdown("""
        <div style="
            border: 1px solid #ddd; 
            height: 400px; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            background-color: #f0f0f0;
        ">
            <p style="color: #888;">생성된 콘텐츠가 여기에 표시됩니다</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Copy to clipboard button (Note: This doesn't actually work in Streamlit for security reasons, but shows the UI)
    if st.button("복사하기"):
        if st.session_state.generated_content:
            st.success("콘텐츠가 클립보드에 복사되었습니다!")
        else:
            st.error("복사할 콘텐츠가 없습니다!")
