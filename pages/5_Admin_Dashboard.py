import streamlit as st
import os
import sys
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import _sb_get

st.set_page_config(page_title="Admin Dashboard - Padhai AI", page_icon="📊", layout="wide")

# ── Auth ──────────────────────────────────────────────────────────────────────

ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "nic_raisen_2024")

if not st.session_state.get("admin_auth"):
    st.markdown("## 🔐 Admin Login — NIC Raisen DIO")
    pwd = st.text_input("Password", type="password")
    if st.button("Login", type="primary"):
        if pwd == ADMIN_PASS:
            st.session_state.admin_auth = True
            st.rerun()
        else:
            st.error("❌ Wrong password")
    st.stop()

# ── Load data ─────────────────────────────────────────────────────────────────

st.markdown("# 📊 Padhai AI — Impact Dashboard")
st.markdown("**NIC Raisen DIO | Real-time Usage Analytics**")
st.divider()

if not (os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY")):
    st.warning("⚠️ Supabase credentials missing. `SUPABASE_URL` aur `SUPABASE_KEY` secrets mein add karo.")
    st.markdown("""
    **Setup karne ke liye:**
    1. [supabase.com](https://supabase.com) → New project (free)
    2. SQL Editor mein yeh run karo:
    ```sql
    CREATE TABLE registrations (
      id bigint generated always as identity primary key,
      created_at timestamptz default now(),
      name text, class text, school_name text, district text, session_id text
    );
    CREATE TABLE usage_logs (
      id bigint generated always as identity primary key,
      created_at timestamptz default now(),
      user_name text, user_class text, school_name text, district text,
      feature text, subject text, topic text, session_id text
    );
    ```
    3. Settings → API → URL aur anon key copy karo → Streamlit Secrets mein add karo:
    ```toml
    SUPABASE_URL = "https://xxxx.supabase.co"
    SUPABASE_KEY = "eyJ..."
    ADMIN_PASSWORD = "apna_password_yahan"
    ```
    """)
    st.stop()

with st.spinner("Data load ho raha hai..."):
    regs  = _sb_get("registrations")
    usage = _sb_get("usage_logs")

reg_df   = pd.DataFrame(regs)   if regs   else pd.DataFrame()
usage_df = pd.DataFrame(usage)  if usage  else pd.DataFrame()

# ── KPI row ───────────────────────────────────────────────────────────────────

total_students  = len(reg_df)
total_queries   = len(usage_df)
unique_schools  = reg_df["school_name"].nunique() if not reg_df.empty else 0
unique_districts = reg_df["district"].nunique()   if not reg_df.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("👨‍🎓 Total Students", total_students)
c2.metric("🔍 Total Queries", total_queries)
c3.metric("🏫 Schools", unique_schools)
c4.metric("📍 Districts", unique_districts)

st.divider()

if usage_df.empty and reg_df.empty:
    st.info("Abhi tak koi data nahi hai. Students ke register karne ke baad yahan stats dikhenge.")
    st.stop()

# ── Charts ────────────────────────────────────────────────────────────────────

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Feature-wise Usage")
    if not usage_df.empty:
        fc = usage_df["feature"].value_counts().reset_index()
        fc.columns = ["Feature", "Count"]
        st.bar_chart(fc.set_index("Feature"))

    st.markdown("### Class-wise Registrations")
    if not reg_df.empty:
        cc = reg_df["class"].value_counts().sort_index().reset_index()
        cc.columns = ["Class", "Students"]
        st.bar_chart(cc.set_index("Class"))

with col_right:
    st.markdown("### Subject Popularity")
    if not usage_df.empty:
        sc = usage_df[usage_df["subject"] != ""]["subject"].value_counts().head(10).reset_index()
        sc.columns = ["Subject", "Queries"]
        st.bar_chart(sc.set_index("Subject"))

    st.markdown("### District-wise Reach")
    if not reg_df.empty:
        dc = reg_df["district"].value_counts().reset_index()
        dc.columns = ["District", "Students"]
        st.bar_chart(dc.set_index("District"))

st.divider()

# ── Daily activity ────────────────────────────────────────────────────────────

st.markdown("### Daily Activity (Last 30 Days)")
if not usage_df.empty:
    usage_df["created_at"] = pd.to_datetime(usage_df["created_at"])
    daily = usage_df.groupby(usage_df["created_at"].dt.date).size().reset_index()
    daily.columns = ["Date", "Queries"]
    st.line_chart(daily.set_index("Date"))

# ── School leaderboard ────────────────────────────────────────────────────────

st.markdown("### School-wise Usage")
if not usage_df.empty:
    school_usage = usage_df.groupby("school_name").size().reset_index(name="Queries")
    school_regs  = reg_df.groupby("school_name").size().reset_index(name="Students") if not reg_df.empty else pd.DataFrame()
    if not school_regs.empty:
        merged = school_usage.merge(school_regs, on="school_name", how="left").fillna(0)
        merged.columns = ["School", "Total Queries", "Registered Students"]
        merged = merged.sort_values("Total Queries", ascending=False)
        st.dataframe(merged, use_container_width=True, hide_index=True)

# ── Recent activity ───────────────────────────────────────────────────────────

st.divider()
st.markdown("### Recent Activity Log")
if not usage_df.empty:
    display = usage_df[["created_at","user_name","user_class","school_name","district","feature","subject","topic"]].copy()
    display.columns = ["Time","Student","Class","School","District","Feature","Subject","Topic"]
    display["Time"] = pd.to_datetime(display["Time"]).dt.strftime("%d %b %H:%M")
    st.dataframe(display.head(50), use_container_width=True, hide_index=True)

st.divider()
col1, col2 = st.columns(2)
with col1:
    if not reg_df.empty:
        st.download_button("⬇️ Download Registrations CSV",
                           data=reg_df.to_csv(index=False),
                           file_name="padhai_ai_registrations.csv", mime="text/csv")
with col2:
    if not usage_df.empty:
        st.download_button("⬇️ Download Usage Logs CSV",
                           data=usage_df.to_csv(index=False),
                           file_name="padhai_ai_usage.csv", mime="text/csv")

if st.sidebar.button("🚪 Logout"):
    st.session_state.admin_auth = False
    st.rerun()
