import streamlit as st
from google import genai
from google.genai import types
import os

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

MODEL = "gemini-2.0-flash"
MAX_HISTORY = 6

def get_client(api_key: str):
    return genai.Client(api_key=api_key)

def build_user_message(question: str, cls: str, subject: str, medium: str) -> str:
    lang = "Respond in Hindi (Devanagari)." if medium == "Hindi Medium" else "Respond in English."
    return f"[{cls} | {subject}] {lang}\n{question}"

def stream_response(client, messages: list):
    trimmed = messages[-MAX_HISTORY:]
    history = []
    for m in trimmed[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))

    chat = client.chats.create(
        model=MODEL,
        history=history,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    for chunk in chat.send_message_stream(trimmed[-1]["content"]):
        if chunk.text:
            yield chunk.text

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

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    st.warning("⚠️ **GEMINI_API_KEY** set nahi hai.")
    st.info("Free API key: https://aistudio.google.com/app/apikey")
    st.code("export GEMINI_API_KEY='your-key-here'", language="bash")
    st.stop()

client = get_client(api_key)

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
            for chunk in stream_response(client, st.session_state.tutor_messages):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
        except Exception as e:
            placeholder.error(f"❌ Error: {e}")

    st.session_state.tutor_messages.append({"role": "assistant", "content": full_text})
