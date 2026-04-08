import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Road Safety Dashboard",
    page_icon="🚦",
    layout="wide",
)


@st.cache_data
def load_data():
    df = pd.read_csv("data/accidents.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["day_of_week"] = df["date"].dt.day_name()
    # Severity score: each fatality weighs twice as much as an injury
    df["severity"] = df["injuries"] + df["fatalities"] * 2
    return df


df = load_data()

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.header("🔧 Filters")

districts = ["All"] + sorted(df["district"].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("District", districts)

causes = ["All"] + sorted(df["cause"].dropna().unique().tolist())
selected_cause = st.sidebar.selectbox("Cause", causes)

start_date = st.sidebar.date_input("Start date", df["date"].min().date())
end_date = st.sidebar.date_input("End date", df["date"].max().date())

# ── Apply filters ────────────────────────────────────────────────────────────
mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
if selected_district != "All":
    mask &= df["district"] == selected_district
if selected_cause != "All":
    mask &= df["cause"] == selected_cause
sub = df.loc[mask].copy()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🚦 Road Safety Dashboard")
filter_tags = []
if selected_district != "All":
    filter_tags.append(f"District: **{selected_district}**")
if selected_cause != "All":
    filter_tags.append(f"Cause: **{selected_cause}**")
filter_tags.append(f"Period: **{start_date}** → **{end_date}**")
st.caption("  |  ".join(filter_tags))

if len(sub) == 0:
    st.warning("No incidents match the current filters.")
    st.stop()

# ── Key metrics ──────────────────────────────────────────────────────────────
total = len(sub)
total_injuries = int(sub["injuries"].sum())
total_fatalities = int(sub["fatalities"].sum())
fatality_rate = round(total_fatalities / total * 100, 1) if total else 0
avg_severity = round(sub["severity"].mean(), 2) if total else 0
high_sev_count = int((sub["severity"] >= 4).sum())

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Incidents", total)
c2.metric("Total Injuries", total_injuries)
c3.metric("Total Fatalities", total_fatalities)
c4.metric("Fatality Rate", f"{fatality_rate}%")
c5.metric("Avg Severity Score", avg_severity)
c6.metric("High-Severity Incidents", high_sev_count)

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_trends, tab_causes, tab_districts, tab_severity, tab_data = st.tabs(
    ["📈 Trends", "🔍 Causes", "🗺️ Districts", "⚠️ Severity", "📋 Raw Data"]
)

# ── Tab 1: Trends ────────────────────────────────────────────────────────────
with tab_trends:
    st.subheader("Monthly Incident Trends")
    monthly = (
        sub.groupby("month")
        .agg(incidents=("date", "count"), injuries=("injuries", "sum"), fatalities=("fatalities", "sum"))
        .reset_index()
        .sort_values("month")
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=monthly["month"], y=monthly["incidents"], name="Incidents",
                   mode="lines+markers", line=dict(color="royalblue", width=2))
    )
    fig.add_trace(
        go.Bar(x=monthly["month"], y=monthly["injuries"], name="Injuries",
               marker_color="orange", opacity=0.65)
    )
    fig.add_trace(
        go.Bar(x=monthly["month"], y=monthly["fatalities"], name="Fatalities",
               marker_color="crimson", opacity=0.75)
    )
    fig.update_layout(
        barmode="group", xaxis_title="Month", yaxis_title="Count",
        legend=dict(orientation="h", y=1.12), hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Incidents by Day of Week")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_day = (
        sub["day_of_week"]
        .value_counts()
        .reindex(day_order, fill_value=0)
        .reset_index()
    )
    by_day.columns = ["Day", "Count"]
    fig_dow = px.bar(by_day, x="Day", y="Count", color="Count",
                     color_continuous_scale="reds", title="Incidents per Weekday")
    fig_dow.update_coloraxes(showscale=False)
    st.plotly_chart(fig_dow, use_container_width=True)

# ── Tab 2: Causes ─────────────────────────────────────────────────────────────
with tab_causes:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Incidents by Cause")
        by_cause = sub["cause"].value_counts().reset_index()
        by_cause.columns = ["Cause", "Count"]
        fig_cause = px.bar(by_cause, x="Cause", y="Count", color="Count",
                           color_continuous_scale="blues")
        fig_cause.update_coloraxes(showscale=False)
        st.plotly_chart(fig_cause, use_container_width=True)

    with col_b:
        st.subheader("Cause Severity Bubble Chart")
        cause_sev = (
            sub.groupby("cause")
            .agg(avg_injuries=("injuries", "mean"), avg_fatalities=("fatalities", "mean"),
                 count=("date", "count"))
            .round(2)
            .reset_index()
        )
        fig_bubble = px.scatter(
            cause_sev, x="avg_injuries", y="avg_fatalities",
            size="count", color="cause", size_max=50,
            labels={"avg_injuries": "Avg Injuries", "avg_fatalities": "Avg Fatalities",
                    "cause": "Cause"},
            title="Avg Injuries vs Fatalities (bubble = frequency)",
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    st.subheader("Injuries & Fatalities by Cause (Stacked)")
    cause_totals = (
        sub.groupby("cause")
        .agg(injuries=("injuries", "sum"), fatalities=("fatalities", "sum"))
        .reset_index()
        .sort_values("injuries", ascending=False)
    )
    fig_stack = go.Figure()
    fig_stack.add_trace(go.Bar(name="Injuries", x=cause_totals["cause"],
                                y=cause_totals["injuries"], marker_color="orange"))
    fig_stack.add_trace(go.Bar(name="Fatalities", x=cause_totals["cause"],
                                y=cause_totals["fatalities"], marker_color="crimson"))
    fig_stack.update_layout(barmode="stack", xaxis_title="Cause", yaxis_title="Total")
    st.plotly_chart(fig_stack, use_container_width=True)

# ── Tab 3: Districts ──────────────────────────────────────────────────────────
with tab_districts:
    district_stats = (
        sub.groupby("district")
        .agg(incidents=("date", "count"), injuries=("injuries", "sum"),
             fatalities=("fatalities", "sum"))
        .reset_index()
    )
    district_stats["fatality_rate"] = (
        district_stats["fatalities"] / district_stats["incidents"] * 100
    ).round(1)
    district_stats = district_stats.sort_values("incidents", ascending=False)

    col_c, col_d = st.columns(2)
    with col_c:
        fig_dist = px.bar(district_stats, x="district", y="incidents",
                          title="Incidents by District", color="incidents",
                          color_continuous_scale="reds")
        fig_dist.update_coloraxes(showscale=False)
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_d:
        fig_fat = px.bar(district_stats, x="district", y="fatality_rate",
                         title="Fatality Rate by District (%)", color="fatality_rate",
                         color_continuous_scale="oranges")
        fig_fat.update_coloraxes(showscale=False)
        st.plotly_chart(fig_fat, use_container_width=True)

    st.subheader("Cause Distribution per District")
    heatmap_data = (
        sub.groupby(["district", "cause"])
        .size()
        .reset_index(name="count")
    )
    fig_heat = px.density_heatmap(
        heatmap_data, x="cause", y="district", z="count",
        color_continuous_scale="YlOrRd",
        title="Incident Count: District × Cause",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("District Summary")
    st.dataframe(
        district_stats.rename(columns={
            "district": "District", "incidents": "Incidents",
            "injuries": "Total Injuries", "fatalities": "Total Fatalities",
            "fatality_rate": "Fatality Rate (%)",
        }),
        use_container_width=True,
        hide_index=True,
    )

# ── Tab 4: Severity ───────────────────────────────────────────────────────────
with tab_severity:
    col_e, col_f = st.columns(2)

    with col_e:
        st.subheader("Severity Score Distribution")
        fig_hist = px.histogram(
            sub, x="severity", nbins=10,
            title="Severity Score (injuries + 2 × fatalities)",
            labels={"severity": "Severity Score"},
            color_discrete_sequence=["crimson"],
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_f:
        high_sev = sub[sub["severity"] >= 4]
        if len(high_sev) > 0:
            st.subheader("High-Severity Incidents by Cause (score ≥ 4)")
            hs_cause = high_sev["cause"].value_counts().reset_index()
            hs_cause.columns = ["Cause", "Count"]
            fig_pie = px.pie(hs_cause, values="Count", names="Cause",
                             hole=0.35, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No high-severity incidents in the selected range.")

    st.subheader("Average Severity Score by Month")
    monthly_sev = (
        sub.groupby("month")["severity"]
        .mean()
        .round(2)
        .reset_index()
        .sort_values("month")
    )
    overall_avg = monthly_sev["severity"].mean()
    fig_sev = px.line(monthly_sev, x="month", y="severity", markers=True,
                      labels={"severity": "Avg Severity", "month": "Month"})
    fig_sev.add_hline(y=overall_avg, line_dash="dash", line_color="red",
                      annotation_text=f"Overall avg: {overall_avg:.2f}",
                      annotation_position="bottom right")
    st.plotly_chart(fig_sev, use_container_width=True)

# ── Tab 5: Raw Data ───────────────────────────────────────────────────────────
with tab_data:
    st.subheader("Incident Records")
    search = st.text_input("Search by district or cause")
    display = sub.copy()
    if search:
        search_mask = (
            display["district"].str.contains(search, case=False, na=False)
            | display["cause"].str.contains(search, case=False, na=False)
        )
        display = display[search_mask]

    st.dataframe(
        display[["date", "district", "cause", "injuries", "fatalities", "severity"]]
        .sort_values("date", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
    )
    st.download_button(
        "⬇️ Download filtered data as CSV",
        display.to_csv(index=False),
        "filtered_accidents.csv",
        "text/csv",
    )
