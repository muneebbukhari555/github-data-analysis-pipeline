# AI Assistance Disclosure

This folder documents where and how AI tooling (Claude by Anthropic) was used during
the development of this project. Each file maps to a specific module or layer of the
codebase and describes the split between AI-generated code and student-directed decisions.

---

## Summary Table

| File | Module Covered | AI Contribution Level | My Contribution |
|---|---|---|---|
| [analysis-feature-engineering.md](./analysis-feature-engineering.md) | `analysis/feature_engineering.py` | Code implementation | Feature selection, time-window decision, bus factor concept |
| [analysis-scoring.md](./analysis-scoring.md) | `analysis/scoring.py` | Code implementation | All weight values, normalisation method choice |
| [analysis-community.md](./analysis-community.md) | `analysis/community_analysis.py`, `contributor_analysis.py`, `time_series.py` | Code + Gini formula | Grade thresholds, 4 sub-score weights, 90-day window |
| [collectors.md](./collectors.md) | `collectors/` | Rate-limit + pagination code | Endpoint selection, 100-commit limit, `anon=false` decision |
| [database.md](./database.md) | `database/` | Query syntax, upsert, indexes | MongoDB choice, two-collection design, snapshot field selection |
| [dashboard.md](./dashboard.md) | `dashboard/` | Plotly/Streamlit chart code | 5-page layout, chart type choices, grade card design |
| [pipeline-and-models.md](./pipeline-and-models.md) | `pipeline/`, `models/`, `config/` | Dataclass patterns, argparse | Three CLI modes, field selections, env-var security requirement |
| [deployment.md](./deployment.md) | `Dockerfile`, `docker-compose.yml`, `.github/workflows/` | Docker/YAML syntax | Azure correction, image pull fix, 6-hour frequency, service design |
| [tests.md](./tests.md) | `tests/` | Fixture patterns, assertions | Edge case specification, fixture values |

---

## Overall Contribution Split

**AI generated:** boilerplate class structures, Python syntax, pandas/NumPy operations,
Docker Compose YAML, GitHub Actions YAML, Plotly chart code, MongoDB query syntax,
statistical formula implementations (Gini coefficient, percentile ranking).

**I directed and decided:**
- What the project analyses (ML framework GitHub repositories)
- Which metrics matter and why (bus factor, contributor diversity, commit velocity)
- All scoring weights across all four dimensions (specified to AI)
- The time-window approach for commit frequency (not repo age)
- MongoDB over relational database (nested JSON reasoning)
- Two-collection design (repositories vs. snapshots)
- 90-day lookback window for time-series
- 6-hour collection frequency (API rate limit reasoning)
- All five dashboard pages and their visual layouts
- Three CLI modes for the pipeline
- Azure corrections (not AWS) throughout deployment config
- Docker image pull from Docker Hub rather than building on VM

AI was used as a coding tool — equivalent to using a documentation resource or a code
assistant — while all problem scoping, architectural choices, metric definitions, and
technical understanding remain my own. I can explain every formula, every weight, and
every design decision in this project.

---

## AI Tool Used
AI assistant — Both Inline and conversational AI used for code generation and Readme files
given my specifications:
- https://chatgpt.com/share/69debc53-02a8-8330-a226-bb051a0cccfa
- https://chatgpt.com/share/69debcbf-30b8-8326-aa1d-fd95b5025919
- https://chatgpt.com/g/g-p-697235e1df0881919f87eee4a5e4386f/c/69d83487-2468-832a-aa1a-fe2c2523f46c
