
import os
import pytest
from pymongo.mongo_client import MongoClient

# Use MONGODB_URL from env; skip test if not set to avoid leaking credentials
MONGODB_URL = os.getenv("MONGODB_URL")

if not MONGODB_URL:
    pytest.skip("MONGODB_URL not set; skipping Mongo connectivity test", allow_module_level=True)

# Create a new client and connect to the server
client = MongoClient(MONGODB_URL)

# Send a ping to confirm a successful connection
def test_mongo_ping():
    client.admin.command('ping')