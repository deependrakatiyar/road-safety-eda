import streamlit as st
import os

st.set_page_config(
    page_title="Padhai AI - MP Board Study Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        color: #1a237e;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #e8eaf6, #f3e5f5);
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        border-left: 5px solid #3949ab;
        margin-bottom: 16px;
        transition: transform 0.2s;
    }
    .feature-card h3 {
        color: #1a237e;
        margin-bottom: 8px;
    }
    .feature-card p {
        color: #444;
        font-size: 0.95rem;
    }
    .badge {
        display: inline-block;
        background: #3949ab;
        color: white;
        border-radius: 20px;
        padding: 3px 14px;
        font-size: 0.82rem;
        margin: 3px;
    }
    .stats-box {
        background: #1a237e;
        color: white;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
    }
    .stats-box h2 { color: #90caf9; margin: 0; }
    .stats-box p { margin: 4px 0 0 0; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">📚 Padhai AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">MP Board School Students ke liye AI-Powered Study Platform | Class 6 se 12</div>', unsafe_allow_html=True)

st.divider()

# Stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="stats-box"><h2>7</h2><p>Classes (6-12)</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stats-box"><h2>10+</h2><p>Subjects</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stats-box"><h2>24/7</h2><p>AI Tutor Available</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="stats-box"><h2>2</h2><p>Medium: Hindi & English</p></div>', unsafe_allow_html=True)

st.divider()

# Features section
st.markdown("## Kya Milega Yahan? (What's Available?)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🤖 AI Tutor (AI Shikshak)</h3>
        <p>Apna koi bhi sawal pucho! AI tutor Hindi aur English dono mein samjhayega.
        Step-by-step explanations ke saath difficult topics ko aasan banao.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <h3>📝 Study Notes (Notes Banao)</h3>
        <p>Kisi bhi chapter ka summary, important points aur definitions turant generate karo.
        Board exam ki preparation ke liye perfect revision notes.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>❓ Quiz Practice (Practice Karo)</h3>
        <p>MCQ questions ke saath apni taiyari test karo. Subject, class aur chapter choose karo
        aur AI automatically questions generate karega MP Board pattern mein.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <h3>⭐ Important Questions</h3>
        <p>MP Board exams mein frequently aane wale important questions.
        2-3 mark, 4-5 mark aur essay type questions — sab ek jagah.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Subjects available
st.markdown("## Subjects Available")

subjects_by_class = {
    "Class 6-8 (Middle School)": ["Hindi", "English", "Ganit (Mathematics)", "Vigyan (Science)", "Samajik Vigyan (Social Science)", "Sanskrit"],
    "Class 9-10 (High School)": ["Hindi", "English", "Ganit (Mathematics)", "Vigyan (Science)", "Samajik Vigyan (Social Science)", "Sanskrit", "Computer Science"],
    "Class 11-12 (Higher Secondary)": ["Hindi", "English", "Physics (Bhautiki)", "Chemistry (Rasayan Vigyan)", "Mathematics (Ganit)", "Biology (Jeev Vigyan)", "History (Itihas)", "Geography (Bhugol)", "Political Science (Rajniti Shastra)", "Economics (Arthshastra)", "Business Studies", "Accountancy", "Computer Science"],
}

for group, subjects in subjects_by_class.items():
    with st.expander(f"**{group}**", expanded=True):
        badges_html = "".join([f'<span class="badge">{s}</span>' for s in subjects])
        st.markdown(badges_html, unsafe_allow_html=True)

st.divider()

# How to use
st.markdown("## Kaise Use Karein? (How to Use?)")
steps = [
    ("1️⃣", "Left sidebar mein apni page choose karo", "AI Tutor, Quiz, Notes ya Important Questions"),
    ("2️⃣", "Apni class aur subject select karo", "Class 6 se 12 tak, MP Board ke sabhi subjects"),
    ("3️⃣", "Hindi ya English medium choose karo", "Dono languages mein support available hai"),
    ("4️⃣", "Apna sawal pucho ya topic enter karo", "AI turant jawab dega ya content generate karega"),
]

cols = st.columns(4)
for col, (num, title, desc) in zip(cols, steps):
    with col:
        st.info(f"**{num} {title}**\n\n{desc}")

st.divider()

# Footer
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.9rem; padding:10px 0;">
    📚 <strong>Padhai AI</strong> — MP Board Students ke liye, AI ki Shakti ke Saath<br>
    Powered by Claude AI | Made with ❤️ for MP Board Students
</div>
""", unsafe_allow_html=True)

# Sidebar info
with st.sidebar:
    st.markdown("### Padhai AI")
    st.markdown("**MP Board Study Platform**")
    st.divider()
    st.markdown("**Quick Navigation:**")
    st.markdown("- 🤖 **AI Tutor** — Sawal Pucho")
    st.markdown("- ❓ **Quiz** — Practice Karo")
    st.markdown("- 📝 **Notes** — Notes Banao")
    st.markdown("- ⭐ **Important Q** — Exam Prep")
    st.divider()

    # API Connection Test
    st.markdown("### 🔌 API Connection Test")
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("❌ GEMINI_API_KEY missing!")
        st.caption("Streamlit Cloud → Manage app → Secrets mein add karo.")
    else:
        st.success(f"✅ Key found: `...{api_key[-6:]}`")
        if st.button("🧪 Test Karo", use_container_width=True):
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                resp = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents="Say: OK"
                )
                st.success(f"✅ API Working! Response: {resp.text[:40]}")
            except Exception as e:
                st.error("❌ API Error:")
                st.code(str(e), language="text")
