import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import os
from dotenv import load_dotenv

# 로컬 실행 시만 dotenv 불러오기
if os.getenv("IS_STREAMLIT_CLOUD") != "true":
    from dotenv import load_dotenv
    load_dotenv()

YOUTUBE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.write("🔑 API Key Loaded:", bool(YOUTUBE_API_KEY and OPENAI_API_KEY))
