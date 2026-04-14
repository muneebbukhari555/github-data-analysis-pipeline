import streamlit as st
import pandas as pd
from dashboard.components.charts import create_radar_chart, create_bar_chart, create_scatter_chart
from dashboard.components.metrics import display_metric_row

def render_repository_scores(results: dict):
    #Render the repository scores page
    st.title("Repository Scores — Multi-Dimensional Analysis")
    df = results.get("df")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    repo_names = df["name"].tolist()
    selected_repo = st.selectbox("Select Repository", repo_names)
    repo_data = df[df["name"] == selected_repo].iloc[0]

    st.markdown("### Score Profile")
    col1, col2 = st.columns([2, 1])
    score_dimensions = {
        "Activity": repo_data.get("activity_score", 0),
        "Success": repo_data.get("success_score", 0),
        "Dev Influence": repo_data.get("developer_influence_score", 0),
        "Community": repo_data.get("community_strength_score", 0),
    }
    with col1:
        fig = create_radar_chart(
            categories=list(score_dimensions.keys()),
            values=list(score_dimensions.values()),
            title=f"Score Profile: {selected_repo}",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("#### Scores")
        for dim, score in score_dimensions.items():
            st.metric(dim, f"{score:.1f}/100")
        st.metric("Overall", f"{repo_data.get('overall_score', 0):.1f}/100")
        if "overall_score_rank" in repo_data:
            st.metric("Rank", f"#{int(repo_data['overall_score_rank'])} of {len(df)}")
    st.markdown("---")

    st.markdown("### Feature Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Repository Metrics**")
        display_metric_row({
            "Stars": f"{repo_data.get('stars', 0):,}",
            "Forks": f"{repo_data.get('forks', 0):,}",
        })
        display_metric_row({
            "Age (days)": f"{repo_data.get('age_days', 0):,}",
            "Stars/day": f"{repo_data.get('stars_per_day', 0):.2f}",
        })
    with col2:
        st.markdown("**Activity Metrics**")
        display_metric_row({
            "Commits": repo_data.get("commit_count", 0),
            "Frequency": f"{repo_data.get('commit_frequency', 0):.2f}/day",
        })
        display_metric_row({
            "Active Days": repo_data.get("active_commit_days", 0),
            "Authors": repo_data.get("unique_commit_authors", 0),
        })

    with col3:
        st.markdown("**Community Metrics**")
        display_metric_row({
            "Contributors": repo_data.get("contributors_count", 0),
            "Engagement": f"{repo_data.get('engagement_ratio', 0):.3f}",
        })
        display_metric_row({
            "Bus Factor": f"{repo_data.get('bus_factor_estimate', 0):.1f}",
            "Top Share": f"{repo_data.get('top_contributor_share', 0):.1%}",
        })
    st.markdown("---")

    st.markdown("### Comparison Across All Repositories")
    tab1, tab2, tab3, tab4 = st.tabs(["Activity", "Success", "Dev Influence", "Community"])
    with tab1:
        score_col = "activity_score"
        if score_col in df.columns:
            chart_df = df[["name", score_col]].sort_values(score_col, ascending=True)
            fig = create_bar_chart(
                chart_df, x=score_col, y="name",
                title="Activity Score Comparison",
                orientation="h",
            )
            st.plotly_chart(fig, use_container_width=True)
    with tab2:
        score_col = "success_score"
        if score_col in df.columns:
            chart_df = df[["name", score_col]].sort_values(score_col, ascending=True)
            fig = create_bar_chart(
                chart_df, x=score_col, y="name",
                title="Success Score Comparison",
                orientation="h",
            )
            st.plotly_chart(fig, use_container_width=True)
    with tab3:
        score_col = "developer_influence_score"
        if score_col in df.columns:
            chart_df = df[["name", score_col]].sort_values(score_col, ascending=True)
            fig = create_bar_chart(
                chart_df, x=score_col, y="name",
                title="Developer Influence Comparison",
                orientation="h",
            )
            st.plotly_chart(fig, use_container_width=True)
    with tab4:
        score_col = "community_strength_score"
        if score_col in df.columns:
            chart_df = df[["name", score_col]].sort_values(score_col, ascending=True)
            fig = create_bar_chart(
                chart_df, x=score_col, y="name",
                title="Community Strength Comparison",
                orientation="h",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Compare Two Repositories")
    col1, col2 = st.columns(2)
    with col1:
        repo_a = st.selectbox("Repository A", repo_names, index=0, key="compare_a")
    with col2:
        repo_b = st.selectbox("Repository B", repo_names, index=min(1, len(repo_names) - 1), key="compare_b")

    if repo_a != repo_b:
        data_a = df[df["name"] == repo_a].iloc[0]
        data_b = df[df["name"] == repo_b].iloc[0]
        dimensions = ["Activity", "Success", "Dev Influence", "Community"]
        score_keys = ["activity_score", "success_score", "developer_influence_score", "community_strength_score"]
        import plotly.graph_objects as go
        fig = go.Figure()
        for data, name in [(data_a, repo_a), (data_b, repo_b)]:
            values = [data.get(k, 0) for k in score_keys]
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=dimensions + [dimensions[0]],
                fill="toself",
                name=name.split("/")[-1],
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title=f"Comparison: {repo_a.split('/')[-1]} vs {repo_b.split('/')[-1]}",
            height=450,
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)
