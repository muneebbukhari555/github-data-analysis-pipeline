# AI Assistance — `database/`

## Files Covered
- `connection.py` — MongoDB connection manager with singleton pattern
- `repository_store.py` — stores and retrieves raw repository documents
- `snapshot_store.py` — stores lightweight numeric snapshots for time-series analysis

---

## What AI Helped With

### 1. Singleton Connection Pattern (`connection.py`)
AI implemented the singleton pattern so only one MongoDB connection is created per
process, regardless of how many modules import the connection:
```python
class MongoConnection:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```
**My decision:** I chose MongoDB over a relational database because GitHub data is
hierarchical JSON (repos contain lists of contributors, which contain nested objects).
MongoDB stores it natively without flattening into joins. I specified this requirement;
AI implemented the connection pattern.

### 2. Upsert Logic (`repository_store.py`)
AI used MongoDB's `update_one` with `upsert=True` rather than `insert_one`:
```python
collection.update_one(
    {"name": repo["name"]},
    {"$set": repo},
    upsert=True
)
```
This means re-running the collector does not create duplicate documents — it updates
the existing record in place. I had raised the question of what happens if the same
repo is collected twice, and AI suggested upsert as the clean solution.

### 3. Snapshot Store — Time-Series Document Model (`snapshot_store.py`)
AI designed a separate `snapshots` collection that stores lightweight records:
```json
{
  "name": "tensorflow/tensorflow",
  "snapshot_date": "2026-04-10T06:00:00",
  "overall_score": 72.4,
  "activity_score": 68.1,
  "stars": 182000
}
```
The design separates raw repo data (in `repositories` collection) from time-stamped
score history (in `snapshots`). I had asked for historical trending — AI proposed
this two-collection design as the right approach.

**My decision:** I specified which fields to snapshot. I chose scores and star counts
because those are the metrics I want to track over time. Raw commit data is too large
to snapshot every 6 hours.

### 4. Compound Index for Efficient Queries
AI added a compound index on `(name, snapshot_date)` to ensure that the 90-day
lookback query does not perform a full collection scan:
```python
collection.create_index([("name", 1), ("snapshot_date", -1)])
```
I had not thought of this — AI proactively suggested it when I mentioned the dashboard
needed to load history for 5 repos quickly.

### 5. `get_all_history(days=90)` Query
AI wrote the MongoDB aggregation that filters snapshots by date and sorts them:
```python
cutoff = datetime.utcnow() - timedelta(days=days)
return list(collection.find(
    {"snapshot_date": {"$gte": cutoff}},
    sort=[("snapshot_date", 1)]
))
```
The 90-day default was my specification. AI implemented the query with correct
MongoDB comparison operators.

---

## What I Did

- Chose MongoDB as the database (document model fits nested GitHub API JSON)
- Decided on two-collection design: raw repositories vs. lightweight snapshots
- Specified the 90-day lookback window for trend analysis
- Identified the duplicate-on-recollect problem and asked for upsert
- Decided which fields to store in snapshots (scores + stars, not raw commit lists)

---

## AI Tool Used
AI assistant — used for MongoDB query syntax, index creation, and connection
management patterns. All schema and data model decisions were mine.
