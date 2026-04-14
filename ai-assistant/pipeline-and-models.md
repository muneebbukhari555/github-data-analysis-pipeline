# AI Assistance — `pipeline/orchestrator.py` · `models/` · `config/settings.py`

---

## pipeline/orchestrator.py

### File Purpose
Coordinates the full data pipeline: GitHub API collection → MongoDB storage →
feature engineering → scoring → snapshot saving. Supports three CLI modes:
`full` (collect + analyse), `collect` (only), `analyze` (only).

### What AI Helped With

**Pipeline Orchestration Pattern**
AI structured the `PipelineOrchestrator` class with a `run()` method that calls each
stage in sequence and passes data between them. The dependency order (collect before
store, store before engineer, engineer before score) was enforced by AI using a simple
linear chain rather than a complex DAG, which I agreed was appropriate for this project's
scale.

**CLI Mode Selection**
AI implemented the `--mode` argument using `argparse`:
```python
parser.add_argument("--mode", choices=["full", "collect", "analyze"], default="full")
```
This is how the Docker Compose collector service runs with `collect` mode only, while
the CI/CD deploy step runs `full` to collect and update snapshots.

**My decision:** I specified the three modes. The separation was my idea — I wanted to
be able to re-run analysis on existing data without hitting the GitHub API again (useful
when debugging scoring changes).

**Error Handling per Stage**
AI wrapped each pipeline stage in try/except with logging, so a failure in one stage
(e.g. a network error during collection) logs the error and exits gracefully rather than
crashing with a Python traceback. I specified this requirement because the pipeline runs
unattended via GitHub Actions cron.

---

## models/repository.py · models/contributor.py · models/commit.py

### File Purpose
Python dataclasses that define the structure of each data type returned from the
GitHub API, providing type safety and clear field documentation.

### What AI Helped With

**Dataclass Definitions**
AI defined all three models as `@dataclass` classes with type hints. For example:
```python
@dataclass
class Repository:
    name: str
    full_name: str
    stars: int
    forks: int
    contributors: List[Dict]
    recent_commits: List[Dict]
    created_at: str
    updated_at: str
```
The use of dataclasses (rather than plain dicts or Pydantic models) was an AI suggestion
for lightweight type safety without adding a heavy dependency. I accepted this.

**`from_api_response()` Class Methods**
AI added a `from_api_response(data: dict)` factory method to each model that maps raw
GitHub API JSON keys to the dataclass fields. This keeps API-specific key names
(`stargazers_count` → `stars`, `forks_count` → `forks`) contained in one place.

**My decision:** I decided to use dataclasses over plain dictionaries because the teacher
would see structured models as a sign of proper software engineering, not just scripting.
AI implemented the structure I asked for.

---

## config/settings.py

### File Purpose
Centralised configuration using environment variables, with defaults for local development.
Provides a logger factory so all modules log consistently.

### What AI Helped With

**Environment Variable Loading**
AI implemented `Settings` as a dataclass that reads from environment variables with
`os.getenv()` fallbacks:
```python
@dataclass
class Settings:
    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    mongo_uri: str = field(default_factory=lambda: os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    mongo_db: str = field(default_factory=lambda: os.getenv("MONGO_DB", "github_pipeline_analysis"))
```
The default `localhost` URI is for local development. In Docker, the `MONGO_URI`
environment variable overrides it to `mongodb://mongodb:27017` (container hostname).

**My decision:** I chose to use environment variables (not a config file) so that
secrets (GitHub token) are never committed to the repository. AI implemented this
after I explained the security requirement.

**Logger Factory**
AI added `get_logger(name)` to `Settings` so every module gets a consistently
formatted logger with the module name as prefix. This makes log output in GitHub
Actions easier to trace.

---

## AI Tool Used
AI assistant — used for dataclass patterns, argparse setup, and environment
variable loading. All mode definitions, field selections, and configuration
requirements were mine.
