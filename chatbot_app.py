import streamlit as st
from PIL import Image
import openai
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
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")

    openai_api_key = st.text_input("OpenAI API 키를 입력하세요 (선택사항):", type="password", value=st.session_state.openai_api_key)
    if openai_api_key:
        st.session_state.openai_api_key = openai_api_key
        openai.api_key = openai_api_key

# 입력을 처리하는 함수
def process_input(input_content, input_type, criteria, custom_prompt):
    if not st.session_state.openai_api_key:
        return "API 키가 설정되지 않았습니다. 환경 변수나 사이드바에서 API 키를 입력하세요."

    system_message = """
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

    try:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"이 {input_type}를 {criteria}에 맞춰 평가해줘: {input_content[:1000]}..."}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500
        )

        return response['choices'][0]['message']['content']

    except openai.error.OpenAIError as e:
        return f"API 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return f"알 수 없는 오류가 발생했습니다: {str(e)}"

# 메인 함수
def main():
    # 제목과 설명
    st.markdown("<h1 class='main-title'>🤖📚 멀티모달 교육 피드백 챗봇 📝🌟</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='service-summary'>
        이 챗봇은 여러분의 학습 여정을 돕기 위해 만들어졌어요! 📚✨<br>
        여러분이 작성한 텍스트나 그린 그림을 분석해서 꼼꼼한 피드백을 제공해드려요. 💌<br>
        맞춤형 조언으로 여러분의 실력 향상을 응원합니다. 함께 성장해 나가요! 🚀😊
    </div>
    """, unsafe_allow_html=True)

    # 사이드바에 설정 추가
    with st.sidebar:
        st.markdown("<h2 class='sidebar-title'>⚙️ 설정</h2>", unsafe_allow_html=True)
        set_openai_api_key()

        # 평가 기준 입력
        st.markdown("<h2 class='sidebar-title'>📈 평가 기준</h2>", unsafe_allow_html=True)
        criteria = st.text_area("성취기준 또는 평가 기준을 입력하세요:", key="criteria_input")

        # 사용자 정의 프롬프트 사용 여부
        use_custom_prompt = st.checkbox("🎭 사용자 정의 프롬프트 사용")
        custom_prompt = ""
        if use_custom_prompt:
            st.write("프롬프트를 수정해보세요:")
            custom_prompt = st.text_area(
                "사용자 정의 프롬프트:",
                "안녕 선생님~ {content}를 {criteria}에 맞춰 평가해줘! 좋은 점 몇 가지랑 개선할 점 한두 개만 간단히 알려주면 돼. 앞으로 어떻게 공부하면 좋을지도 살짝 힌트 줘! 고마워! 😊",
                help="프롬프트를 자유롭게 수정하세요. {criteria}와 {content}는 자동으로 채워집니다."
            )

    # 화면을 넓게 활용하기 위해 컬럼 폭을 동일하게 설정
    col1, col2 = st.columns([1, 1])

    # 입력 및 피드백 생성 섹션
    with col1:
        st.markdown("<h2 class='section-title'>📥 입력</h2>", unsafe_allow_html=True)

        # 입력 유형 선택
        input_type = st.radio("평가할 입력 유형을 선택하세요", ("텍스트", "이미지"))

        if input_type == "텍스트":
            input_content = st.text_area("텍스트를 입력하세요")
            if st.button("피드백 생성"):
                feedback = process_input(input_content, '텍스트', criteria, custom_prompt if use_custom_prompt else "")
                st.session_state.feedback = feedback

        elif input_type == "이미지":
            uploaded_image = st.file_uploader("이미지를 업로드하세요", type=['png', 'jpg', 'jpeg'])
            if uploaded_image is not None:
                image = Image.open(uploaded_image)
                st.image(image, caption="업로드된 이미지", use_column_width=True)

                # 이미지를 압축 및 리사이즈하여 토큰 수 줄이기
                image.thumbnail((512, 512))
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                if st.button("피드백 생성"):
                    feedback = process_input(image_base64, '이미지', criteria, custom_prompt if use_custom_prompt else "")
                    st.session_state.feedback = feedback

    # 피드백 섹션
    with col2:
        st.markdown("<h2 class='section-title'>💬 피드백</h2>", unsafe_allow_html=True)
        feedback = st.session_state.get('feedback', "아직 생성된 피드백이 없습니다.")
        st.markdown(f"<div class='feedback-box'>{feedback}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
