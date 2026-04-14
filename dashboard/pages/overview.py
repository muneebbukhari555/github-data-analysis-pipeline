import streamlit as st
import pandas as pd
from dashboard.components.metrics import display_metric_row, format_number, display_insights_list
from dashboard.components.charts import create_bar_chart, create_scatter_chart


def render_overview(results: dict):
    #Render the overview dashboard page.
    st.title("GitHub Pipeline Analysis Overview")
    st.markdown("Multi dimensional analysis of open-source repository health and performance.")

    df = results.get("df")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    # --- Key Metrics Row ---
    st.markdown("### Key Metrics")
    display_metric_row({
        "Repositories Analyzed": len(df),
        "Total Stars": format_number(df["stars"].sum()),
        "Total Forks": format_number(df["forks"].sum()),
        "Total Contributors": format_number(df["contributors_count"].sum()),
        "Total Commits Analyzed": format_number(df["commit_count"].sum()),
    })

    st.markdown("---")

    # --- Overall Score Ranking ---
    col1, col2 = st.columns(2)

    with col1:
        if "overall_score" in df.columns:
            chart_df = df[["name", "overall_score"]].sort_values("overall_score", ascending=True)
            fig = create_bar_chart(
                chart_df, x="overall_score", y="name",
                title="Overall Score Ranking",
                orientation="h", height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "stars" in df.columns and "forks" in df.columns:
            fig = create_scatter_chart(
                df, x="stars", y="forks",
                title="Stars vs Forks (size = contributors)",
                size="contributors_count",
                hover_name="name",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Dimension Leaders ---
    leaders = results.get("dimension_leaders", {})
    if leaders:
        st.markdown("### Dimension Leaders")
        cols = st.columns(len(leaders))
        for col, (dim, repo) in zip(cols, leaders.items()):
            col.metric(dim, repo.split("/")[-1])

    st.markdown("---")

    # --- Score Summary Table ---
    score_summary = results.get("score_summary")
    if score_summary is not None and not score_summary.empty:
        st.markdown("### Repository Score Summary")
        st.dataframe(
            score_summary.style.format({
                col: "{:.1f}" for col in score_summary.columns if "score" in col
            }),
            use_container_width=True,
            height=350,
        )

    # --- Community Insights ---
    insights = results.get("community_insights", [])
    if insights:
        st.markdown("### Community Insights")
        display_insights_list(insights)

    # --- Language Distribution ---
    if "language" in df.columns:
        st.markdown("### Language Distribution")
        lang_df = df.groupby("language")["stars"].sum().reset_index()
        lang_df = lang_df.sort_values("stars", ascending=False)
        fig = create_bar_chart(
            lang_df, x="language", y="stars",
            title="Total Stars by Language",
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
