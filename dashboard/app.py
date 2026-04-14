import streamlit as st
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from pipeline.orchestrator import PipelineOrchestrator

def init_session_state():
    #Initialize Streamlit session state with analysis results
    if "results" not in st.session_state:
        st.session_state.results = None
    if "settings" not in st.session_state:
        st.session_state.settings = Settings()

def load_data():
    #Load and cache analysis results
    if st.session_state.results is None:
        with st.spinner("Running analysis pipeline..."):
            orchestrator = PipelineOrchestrator(st.session_state.settings)
            st.session_state.results = orchestrator.run_analysis_only()
    return st.session_state.results

def main():
    st.set_page_config(
        page_title="GitHub Pipeline Analysis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_session_state()
    # Sidebar navigation
    st.sidebar.title("GitHub Pipeline Analysis")
    st.sidebar.markdown("Programming for Data Analysis Project")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate",
        [
            "Overview",
            "Repository Scores",
            "Time-Series Analysis",
            "Contributor Insights",
            "Community Health",
        ],
    )

    # Sidebar actions
    st.sidebar.markdown("---")
    if st.sidebar.button("Refresh Data"):
        st.session_state.results = None
        st.rerun()

    # Load data
    results = load_data()

    if not results:
        st.error("No data available. Please run the collection pipeline first:")
        st.code("python main.py --mode full", language="bash")
        return

    # Route to pages
    if page == "Overview":
        from dashboard.pages.overview import render_overview
        render_overview(results)
    elif page == "Repository Scores":
        from dashboard.pages.repository_scores import render_repository_scores
        render_repository_scores(results)
    elif page == "Time-Series Analysis":
        from dashboard.pages.time_series_page import render_time_series
        render_time_series(results)
    elif page == "Contributor Insights":
        from dashboard.pages.contributor_insights import render_contributor_insights
        render_contributor_insights(results)
    elif page == "Community Health":
        from dashboard.pages.community_page import render_community
        render_community(results)

if __name__ == "__main__":
    main()
