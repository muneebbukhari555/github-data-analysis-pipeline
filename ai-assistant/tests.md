# AI Assistance — `tests/`

## Files Covered
- `tests/test_models.py` — unit tests for Repository, Contributor, Commit dataclasses
- `tests/test_feature_engineering.py` — unit tests for FeatureEngineer class
- `tests/test_scoring.py` — unit tests for RepositoryScorer class

---

## What AI Helped With

### 1. Test Structure and Fixtures
AI set up pytest fixtures to create sample DataFrames that mimic what MongoDB would
return after collection. For example, a mock repo row with known values so the test
can assert exact expected outputs:
```python
@pytest.fixture
def sample_df():
    return pd.DataFrame([{
        "name": "test/repo",
        "stars": 1000,
        "forks": 200,
        "contributors": [
            {"login": "user_a", "contributions": 800},
            {"login": "user_b", "contributions": 200}
        ],
        "recent_commits": [...]
    }])
```

### 2. Feature Engineering Assertions (`test_feature_engineering.py`)
AI wrote assertions that verify specific calculated values. For example:
- `top_contributor_share` for the fixture above should be `800 / 1000 = 0.8`
- `bus_factor_estimate` should be `1 / 0.8 = 1.25`
- `contributor_diversity` should reflect only contributors above 1% threshold

These are deterministic tests — given fixed inputs, the output is always predictable.

### 3. Scoring Boundary Tests (`test_scoring.py`)
AI added edge case tests:
- Single-repo DataFrame (percentile rank with one repo should return 1.0)
- All-zero metrics (should not produce NaN or divide-by-zero errors)
- Score range assertion: all scores must be between 0 and 100

### 4. Model Validation Tests (`test_models.py`)
AI tested that `Repository.from_api_response()` correctly maps GitHub API field names
to dataclass field names:
- `stargazers_count` → `stars`
- `forks_count` → `forks`
- Missing optional fields default to empty list `[]`

---

## What I Did

- Specified that edge cases (zero metrics, single repo) must be tested because the
  pipeline runs unattended and cannot crash on unusual data
- Chose the fixture values (800/200 contributor split) to make manual verification easy
- Confirmed all tests pass locally: `pytest tests/ -v` passes with no failures

---

## AI Tool Used
AI assistant — used for pytest fixture syntax and assertion patterns.
Test cases and edge case identification were mine.
