from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import time

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 플래시 메시지용 시크릿 키

# 질문 리스트 (칭찬 - 감정상태 - 오늘할일)
questions = [
    "당신의 장점을 하나 말해보세요.",
    "오늘 기분이 어떠신가요?",
    "요즘 어떤 감정이 가장 자주 드시나요?",
    "오늘 하루 중 가장 기뻤던 순간은 언제인가요?",
    "무엇이 가장 큰 스트레스를 주나요?",
    "오늘 하셔야 할 일이 무엇인가요?",
    "오늘 목표를 이루기 위해 어떻게 노력하셨나요?",
    "내일을 위해 미리 준비하고 싶은 일이 있나요?",
    "누군가에게 감사한 일이 있나요?",
    "오늘 하루를 한 마디로 표현한다면 무엇인가요?"
]

# 루트 경로 (로딩 페이지 표시)
@app.route('/')
def loading():
    return render_template('loading.html')

@app.route('/main')
def main():
    return render_template('main.html')

# 대화 시작 페이지 (챗봇)
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'question_index' not in session:
        session['question_index'] = 0
        session['gauge'] = 0
        session['experience'] = 0  # 경험치 초기화

    question_index = session['question_index']
    gauge = session['gauge']
    experience = session['experience']

    if request.method == 'POST':
        user_response = request.form.get('response')
        if user_response:
            session['gauge'] += 10  # 게이지 10% 증가
            session['experience'] += 5  # 경험치 5점 증가
            session['question_index'] += 1
            question_index = session['question_index']

            if session['question_index'] >= len(questions):
                flash('모든 질문이 완료되었습니다. 요약하기 버튼을 누르세요.')
                return redirect(url_for('chat_summary'))

    if question_index < len(questions):
        current_question = questions[question_index]
    else:
        current_question = "질문이 모두 완료되었습니다."

    return render_template('chat.html', question=current_question, gauge=gauge, experience=experience)

# 요약 페이지 (현재는 고정된 내용 표시)
@app.route('/chat_summary')
def chat_summary():
    todo_list = ["운동하기", "독서 30분", "명상 10분"]  # 고정된 투두리스트
    summary = "오늘 하루 동안 기분을 살펴보고 할 일을 계획하는 시간이었습니다."  # 고정된 요약
    return render_template('summary.html', summary=summary, todo_list=todo_list)

if __name__ == '__main__':
    app.run(debug=True)