import os
from pymongo import MongoClient

MONGO_URI = os.environ['MONGO_URI']
client = MongoClient(MONGO_URI)
db = client.get_default_database()

def get_user_tokens(user_id):
    user = db.users.find_one({"user_id": user_id})
    if user:
        return user['tokens']
    return None

def update_user_tokens(user_id, tokens):
    db.users.update_one({"user_id": user_id}, {"$set": {"tokens": tokens}}, upsert=True)
