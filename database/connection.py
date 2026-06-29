"""
AuraStyle - MongoDB Connection
Manages the PyMongo client and database access.
"""

from pymongo import MongoClient
from config import config

_client = None

def get_client():
    """Return a cached MongoClient instance."""
    global _client
    if _client is None:
        _client = MongoClient(config.MONGO_URI)
    return _client

def get_db():
    """Return the aurastyle database."""
    return get_client()[config.DB_NAME]

def get_collection(name: str):
    """Return a named collection from the aurastyle database."""
    return get_db()[name]
