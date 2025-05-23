import streamlit as st
from PIL import Image
from openai import OpenAI # Corrected import
import base64
from io import BytesIO
import os

# Streamlit 페이지 설정
st.set_page_config(page_title="멀티모달 교육 피드백 챗봇", layout="wide")

# CSS 스타일
css = """
.main-title {
    font-size: 2.5em;
    color: #4A4A4A;
    text-align: center;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.service-summary {
    background-color: #F0F8FF;
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    text-align: center;
    font-size: 1.1em;
    line-height: 1.6;
}
.section-title {
    font-size: 1.8em;
    color: #2C3E50;
    margin-top: 20px;
    margin-bottom: 10px;
}
.sidebar-title {
    font-size: 1.5em;
    color: #34495E;
    margin-bottom: 15px;
}
.feedback-box {
    background-color: #F0F8FF;
    border-left: 5px solid #3498DB;
    padding: 15px;
    border-radius: 5px;
    margin-top: 20px;
    overflow-wrap: break-word;
    word-wrap: break-word;
    white-space: pre-wrap; /* Ensure newlines in feedback are rendered */
}
.prompt-example {
    background-color: #E8F5E9;
    border: 1px solid #81C784;
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
    font-style: italic;
}
"""

# CSS 적용
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# API 키 설정 함수
def set_openai_api_key():
    # Ensure session state for API key is initialized
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")

    # Get API key from user input
    openai_api_key_input = st.text_input(
        "OpenAI API 키를 입력하세요 (필수사항):", 
        type="password", 
        value=st.session_state.openai_api_key,
        key="api_key_input_widget" # Added a unique key
    )
    if openai_api_key_input:
        st.session_state.openai_api_key = openai_api_key_input

# 입력을 처리하는 함수
def process_input(input_content, input_type, criteria, custom_prompt_text, use_custom_prompt_flag):
    # Check if API key is set
    if not st.session_state.get("openai_api_key"): # More robust check
        return "API 키가 설정되지 않았습니다. 환경 변수나 사이드바에서 API 키를 입력하세요."

    # Initialize OpenAI client
    client = OpenAI(api_key=st.session_state.openai_api_key)

    # Default system message
    system_message_content = """
    넌 학생들에게 친절하고 간결한 피드백을 주는 선생님이야. 다음 지침을 따라줘:

    1. 긍정적으로 시작해 🌟
    2. 기준에 따라 구체적인 피드백을 줘 📝
    3. 개선점을 친절하게 말해줘 🔍
    4. 개선 방법을 간단히 제안해 🚶‍♂️
    5. 앞으로의 학습에 대한 짧은 조언도 주면 좋아 🚀
    6. 격려의 말로 마무리해 💪
    7. 이모티콘을 적절히 써서 친근감을 줘 😊

    답변은 한국어로 해줘. 그리고 되도록 짧고 간결하게, 친구에게 말하듯이 해줘!
    """
    
    messages = [{"role": "system", "content": system_message_content}]
    model_to_use = "gpt-4" # Default model

    # Construct user message based on input type and custom prompt usage
    if input_type == "텍스트":
        user_content_m
