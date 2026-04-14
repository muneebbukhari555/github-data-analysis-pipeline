# GitHub Pipeline Analysis

**Programming for Data Analysis Project**

A data engineering pipeline that collects, processes, and analyzes open-source GitHub repository data. Uses feature engineering to extract metrics from nested API JSON, computes multi-dimensional scores, and presents insights through a Streamlit dashboard. Historical snapshots in MongoDB enable time-series trend analysis.

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
├── .github/workflows/  # CI/CD pipeline + scheduled data collection
├── docker-compose.yml  # MongoDB + Dashboard + Collector containers
├── Dockerfile          # App container image
└── main.py             # CLI entry point (full / collect / analyze modes)
```

## What It Does

**Data Acquisition** — Collects repository metadata, contributor lists, and commit history from the GitHub REST API for 8 major open-source projects (Kubernetes, PyTorch, TensorFlow, etc.). Handles pagination, rate limiting, and error recovery.

**Feature Engineering** — Transforms nested JSON into numerical features across four categories:
- Temporal: age_days, stars_per_day, active_lifespan_ratio
- Contributor: contributors_count, total_contributions, top_contributor_share, diversity
- Commit: commit_frequency (time-window based), active_commit_days, unique_commit_authors
- Derived: engagement_ratio, stability_score, bus_factor_estimate, community_health

**Multi-Dimensional Scoring** — Computes four independent scores using percentile-rank normalization:
- Activity Score (development velocity)
- Success Score (popularity and adoption)
- Developer Influence Score (contribution quality and depth)
- Community Strength Score (health, diversity, resilience)
- Overall Score (weighted composite: 30/25/25/20)

**Analysis** — Time-series commit timelines, velocity trend detection, person-level contributor insights, cross-repo participation, contributor dominance, and community health grading (A+ to F).

**Dashboard** — 5-page Streamlit app with radar charts, bar charts, scatter plots, heatmaps, and community grade cards.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Set GITHUB_TOKEN and MONGO_URI in .env

# Run full pipeline (collect + analyze)
python main.py --mode full

# Launch dashboard
streamlit run dashboard/app.py
```

## Pipeline Modes

```bash
python main.py --mode full      # Collect from GitHub API + Store + Analyze
python main.py --mode collect   # Only collect and store data
python main.py --mode analyze   # Only run analysis (requires existing data)
```

## Deployment (Docker Compose)

```bash
# Start MongoDB + Dashboard
docker compose up -d

# Run data collection
docker compose --profile collect run --rm collector
```

The GitHub Actions CI/CD pipeline automatically builds, tests, pushes to Docker Hub, and deploys to the AWS VM on every push to main. A separate scheduled workflow triggers data collection every 6 hours.

## MongoDB Collections

- **repositories** — Full nested JSON from each pipeline run (raw API data preserved)
- **snapshots** — Lightweight time-series metrics (stars, forks, issues, contributors) with timestamps for longitudinal growth analysis

## Tech Stack

Python, Pandas, NumPy, Requests, PyMongo, Streamlit, Plotly, MongoDB, Docker, GitHub Actions
