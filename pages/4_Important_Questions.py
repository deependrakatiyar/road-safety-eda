import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Important Questions - Padhai AI", page_icon="⭐", layout="wide")

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

QUESTION_TYPES = {
    "All Types (Sabhi)":              "Include all types: 1-mark, 2-mark, 3-mark, 5-mark, and essay questions",
    "1 Mark (Objective)":             "Very short answer — definitions, fill in the blanks, true/false",
    "2-3 Mark (Short Answer)":        "Short answer questions requiring 2-4 sentence answers",
    "4-5 Mark (Long Answer)":         "Detailed questions requiring paragraph answers",
    "Essay / Nibandh (6-8 Marks)":    "Long essay type questions for Hindi and language subjects",
    "Numerical / Practical Problems": "Calculation-based and application problems (for Science, Math)",
}

TYPE_INSTRUCTIONS = {
    "All Types (Sabhi)":              "mix 1-mark, 2-3 mark, 4-5 mark questions",
    "1 Mark (Objective)":             "definitions, one-word, fill in blanks, true/false",
    "2-3 Mark (Short Answer)":        "explain/describe/differentiate type",
    "4-5 Mark (Long Answer)":         "detail with diagram, compare/contrast",
    "Essay / Nibandh (6-8 Marks)":    "essay writing, nibandh",
    "Numerical / Practical Problems": "solve/calculate/application problems",
}

IMP_Q_PROMPT = """MP Board {cls} {subject}, topic: {topic}. Language: {medium_lang}.
Generate 12 important exam questions ({q_type}). Focus: {type_instruction}.

Format each as:
**Q[N]. [question]** ([marks] marks) [⭐/⭐⭐/⭐⭐⭐]
💡 Hint: [1-line hint]
---"""

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


def stream_questions(model, cls, subject, topic, q_type, medium):
    medium_lang = "Hindi (Devanagari script)" if medium == "Hindi Medium" else "English"
    prompt = IMP_Q_PROMPT.format(
        cls=cls, subject=subject, topic=topic, q_type=q_type,
        medium_lang=medium_lang, type_instruction=TYPE_INSTRUCTIONS.get(q_type, ""),
    )
    response = model.generate_content(prompt, stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text

# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("# ⭐ Important Questions")
st.markdown("MP Board exam mein aane wale most important questions — hints ke saath!")
st.divider()

with st.sidebar:
    st.markdown("### Question Settings")
    selected_class   = st.selectbox("Class", CLASSES, index=4)
    selected_subject = st.selectbox("Subject", SUBJECTS[selected_class])
    topic            = st.text_input("Chapter / Topic", placeholder="e.g., Electricity, Mughal Empire")
    q_type           = st.selectbox("Question Type", list(QUESTION_TYPES.keys()))
    medium           = st.radio("Medium", ["Hindi Medium", "English Medium"])
    generate_btn     = st.button("⭐ Questions Generate Karo!", use_container_width=True, type="primary")
    st.divider()
    st.markdown(f"**Selected:** {QUESTION_TYPES[q_type]}")
    st.divider()
    st.markdown("**Legend:**")
    st.markdown("⭐ Important")
    st.markdown("⭐⭐ Very Important")
    st.markdown("⭐⭐⭐ Most Important (zaroor padhna!)")

# API check
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    st.warning("⚠️ **GEMINI_API_KEY** set nahi hai.")
    st.info("Free API key lo: https://aistudio.google.com/app/apikey")
    st.code("export GEMINI_API_KEY='your-key-here'", language="bash")
    st.stop()

model = get_model(api_key)

if "iq_content" not in st.session_state: st.session_state.iq_content = ""
if "iq_config"   not in st.session_state: st.session_state.iq_config  = {}

if generate_btn:
    if not topic.strip():
        st.error("Chapter ya topic ka naam likhein!")
    else:
        st.session_state.iq_config  = {"class": selected_class, "subject": selected_subject,
                                        "topic": topic, "type": q_type, "medium": medium}
        st.session_state.iq_content = ""

        col1, col2, col3 = st.columns(3)
        col1.metric("Class", selected_class)
        col2.metric("Subject", selected_subject)
        col3.metric("Type", q_type.split("(")[0].strip())
        st.markdown(f"**Topic:** {topic} | **Medium:** {medium}")
        st.divider()

        placeholder = st.empty()
        full_text   = ""
        with st.spinner("Important questions dhundhe ja rahe hain..."):
            for chunk in stream_questions(model, selected_class, selected_subject, topic, q_type, medium):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        st.session_state.iq_content = full_text

        st.divider()
        col1, col2 = st.columns(2)
        col1.success("✅ Questions ready!")
        col2.download_button("⬇️ Download Questions (.txt)", data=full_text,
                             file_name=f"{selected_class}_{selected_subject}_{topic}_important_questions.txt",
                             mime="text/plain", use_container_width=True)

elif st.session_state.iq_content:
    cfg = st.session_state.iq_config
    col1, col2, col3 = st.columns(3)
    col1.metric("Class", cfg["class"])
    col2.metric("Subject", cfg["subject"])
    col3.metric("Type", cfg["type"].split("(")[0].strip())
    st.markdown(f"**Topic:** {cfg['topic']} | **Medium:** {cfg['medium']}")
    st.divider()
    st.markdown(st.session_state.iq_content)
    st.divider()
    st.download_button("⬇️ Download Questions (.txt)", data=st.session_state.iq_content,
                       file_name=f"{cfg['class']}_{cfg['subject']}_{cfg['topic']}_important_questions.txt",
                       mime="text/plain", use_container_width=True)
else:
    st.info("👈 Left sidebar mein class, subject, topic fill karo aur **Questions Generate Karo** button dabao!")

    st.markdown("### Board Exam Tips / Pariksha Ki Taiyari")
    tips = [
        ("📅", "Timetable Banao", "Har subject ko equal time do. 3-4 ghante regularly padhna better hai badi breaks se."),
        ("📖", "NCERT Pehle Padho", "MP Board mein 80% questions NCERT se aate hain. Pehle NCERT complete karo."),
        ("✍️", "Likhkar Practice Karo", "Sirf padhna kaafi nahi. Exam mein likhna hota hai, isliye practice writing karein."),
        ("🔄", "Revision Zaruri Hai", "Har topic padhne ke baad revision karo. Spaced repetition se yaad zyada rehta hai."),
        ("📝", "Previous Papers Solve Karo", "Pichle 5 saal ke papers solve karo — pattern samjho aur time management seekho."),
        ("😴", "Neend Poori Lo", "Exam se pehle raat achi neend lo. Thaka hua dimag ache se kaam nahi karta."),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(tips):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#e8f5e9; border-radius:12px; padding:16px; margin-bottom:12px; border-left:4px solid #2e7d32;">
                <h4 style="color:#1b5e20; margin:0 0 6px;">{icon} {title}</h4>
                <p style="color:#444; font-size:0.88rem; margin:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### High-Yield Topics by Subject")
    for sub, topics_str in {
        "Class 10 Science":        "Electricity, Life Processes, Carbon & Its Compounds, Heredity & Evolution",
        "Class 10 Social Science": "Nationalism in India, Resources & Development, Money & Credit, Sectors of Indian Economy",
        "Class 10 Mathematics":    "Real Numbers, Triangles, Circles, Quadratic Equations, Arithmetic Progressions",
        "Class 12 Physics":        "Electrostatics, Current Electricity, Optics, Dual Nature of Radiation",
        "Class 12 Chemistry":      "p-Block Elements, Coordination Compounds, Biomolecules, Polymers",
        "Class 12 Biology":        "Genetics, Reproduction, Evolution, Biotechnology",
    }.items():
        st.markdown(f"**{sub}:** {topics_str}")
