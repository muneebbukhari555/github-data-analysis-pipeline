from pymongo import MongoClient
import os

def get_collection():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["github_analysis"]
    return db["repositories"]

def insert_data(records):
    collection = get_collection()
    if records:
        collection.insert_many(records)