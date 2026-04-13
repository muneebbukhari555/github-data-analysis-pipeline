from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from database.connection import MongoConnection
from config.settings import Settings

class SnapshotStore:
    COLLECTION_NAME = "snapshots"

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = self.settings.get_logger("SnapshotStore")
        self.connection = MongoConnection(self.settings)
        self.collection = self.connection.get_collection(self.COLLECTION_NAME)
        self._ensure_indexes()

    def _ensure_indexes(self):
        "Create indexes for efficient time-series queries."
        self.collection.create_index([("name", 1), ("snapshot_date", -1)])
        self.collection.create_index("snapshot_date")

    def save_snapshot(self, records: List[Dict[str, Any]]) -> int:
        "Save a point-in-time snapshot of repository metrics."
        snapshot_date = datetime.utcnow()
        snapshots = []
        for record in records:
            snapshot = {
                "name": record.get("name"),
                "snapshot_date": snapshot_date,
                "stars": record.get("stars", 0),
                "forks": record.get("forks", 0),
                "open_issues": record.get("open_issues", record.get("issues", 0)),
                "watchers": record.get("watchers", 0),
                "size": record.get("size", 0),
                "contributors_count": (
                    len(record["contributors"])
                    if isinstance(record.get("contributors"), list)
                    else record.get("contributors_count", 0)
                ),
                "commit_count": (
                    len(record["recent_commits"])
                    if isinstance(record.get("recent_commits"), list)
                    else record.get("commit_count", 0)
                ),
            }
            snapshots.append(snapshot)
        if snapshots:
            self.collection.insert_many(snapshots)
            self.logger.info("Saved %d snapshots at %s", len(snapshots), snapshot_date)
        return len(snapshots)

    def get_history(self, repo_name: str, days: int = 30) -> List[Dict[str, Any]]:
        "Retrieve historical snapshots for a repository"
        cutoff = datetime.utcnow() - timedelta(days=days)
        results = list(self.collection.find(
            {"name": repo_name, "snapshot_date": {"$gte": cutoff}},
            {"_id": 0}
        ).sort("snapshot_date", 1))
        self.logger.info("Retrieved %d snapshots for %s", len(results), repo_name)
        return results

    def get_all_history(self, days: int = 90) -> List[Dict[str, Any]]:
        "Retrieve historical snapshots for all repositories."
        cutoff = datetime.utcnow() - timedelta(days=days)
        results = list(self.collection.find(
            {"snapshot_date": {"$gte": cutoff}},
            {"_id": 0}
        ).sort("snapshot_date", 1))
        return results

    def compute_growth_rate(self, repo_name: str, metric: str = "stars", days: int = 30) -> float:
        "Compute growth rate for a specific metric over the given time period."
        history = self.get_history(repo_name, days)
        if len(history) < 2:
            return 0.0
        first_value = history[0].get(metric, 0)
        last_value = history[-1].get(metric, 0)
        if first_value == 0:
            return 0.0
        growth = ((last_value - first_value) / first_value) * 100
        return round(growth, 2)

    def get_snapshot_count(self) -> int:
        "Get total number of snapshot documents."
        return self.collection.count_documents({})
