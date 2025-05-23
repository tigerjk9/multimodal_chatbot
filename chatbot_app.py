import streamlit as st
from PIL import Image
from openai import OpenAI
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
    background-color: #F9F9F9; /* Slight change for better visibility */
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
    if openai_api_key_input: # Update if user provides a new key
        st.session_state.openai_api_key = openai_api_key_input
    
    if not st.session_state.openai_api_key:
        st.warning("OpenAI API 키가 필요합니다. 입력하거나 환경 변수로 설정해주세요.")


# 입력을 처리하는 함수
def process_input(input_content, input_type, criteria, custom_prompt_text, use_custom_prompt_flag):
    # Check if API key is set
    if not st.session_state.get("openai_api_key"):
        st.error("API 키가 설정되지 않았습니다. 사이드바에서 API 키를 입력하세요.")
        return "API 키가 설정되지 않았습니다. 사이드바에서 API 키를 입력하세요."

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=st.session_state.openai_api_key)
    except Exception as e:
        st.error(f"OpenAI 클라이언트 초기화 중 오류 발생: {str(e)}")
        return f"OpenAI 클라이언트 초기화 오류: {str(e)}"

    # Default system message
    system_message_content = """
    당신은 학생들에게 친절하고 상세한 피드백을 제공하는 교육용 AI 챗봇입니다. 다음 지침을 따라 응답해주세요:
    1.  항상 긍정적인 부분으로 시작합니다. (예: "정말 좋은 시도예요! 🌟")
    2.  제시된 평가 기준에 따라 구체적으로 어떤 점이 잘 되었는지 언급합니다. 📝
    3.  개선할 부분을 명확하지만 부드럽게 지적합니다. 🔍
    4.  개선 방법에 대한 실질적이고 간단한 제안을 1-2가지 합니다. 🚶‍♂️
    5.  앞으로의 학습 방향에 대한 짧은 조언을 덧붙입니다. 🚀
    6.  격려의 말과 함께 이모티콘을 사용하여 친근하게 마무리합니다. 💪😊
    7.  모든 답변은 한국어로, 친구에게 말하듯 친절하고 간결하게 작성해주세요.
    """
    
    messages = [{"role": "system", "content": system_message_content}]
    # Using gpt-4o as it's generally strong for multimodal and text tasks.
    model_to_use = "gpt-4o" 

    try:
        # Construct user message based on input type and custom prompt usage
        if input_type == "텍스트":
            # Truncate text input if it's too long to avoid excessive token usage
            content_for_prompt = input_content[:4000] 

            if use_custom_prompt_flag and custom_prompt_text:
                # Fill placeholders in the custom prompt.
                try:
                    user_message_text = custom_prompt_text.format(content=content_for_prompt, criteria=criteria)
                except KeyError: 
                    # If custom prompt has different/missing placeholders, use it as is and append info
                    user_message_text = custom_prompt_text
                    if "{content}" not in custom_prompt_text and content_for_prompt:
                        user_message_text += f"\n\n[입력 내용]\n{content_for_prompt}"
                    if "{criteria}" not in custom_prompt_text and criteria:
                        user_message_text += f"\n\n[평가 기준]\n{criteria}"
            else:
                # Default prompt for text input
                user_message_text = f"다음 텍스트를 '{criteria}' 기준에 맞춰 평가하고 피드백을 제공해줘:\n\n[입력 내용]\n{content_for_prompt}"
            
            messages.append({"role": "user", "content": user_message_text})

        elif input_type == "이미지":
            # input_content here is the base64 encoded image string
            image_prompt_text_parts = []

            if use_custom_prompt_flag and custom_prompt_text:
                try:
                    # For images, {content} usually refers to the image itself.
                    # We format {criteria} into the text part of the prompt.
                    formatted_prompt = custom_prompt_text.format(criteria=criteria, content="[첨부된 이미지]")
                    image_prompt_text_parts.append({"type": "text", "text": formatted_prompt})
                except KeyError:
                    image_prompt_text_parts.append({"type": "text", "text": custom_prompt_text})
                    if "{criteria}" not in custom_prompt_text and criteria:
                         image_prompt_text_parts.append({"type": "text", "text": f"\n\n[평가 기준]\n{criteria}"})
            else:
                # Default prompt for image input
                image_prompt_text_parts.append({"type": "text", "text": f"이 이미지를 '{criteria}' 기준에 맞춰 평가하고 피드백을 제공해줘."})

            # Add the image URL part
            image_prompt_text_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{input_content}", # input_content is base64
                    "detail": "auto" # "low", "high", or "auto" for image detail
                }
            })
            messages.append({"role": "user", "content": image_prompt_text_parts})
        
        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            max_tokens=1200 # Increased max_tokens for potentially detailed feedback
        )
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류 발생: {str(e)}")
        return f"OpenAI API 오류가 발생했습니다: {str(e)}"

# 메인 함수
def main():
    st.markdown("<h1 class='main-title'>🤖📚 멀티모달 교육 피드백 챗봇 📝🌟</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='service-summary'>
        이 챗봇은 여러분의 학습 여정을 돕기 위해 만들어졌어요! 📚✨<br>
        여러분이 작성한 텍스트나 그림(이미지)을 분석해서 꼼꼼한 피드백을 제공해드려요. 💌<br>
        맞춤형 조언으로 여러분의 실력 향상을 응원합니다. 함께 성장해 나가요! �😊
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for settings
    with st.sidebar:
        st.markdown("<h2 class='sidebar-title'>⚙️ 설정</h2>", unsafe_allow_html=True)
        set_openai_api_key() # API Key input

        st.markdown("<h2 class='sidebar-title'>📈 평가 기준</h2>", unsafe_allow_html=True)
        criteria = st.text_area(
            "성취기준 또는 평가 기준을 입력하세요 (예: 내용의 명확성, 그림의 창의성):", 
            key="criteria_input", 
            height=100
        )

        # Option to use a custom prompt
        use_custom_prompt = st.checkbox("🎭 사용자 정의 프롬프트 사용", key="use_custom_prompt_checkbox")
        custom_prompt_template = "" # Initialize
        default_custom_prompt = "안녕 선생님! 다음 {content}를 '{criteria}' 기준으로 평가해줘. 좋은 점, 개선할 점, 그리고 앞으로 어떻게 하면 좋을지 간단히 조언해주면 좋겠어. 고마워! 😊"
        
        if use_custom_prompt:
            st.write("아래 프롬프트 템플릿을 수정하여 AI의 응답 스타일을 조절할 수 있습니다. `{content}`와 `{criteria}`는 자동으로 채워집니다.")
            custom_prompt_template = st.text_area(
                "사용자 정의 프롬프트 템플릿:",
                value=default_custom_prompt, # Default template
                help="프롬프트를 자유롭게 수정하세요. {content}는 입력 내용(텍스트 또는 이미지 설명)으로, {criteria}는 평가 기준으로 대체됩니다.",
                height=150,
                key="custom_prompt_template_area"
            )

    # Main layout with two columns
    col1, col2 = st.columns([1, 1]) 

    with col1: # Input section
        st.markdown("<h2 class='section-title'>📥 입력</h2>", unsafe_allow_html=True)
        input_type = st.radio(
            "평가할 입력 유형을 선택하세요:", 
            ("텍스트", "이미지"), 
            key="input_type_radio"
        )

        input_content_value = "" # To store text or base64 image
        proceed_to_feedback = False # Flag to control when to call process_input

        if input_type == "텍스트":
            text_input = st.text_area("여기에 텍스트를 입력하세요:", height=200, key="text_input_area")
            if st.button("피드백 생성", key="text_feedback_button"):
                if not text_input.strip():
                    st.warning("피드백을 생성하려면 텍스트를 입력해주세요.")
                elif not criteria.strip():
                    st.warning("피드백을 생성하려면 평가 기준을 입력해주세요.")
                elif not st.session_state.get("openai_api_key"): # Check API key again before proceeding
                    st.error("OpenAI API 키를 먼저 설정해주세요.")
                else:
                    input_content_value = text_input
                    proceed_to_feedback = True
        
        elif input_type == "이미지":
            uploaded_image = st.file_uploader(
                "이미지 파일을 업로드하세요 (PNG, JPG, JPEG):", 
                type=['png', 'jpg', 'jpeg'], 
                key="image_uploader"
            )
            if uploaded_image is not None:
                try:
                    image = Image.open(uploaded_image)
                    st.image(image, caption="업로드된 이미지", use_column_width=True)

                    # Compress and resize image to reduce token usage and processing time
                    image.thumbnail((1024, 1024)) # Max size 1024x1024
                    buffered = BytesIO()
                    # Convert to PNG for consistent base64 encoding
                    image_format = "PNG" 
                    if image.mode == 'RGBA' and image_format == 'JPEG': # JPEG doesn't support alpha
                        image = image.convert('RGB')
                    image.save(buffered, format=image_format)
                    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    
                    if st.button("피드백 생성", key="image_feedback_button"):
                        if not criteria.strip():
                            st.warning("피드백을 생성하려면 평가 기준을 입력해주세요.")
                        elif not st.session_state.get("openai_api_key"): # Check API key
                            st.error("OpenAI API 키를 먼저 설정해주세요.")
                        else:
                            input_content_value = image_base64
                            proceed_to_feedback = True
                except Exception as e:
                    st.error(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")
        
        # If all checks pass and button is clicked, process input
        if proceed_to_feedback:
            with st.spinner("AI가 피드백을 생성 중입니다... 잠시만 기다려주세요 ✨"):
                feedback_result = process_input(
                    input_content_value, 
                    input_type, 
                    criteria, 
                    custom_prompt_template, 
                    use_custom_prompt
                )
                st.session_state.feedback = feedback_result # Store feedback in session state


    with col2: # Feedback display section
        st.markdown("<h2 class='section-title'>💬 AI 피드백</h2>", unsafe_allow_html=True)
        # Get feedback from session state, or show a default message
        feedback_display = st.session_state.get('feedback', "아직 생성된 피드백이 없습니다. 왼쪽에서 내용을 입력하고 '피드백 생성' 버튼을 눌러주세요.")
        st.markdown(f"<div class='feedback-box'>{feedback_display}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
�
