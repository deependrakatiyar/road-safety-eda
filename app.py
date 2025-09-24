import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Road Safety EDA", page_icon="🚦")

@st.cache_data
def load_data():
    df = pd.read_csv("data/accidents.csv", parse_dates=["date"])
    return df

df = load_data()
st.title("🚦 Road Safety EDA")
st.caption("Demo with sample data — replace CSV with real district accident data when available.")

# Filters
col1, col2, col3 = st.columns(3)
with col1:
    districts = ["All"] + sorted(df["district"].dropna().unique().tolist())
    d = st.selectbox("District", districts)
with col2:
    start = st.date_input("Start date", df["date"].min().date())
with col3:
    end = st.date_input("End date", df["date"].max().date())

mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
if d != "All":
    mask &= (df["district"] == d)
sub = df.loc[mask]

st.metric("Incidents", len(sub))
st.metric("Injuries", int(sub["injuries"].sum()))
st.metric("Fatalities", int(sub["fatalities"].sum()))

# Accidents by month
st.subheader("Accidents by Month")
by_month = sub.groupby(sub["date"].dt.to_period("M")).size().sort_index()
fig1 = plt.figure()
by_month.index = by_month.index.astype(str)
plt.plot(by_month.index, by_month.values, marker="o")
plt.xticks(rotation=45)
plt.title("Incidents per Month")
plt.xlabel("Month")
plt.ylabel("Incidents")
st.pyplot(fig1)

# Causes breakdown
st.subheader("Causes Breakdown")
by_cause = sub["cause"].value_counts()
fig2 = plt.figure()
plt.bar(by_cause.index, by_cause.values)
plt.xticks(rotation=30, ha="right")
plt.title("Top Causes")
plt.xlabel("Cause")
plt.ylabel("Count")
st.pyplot(fig2)
