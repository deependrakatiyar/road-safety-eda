import streamlit as st
import anthropic
import os
import json
import re

st.set_page_config(page_title="Quiz Practice - Padhai AI", page_icon="❓", layout="wide")

# ── Data ─────────────────────────────────────────────────────────────────────

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

QUIZ_PROMPT = """You are an expert MP Board (Madhya Pradesh Board) exam question setter for school students.

Generate exactly {num_questions} multiple choice questions (MCQs) for:
- Class: {cls}
- Subject: {subject}
- Topic/Chapter: {topic}
- Difficulty: {difficulty}
- Medium: {medium}

Rules:
1. Questions must be based on MP Board curriculum and NCERT textbook syllabus
2. Each question must have exactly 4 options (A, B, C, D)
3. Only one option should be correct
4. If medium is Hindi, write questions and options in Hindi (Devanagari). If English, write in English.
5. Difficulty levels: Easy = direct fact-based, Medium = application-based, Hard = analytical/conceptual
6. Include questions from different parts of the topic

Return ONLY a valid JSON array — no markdown, no explanation, just the JSON:
[
  {{
    "question": "Question text here?",
    "options": {{"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"}},
    "correct": "A",
    "explanation": "Brief explanation of why this is correct (1-2 lines)"
  }}
]"""

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def generate_quiz(client, cls, subject, topic, num_q, difficulty, medium) -> list:
    prompt = QUIZ_PROMPT.format(
        num_questions=num_q, cls=cls, subject=subject,
        topic=topic, difficulty=difficulty, medium=medium
    )
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    # Extract JSON from response
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(raw)


def score_color(score, total):
    pct = score / total * 100
    if pct >= 80:
        return "green"
    elif pct >= 50:
        return "orange"
    return "red"

# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("# ❓ Quiz Practice")
st.markdown("MP Board pattern mein MCQ practice karo aur apni taiyari check karo!")
st.divider()

# Sidebar config
with st.sidebar:
    st.markdown("### Quiz Settings")
    selected_class   = st.selectbox("Class", CLASSES, index=4)
    selected_subject = st.selectbox("Subject", SUBJECTS[selected_class])
    topic            = st.text_input("Topic / Chapter", placeholder="e.g., Electricity, Mughal Empire")
    num_questions    = st.slider("Number of Questions", 3, 15, 5)
    difficulty       = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")
    medium           = st.radio("Medium", ["Hindi Medium", "English Medium"])
    generate_btn     = st.button("🎯 Quiz Generate Karo!", use_container_width=True, type="primary")

# API check
api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    st.warning("⚠️ **ANTHROPIC_API_KEY** set nahi hai. Please API key add karein.")
    st.code("export ANTHROPIC_API_KEY='your-key-here'", language="bash")
    st.stop()

client = get_client()

# Initialize state
if "quiz_questions"  not in st.session_state: st.session_state.quiz_questions  = []
if "quiz_answers"    not in st.session_state: st.session_state.quiz_answers    = {}
if "quiz_submitted"  not in st.session_state: st.session_state.quiz_submitted  = False
if "quiz_config"     not in st.session_state: st.session_state.quiz_config     = {}

# Generate quiz
if generate_btn:
    if not topic.strip():
        st.error("Please topic ya chapter ka naam likhein!")
    else:
        with st.spinner(f"Quiz generate ho raha hai... {selected_class} | {selected_subject} | {topic}"):
            try:
                questions = generate_quiz(client, selected_class, selected_subject, topic, num_questions, difficulty, medium)
                st.session_state.quiz_questions = questions
                st.session_state.quiz_answers   = {}
                st.session_state.quiz_submitted  = False
                st.session_state.quiz_config     = {
                    "class": selected_class, "subject": selected_subject,
                    "topic": topic, "difficulty": difficulty, "medium": medium
                }
                st.rerun()
            except Exception as e:
                st.error(f"Quiz generate karne mein problem: {e}")

# Display quiz
if st.session_state.quiz_questions:
    cfg = st.session_state.quiz_config
    st.markdown(f"### {cfg['class']} | {cfg['subject']} | {cfg['topic']} | {cfg['difficulty']}")
    st.markdown(f"**{len(st.session_state.quiz_questions)} Questions** | {cfg['medium']}")
    st.divider()

    if not st.session_state.quiz_submitted:
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i+1}.** {q['question']}")
                options = q["options"]
                choice = st.radio(
                    f"Q{i+1}",
                    options=[f"{k}. {v}" for k, v in options.items()],
                    key=f"q_{i}",
                    label_visibility="collapsed"
                )
                st.session_state.quiz_answers[i] = choice[0] if choice else None
                st.markdown("---")

            submitted = st.form_submit_button("✅ Submit Quiz", use_container_width=True, type="primary")
            if submitted:
                if len([v for v in st.session_state.quiz_answers.values() if v]) < len(st.session_state.quiz_questions):
                    st.error("Sabhi questions ke jawab do!")
                else:
                    st.session_state.quiz_submitted = True
                    st.rerun()

    else:
        # Show results
        questions = st.session_state.quiz_questions
        answers   = st.session_state.quiz_answers
        score     = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["correct"])
        total     = len(questions)
        pct       = int(score / total * 100)
        color     = score_color(score, total)

        # Score card
        st.markdown(f"""
        <div style="background:{'#e8f5e9' if color=='green' else '#fff3e0' if color=='orange' else '#ffebee'};
                    border-radius:16px; padding:24px; text-align:center; border:2px solid {color};">
            <h2 style="color:{color}; margin:0;">Score: {score}/{total} ({pct}%)</h2>
            <p style="margin:8px 0 0;">{'Bahut badhiya! Excellent!' if pct>=80 else 'Accha kiya! Keep it up!' if pct>=50 else 'Aur mehnat karo! You can do it!'}</p>
        </div>
        """, unsafe_allow_html=True)

        st.progress(score / total)
        st.divider()

        # Detailed review
        st.markdown("### Detailed Review / Jawab Dekho")
        for i, q in enumerate(questions):
            user_ans    = answers.get(i)
            correct_ans = q["correct"]
            is_correct  = user_ans == correct_ans

            icon = "✅" if is_correct else "❌"
            bg   = "#e8f5e9" if is_correct else "#ffebee"

            st.markdown(f"""
            <div style="background:{bg}; border-radius:10px; padding:14px; margin-bottom:12px;">
                <strong>{icon} Q{i+1}.</strong> {q['question']}<br>
                <span style="color:{'green' if is_correct else 'red'};">
                    Aapka jawab: <strong>{user_ans}. {q['options'].get(user_ans,'')}</strong>
                </span><br>
                <span style="color:green;">Sahi jawab: <strong>{correct_ans}. {q['options'][correct_ans]}</strong></span><br>
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
            st.session_state.quiz_submitted  = False
            st.session_state.quiz_answers    = {}
            st.rerun()

else:
    # Empty state
    st.info("👈 Left sidebar mein class, subject aur topic fill karo, phir **Quiz Generate Karo** button dabao!")
    st.markdown("""
    **Topics ka example:**
    - Mathematics: *Quadratic Equations, Triangles, Statistics*
    - Science: *Electricity, Life Processes, Carbon Compounds*
    - History: *Mughal Empire, Nationalism in India, World War II*
    - Geography: *Resources, Climate of India, Natural Vegetation*
    - Hindi: *Kabir ke Dohe, Samas, Sandhi*
    """)
