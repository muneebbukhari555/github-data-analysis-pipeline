# AI Assistance: `analysis/community_analysis.py` · `analysis/contributor_analysis.py` · `analysis/time_series.py`

## File Purpose
Three specialist analysis modules:
- **community_analysis.py** — four sub-score community health system with grading
- **contributor_analysis.py** — per-contributor breakdowns, top-N rankings, Gini coefficient
- **time_series.py** — trend analysis using 90-day historical snapshots from MongoDB

---

## community_analysis.py

### What AI Helped With

**Community Health Grade Thresholds**
AI implemented the grade mapping (A+ ≥ 90, A ≥ 80, B+ ≥ 70, … F < 30) as a sorted
list of tuples, which is a cleaner pattern than a long if-elif chain. I specified all
the grade boundaries based on a standard academic grading analogy I wanted to follow.

**Four Sub-Score Structure**
AI structured the four sub-scores as separate methods:
- `_compute_size_score` — contributors 40%, stars 30%, forks 30%
- `_compute_diversity_index` — Gini coefficient, inverted
- `_compute_engagement_quality` — engagement_ratio 40%, commit_frequency 30%, unique authors 30%
- `_compute_resilience_score` — (1 − top_contributor_share) 50%, contributors 30%, diversity 20%

Each uses the same percentile-rank normalisation as `scoring.py`. I specified all weight
values. AI implemented the method structure.

**Gini Coefficient Calculation**
AI implemented the Gini formula for measuring contribution inequality:
```python
sorted_c = np.sort(contributions)
n = len(sorted_c)
gini = (2 * np.sum((np.arange(1, n+1)) * sorted_c) - (n + 1) * sorted_c.sum()) / (n * sorted_c.sum())
diversity_index = 1 - gini  # invert: higher = more equal
```
I had described wanting a measure where equal contributions = high score and one person
dominating = low score. AI identified Gini as the standard statistical tool for this and
implemented it.

**My decision:** I chose to invert the Gini coefficient (1 − Gini) so the metric reads
intuitively: higher diversity score = healthier community.

---

## contributor_analysis.py

### What AI Helped With

**Top-N Contributor Extraction**
AI wrote the `get_top_contributors()` method that flattens the nested contributors list
across all repos, aggregates by login, and returns the top N by total contributions.
The aggregation uses pandas groupby which AI suggested for efficiency.

**Contribution Share Calculation**
For each contributor, AI computed their share as a percentage of the total across all
repos — used to display the "X% of total contributions" stat in the dashboard.

### What I Did
Specified that contributor analysis should work across all repos combined (not per-repo)
so the dashboard can show a global leaderboard. I also decided which stats to surface
(login, contributions, repo count, share %) based on what I thought would be interesting.

---

## time_series.py

### What AI Helped With

**90-Day Lookback Window**
AI implemented the query that fetches snapshots from MongoDB with a 90-day cutoff:
```python
cutoff = datetime.utcnow() - timedelta(days=90)
```
I had specified 90 days as the analysis window because it is long enough to show trends
but short enough to remain relevant.

**Growth Rate Calculation**
AI wrote `compute_growth_rate()` using first vs last snapshot comparison:
```python
growth = ((last_val - first_val) / abs(first_val)) * 100
```
This produces a percentage change which is displayed on the Time-Series dashboard page
as "+X% over 90 days".

**Trend Direction Classification**
AI added a helper that classifies trends as "Growing", "Stable", or "Declining" based
on the slope of a linear regression fit over the snapshot series. I asked for this because
a single percentage change can be misleading if there was a spike mid-period.

### What I Did
Decided that 90 days is the right window. Specified growth rate and trend direction
as the two key metrics for the time-series page. Verified the page displays correct
direction labels when running the dashboard locally.

---

## AI Tool Used
AI assistant — used for implementing statistical methods (Gini coefficient,
linear regression trend) and pandas aggregation patterns given my metric specifications.
