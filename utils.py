import streamlit as st
import re

def show_api_error(e: Exception):
    err = str(e)
    if "429" in err or "RESOURCE_EXHAUSTED" in err:
        wait = re.search(r'retry in (\d+)', err)
        secs = int(wait.group(1)) + 1 if wait else 60
        st.warning(f"""
⏳ **Rate limit hit — free tier mein 15 requests/minute limit hai.**

**{secs} seconds baad dobara try karo.** Tab tak dusra topic soch lo!

> Free tier limit: 15 req/min · 1,500 req/day
        """)
    else:
        st.error("❌ Error aaya — neeche dekho:")
        st.code(err, language="text")
