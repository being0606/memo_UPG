import streamlit as st
import openai
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'chat_count' not in st.session_state:
    st.session_state.chat_count = 0  # 핑퐁 횟수 관리
if 'max_chats' not in st.session_state:
    st.session_state.max_chats = 4  # 최대 4번의 대화
if 'total_chars' not in st.session_state:
    st.session_state.total_chars = 0  # 총 글자수 카운트

# 글자수 피드백 함수
def char_count_feedback(message):
    return f"{len(message)}/100자"

# 응답에서 {} 안의 내용을 추출하는 파서 함수
def extract_tasks_from_response(response_text):
    try:
        last_open_brace = response_text.rfind('{')
        last_close_brace = response_text.rfind('}')
        if last_open_brace != -1 and last_close_brace != -1 and last_close_brace > last_open_brace:
            tasks_str = response_text[last_open_brace+1:last_close_brace]
            tasks = tasks_str.strip().split(',')
            tasks = [task.strip() for task in tasks if task.strip()]
            return tasks
        else:
            return []
    except Exception as e:
        st.error(f"할 일을 추출하는 중 오류 발생: {e}")
        return []

# OpenAI API 호출하여 할 일 추출
def parse_task_from_chat(messages):
    # 프롬프트 구성
    prompt = (
        "You are an assistant that extracts tasks from a conversation.\n"
        "Include the things I need to do now inside the {}.\n"
        'For your final answer, say "Therefore, the things I need to do are {}."'
        "\n\nConversation:\n"
    )
    # 대화 내역 추가
    for msg in messages:
        prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
    prompt += "Assistant:"

    response = openai.Completion.create(
        engine="text-davinci-003",  # 사용 가능한 모델로 변경 가능
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
        stop=None
    )
    return response.choices[0].text.strip()

# 채팅 입력 단계 함수
def task_input_step():
    st.header("📝 할 일 입력 (채팅 기반)")
    st.write("최대 4번까지 대화를 통해 해야 할 일을 작성하세요. 각 메시지는 **100자 제한**이 있습니다.")

    # 채팅 내역 표시
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.write(f"**사용자:** {msg['content']}")
        else:
            st.write(f"**어시스턴트:** {msg['content']}")

    # 채팅 입력
    if st.session_state.chat_count < st.session_state.max_chats:
        with st.form(key='chat_form'):
            user_input = st.text_area(
                "메시지를 입력하세요:",
                value='',  # 입력 필드 초기화
                max_chars=100,
                height=50
            )
            st.write(char_count_feedback(user_input))
            submit_button = st.form_submit_button("보내기")

        if submit_button:
            if len(user_input) <= 100:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.chat_count += 1
                st.session_state.total_chars += len(user_input)
                st.experimental_rerun()  # 입력 후 화면 갱신하여 입력 필드 초기화
            else:
                st.error("100자 이상 입력할 수 없습니다.")
    else:
        st.warning("더 이상 메시지를 보낼 수 없습니다. 최대 4번까지 가능합니다.")

    # OpenAI API 호출 및 할 일 추출
    if st.session_state.chat_count == st.session_state.max_chats and not st.session_state.tasks:
        with st.spinner("할 일을 추출하는 중..."):
            response_text = parse_task_from_chat(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            extracted_tasks = extract_tasks_from_response(response_text)
            st.session_state.tasks = extracted_tasks
            if extracted_tasks:
                st.success("할 일이 성공적으로 추출되었습니다!")
            else:
                st.error("할 일을 추출하지 못했습니다. 다시 시도해주세요.")

    # 추출된 할 일 표시
    if st.session_state.tasks:
        st.write("### 추출된 할 일 목록:")
        for task in st.session_state.tasks:
            st.write(f"- {task}")

# 메인 함수
def main():
    task_input_step()

if __name__ == "__main__":
    main()