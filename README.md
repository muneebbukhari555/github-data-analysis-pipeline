# GitHub Pipeline Analysis

**Programming for Data Analysis — MSc Project**

A data engineering pipeline that collects, processes, and analyzes open-source GitHub repository data. Uses feature engineering to extract metrics from nested API JSON, computes multi-dimensional scores, and presents insights through a Streamlit dashboard. Historical snapshots in MongoDB enable time-series trend analysis.

---

## Architecture

```
github-pipeline-analysis/
├── config/             # Settings dataclass, env variable loading
├── models/             # Repository, Contributor, Commit data models
├── collectors/         # GitHub API collectors with pagination & rate-limit handling
├── database/           # MongoDB: connection, repository store, snapshot store
├── analysis/           # Feature engineering, scoring, time-series, contributors, community
├── pipeline/           # Orchestrator coordinating collection → storage → analysis
├── dashboard/          # Streamlit app (5 pages) with Plotly charts
│   ├── pages/          # Overview, Scores, Time-Series, Contributors, Community
│   └── components/     # Reusable chart and metric display components
├── tests/              # Unit tests for models, features, and scoring
├── .github/workflows/  # CI/CD pipeline + scheduled data collection (every 6 hours)
├── docker-compose.yml  # MongoDB + Dashboard + Collector containers
├── Dockerfile          # App container image
└── main.py             # CLI entry point (full / collect / analyze modes)
```

---

## Pipeline Flow

```
GitHub API  →  Collectors  →  MongoDB  →  Feature Engineering  →  Scoring  →  Dashboard
(raw JSON)     (paginated)   (stored)     (numerical features)   (0-100)     (5 pages)
```

Data is collected from the GitHub REST API every 6 hours via GitHub Actions. Raw nested JSON is stored in MongoDB. When the dashboard loads, it reads the latest data, runs feature engineering and scoring in memory, and renders all charts.

---

## Repositories Analysed

Kubernetes, PyTorch, Ansible, scikit-learn, TensorFlow, Apache Spark, Docker Compose, Prometheus

---

## Feature Engineering

Four groups of features are extracted from raw API data:

### 1: Temporal Features (from date strings)

The API returns dates as strings like `"2014-11-07T00:00:00Z"`. These are parsed and used to compute:

```
age_days          = today − created_at
stars_per_day     = stars ÷ age_days          # growth rate, fairer than raw stars
forks_per_day     = forks ÷ age_days
days_since_update = today − updated_at
active_lifespan   = 1 − (days_since_update ÷ age_days)
```

> **Why stars_per_day?** Raw star count is unfair across repos of different ages. A 2-year-old repo with 50K stars is growing faster than a 10-year-old repo with 80K stars. Dividing by age normalises this.

---

### 2: Contributor Features (from nested list)

The API returns contributors as a list of objects:

```json
contributors = [
  { "login": "alice",   "contributions": 500 },
  { "login": "bob",     "contributions": 300 },
  { "login": "charlie", "contributions": 200 }
]
```

Extracted features:

```
contributors_count         = len(contributors list)
total_contributions        = sum of all contributions
avg_contributions_per_person = total ÷ count
top_contributor_share      = max(contributions) ÷ total   # bus factor proxy
contributor_diversity      = fraction with >1% share      # spread of work
```

> **top_contributor_share** is key. If one person wrote 80% of the code, the project collapses if they leave. Low share = resilient. High share = risky.

---

### 3: Commit Features (from deeply nested JSON)

Each commit has author information at two different nesting levels:

```json
{
  "sha": "abc123",
  "commit": {
    "author": {
      "name": "Linus",
      "date": "2024-01-15T10:30:00Z"    ← buried 3 levels deep
    }
  },
  "author": { "login": "torvalds" }      ← at the top level
}
```

Extracted features:

```
commit_count          = total commits in fetched window (up to 500)
commit_frequency      = commit_count ÷ (last_date − first_date) in days
active_commit_days    = distinct calendar days with commits
unique_commit_authors = distinct login values
commits_per_author    = commit_count ÷ unique_commit_authors
```

> **Commit frequency is time-window based** — measured over the span of the fetched commits (first to last date), not the repository's total age. This reflects current velocity, not historical average.

---

### 4: Derived Metrics (combining the above)

Higher-order signals computed from the base features:

```
engagement_ratio     = forks ÷ stars
```
Stars mean people like it. Forks mean people actively use and extend it. High ratio = active community, not passive.

```
stability_score      = stars ÷ open_issues
```
Many stars + few issues = popular and well-maintained. High issue count relative to stars = struggling to keep up.

```
bus_factor_estimate  = 1 ÷ top_contributor_share
```
If one person wrote 50% of the code: 1 ÷ 0.5 = 2. Roughly how many people the project can afford to lose.

---

## Multi-Dimensional Scoring

All scores use **percentile-rank normalisation** — each repo is ranked relative to the other repos on a 0–1 scale per feature, then combined using weighted sums, scaled to 0–100.

### Activity Score — *How actively is code being written?*

| Feature | Weight |
|---|---|
| Commit count | 35% |
| Commit frequency | 25% |
| Active commit days | 20% |
| Unique commit authors | 20% |

### Success Score — *How popular and adopted is the project?*

| Feature | Weight |
|---|---|
| Stars | 40% |
| Forks | 30% |
| Contributors count | 20% |
| Watchers | 10% |

### Developer Influence Score — *How productive is each individual?*

| Feature | Weight |
|---|---|
| Total contributions | 30% |
| Average contributions per person | 25% |
| Contribution efficiency | 25% |
| Commits per author | 20% |

### Community Strength Score — *How resilient is the community?*

| Feature | Weight |
|---|---|
| Contributors count | 25% |
| Contributor diversity | 25% |
| Engagement ratio | 20% |
| Bus factor estimate | 15% |
| Active lifespan ratio | 15% |

### Overall Score

```
Activity Score      × 30%
Success Score       × 25%
Community Score     × 25%
Influence Score     × 20%
──────────────────────────
Overall Score  (0–100)
```


---

## Community Health Grading

Each repository is graded A+ to F across four sub-scores, each equally weighted at 25%:

| Sub-score | Inputs | What it measures |
|---|---|---|
| Community Size | contributors (40%), stars (30%), forks (30%) | How large is the community |
| Diversity Index | Gini coefficient of contribution distribution | How evenly spread is the work |
| Engagement Quality | engagement_ratio (40%), commit_frequency (30%), unique_authors (30%) | How actively engaged is the community |
| Resilience Score | (1 − top_contributor_share) (50%), contributors_count (30%), diversity (20%) | How safe is it if key people leave |

**Community Total = (Size + Diversity + Engagement + Resilience) ÷ 4**

**Grade thresholds:** A+ ≥ 90 · A ≥ 80 · B+ ≥ 70 · B ≥ 60 · C+ ≥ 50 · C ≥ 40 · D ≥ 30 · F < 30

---

## Time Windows Used

| Page | Window Applied |
|---|---|
| Overview, Scores, Contributors, Community | Up to 500 most recent commits · Up to 300 contributors |
| Commit frequency | Span between first and last commit in fetched set (not repo age) |
| Time-Series snapshots | 90-day lookback on MongoDB snapshot history |
| All scores | Point-in-time from latest pipeline collection |

---

## MongoDB Collections

- **repositories** — Full raw nested JSON from each pipeline run (contributors list, commits list, all metadata preserved as-is)
- **snapshots** — Lightweight numeric summaries with timestamps (stars, forks, issues, contributor count) stored every 6 hours for longitudinal trend analysis



---

## Dashboard Pages

| Page | What It Shows |
|---|---|
| Overview | Score rankings, stars vs forks scatter, dimension leaders, language distribution |
| Repository Scores | Radar chart per repo, feature breakdown, two-repo comparison |
| Time-Series | Monthly commit timelines, velocity trends, activity heatmap, historical growth |
| Contributor Insights | Top contributors, top committers, cross-repo participation, dominance analysis |
| Community Health | A+–F grades, Gini diversity, resilience scores, engagement quality |

---

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env           # add GITHUB_TOKEN
python main.py --mode full     # collect + store + analyze
streamlit run dashboard/app.py
```

## Pipeline Modes

```bash
python main.py --mode full      # Collect from GitHub API + Store + Analyze
python main.py --mode collect   # Only collect and store
python main.py --mode analyze   # Only analyze (requires existing data in MongoDB)
```

## Deployment

```bash
docker compose up -d                                      # Start MongoDB + Dashboard
docker compose --profile collect run --rm collector       # Run data collection
```

CI/CD via GitHub Actions: push to `main` → tests → Docker build → push to Docker Hub → deploy to Azure VM. Data collection runs automatically every 6 hours.

## Tech Stack

Python · Pandas · NumPy · Requests · PyMongo · Streamlit · Plotly · MongoDB · Docker · GitHub Actions
