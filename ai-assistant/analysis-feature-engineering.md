# AI Assistance — `analysis/feature_engineering.py`

## File Purpose
Extracts and engineers numerical features from raw GitHub API data stored in MongoDB,
transforming nested JSON structures into a flat DataFrame ready for scoring and analysis.

---

## What AI Helped With

### 1. Class Skeleton and Pipeline Structure
AI suggested wrapping the feature logic inside a `FeatureEngineer` class with a single
public method `engineer_features()` that chains private stage methods. The stage order
(parse → temporal → contributors → commits → derived) was proposed by AI based on data
dependency — you cannot compute `stars_per_day` before parsing `created_at`.

**My decision:** I chose which features were meaningful for comparing ML framework repos.
Temporal velocity, contributor concentration, and commit rhythm were domain choices I made,
not AI defaults.

### 2. Nested JSON Parsing for Commits
AI wrote the try/except pattern for safely navigating three levels of nesting:
```python
date_str = c["commit"]["author"]["date"]
```
The challenge here is that the GitHub API response wraps commit metadata inside a `commit`
sub-object which itself contains an `author` sub-object. AI helped write the guard against
missing keys that would otherwise crash the pipeline on incomplete API responses.

**My decision:** I identified that commits were the deepest nested structure and flagged
it as a problem. AI then provided the safe extraction pattern.

### 3. Time-Window Commit Frequency Formula
AI implemented the formula:
```python
time_span_days = (dates_sorted[-1] - dates_sorted[0]).days
return len(dates) / time_span_days
```
I specified to AI that I did **not** want repo age as the denominator — I wanted the
window between the first and last commit in the collected sample. AI then wrote the
sorted-date approach to achieve this.

**My decision:** The time-window decision was mine. I understood that a 10-year-old repo
should not be penalised for its age.

### 4. Bus Factor Estimate
AI suggested the formula `bus_factor = 1 / top_contributor_share` and recommended
capping it at 100 to avoid infinity when one person dominates entirely. I had described
the concept of bus factor and AI translated it into code.

### 5. Contributor Diversity Metric
AI implemented the 1% threshold approach:
```python
threshold = total * 0.01
meaningful = sum(1 for c in contributors if c.get("contributions", 0) > threshold)
```
I had asked for a diversity measure that filters out token contributors (people with a
single commit), and AI suggested the 1% threshold as a reasonable cut-off.

---

## What I Did

- Decided which features to include based on what matters for ML framework evaluation
- Specified the time-window requirement for commit frequency
- Identified the nested JSON depth problem before asking AI to solve it
- Tested the output locally and verified that `bus_factor_estimate` and
  `contributor_diversity` produced sensible values for known repos (e.g. TensorFlow
  showing low diversity due to Google engineer dominance)
- Debugged the `active_lifespan_ratio` clip to ensure it stays within [0, 1]

---

## AI Tool Used
AI assistant — used for code generation given my feature specifications.
