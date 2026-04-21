import streamlit as st
import os
from utils import MODEL, get_client, require_api_key, show_api_error, ensure_registered, log_usage

st.set_page_config(page_title="AI Tutor - Padhai AI", page_icon="🤖", layout="wide")

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

SYSTEM_PROMPT = """You are Padhai AI, an MP Board tutor (Class 6-12).
- Answer in Hindi if student writes in Hindi, else English.
- Step-by-step explanations; bold key terms and formulas.
- Keep answers concise but complete. End with one follow-up question."""

MAX_HISTORY = 6

def stream_response(messages: list):
    trimmed = messages[-MAX_HISTORY:]
    groq_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in trimmed:
        role = "user" if m["role"] == "user" else "assistant"
        groq_msgs.append({"role": role, "content": m["content"]})
    stream = get_client().chat.completions.create(
        model=MODEL, messages=groq_msgs, stream=True, max_tokens=800,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text

def build_user_message(question: str, cls: str, subject: str, medium: str) -> str:
    lang = "Respond in Hindi (Devanagari)." if medium == "Hindi Medium" else "Respond in English."
    return f"[{cls} | {subject}] {lang}\n{question}"

# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("# 🤖 AI Tutor (AI Shikshak)")
st.markdown("Koi bhi sawal pucho — AI step-by-step samjhayega!")
st.divider()

with st.sidebar:
    st.markdown("### Apni Details Bharo")
    selected_class   = st.selectbox("Apni Class Chuniye", CLASSES, index=4)
    selected_subject = st.selectbox("Subject Chuniye", SUBJECTS[selected_class])
    medium           = st.radio("Medium", ["Hindi Medium", "English Medium"])
    st.divider()
    if st.button("🗑️ Chat Clear Karo", use_container_width=True):
        st.session_state.tutor_messages = []
        st.rerun()
    st.divider()
    st.markdown("**Tips:**\n- Sawal clearly likhein\n- Chapter bhi batayein\n- 'Aur explain karo' bol sakte ho")

if not require_api_key():
    st.stop()
if not ensure_registered():
    st.stop()

if "tutor_messages" not in st.session_state:
    st.session_state.tutor_messages = []

for msg in st.session_state.tutor_messages:
    avatar = "🧑‍🎓" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if not st.session_state.tutor_messages:
    st.markdown("**Suggested Sawale:**")
    suggestions = {
        "Mathematics": ["Pythagoras theorem kya hai?", "Quadratic equation solve kaise karte hain?", "Trigonometry ke basic formulas kya hain?"],
        "Science":     ["Photosynthesis kya hoti hai?", "Newton ke teen laws explain karo", "Atom aur molecule mein kya farak hai?"],
        "Hindi":       ["Samas kya hota hai? Uske prakar batao", "Ras kise kehte hain?", "Kriya ke bhed batao"],
        "History":     ["1857 ki kranti ke karan kya the?", "Mughal samrajya kab sthapit hua?", "Gandhi ji ka yogdan batao"],
        "English":     ["What is a figure of speech?", "Explain active and passive voice", "What are types of sentences?"],
    }.get(selected_subject, ["Aaj ka topic kya padhna hai?", "Is subject mein kya mushkil lag raha hai?", "Koi formula samajhna hai?"])
    cols = st.columns(3)
    for i, q in enumerate(suggestions[:3]):
        if cols[i].button(q, use_container_width=True, key=f"sug_{i}"):
            st.session_state.tutor_messages.append({"role": "user", "content": q})
            st.rerun()

if prompt := st.chat_input(f"Apna sawal likhein... ({selected_class} | {selected_subject})"):
    user_msg = build_user_message(prompt, selected_class, selected_subject, medium)
    st.session_state.tutor_messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_text = ""
        try:
            for chunk in stream_response(st.session_state.tutor_messages):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            log_usage("AI Tutor", selected_subject, prompt[:80])
        except Exception as e:
            show_api_error(e)
    st.session_state.tutor_messages.append({"role": "assistant", "content": full_text})
