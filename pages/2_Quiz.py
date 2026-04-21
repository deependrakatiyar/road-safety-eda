import streamlit as st
import os
import json
import re
from utils import MODEL, get_client, require_api_key, show_api_error, ensure_registered, log_usage

st.set_page_config(page_title="Quiz Practice - Padhai AI", page_icon="❓", layout="wide")

CLASSES = ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12"]
SUBJECTS = {
    "Class 6":  ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit"],
    "Class 7":  ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit"],
    "Class 8":  ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit"],
    "Class 9":  ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit", "Computer Science"],
    "Class 10": ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit", "Computer Science"],
    "Class 11": ["Hindi", "English", "Physics", "Chemistry", "Mathematics", "Biology", "History", "Geography", "Political Science", "Economics", "Business Studies", "Accountancy", "Computer Science"],
    "Class 12": ["Hindi", "English", "Physics", "Chemistry", "Mathematics", "Biology", "History", "Geography", "Political Science", "Economics", "Business Studies", "Accountancy", "Computer Science"],
}

QUIZ_PROMPT = """Generate {num_questions} MCQs for MP Board {cls} {subject}, topic: {topic}.
Difficulty: {difficulty}. Language: {medium} (Hindi = Devanagari script).

Return ONLY valid JSON: {{"questions":[{{"question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"correct":"A","explanation":"1-line reason"}}]}}"""

def generate_quiz(cls, subject, topic, num_q, difficulty, medium) -> list:
    prompt = QUIZ_PROMPT.format(
        num_questions=num_q, cls=cls, subject=subject,
        topic=topic, difficulty=difficulty, medium=medium,
    )
    response = get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)
    return data.get("questions", data) if isinstance(data, dict) else data

def score_color(score, total):
    pct = score / total * 100
    if pct >= 80: return "green"
    if pct >= 50: return "orange"
    return "red"

# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("# ❓ Quiz Practice")
st.markdown("MP Board pattern mein MCQ practice karo!")
st.divider()

with st.sidebar:
    st.markdown("### Quiz Settings")
    selected_class   = st.selectbox("Class", CLASSES, index=4)
    selected_subject = st.selectbox("Subject", SUBJECTS[selected_class])
    topic            = st.text_input("Topic / Chapter", placeholder="e.g., Electricity, Mughal Empire")
    num_questions    = st.slider("Number of Questions", 3, 15, 5)
    difficulty       = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")
    medium           = st.radio("Medium", ["Hindi Medium", "English Medium"])
    generate_btn     = st.button("🎯 Quiz Generate Karo!", use_container_width=True, type="primary")

if not require_api_key():
    st.stop()
if not ensure_registered():
    st.stop()

if "quiz_questions" not in st.session_state: st.session_state.quiz_questions = []
if "quiz_answers"   not in st.session_state: st.session_state.quiz_answers   = {}
if "quiz_submitted" not in st.session_state: st.session_state.quiz_submitted = False
if "quiz_config"    not in st.session_state: st.session_state.quiz_config    = {}

if generate_btn:
    if not topic.strip():
        st.error("Please topic ya chapter ka naam likhein!")
    else:
        with st.spinner(f"Quiz generate ho raha hai... {selected_class} | {selected_subject} | {topic}"):
            try:
                questions = generate_quiz(selected_class, selected_subject, topic, num_questions, difficulty, medium)
                st.session_state.quiz_questions = questions
                st.session_state.quiz_answers   = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_config    = {"class": selected_class, "subject": selected_subject,
                                                    "topic": topic, "difficulty": difficulty, "medium": medium}
                log_usage("Quiz", selected_subject, topic)
                st.rerun()
            except Exception as e:
                show_api_error(e)

if st.session_state.quiz_questions:
    cfg = st.session_state.quiz_config
    st.markdown(f"### {cfg['class']} | {cfg['subject']} | {cfg['topic']} | {cfg['difficulty']}")
    st.markdown(f"**{len(st.session_state.quiz_questions)} Questions** | {cfg['medium']}")
    st.divider()

    if not st.session_state.quiz_submitted:
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i+1}.** {q['question']}")
                choice = st.radio(f"Q{i+1}", options=[f"{k}. {v}" for k, v in q["options"].items()],
                                  key=f"q_{i}", label_visibility="collapsed")
                st.session_state.quiz_answers[i] = choice[0] if choice else None
                st.markdown("---")
            if st.form_submit_button("✅ Submit Quiz", use_container_width=True, type="primary"):
                if len([v for v in st.session_state.quiz_answers.values() if v]) < len(st.session_state.quiz_questions):
                    st.error("Sabhi questions ke jawab do!")
                else:
                    st.session_state.quiz_submitted = True
                    st.rerun()
    else:
        questions = st.session_state.quiz_questions
        answers   = st.session_state.quiz_answers
        score     = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["correct"])
        total     = len(questions)
        pct       = int(score / total * 100)
        color     = score_color(score, total)

        st.markdown(f"""
        <div style="background:{'#e8f5e9' if color=='green' else '#fff3e0' if color=='orange' else '#ffebee'};
                    border-radius:16px; padding:24px; text-align:center; border:2px solid {color};">
            <h2 style="color:{color}; margin:0;">Score: {score}/{total} ({pct}%)</h2>
            <p style="margin:8px 0 0;">{'Bahut badhiya! Excellent!' if pct>=80 else 'Accha kiya! Keep it up!' if pct>=50 else 'Aur mehnat karo! You can do it!'}</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(score / total)
        st.divider()
        st.markdown("### Detailed Review")
        for i, q in enumerate(questions):
            user_ans    = answers.get(i)
            correct_ans = q["correct"]
            is_correct  = user_ans == correct_ans
            bg = "#e8f5e9" if is_correct else "#ffebee"
            st.markdown(f"""
            <div style="background:{bg}; border-radius:10px; padding:14px; margin-bottom:12px;">
                <strong>{'✅' if is_correct else '❌'} Q{i+1}.</strong> {q['question']}<br>
                <span style="color:{'green' if is_correct else 'red'};">Aapka: <strong>{user_ans}. {q['options'].get(user_ans,'')}</strong></span><br>
                <span style="color:green;">Sahi: <strong>{correct_ans}. {q['options'][correct_ans]}</strong></span><br>
                <span style="color:#555; font-size:0.9rem;">💡 {q.get('explanation','')}</span>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        if col1.button("🔄 Dobara Quiz Do", use_container_width=True):
            st.session_state.quiz_submitted = False
            st.session_state.quiz_answers   = {}
            st.rerun()
        if col2.button("🆕 Naya Quiz Banao", use_container_width=True):
            st.session_state.quiz_questions = []
            st.session_state.quiz_submitted = False
            st.session_state.quiz_answers   = {}
            st.rerun()
else:
    st.info("👈 Left sidebar mein class, subject aur topic fill karo, phir **Quiz Generate Karo** button dabao!")
    st.markdown("""
    **Topics ka example:**
    - Mathematics: *Quadratic Equations, Triangles, Statistics*
    - Science: *Electricity, Life Processes, Carbon Compounds*
    - History: *Mughal Empire, Nationalism in India*
    - Hindi: *Kabir ke Dohe, Samas, Sandhi*
    """)
