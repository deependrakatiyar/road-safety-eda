import streamlit as st
import anthropic
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
    "Summary Notes (Saar)":         "Concise chapter summary with key points",
    "Detailed Notes (Vistrit)":     "Comprehensive notes with explanations, examples, and diagrams description",
    "Formula Sheet (Sutre)":        "All formulas, definitions, and key terms",
    "Revision Notes (Revision)":    "Quick revision bullet points — perfect for last-minute prep",
    "Mind Map (Diagram Style)":     "Topic breakdown in hierarchical structure",
}

NOTES_PROMPT = """You are an expert MP Board study notes creator for {cls} students.

Create **{note_type}** for:
- Class: {cls}
- Subject: {subject}
- Chapter/Topic: {topic}
- Language: {medium}

{type_instruction}

Format requirements:
- Use proper headings (##, ###)
- Use bullet points and numbered lists
- Highlight key terms with **bold**
- For Science/Math: include all important formulas in a formula box (use ``` code blocks)
- For History/Geography: include important dates, names, places clearly
- For Hindi/Sanskrit: include definitions, examples, and literary terms clearly
- End with a "Remember / Yaad Rakho" box with the 5 most important points

Write in {medium_lang}. Make notes board-exam focused for MP Board students."""

TYPE_INSTRUCTIONS = {
    "Summary Notes (Saar)":         "Create a concise 400-600 word summary covering all major concepts.",
    "Detailed Notes (Vistrit)":     "Create comprehensive notes (800-1200 words) with detailed explanations, examples, and all sub-topics.",
    "Formula Sheet (Sutre)":        "List ALL formulas, definitions, key terms, and important facts. Use tables where appropriate.",
    "Revision Notes (Revision)":    "Create quick bullet-point revision notes. Each point should be short (1-2 lines). Focus on what examiners ask.",
    "Mind Map (Diagram Style)":     "Create a hierarchical text-based mind map using indentation. Show how topics connect to sub-topics.",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def stream_notes(client, cls, subject, topic, note_type, medium):
    medium_lang = "Hindi (Devanagari script)" if medium == "Hindi Medium" else "English"
    prompt = NOTES_PROMPT.format(
        cls=cls, subject=subject, topic=topic,
        note_type=note_type, medium=medium,
        medium_lang=medium_lang,
        type_instruction=TYPE_INSTRUCTIONS.get(note_type, "")
    )
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "adaptive"},
    ) as stream:
        for text in stream.text_stream:
            yield text

# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("# 📝 Study Notes Generator")
st.markdown("Kisi bhi chapter ke AI-powered notes instant banao — board exam ke liye!")
st.divider()

# Sidebar
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
api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    st.warning("⚠️ **ANTHROPIC_API_KEY** set nahi hai. Please API key add karein.")
    st.code("export ANTHROPIC_API_KEY='your-key-here'", language="bash")
    st.stop()

client = get_client()

# State
if "notes_content" not in st.session_state: st.session_state.notes_content = ""
if "notes_config"  not in st.session_state: st.session_state.notes_config  = {}

# Generate
if generate_btn:
    if not topic.strip():
        st.error("Chapter ya topic ka naam likhein!")
    else:
        cfg = {"class": selected_class, "subject": selected_subject,
               "topic": topic, "type": note_type, "medium": medium}
        st.session_state.notes_config  = cfg
        st.session_state.notes_content = ""

        st.markdown(f"### {selected_class} | {selected_subject} | {topic}")
        st.markdown(f"**{note_type}** | {medium}")
        st.divider()

        placeholder = st.empty()
        full_text   = ""
        with st.spinner("Notes generate ho rahi hain..."):
            for chunk in stream_notes(client, selected_class, selected_subject, topic, note_type, medium):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        st.session_state.notes_content = full_text

        st.divider()
        st.success("✅ Notes ready! Copy karein ya dobara generate karein.")
        st.download_button(
            label="⬇️ Notes Download Karo (.txt)",
            data=full_text,
            file_name=f"{selected_class}_{selected_subject}_{topic}_notes.txt",
            mime="text/plain",
            use_container_width=True,
        )

elif st.session_state.notes_content:
    cfg = st.session_state.notes_config
    st.markdown(f"### {cfg['class']} | {cfg['subject']} | {cfg['topic']}")
    st.markdown(f"**{cfg['type']}** | {cfg['medium']}")
    st.divider()
    st.markdown(st.session_state.notes_content)
    st.divider()
    st.download_button(
        label="⬇️ Notes Download Karo (.txt)",
        data=st.session_state.notes_content,
        file_name=f"{cfg['class']}_{cfg['subject']}_{cfg['topic']}_notes.txt",
        mime="text/plain",
        use_container_width=True,
    )

else:
    # Empty state
    st.info("👈 Left sidebar mein class, subject, topic aur notes type choose karo, phir **Notes Banao** dabao!")

    st.markdown("### Notes ke Types / Types of Notes")
    cols = st.columns(2)
    items = list(NOTE_TYPES.items())
    for i, (name, desc) in enumerate(items):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#f3e5f5; border-radius:10px; padding:14px; margin-bottom:12px; border-left:4px solid #7b1fa2;">
                <strong>{name}</strong><br>
                <span style="color:#555; font-size:0.9rem;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Example Topics")
    examples = {
        "Class 10 Science": ["Light - Reflection and Refraction", "Carbon and its Compounds", "Life Processes"],
        "Class 10 Social Science": ["Nationalism in India", "Resources and Development", "Money and Credit"],
        "Class 12 Physics": ["Electric Charges and Fields", "Ray Optics", "Semiconductor Electronics"],
        "Class 12 Chemistry": ["p-Block Elements", "Coordination Compounds", "Biomolecules"],
        "Class 9 Mathematics": ["Number Systems", "Triangles", "Statistics"],
    }
    for subject, topics in examples.items():
        st.markdown(f"**{subject}:** {' | '.join(topics)}")
