from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from config.settings import Settings

class MongoConnection:
    _instance: Optional["MongoConnection"] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    def __new__(cls, settings: Optional[Settings] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings: Optional[Settings] = None):
        if self._client is None:
            self.settings = settings or Settings()
            self.logger = self.settings.get_logger("MongoConnection")
            self._connect()

    def _connect(self):
        "Establish MongoDB connection."
        try:
            self._client = MongoClient(self.settings.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self._client.admin.command("ping")
            self._db = self._client[self.settings.mongo_db]
            self.logger.info(
                "Connected to MongoDB: %s/%s",
                self.settings.mongo_uri, self.settings.mongo_db
            )
        except Exception as e:
            self.logger.error("MongoDB connection failed: %s", str(e))
            raise

    @property
    def db(self) -> Database:
        "Get the database instance."
        if self._db is None:
            self._connect()
        return self._db

    def get_collection(self, name: str):
        "Get a named collection from the database."
        return self.db[name]

    def close(self):
        "Close the MongoDB connection."
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            MongoConnection._instance = None
            self.logger.info("MongoDB connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
