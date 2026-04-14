import streamlit as st
import pandas as pd
from typing import Any, Optional

def display_metric_row(metrics: dict):
    #Display a row of key metrics using st.metric.
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        if isinstance(value, tuple):
            col.metric(label, value[0], delta=value[1])
        else:
            col.metric(label, value)

def display_score_card(name: str, scores: dict):
    #Display a score card for a repository with all dimension scores
    with st.container():
        st.subheader(name)
        cols = st.columns(5)
        score_labels = [
            ("Overall", "overall_score"),
            ("Activity", "activity_score"),
            ("Success", "success_score"),
            ("Dev Influence", "developer_influence_score"),
            ("Community", "community_strength_score"),
        ]
        for col, (label, key) in zip(cols, score_labels):
            val = scores.get(key, 0)
            col.metric(label, f"{val:.1f}")

def display_dataframe_styled(
    df: pd.DataFrame,
    title: Optional[str] = None,
    height: int = 400,
):
    #Display a styled DataFrame with optional title.
    if title:
        st.subheader(title)
    st.dataframe(df, height=height, use_container_width=True)

def format_number(n: Any) -> str:
    #Format large numbers with K/M suffixes
    if not isinstance(n, (int, float)):
        return str(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))


def display_insights_list(insights: list):
    #Display community insights with appropriate icons
    icons = {"strength": "✅", "concern": "⚠️", "risk": "🔴"}
    for insight in insights:
        icon = icons.get(insight.get("type", ""), "ℹ️")
        st.markdown(f"{icon} **{insight.get('type', '').title()}**: {insight.get('message', '')}")
