import streamlit as st
import pandas as pd
from dashboard.components.charts import create_bar_chart, create_scatter_chart, create_pie_chart
from dashboard.components.metrics import display_metric_row, format_number

def render_contributor_insights(results: dict):
    #Render the contributor insights page
    st.title("Contributor Insights — Person-Level Analytics")
    df = results.get("df")
    if df is None or df.empty:
        st.warning("No data available.")
        return
    
    st.markdown("### Contributor Overview")
    total_contributors = df["contributors_count"].sum() if "contributors_count" in df.columns else 0
    total_contributions = df["total_contributions"].sum() if "total_contributions" in df.columns else 0
    unique_authors = df["unique_commit_authors"].sum() if "unique_commit_authors" in df.columns else 0
    display_metric_row({
        "Total Contributors": format_number(total_contributors),
        "Total Contributions": format_number(total_contributions),
        "Unique Commit Authors": format_number(unique_authors),
    })
    st.markdown("---")

    top_contribs = results.get("top_contributors")
    if top_contribs is not None and not top_contribs.empty:
        st.markdown("### Top Contributors Across All Repositories")

        col1, col2 = st.columns([2, 1])
        with col1:
            chart_df = top_contribs.head(15)
            fig = create_bar_chart(
                chart_df, x="total_contributions", y="login",
                title="Top 15 Contributors by Total Contributions",
                color="repo_count",
                orientation="h", height=500,
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("#### Details")
            st.dataframe(
                top_contribs.head(15)[["login", "total_contributions", "repo_count"]],
                use_container_width=True,
                height=450,
            )
    st.markdown("---")

    top_committers = results.get("top_committers")
    if top_committers is not None and not top_committers.empty:
        st.markdown("### Top Recent Committers (from commit history)")
        fig = create_bar_chart(
            top_committers.head(15), x="recent_commits", y="login",
            title="Most Active Recent Committers",
            orientation="h", height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    dominance = results.get("contributor_dominance")
    if dominance is not None and not dominance.empty:
        st.markdown("### Contributor Dominance per Repository")
        st.markdown("High dominance = single contributor dependency risk (low bus factor).")
        col1, col2 = st.columns(2)
        with col1:
            fig = create_bar_chart(
                dominance.sort_values("top1_contribution_share", ascending=True),
                x="top1_contribution_share", y="name",
                title="Top Contributor's Share of Contributions",
                orientation="h", height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(
                dominance[["name", "top_contributor", "top1_contribution_share",
                           "top5_contribution_share", "dominance_level"]],
                use_container_width=True,
                height=350,
            )
    st.markdown("---")

    cross_repo = results.get("cross_repo_contributors")
    if cross_repo is not None and not cross_repo.empty:
        st.markdown("### Cross-Repository Contributors")
        st.markdown("Developers contributing to multiple analyzed repositories.")
        st.dataframe(cross_repo, use_container_width=True, height=300)
    st.markdown("---")

    influence = results.get("developer_influence")
    if influence is not None and not influence.empty:
        st.markdown("### Developer Influence Scores")
        st.markdown("Composite score based on contribution volume, repo diversity, and concentration.")
        fig = create_scatter_chart(
            influence.head(30),
            x="total_contributions", y="influence_score",
            title="Contributions vs Influence Score",
            size="repo_count",
            hover_name="login",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            influence.head(20)[["login", "total_contributions", "repo_count",
                                "influence_score", "volume_score", "diversity_score"]],
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("### Per-Repository Contributor Details")
    if "contributors_count" in df.columns:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_bar_chart(
                df.sort_values("contributors_count", ascending=True),
                x="contributors_count", y="name",
                title="Contributors Count by Repository",
                orientation="h", height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if "avg_contributions_per_person" in df.columns:
                fig = create_bar_chart(
                    df.sort_values("avg_contributions_per_person", ascending=True),
                    x="avg_contributions_per_person", y="name",
                    title="Average Contributions per Person",
                    orientation="h", height=400,
                )
                st.plotly_chart(fig, use_container_width=True)
