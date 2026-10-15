import sys
from bson.objectid import ObjectId
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config

_client = None
_db = None

def get_mongo_client():
    """Returns the singleton MongoDB client instance."""
    global _client
    if _client is None:
        try:
            _client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=3000)
            # Force a connection check
            _client.admin.command('ping')
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[MongoDB Connection Warning] Could not connect to MongoDB at {Config.MONGODB_URI}: {e}")
    return _client

def get_db():
    """Returns the MongoDB database instance."""
    global _db
    if _db is None:
        client = get_mongo_client()
        if client:
            _db = client[Config.MONGODB_DATABASE]
            init_indexes(_db)
    return _db

def init_indexes(db):
    """Initializes required MongoDB indexes, including unique constraints."""
    if db is None:
        return
    try:
        # Unique email index on users collection
        db.users.create_index([("email", ASCENDING)], unique=True)
        # Indexes for fast querying
        db.study_tasks.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
        db.coding_problems.create_index([("slug", ASCENDING)], unique=True)
        db.coding_drafts.create_index([("user_id", ASCENDING), ("problem_id", ASCENDING)], unique=True)
        db.quiz_attempts.create_index([("user_id", ASCENDING), ("category", ASCENDING)])
        db.revision_entries.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
    except Exception as e:
        print(f"[MongoDB Index Init Warning]: {e}")

def to_object_id(id_str):
    """Safely converts string to ObjectId or returns None if invalid."""
    if not id_str:
        return None
    try:
        return ObjectId(str(id_str))
    except Exception:
        return None
