import streamlit as st
import time
import random
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 폰트 설정 (필요 시 제거하거나 수정)
plt.rcParams['font.family'] = 'AppleGothic'

# 세션 상태 초기화
if 'step' not in st.session_state:
    st.session_state.step = 0  # 로딩 페이지를 0단계로 설정
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'evaluated_tasks' not in st.session_state:
    st.session_state.evaluated_tasks = []
if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = []
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'reset' not in st.session_state:
    st.session_state.reset = False
if 'sliders_moved' not in st.session_state:
    st.session_state.sliders_moved = [False] * 4
if 'loading_complete' not in st.session_state:
    st.session_state.loading_complete = False  # 로딩 완료 여부

def reset_app():
    st.session_state.step = 0  # 로딩 페이지로 돌아감
    st.session_state.tasks = []
    st.session_state.evaluated_tasks = []
    st.session_state.completed_tasks = []
    st.session_state.xp = 0
    st.session_state.reset = True
    st.session_state.sliders_moved = [False] * 4
    st.session_state.loading_complete = False

def loading_page():
    st.header("환영합니다! 잠시만 기다려주세요...")
    
    positive_messages = [
        "오늘의 기록은 나를 더 성장시켜요",
        "어제보다 더 나은 오늘",
        "작은 노력들이 큰 변화를 만듭니다",
        "지금 이 순간이 가장 소중해요",
        "포기하지 마세요, 당신은 할 수 있어요",
        "한 걸음씩 앞으로 나아가요",
        "긍정적인 생각은 긍정적인 결과를 가져옵니다",
        "당신의 노력이 빛을 발할 거예요",
        "꿈을 향해 달려가세요",
        "매일매일 새로운 시작입니다"
    ]
    
    progress_bar = st.progress(0)
    message_placeholder = st.empty()
    
    for i in range(101):
        time.sleep(0.03)  # 로딩 속도 조절 가능
        progress_bar.progress(i)
        if i % 20 == 0:
            message = random.choice(positive_messages)
            message_placeholder.write(f"**{message}**")
    st.success("업그레이드 시작!")
    time.sleep(1)
    st.session_state.loading_complete = True
    st.session_state.step += 1  # 다음 단계로 이동
    # st.experimental_rerun()
    st.rerun()

def task_input_step():
    st.header("📝 할 일 입력")
    st.write("해야 할 일 4가지를 입력해주세요. 각 할 일은 **200자 이내**로 작성해주세요.")

    total_tasks = 4
    entered_tasks = sum(1 for i in range(1, 5) if isinstance(st.session_state.get(f'task_{i}', ''), str) and st.session_state.get(f'task_{i}', '').strip() != '')
    sub_progress = entered_tasks / total_tasks
    st.progress(sub_progress)

    with st.form(key='task_form'):
        tasks = []
        for i in range(1, 5):
            default_value = ''
            if st.session_state.reset:
                default_value = ''
            else:
                default_value = st.session_state.get(f'task_{i}', '')

            task = st.text_input(f"할 일 {i}", value=default_value, key=f'task_{i}')
            tasks.append(task)
        submitted = st.form_submit_button("제출")

    if submitted:
        st.session_state.tasks = []
        for i, task in enumerate(tasks, start=1):
            task = task.strip()
            if task:
                if len(task) > 200:
                    st.warning(f"할 일 {i}은(는) 200자 이내로 입력해주세요.")
                    return
                else:
                    st.session_state.tasks.append(task)
            else:
                st.warning(f"할 일 {i}을(를) 입력해주세요.")
                return
        st.session_state.step += 1
        st.session_state.reset = False

def eisenhower_step():
    st.header("📝 아이젠하워 매트릭스 평가")
    st.write("각 할 일에 대해 중요도와 긴급도를 실수 값으로 평가해주세요.")

    total_tasks = len(st.session_state.tasks)
    evaluated_count = len(st.session_state.evaluated_tasks)

    # 각 슬라이더의 현재 값을 저장할 리스트
    current_values = []

    st.write("### 아이젠하워 매트릭스 시각화")
    fig, ax = plt.subplots()
    ax.set_xlabel("긴급도")
    ax.set_ylabel("중요도")
    ax.set_title("아이젠하워 매트릭스")
    ax.grid(True)

    # 축을 (0, 0)으로 설정하고, 각 점들을 사분면으로 배치
    ax.axvline(x=0, color='gray', linestyle='--')  # 수직 축(긴급도 기준)
    ax.axhline(y=0, color='gray', linestyle='--')  # 수평 축(중요도 기준)
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)

    # 평가된 할 일들 시각화 (중심을 0, 0으로 변경)
    for idx, (task, urgency_score, importance_score) in enumerate(st.session_state.evaluated_tasks):
        ax.scatter(urgency_score, importance_score, s=100)
        ax.text(urgency_score + 0.1, importance_score, f'할 일 {idx+1}', fontsize=9)

    # 실시간 시각화 업데이트를 위해 선택한 슬라이더 값도 바로 시각화
    if evaluated_count < total_tasks:
        idx = evaluated_count
        task = st.session_state.tasks[idx]
        st.write(f"**할 일 {idx+1}:** {task}")

        # 슬라이더로 중요도와 긴급도를 -2.0에서 2.0까지 실수 값으로 선택
        importance_score = st.slider(
            "중요도를 선택하세요",
            min_value=-2.0,
            max_value=2.0,
            value=0.0,  # 기본값
            step=0.1,   # 실수 값 반영
            key=f"importance_{idx}"
        )

        urgency_score = st.slider(
            "긴급도를 선택하세요",
            min_value=-2.0,
            max_value=2.0,
            value=0.0,  # 기본값
            step=0.1,   # 실수 값 반영
            key=f"urgency_{idx}"
        )

        # 슬라이더 값이 변경될 때마다 그래프에 실시간으로 반영
        ax.scatter(urgency_score, importance_score, s=150, color='red')
        ax.text(urgency_score + 0.1, importance_score, f'현재 위치', fontsize=9, color='red')

    # 그래프 출력
    st.pyplot(fig)

    # "이전 평가로"와 "다음 평가로" 버튼 처리
    col1, spacer_between, col2 = st.columns([1, 3.5, 1])

    # "이전 평가로" 버튼 비활성화 조건 (첫 번째 평가 시 비활성화)
    if evaluated_count == 0:
        col1.button("이전 평가로", disabled=True)
    else:
        if col1.button("이전 평가로"):
            st.session_state.evaluated_tasks.pop()
            st.session_state.sliders_moved[idx] = False
            # st.experimental_rerun()
            st.rerun()

    # "다음 평가로" 버튼 비활성화 조건 (마지막 평가 시 비활성화)
    if evaluated_count >= total_tasks:
        col2.button("다음 평가로", disabled=True)
    else:
        if col2.button("다음 평가로", key=f"next_evaluation_{idx}"):
            st.session_state.evaluated_tasks.append((task, urgency_score, importance_score))
            st.session_state.sliders_moved[idx] = True
            # st.experimental_rerun()
            st.rerun()

    # 평가가 완료되기 전까지 버튼 비활성화
    if evaluated_count < total_tasks:
        col1.button("다시 평가하기", disabled=True)
        col2.button("평가 완료", disabled=True)
    else:
        # 평가가 완료된 경우 버튼 활성화
        if col1.button("다시 평가하기"):
            st.session_state.step = 2 
            # st.experimental_rerun()
            st.rerun()

        if col2.button("평가 완료"):
            st.session_state.step += 1

def todo_step():
    st.header("✅ 투두리스트")
    st.write("우선순위에 따라 정렬된 투두리스트입니다.")

    # 카테고리별로 경험치와 풍선 설정 (우선순위에 따라 차등 지급)
    xp_by_category = {
        "1순위: 중요하고 긴급": 40,
        "2순위: 긴급": 30,
        "3순위: 중요": 20,
        "4순위: 중요하지 않고 긴급하지 않음": 10
    }
    balloons_by_category = {
        "1순위: 중요하고 긴급": 150,  # 최상위 우선순위에서 더 많은 풍선을 지급
        "2순위: 긴급": 100,
        "3순위: 중요": 70,
        "4순위: 중요하지 않고 긴급하지 않음": 50
    }

    # 카테고리별 할 일 분류
    categories = {
        "1순위: 중요하고 긴급": [],
        "2순위: 긴급": [],
        "3순위: 중요": [],
        "4순위: 중요하지 않고 긴급하지 않음": []
    }

    # 세션 상태 초기화
    if 'balloons_collected' not in st.session_state:
        st.session_state.balloons_collected = {}
    if 'collectable_xp' not in st.session_state:
        st.session_state.collectable_xp = 0
    if 'effect_used' not in st.session_state:
        st.session_state.effect_used = False
    if 'total_balloons' not in st.session_state:
        st.session_state.total_balloons = 0  # 누적 풍선 수
    if 'max_balloons' not in st.session_state:
        st.session_state.max_balloons = 0  # 최대 풍선 수

    # 각 카테고리로 할 일 분류
    for idx, (task, urgency, importance) in enumerate(st.session_state.evaluated_tasks):
        task_key = f"task_{idx}"
        completed = st.session_state.get(task_key, False)

        # 할 일을 카테고리로 분류
        if importance > 0 and urgency > 0:
            categories["1순위: 중요하고 긴급"].append((task_key, task, completed))
        elif urgency > 0 and importance <= 0:
            categories["2순위: 긴급"].append((task_key, task, completed))
        elif importance > 0 and urgency <= 0:
            categories["3순위: 중요"].append((task_key, task, completed))
        else:
            categories["4순위: 중요하지 않고 긴급하지 않음"].append((task_key, task, completed))

    # 카테고리별로 최대 풍선 수 계산 (전체 미션 완료 시 얻을 수 있는 최대 풍선 수)
    st.session_state.max_balloons = sum([balloons_by_category[category] * len(tasks) for category, tasks in categories.items()])

    # 카테고리별로 투두리스트 출력
    all_tasks_completed = True  # 모든 미션 완료 여부 체크
    for category, tasks in categories.items():
        if tasks:  # 카테고리가 공란이 아닐 경우에만 출력
            st.write(f"### {category}")
            for task_key, task, completed in tasks:
                checkbox = st.checkbox(f"{task}", key=task_key)
                if not checkbox:
                    all_tasks_completed = False  # 모든 할 일이 완료되지 않음

                if checkbox and not completed:
                    st.session_state.completed_tasks.append(task)
                    st.session_state.xp += xp_by_category.get(category, 0)
                    st.success(f"{category} 완료! 경험치 +{xp_by_category.get(category, 0)}")
                    st.session_state[task_key] = True
                elif not checkbox and completed:
                    if task in st.session_state.completed_tasks:
                        st.session_state.completed_tasks.remove(task)
                        st.warning(f"'{task}'가 다시 활성화되었습니다.")
                        st.session_state.xp -= xp_by_category.get(category, 0)
                    st.session_state[task_key] = False

                # 풍선 차등 지급 및 누적 풍선 개수 표시
                if checkbox and not st.session_state.balloons_collected.get(task_key, False):
                    balloons = balloons_by_category.get(category, 50)  # 기본값 50
                    if st.button(f"🎈 {task} - 풍선 {balloons}개 쌓기", key=f"collect_{task_key}"):
                        st.session_state.collectable_xp += balloons
                        st.session_state.balloons_collected[task_key] = True
                        st.session_state.total_balloons += balloons  # 누적 풍선 개수 업데이트
                        st.success(f"풍선 {balloons}개를 모았습니다! 현재까지 모은 풍선: {st.session_state.total_balloons}개")
                elif checkbox and st.session_state.balloons_collected.get(task_key, False):
                    st.write(f"🎈 {task} - 풍선 {balloons_by_category.get(category, 50)}개 모음 완료 (현재까지 모은 풍선: {st.session_state.total_balloons}개)")

    # 게이지 바로 누적 풍선 수 표시 (붉은색 게이지)
    st.write(f"현재까지 모은 풍선: **{st.session_state.total_balloons}개**")
    st.progress(min(st.session_state.total_balloons / st.session_state.max_balloons, 1.0))  # 동적으로 계산된 최대 풍선 기준으로 게이지 바 표시

    # 모든 미션이 완료되었을 때만 경험치 획득 버튼을 활성화
    if all_tasks_completed and not st.session_state.effect_used:
        if st.button("🎉 풍선 얻기"):
            st.balloons()
            st.session_state.effect_used = True  # 이펙트는 한 번만 실행
            st.session_state.xp += st.session_state.collectable_xp  # 추가 경험치 획득
            st.session_state.collectable_xp = 0  # 획득 가능 경험치 초기화
            st.success(f"풍선 경험치 {st.session_state.xp}점을 획득했습니다!")
            st.session_state.total_balloons = 0  # 풍선 게이지 리셋

            # 상단 프로그레스바를 가득 채우기
            st.session_state.step = 3  # 단계 값 3으로 설정
            st.progress(1.0)  # 상단 프로그레스바 가득 채우기

    # 현재 경험치 표시
    st.write(f"현재 경험치: **{st.session_state.xp} XP**")

    # 경험치에 따른 보상 예시
    if st.session_state.xp >= 200:
        st.balloons()
        st.success("축하합니다! '시간 관리 마스터' 뱃지를 획득하셨습니다.")

    # 초기화 버튼
    st.button("초기화", on_click=reset_app)
    
def main():
    total_steps = 3  # 로딩 페이지는 제외
    current_step = st.session_state.step

    if current_step == 0:
        loading_page()
    else:
        overall_progress = (current_step - 1) / total_steps
        st.progress(overall_progress)

        if st.session_state.step == 1:
            task_input_step()
        elif st.session_state.step == 2:
            eisenhower_step()
        elif st.session_state.step == 3:
            todo_step()

if __name__ == "__main__":
    main()