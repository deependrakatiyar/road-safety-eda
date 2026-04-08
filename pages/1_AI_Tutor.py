import streamlit as st
import anthropic
import os

st.set_page_config(page_title="AI Tutor - Padhai AI", page_icon="🤖", layout="wide")

# ── Data ─────────────────────────────────────────────────────────────────────

CLASSES = ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12"]

SUBJECTS = {
    "Class 6": ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit"],
    "Class 7": ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit"],
    "Class 8": ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit"],
    "Class 9": ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit", "Computer Science"],
    "Class 10": ["Hindi", "English", "Mathematics", "Science", "Social Science", "Sanskrit", "Computer Science"],
    "Class 11": ["Hindi", "English", "Physics", "Chemistry", "Mathematics", "Biology", "History", "Geography", "Political Science", "Economics", "Business Studies", "Accountancy", "Computer Science"],
    "Class 12": ["Hindi", "English", "Physics", "Chemistry", "Mathematics", "Biology", "History", "Geography", "Political Science", "Economics", "Business Studies", "Accountancy", "Computer Science"],
}

SYSTEM_PROMPT = """You are Padhai AI, an MP Board tutor (Class 6-12).
- Answer in Hindi if student writes in Hindi, else English.
- Step-by-step explanations; bold key terms and formulas.
- Keep answers concise but complete. End with one follow-up question."""

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def build_user_message(question: str, cls: str, subject: str, medium: str) -> str:
    lang_note = "Please respond in Hindi (Devanagari script)." if medium == "Hindi Medium" else "Please respond in English."
    return f"[{cls} | {subject} | {medium}] {lang_note}\n\nMera sawal hai / My question is:\n{question}"


MAX_HISTORY = 6  # keep last 3 pairs to limit input tokens

def stream_response(client, messages: list) -> str:
    # Trim history: always keep first (context) msg + last MAX_HISTORY msgs
    trimmed = messages[-MAX_HISTORY:] if len(messages) > MAX_HISTORY else messages
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=trimmed,
    ) as stream:
        for text in stream.text_stream:
            yield text

# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("# 🤖 AI Tutor (AI Shikshak)")
st.markdown("Koi bhi sawal pucho — AI step-by-step samjhayega! | Ask anything — AI will explain step by step!")
st.divider()

# Sidebar config
with st.sidebar:
    st.markdown("### Apni Details Bharo")
    selected_class = st.selectbox("Apni Class Chuniye", CLASSES, index=4)
    selected_subject = st.selectbox("Subject Chuniye", SUBJECTS[selected_class])
    medium = st.radio("Medium", ["Hindi Medium", "English Medium"])
    st.divider()
    if st.button("🗑️ Chat Clear Karo", use_container_width=True):
        st.session_state.tutor_messages = []
        st.rerun()
    st.divider()
    st.markdown("**Tips:**")
    st.markdown("- Sawal clearly likhein")
    st.markdown("- Chapter ya topic bhi batayein")
    st.markdown("- 'Aur explain karo' bol sakte ho")

# API Key check
api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    st.warning("⚠️ **ANTHROPIC_API_KEY** environment variable set nahi hai. Please API key add karein.")
    st.code("export ANTHROPIC_API_KEY='your-key-here'", language="bash")
    st.stop()

client = get_client()

# Initialize chat history
if "tutor_messages" not in st.session_state:
    st.session_state.tutor_messages = []

# Display chat history
for msg in st.session_state.tutor_messages:
    role_label = "Aap (You)" if msg["role"] == "user" else "AI Tutor"
    avatar = "🧑‍🎓" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Suggested questions
if not st.session_state.tutor_messages:
    st.markdown("**Suggested Questions / Suggested Sawale:**")
    suggestions = {
        "Mathematics": ["Pythagoras theorem kya hai?", "Quadratic equation solve kaise karte hain?", "Trigonometry ke basic formulas kya hain?"],
        "Science": ["Photosynthesis kya hoti hai?", "Newton ke teen laws explain karo", "Atom aur molecule mein kya farak hai?"],
        "Hindi": ["Samas kya hota hai? Uske prakar batao", "Ras kise kehte hain?", "Kriya ke bhed batao"],
        "History": ["1857 ki kranti ke karan kya the?", "Mughal samrajya ka patna kab hua?", "Swatantrata sangram mein Gandhi ji ka yogdan"],
        "English": ["What is a figure of speech?", "Explain active and passive voice", "What are the types of sentences?"],
    }.get(selected_subject, ["Aaj ka topic kya padhna hai?", "Is subject mein kya mushkil lag raha hai?", "Koi formula samajhna hai?"])

    cols = st.columns(3)
    for i, q in enumerate(suggestions[:3]):
        if cols[i].button(q, use_container_width=True, key=f"sug_{i}"):
            st.session_state.tutor_messages.append({"role": "user", "content": q})
            st.rerun()

# Chat input
if prompt := st.chat_input(f"Apna sawal likhein... ({selected_class} | {selected_subject})"):
    user_msg = build_user_message(prompt, selected_class, selected_subject, medium)
    st.session_state.tutor_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        # Build messages for API (use full formatted message only for latest)
        api_messages = []
        for i, m in enumerate(st.session_state.tutor_messages[:-1]):
            api_messages.append({"role": m["role"], "content": m["content"]})
        # Last user message with context
        api_messages.append({"role": "user", "content": user_msg})

        response_placeholder = st.empty()
        full_text = ""
        for chunk in stream_response(client, api_messages):
            full_text += chunk
            response_placeholder.markdown(full_text + "▌")
        response_placeholder.markdown(full_text)

    st.session_state.tutor_messages.append({"role": "assistant", "content": full_text})
