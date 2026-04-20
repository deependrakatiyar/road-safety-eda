import streamlit as st
import re
import os
from groq import Groq

MODEL = "llama-3.3-70b-versatile"

def get_api_key() -> str:
    env = os.environ.get("GROQ_API_KEY", "")
    if env:
        return env
    return st.session_state.get("groq_api_key", "")

def get_client():
    return Groq(api_key=get_api_key())

def require_api_key() -> bool:
    """Show key input in sidebar if missing. Returns True when key is ready."""
    if get_api_key():
        return True
    st.sidebar.divider()
    st.sidebar.markdown("### 🔑 API Key Chahiye")
    st.sidebar.markdown(
        "**Free key (30 sec):**\n"
        "1. [console.groq.com](https://console.groq.com) → Sign up\n"
        "2. API Keys → Create Key\n"
        "3. Neeche paste karo"
    )
    key = st.sidebar.text_input("Groq API Key", type="password", placeholder="gsk_...")
    if key:
        st.session_state.groq_api_key = key
        st.rerun()
    st.info("👈 Sidebar mein apni **free Groq API key** enter karo — 30 seconds mein milti hai!")
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
