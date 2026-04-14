# AI Assistance — `analysis/scoring.py`

## File Purpose
Computes four dimension scores (Activity, Success, Developer Influence, Community Strength)
and one overall composite score for each repository, all normalised to a 0–100 scale.

---

## What AI Helped With

### 1. Percentile Rank Normalisation Pattern
AI implemented the core normalisation method:
```python
normalized = df[metric].rank(pct=True).fillna(0)
score += normalized * weight
```
I had explained that I did not want min-max normalisation because a single outlier
(e.g. TensorFlow's 180,000 stars) would compress all other repos to near zero.
AI recommended percentile ranking as the solution — each repo gets a value between
0 and 1 representing what fraction of other repos it outperforms on that metric.

**My decision:** I chose percentile over min-max after AI explained the outlier problem.
This was a genuine technical decision I made with understanding.

### 2. Weight Dictionaries for Each Dimension
AI structured the weights as class-level dictionaries (ACTIVITY_WEIGHTS, SUCCESS_WEIGHTS,
etc.) so they are visible, adjustable, and not buried inside methods. The structure makes
it easy to change weights without touching calculation logic.

**My decision:** I specified every weight value. For example:
- Activity: commit_count 35% (most important — raw volume of work)
- Activity: commit_frequency 25% (velocity within the window)
- Success: stars 40% (community's most direct popularity signal)
- Overall: Activity 30% > Community 25% = Success 25% > Influence 20%

These weights reflect my understanding of what matters when evaluating an ML framework.

### 3. `_compute_dimension_score` as a Reusable Method
AI suggested a single generic method that takes any weight dictionary, rather than four
separate methods for each dimension. This keeps the code DRY and is an MSc-level design
pattern. I accepted this after AI explained the benefit.

### 4. Overall Score Composition
AI wrote the `_compute_overall_score` method that multiplies already-scored dimensions
by the OVERALL_WEIGHTS. The key point AI clarified: dimension scores are already 0–100,
so the overall score is also naturally 0–100 without any further scaling.

### 5. Rank Assignment
AI added the `_assign_ranks` method using pandas `.rank(ascending=False)` to generate
leaderboard positions for each dimension. I had asked for rank columns so the dashboard
could show "Rank #1 in Activity" style labels.

---

## What I Did

- Defined all weight values based on domain reasoning about ML framework evaluation
- Chose percentile ranking over min-max after understanding the outlier problem
- Verified the formula manually: for 5 repos, the repo ranked 5th/5 on stars gets
  percentile = 1.0 (100th percentile), which then contributes 1.0 × 0.40 = 0.40 to
  the success score before scaling
- Confirmed TensorFlow's overall score (~70) matches manual calculation through the
  dashboard Page 2 output
- Decided that Activity should carry the highest weight (30%) because for a developer
  choosing a library, recent development activity signals whether it is maintained

---

## AI Tool Used
AI assistant — used for code implementation given my weight specifications and
normalisation approach decision.
