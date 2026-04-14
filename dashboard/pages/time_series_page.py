import streamlit as st
import pandas as pd
from dashboard.components.charts import create_line_chart, create_bar_chart, create_heatmap
from dashboard.components.metrics import display_metric_row

def render_time_series(results: dict):
    #Render the time-series analysis page
    st.title("Time-Series Analysis")
    st.markdown("Temporal patterns in commit activity, growth trends, and development velocity.")
    df = results.get("df")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    st.markdown("### Commit Velocity Overview")
    velocity_cols = ["name", "commit_count", "commit_frequency", "weekly_commit_rate", "commit_velocity_trend"]
    available = [c for c in velocity_cols if c in df.columns]
    if available:
        velocity_df = df[available].sort_values(
            "commit_frequency" if "commit_frequency" in df.columns else "commit_count",
            ascending=False
        )
        st.dataframe(velocity_df, use_container_width=True, height=300)
    st.markdown("---")

    timeline = results.get("commit_timeline")
    if timeline is not None and not timeline.empty:
        st.markdown("### Monthly Commit Activity")
        # Filter by repository
        repos = timeline["repo_name"].unique().tolist()
        selected_repos = st.multiselect(
            "Filter Repositories",
            repos,
            default=repos[:4],
            key="timeline_filter",
        )
        if selected_repos:
            filtered = timeline[timeline["repo_name"].isin(selected_repos)]
            fig = create_line_chart(
                filtered, x="month_str", y="commits",
                title="Commits per Month by Repository",
                color="repo_name",
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    st.markdown("### Commit Frequency Comparison")
    col1, col2 = st.columns(2)
    with col1:
        if "commit_frequency" in df.columns:
            chart_df = df[["name", "commit_frequency"]].sort_values("commit_frequency", ascending=True)
            fig = create_bar_chart(
                chart_df, x="commit_frequency", y="name",
                title="Commits per Day (time-window based)",
                orientation="h", height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if "weekly_commit_rate" in df.columns:
            chart_df = df[["name", "weekly_commit_rate"]].sort_values("weekly_commit_rate", ascending=True)
            fig = create_bar_chart(
                chart_df, x="weekly_commit_rate", y="name",
                title="Average Commits per Week",
                orientation="h", height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    if "commit_velocity_trend" in df.columns:
        st.markdown("### Commit Velocity Trends")
        trend_counts = df["commit_velocity_trend"].value_counts().reset_index()
        trend_counts.columns = ["trend", "count"]
        fig = create_bar_chart(
            trend_counts, x="trend", y="count",
            title="Velocity Trend Distribution",
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
        col1, col2, col3 = st.columns(3)
        for col, trend in zip(
            [col1, col2, col3],
            ["accelerating", "stable", "decelerating"]
        ):
            repos = df[df["commit_velocity_trend"] == trend]["name"].tolist()
            col.markdown(f"**{trend.title()}**")
            for r in repos:
                col.markdown(f"- {r.split('/')[-1]}")
    st.markdown("---")

    heatmap = results.get("heatmap_data")
    if heatmap is not None and not heatmap.empty:
        st.markdown("### Commit Activity Heatmap (Day x Hour)")
        fig = create_heatmap(
            heatmap, x="hour", y="day_of_week", z="count",
            title="When are commits made?",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    trends = results.get("historical_trends")
    if trends is not None and not trends.empty:
        st.markdown("### Historical Growth Trends (from snapshots)")
        growth_cols = [c for c in trends.columns if "growth_pct" in c]
        if growth_cols:
            display_cols = ["name"] + growth_cols
            available = [c for c in display_cols if c in trends.columns]
            st.dataframe(trends[available], use_container_width=True)
