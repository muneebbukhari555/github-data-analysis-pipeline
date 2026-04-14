# AI Assistance — `collectors/`

## Files Covered
- `base_collector.py` — shared HTTP logic, rate-limit handling, pagination
- `repo_collector.py` — fetches repository metadata
- `commit_collector.py` — fetches recent commits with nested author data
- `contributor_collector.py` — fetches contributor list with contribution counts

---

## What AI Helped With

### 1. Base Collector Class Design (`base_collector.py`)
AI designed the `BaseCollector` abstract class with shared logic that all specific
collectors inherit. This pattern avoids repeating the same HTTP request, retry, and
rate-limit code in every collector.

Key AI contribution — the rate-limit check before each request:
```python
def _check_rate_limit(self):
    remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
    if remaining < 10:
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
        sleep_seconds = max(0, reset_time - time.time()) + 5
        time.sleep(sleep_seconds)
```
The GitHub API returns rate-limit headers on every response. AI knew to read
`X-RateLimit-Remaining` and `X-RateLimit-Reset` as the correct header names.

**My decision:** I specified that the system must handle rate limiting automatically
without crashing, because the project collects data every 6 hours via GitHub Actions.
I could not have a manual retry each time.

### 2. Pagination Logic
AI implemented the `link` header parsing for GitHub's cursor-based pagination:
```python
if 'rel="next"' in response.headers.get("Link", ""):
    url = re.search(r'<([^>]+)>; rel="next"', ...).group(1)
```
GitHub paginates results and puts the next page URL inside a `Link` header rather than
the response body. AI knew this API-specific behaviour and implemented it correctly.

**My decision:** I specified that we needed pagination because the commit endpoint only
returns 30 items per page by default, and popular repos have thousands of commits.

### 3. Commit Collector — Nested Response Handling (`commit_collector.py`)
AI wrote the response parsing that extracts from GitHub's commit list endpoint. Each
item in the array has this shape:
```json
{
  "sha": "...",
  "commit": {
    "author": { "name": "...", "email": "...", "date": "..." },
    "message": "..."
  },
  "author": { "login": "...", "avatar_url": "..." }
}
```
Note there are TWO author objects: `commit.author` (the git metadata with date) and
`author` (the GitHub user account with login). AI correctly mapped these to separate
fields. I had identified this as confusing from the API docs and asked AI to handle it.

### 4. Contributor Collector — Sorted Pagination (`contributor_collector.py`)
AI used `?per_page=100&anon=false` query parameters on the contributors endpoint.
The `anon=false` parameter excludes anonymous git contributions that have no GitHub
account, keeping contributor data clean for analysis.

---

## What I Did

- Identified rate limiting as a hard requirement (running every 6 hours automatically)
- Chose which GitHub API endpoints to use for each data type
- Identified the dual `author` object confusion in commits and asked AI to handle both
- Decided to collect 100 commits maximum per repo (balance between data richness and
  API quota usage)
- Specified `anon=false` on contributors after reading GitHub API docs and deciding
  anonymous contributors would distort diversity metrics

---

## AI Tool Used
AI assistant — used for HTTP client implementation, GitHub API header parsing,
and pagination pattern. GitHub API endpoint and parameter selection were my decisions.
