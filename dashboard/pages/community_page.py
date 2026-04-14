import streamlit as st
import pandas as pd
from dashboard.components.charts import create_bar_chart, create_radar_chart, create_scatter_chart
from dashboard.components.metrics import display_metric_row, display_insights_list

def render_community(results: dict):
    #Render the community health page
    st.title("Community Health Analysis")
    st.markdown("Evaluating the strength, diversity, and resilience of open-source communities.")

    df = results.get("df")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    if "community_grade" in df.columns:
        st.markdown("### Community Grades")

        # Display grades as colored badges
        cols = st.columns(len(df))
        for col, (_, row) in zip(cols, df.iterrows()):
            grade = row.get("community_grade", "N/A")
            score = row.get("community_total_score", 0)
            name = row["name"].split("/")[-1]
            grade_color = _grade_color(grade)
            col.markdown(
                f"<div style='text-align:center;padding:10px;background:{grade_color};"
                f"border-radius:8px;color:white;'>"
                f"<b>{name}</b><br/>{grade} ({score:.0f})</div>",
                unsafe_allow_html=True,
            )
    st.markdown("---")

    insights = results.get("community_insights", [])
    if insights:
        st.markdown("### Key Insights")
        display_insights_list(insights)
        st.markdown("---")

    community_summary = results.get("community_summary")
    if community_summary is not None and not community_summary.empty:
        st.markdown("### Detailed Community Scores")
        score_cols = [
            "community_size_score", "diversity_index_score",
            "engagement_quality_score", "resilience_score"
        ]
        available = [c for c in score_cols if c in community_summary.columns]
        if available:
            st.dataframe(
                community_summary.style.format({
                    col: "{:.1f}" for col in available + ["community_total_score"]
                    if col in community_summary.columns
                }),
                use_container_width=True,
                height=350,
            )
    st.markdown("---")

    st.markdown("### Score Breakdown by Dimension")
    col1, col2 = st.columns(2)
    with col1:
        if "community_size_score" in df.columns:
            chart_df = df[["name", "community_size_score"]].sort_values("community_size_score", ascending=True)
            fig = create_bar_chart(
                chart_df, x="community_size_score", y="name",
                title="Community Size Score",
                orientation="h", height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
        if "engagement_quality_score" in df.columns:
            chart_df = df[["name", "engagement_quality_score"]].sort_values("engagement_quality_score", ascending=True)
            fig = create_bar_chart(
                chart_df, x="engagement_quality_score", y="name",
                title="Engagement Quality Score",
                orientation="h", height=350,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "diversity_index_score" in df.columns:
            chart_df = df[["name", "diversity_index_score"]].sort_values("diversity_index_score", ascending=True)
            fig = create_bar_chart(
                chart_df, x="diversity_index_score", y="name",
                title="Diversity Index Score",
                orientation="h", height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
        if "resilience_score" in df.columns:
            chart_df = df[["name", "resilience_score"]].sort_values("resilience_score", ascending=True)
            fig = create_bar_chart(
                chart_df, x="resilience_score", y="name",
                title="Resilience Score",
                orientation="h", height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    st.markdown("### Community Profile (Radar)")
    repo_names = df["name"].tolist()
    selected = st.selectbox("Select Repository", repo_names, key="community_radar")
    repo_data = df[df["name"] == selected].iloc[0]
    dimensions = {
        "Size": repo_data.get("community_size_score", 0),
        "Diversity": repo_data.get("diversity_index_score", 0),
        "Engagement": repo_data.get("engagement_quality_score", 0),
        "Resilience": repo_data.get("resilience_score", 0),
    }
    fig = create_radar_chart(
        categories=list(dimensions.keys()),
        values=list(dimensions.values()),
        title=f"Community Profile: {selected}",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    
    st.markdown("### Engagement Quality vs Resilience")
    if "engagement_quality_score" in df.columns and "resilience_score" in df.columns:
        fig = create_scatter_chart(
            df, x="engagement_quality_score", y="resilience_score",
            title="Community Engagement vs Resilience",
            size="contributors_count",
            hover_name="name",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)


def _grade_color(grade: str) -> str:
    """Map community grade to a background color."""
    colors = {
        "A+": "#1b5e20", "A": "#2e7d32", "B+": "#558b2f",
        "B": "#9e9d24", "C+": "#f9a825", "C": "#ff8f00",
        "D": "#e65100", "F": "#b71c1c",
    }
    return colors.get(grade, "#757575")
