import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Study Notes - Padhai AI", page_icon="📝", layout="wide")

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

NOTE_TYPES = {
    "Summary Notes (Saar)":      "Concise chapter summary with key points",
    "Detailed Notes (Vistrit)":  "Comprehensive notes with explanations, examples, and diagrams description",
    "Formula Sheet (Sutre)":     "All formulas, definitions, and key terms",
    "Revision Notes (Revision)": "Quick revision bullet points — perfect for last-minute prep",
    "Mind Map (Diagram Style)":  "Topic breakdown in hierarchical structure",
}

TYPE_INSTRUCTIONS = {
    "Summary Notes (Saar)":      "concise 300-400 word summary of all major concepts",
    "Detailed Notes (Vistrit)":  "comprehensive notes with explanations, examples, sub-topics (600-800 words)",
    "Formula Sheet (Sutre)":     "only formulas, definitions, key terms — use tables where helpful",
    "Revision Notes (Revision)": "bullet-point revision notes, 1-line each, exam-focused",
    "Mind Map (Diagram Style)":  "hierarchical text mind map using indentation",
}

NOTES_PROMPT = """MP Board {cls} {subject} — create {note_type} for topic: {topic}.
Instructions: {type_instruction}. Language: {medium_lang}.
Use ## headings, **bold** key terms, ``` for formulas. End with 'Yaad Rakho' (5 key points)."""

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


def stream_notes(model, cls, subject, topic, note_type, medium):
    medium_lang = "Hindi (Devanagari script)" if medium == "Hindi Medium" else "English"
    prompt = NOTES_PROMPT.format(
        cls=cls, subject=subject, topic=topic,
        note_type=note_type, medium_lang=medium_lang,
        type_instruction=TYPE_INSTRUCTIONS.get(note_type, ""),
    )
    response = model.generate_content(prompt, stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text

# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("# 📝 Study Notes Generator")
st.markdown("Kisi bhi chapter ke AI-powered notes instant banao — board exam ke liye!")
st.divider()

with st.sidebar:
    st.markdown("### Notes Settings")
    selected_class   = st.selectbox("Class", CLASSES, index=4)
    selected_subject = st.selectbox("Subject", SUBJECTS[selected_class])
    topic            = st.text_input("Chapter / Topic", placeholder="e.g., Electricity, French Revolution")
    note_type        = st.selectbox("Notes ka Type", list(NOTE_TYPES.keys()))
    medium           = st.radio("Medium", ["Hindi Medium", "English Medium"])
    generate_btn     = st.button("📝 Notes Banao!", use_container_width=True, type="primary")
    st.divider()
    st.markdown(f"**Selected type:** {NOTE_TYPES[note_type]}")

# API check
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    st.warning("⚠️ **GEMINI_API_KEY** set nahi hai.")
    st.info("Free API key lo: https://aistudio.google.com/app/apikey")
    st.code("export GEMINI_API_KEY='your-key-here'", language="bash")
    st.stop()

model = get_model(api_key)

if "notes_content" not in st.session_state: st.session_state.notes_content = ""
if "notes_config"  not in st.session_state: st.session_state.notes_config  = {}

if generate_btn:
    if not topic.strip():
        st.error("Chapter ya topic ka naam likhein!")
    else:
        st.session_state.notes_config  = {"class": selected_class, "subject": selected_subject,
                                           "topic": topic, "type": note_type, "medium": medium}
        st.session_state.notes_content = ""

        st.markdown(f"### {selected_class} | {selected_subject} | {topic}")
        st.markdown(f"**{note_type}** | {medium}")
        st.divider()

        placeholder = st.empty()
        full_text   = ""
        with st.spinner("Notes generate ho rahi hain..."):
            for chunk in stream_notes(model, selected_class, selected_subject, topic, note_type, medium):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        st.session_state.notes_content = full_text

        st.divider()
        st.success("✅ Notes ready!")
        st.download_button("⬇️ Notes Download Karo (.txt)", data=full_text,
                           file_name=f"{selected_class}_{selected_subject}_{topic}_notes.txt",
                           mime="text/plain", use_container_width=True)

elif st.session_state.notes_content:
    cfg = st.session_state.notes_config
    st.markdown(f"### {cfg['class']} | {cfg['subject']} | {cfg['topic']}")
    st.markdown(f"**{cfg['type']}** | {cfg['medium']}")
    st.divider()
    st.markdown(st.session_state.notes_content)
    st.divider()
    st.download_button("⬇️ Notes Download Karo (.txt)", data=st.session_state.notes_content,
                       file_name=f"{cfg['class']}_{cfg['subject']}_{cfg['topic']}_notes.txt",
                       mime="text/plain", use_container_width=True)
else:
    st.info("👈 Left sidebar mein class, subject, topic aur notes type choose karo, phir **Notes Banao** dabao!")

    st.markdown("### Notes ke Types / Types of Notes")
    cols = st.columns(2)
    for i, (name, desc) in enumerate(NOTE_TYPES.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#f3e5f5; border-radius:10px; padding:14px; margin-bottom:12px; border-left:4px solid #7b1fa2;">
                <strong>{name}</strong><br>
                <span style="color:#555; font-size:0.9rem;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Example Topics")
    for sub, topics in {
        "Class 10 Science":        ["Light - Reflection and Refraction", "Carbon and its Compounds", "Life Processes"],
        "Class 10 Social Science": ["Nationalism in India", "Resources and Development", "Money and Credit"],
        "Class 12 Physics":        ["Electric Charges and Fields", "Ray Optics", "Semiconductor Electronics"],
        "Class 12 Chemistry":      ["p-Block Elements", "Coordination Compounds", "Biomolecules"],
        "Class 9 Mathematics":     ["Number Systems", "Triangles", "Statistics"],
    }.items():
        st.markdown(f"**{sub}:** {' | '.join(topics)}")
