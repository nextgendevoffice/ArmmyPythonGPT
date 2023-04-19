import os
from pymongo import MongoClient

MONGO_URI = os.environ["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["admin"]
users = db["users"]

def get_user_tokens(user_id):
    user = users.find_one({"user_id": user_id})
    return user["tokens"] if user else None

def update_user_tokens(user_id, new_tokens):
    users.update_one({"user_id": user_id}, {"$set": {"tokens": new_tokens}}, upsert=True)
