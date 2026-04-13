from typing import List, Dict, Any, Optional
from datetime import datetime
from database.connection import MongoConnection
from config.settings import Settings

class RepositoryStore:
    COLLECTION_NAME = "repositories"

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = self.settings.get_logger("RepositoryStore")
        self.connection = MongoConnection(self.settings)
        self.collection = self.connection.get_collection(self.COLLECTION_NAME)

    def insert_many(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            self.logger.warning("No records to insert")
            return 0

        # Add timestamp to each record
        for record in records:
            if "timestamp" not in record:
                record["timestamp"] = datetime.utcnow()

        result = self.collection.insert_many(records)
        count = len(result.inserted_ids)
        self.logger.info("Inserted %d repository records", count)
        return count

    def find_all(self, exclude_id: bool = True) -> List[Dict[str, Any]]:
        projection = {"_id": 0} if exclude_id else None
        records = list(self.collection.find({}, projection))
        self.logger.info("Retrieved %d repository records", len(records))
        return records

    def find_by_name(self, repo_name: str) -> Optional[Dict[str, Any]]:
        "Find the most recent record for a specific repository."
        return self.collection.find_one(
            {"name": repo_name},
            {"_id": 0},
            sort=[("timestamp", -1)]
        )

    def find_latest_snapshot(self) -> List[Dict[str, Any]]:
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$name",
                "doc": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$doc"}},
            {"$project": {"_id": 0}},
        ]
        results = list(self.collection.aggregate(pipeline))
        self.logger.info("Retrieved latest snapshot: %d repos", len(results))
        return results

    def get_repo_count(self) -> int:
        "Get total number of repository documents."
        return self.collection.count_documents({})

    def drop_collection(self):
        "Drop the entire collection (use with caution)."
        self.collection.drop()
        self.logger.warning("Dropped collection: %s", self.COLLECTION_NAME)
