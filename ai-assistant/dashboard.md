# AI Assistance — `dashboard/`

## Files Covered
- `app.py` — Streamlit entry point, page routing, sidebar navigation
- `pages/overview.py` — Page 1: top-level repo comparison and metric cards
- `pages/repository_scores.py` — Page 2: radar chart + dimension score breakdown
- `pages/time_series_page.py` — Page 3: score trends over 90 days
- `pages/contributor_insights.py` — Page 4: contributor leaderboard and distribution
- `pages/community_page.py` — Page 5: community health grades and sub-scores
- `components/charts.py` — reusable Plotly chart builders
- `components/metrics.py` — reusable metric card and KPI display components

---

## What AI Helped With

### 1. Streamlit Multi-Page Architecture (`app.py`)
AI set up the multi-page structure using `st.sidebar.radio()` for navigation between
5 pages. Each page is a separate module imported and called based on the user's
selection. AI used `@st.cache_resource` for the MongoDB connection so it is not
reopened on every Streamlit re-render:
```python
@st.cache_resource
def get_connection():
    return MongoConnection.get_instance()
```
**My decision:** I specified 5 pages and their names. I chose to keep MongoDB
connection logic inside the app rather than a separate API layer because the
dashboard and database run inside the same Docker network.

### 2. Radar Chart for Dimension Scores (`pages/repository_scores.py`)
AI built the radar chart using Plotly's `go.Scatterpolar`:
```python
fig = go.Figure()
for repo in selected_repos:
    fig.add_trace(go.Scatterpolar(
        r=[scores],
        theta=dimensions,
        fill='toself',
        name=repo
    ))
```
I specified that I wanted a radar chart because it allows comparing multiple repos
across all four dimensions simultaneously on a single visual.

### 3. Time-Series Line Chart (`pages/time_series_page.py`)
AI built the 90-day trend chart from snapshot data returned by `snapshot_store.py`.
It uses `plotly.express.line` with date on the x-axis and score on the y-axis.
AI added a date range selector widget (`st.date_input`) so users can zoom into
a specific period within the 90-day window.

**My decision:** I chose score on y-axis (not raw stars) because scores are
normalised and comparable across all repos, while raw metrics are not.

### 4. Contributor Bar Chart and Gini Display (`pages/contributor_insights.py`)
AI built a horizontal bar chart showing top contributors by total contributions.
For the Gini coefficient display, AI used `st.metric()` with a delta arrow showing
whether diversity is above or below average across repos.

### 5. Community Health Grade Cards (`pages/community_page.py`)
AI built the grade display using `st.columns()` to show each repo as a card with:
- The letter grade (A+, B, F, etc.) in large text
- Four sub-scores displayed as progress bars (`st.progress()`)
- A colour-coded background based on grade tier

I specified the visual layout — I wanted card-style display rather than a table
because grades are easier to scan visually.

### 6. Reusable Chart Components (`components/charts.py`, `components/metrics.py`)
AI extracted repeated Plotly and Streamlit patterns into reusable functions so each
page module stays clean. For example, `render_metric_card()` accepts a label, value,
and optional delta and always formats them consistently. This was an AI suggestion
for code quality — I accepted it because it reduces duplication across 5 pages.

---

## What I Did

- Defined all 5 pages and what each should show before writing any code
- Specified radar chart for Page 2 (comparing dimensions visually)
- Chose 90 days as the time-series window (Page 3)
- Specified card layout with grade letters for Page 5 (community health)
- Tested all 5 pages locally against live MongoDB data and verified the
  numbers matched my manual calculations (e.g. TensorFlow community score ~70)
- Decided the sidebar should list pages by name not by number for clarity

---

## AI Tool Used
AI assistant — used for Plotly chart code, Streamlit widget layout, and
component extraction. All page content decisions, chart type choices, and
visual layout specifications were mine.
