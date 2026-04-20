import streamlit as st
import re
import os
import uuid
import requests as _req
from groq import Groq

MODEL = "llama-3.3-70b-versatile"

# ── Groq API ──────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    return os.environ.get("GROQ_API_KEY", "") or st.session_state.get("groq_api_key", "")

def get_client():
    return Groq(api_key=get_api_key())

def require_api_key() -> bool:
    if get_api_key():
        return True
    st.sidebar.divider()
    st.sidebar.markdown("### 🔑 Groq API Key")
    st.sidebar.markdown("**Free key (30 sec):**\n1. [console.groq.com](https://console.groq.com) → Sign up\n2. API Keys → Create Key\n3. Neeche paste karo")
    key = st.sidebar.text_input("Groq API Key", type="password", placeholder="gsk_...")
    if key:
        st.session_state.groq_api_key = key
        st.rerun()
    st.info("👈 Sidebar mein apni **free Groq API key** enter karo.")
    return False

def show_api_error(e: Exception):
    err = str(e)
    if "429" in err or "rate_limit" in err.lower():
        m = re.search(r'try again in (\d+\.?\d*)s', err)
        secs = int(float(m.group(1))) + 1 if m else 30
        st.warning(f"⏳ **Rate limit — {secs} seconds baad dobara try karo.**")
    elif "401" in err or "invalid_api_key" in err.lower():
        st.error("❌ **Invalid API Key.** Sahi key enter karo.")
        st.session_state.pop("groq_api_key", None)
        st.rerun()
    else:
        st.error("❌ Error:")
        st.code(err, language="text")

# ── Supabase helpers (fire-and-forget, never crash app) ───────────────────────

def _sb_url():
    return os.environ.get("SUPABASE_URL", "").rstrip("/")

def _sb_key():
    return os.environ.get("SUPABASE_KEY", "")

def _sb_post(table: str, data: dict):
    url, key = _sb_url(), _sb_key()
    if not url or not key:
        return
    try:
        _req.post(
            f"{url}/rest/v1/{table}",
            headers={"apikey": key, "Authorization": f"Bearer {key}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json=data, timeout=4,
        )
    except Exception:
        pass

def _sb_get(table: str, select: str = "*", order: str = "created_at.desc", limit: int = 1000):
    url, key = _sb_url(), _sb_key()
    if not url or not key:
        return []
    try:
        r = _req.get(
            f"{url}/rest/v1/{table}",
            headers={"apikey": key, "Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            params={"select": select, "order": order, "limit": limit},
            timeout=6,
        )
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

# ── Registration ──────────────────────────────────────────────────────────────

MP_DISTRICTS = ["Raisen","Bhopal","Indore","Jabalpur","Gwalior","Ujjain","Sagar",
                 "Rewa","Satna","Dewas","Chhindwara","Ratlam","Vidisha","Hoshangabad",
                 "Mandla","Seoni","Balaghat","Betul","Damoh","Katni","Murena","Shivpuri",
                 "Guna","Datia","Tikamgarh","Chhatarpur","Panna","Niwari","Other"]

CLASSES = ["Class 6","Class 7","Class 8","Class 9","Class 10","Class 11","Class 12"]

def ensure_registered() -> bool:
    """Show one-time registration form. Returns True once registered."""
    if st.session_state.get("user_registered"):
        return True

    st.markdown("## 👋 Padhai AI mein Swagat Hai!")
    st.markdown("Shuru karne se pehle apni details bharo — **sirf ek baar:**")
    st.divider()

    with st.form("reg_form"):
        name   = st.text_input("Aapka Naam *", placeholder="e.g., Rahul Sharma")
        col1, col2 = st.columns(2)
        cls    = col1.selectbox("Class *", CLASSES)
        dist   = col2.selectbox("District *", MP_DISTRICTS)
        school = st.text_input("School ka Naam *", placeholder="e.g., Govt. HS School Raisen")
        done   = st.form_submit_button("✅ Shuru Karein!", use_container_width=True, type="primary")

    if done:
        if not name.strip() or not school.strip():
            st.error("Naam aur School ka naam zaruri hai!")
            return False
        info = {
            "name": name.strip(), "class": cls,
            "school": school.strip(), "district": dist,
            "session_id": str(uuid.uuid4())[:8],
        }
        st.session_state.user_registered = True
        st.session_state.user_info = info
        _sb_post("registrations", info)
        st.rerun()
    return False

def log_usage(feature: str, subject: str = "", topic: str = ""):
    user = st.session_state.get("user_info", {})
    _sb_post("usage_logs", {
        "user_name":   user.get("name", "Anonymous"),
        "user_class":  user.get("class", ""),
        "school_name": user.get("school", ""),
        "district":    user.get("district", ""),
        "feature":     feature,
        "subject":     subject,
        "topic":       topic,
        "session_id":  user.get("session_id", ""),
    })
