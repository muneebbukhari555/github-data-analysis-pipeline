import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, List

def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    orientation: str = "v",
    height: int = 400,
) -> go.Figure:
    """Create a styled bar chart."""
    fig = px.bar(
        df, x=x, y=y, title=title, color=color,
        orientation=orientation, height=height,
        color_continuous_scale="Viridis",
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(size=12),
        title_font_size=16,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig

def create_scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    size: Optional[str] = None,
    color: Optional[str] = None,
    hover_name: Optional[str] = None,
    height: int = 400,
) -> go.Figure:
    """Create a styled scatter plot."""
    fig = px.scatter(
        df, x=x, y=y, title=title,
        size=size, color=color, hover_name=hover_name,
        height=height,
        color_continuous_scale="Viridis",
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(size=12),
        title_font_size=16,
    )
    return fig

def create_radar_chart(
    categories: List[str],
    values: List[float],
    title: str,
    height: int = 400,
) -> go.Figure:
    """Create a radar/spider chart for multi-dimensional scoring."""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(99, 110, 250, 0.2)",
        line=dict(color="rgb(99, 110, 250)", width=2),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title=title,
        height=height,
        template="plotly_white",
        showlegend=False,
    )
    return fig

def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    height: int = 400,
) -> go.Figure:
    #Create a styled line chart for time-series data
    fig = px.line(
        df, x=x, y=y, title=title, color=color,
        height=height, markers=True,
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(size=12),
        title_font_size=16,
    )
    return fig


def create_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    title: str,
    height: int = 400,
) -> go.Figure:
    #Create a heatmap chart
    pivot = df.pivot_table(values=z, index=y, columns=x, fill_value=0)
    fig = px.imshow(
        pivot,
        title=title,
        height=height,
        color_continuous_scale="YlOrRd",
        aspect="auto",
    )
    fig.update_layout(template="plotly_white")
    return fig


def create_pie_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str,
    height: int = 350,
) -> go.Figure:
    #Create a styled pie/donut chart
    fig = px.pie(
        df, names=names, values=values, title=title,
        height=height, hole=0.4,
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(size=12),
    )
    return fig
