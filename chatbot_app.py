import base64
from io import BytesIO
import os
from dotenv import load_dotenv, find_dotenv
from dotenv import load_dotenv

# Streamlit 페이지 설정
st.set_page_config(page_title="멀티모달 교육 피드백 챗봇", layout="wide")
# .env 파일 로드 (현재 디렉토리에 있는 파일을 명시적으로 로드)
load_dotenv(dotenv_path='.env')

# .env 파일 로드 시도
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    st.sidebar.success(f".env 파일을 찾았습니다: {dotenv_path}")
else:
    st.sidebar.warning(".env 파일을 찾을 수 없습니다.")
# Streamlit 페이지 설정 (화면을 더 넓게 활용하기 위해 'wide' 레이아웃 적용)
st.set_page_config(page_title="멀티모달 교육 피드백 챗봇", layout="wide")

# CSS 스타일
# CSS 스타일 - 화면을 넓게 활용하기 위한 설정
css = """
.main-title {
    font-size: 2.5em;
@@ -71,38 +66,24 @@

# API 키 설정 함수
def set_openai_api_key():
    # 다양한 방법으로 API 키 로드 시도
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    
    if api_key:
        openai.api_key = api_key
        st.sidebar.success("API 키를 환경 변수 또는 Streamlit Secrets에서 성공적으로 로드했습니다.")
    else:
        st.sidebar.warning("환경 변수 또는 Streamlit Secrets에서 API 키를 찾을 수 없습니다.")
    
    # 현재 환경 변수 상태 출력 (디버깅용)
    st.sidebar.write("현재 환경 변수:")
    for key, value in os.environ.items():
        if key == "OPENAI_API_KEY":
            st.sidebar.write(f"{key}: {'*' * len(value)}")  # API 키는 가려서 표시
        elif "API" in key.upper() or "KEY" in key.upper():
            st.sidebar.write(f"{key}: {value}")
    
    # 사용자 입력 받기 (선택사항)
    user_api_key = st.sidebar.text_input("OpenAI API 키를 직접 입력하세요 (선택사항):", type="password")
    
    if user_api_key:
        openai.api_key = user_api_key
        st.sidebar.success("사용자가 입력한 API 키가 설정되었습니다.")
    # API 키 설정 확인
    if not openai.api_key:
        st.sidebar.error("API 키가 설정되지 않았습니다. 환경 변수를 확인하거나 직접 입력해주세요.")
    
    return openai.api_key is not None
    if "openai_api_key" not in st.session_state:
        # 환경 변수에서 API 키를 가져옴
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")
    # 만약 환경 변수에 API 키가 없을 경우에만 사용자 입력 받기
    if not st.session_state.openai_api_key:
        openai_api_key = st.text_input("OpenAI API 키를 입력하세요 (선택사항):", type="password")
        if openai_api_key:
            st.session_state.openai_api_key = openai_api_key
    if st.session_state.openai_api_key:
        openai.api_key = st.session_state.openai_api_key

# 입력을 처리하는 함수
def process_input(input_content, input_type, criteria, custom_prompt):
    if not openai.api_key:
        return "API 키가 설정되지 않았습니다. 환경 변수나 사이드바에서 API 키를 입력하세요."
    system_message = """
    넌 학생들에게 친절하고 간결한 피드백을 주는 선생님이야. 다음 지침을 따라줘:
@@ -121,7 +102,7 @@ def process_input(input_content, input_type, criteria, custom_prompt):
        # 텍스트와 이미지 모두 gpt-4를 사용하여 처리
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"이 {input_type}를 {criteria}에 맞춰 평가해줘: {input_content}"}
            {"role": "user", "content": f"이 {input_type}를 {criteria}에 맞춰 평가해줘: {input_content[:1000]}..."}  # 메시지 길이 제한
        ]

        response = openai.ChatCompletion.create(
@@ -130,7 +111,7 @@ def process_input(input_content, input_type, criteria, custom_prompt):
            max_tokens=500  # 응답 토큰 수 설정
        )

        return response.choices[0].message['content']
        return response['choices'][0]['message']['content']

    except openai.error.OpenAIError as e:
        return f"처리 중 오류가 발생했습니다: {str(e)}"
@@ -139,6 +120,7 @@ def process_input(input_content, input_type, criteria, custom_prompt):

# 메인 함수
def main():
    # 제목과 설명
    st.markdown("<h1 class='main-title'>🤖📚 멀티모달 교육 피드백 챗봇 📝🌟</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='service-summary'>
@@ -148,10 +130,10 @@ def main():
    </div>
    """, unsafe_allow_html=True)

    # 사이드바 설정
    # 사이드바에 설정 추가
    with st.sidebar:
        st.markdown("<h2 class='sidebar-title'>⚙️ 설정</h2>", unsafe_allow_html=True)
        api_key_set = set_openai_api_key()
        set_openai_api_key()

        # 평가 기준 입력
        st.markdown("<h2 class='sidebar-title'>📈 평가 기준</h2>", unsafe_allow_html=True)
@@ -168,45 +150,49 @@ def main():
                help="프롬프트를 자유롭게 수정하세요. {criteria}와 {content}는 자동으로 채워집니다."
            )

    # 메인 콘텐츠
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
                if api_key_set:
                if st.session_state.openai_api_key:
                    feedback = process_input(input_content, '텍스트', criteria, custom_prompt if use_custom_prompt else "")
                    st.session_state['feedback'] = feedback
                else:
                    st.error("API 키가 설정되지 않았습니다. 사이드바에서 API 키 설정을 확인해주세요.")
                    feedback = "API 키가 설정되지 않았습니다. 환경 변수나 사이드바에서 API 키를 입력하세요."
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
                    if api_key_set:
                    if st.session_state.openai_api_key:
                        feedback = process_input(image_base64, '이미지', criteria, custom_prompt if use_custom_prompt else "")
                        st.session_state['feedback'] = feedback
                    else:
                        st.error("API 키가 설정되지 않았습니다. 사이드바에서 API 키 설정을 확인해주세요.")
                        feedback = "API 키가 설정되지 않았습니다. 환경 변수나 사이드바에서 API 키를 입력하세요."
                    st.session_state.feedback = feedback

    # 피드백 섹션
    with col2:
        st.markdown("<h2 class='section-title'>💬 피드백</h2>", unsafe_allow_html=True)
        if 'feedback' in st.session_state:
            st.markdown(f"<div class='feedback-box'>{st.session_state['feedback']}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='feedback-box'>피드백이 여기에 표시됩니다.</div>", unsafe_allow_html=True)
        feedback = st.session_state.get('feedback', "아직 생성된 피드백이 없습니다.")
        st.markdown(f"<div class='feedback-box'>{feedback}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
