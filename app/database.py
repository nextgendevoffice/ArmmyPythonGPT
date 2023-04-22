import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.environ["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["admin"]
users = db["users"]

def get_db():
    return db

def get_user_tokens(user_id):
    user = users.find_one({"user_id": user_id})
    return user["tokens"] if user else None

def update_user_tokens(user_id, new_tokens):
    users.update_one({"user_id": user_id}, {"$set": {"tokens": new_tokens}}, upsert=True)

def save_chat_history(user_id, question, answer, prompt_tokens, completion_tokens, total_tokens):
    db = get_db()
    chat_history = {
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "timestamp": datetime.utcnow()
    }
    db.chat_history.insert_one(chat_history)

def get_chat_history(user_id):
    db = get_db()
    return list(db.chat_history.find({"user_id": user_id}).sort("timestamp", -1))

def create_coupon(tokens):
    coupon_code = generate_coupon_code()
    coupon = {"coupon_code": coupon_code, "tokens": tokens}
    db.coupons.insert_one(coupon)
    return coupon_code

def add_token(user_id, coupon_code):
    coupon = db.coupons.find_one({"coupon_code": coupon_code})

    if not coupon:
        return "Invalid coupon code."

    usage = db.coupon_usage.find_one({"coupon_id": coupon["_id"]})
    if usage:
        return "Coupon has already been used."

    # Update user's tokens here
    user = users.find_one({"user_id": user_id})
    new_tokens = user["tokens"] + coupon["tokens"]
    users.update_one({"user_id": user_id}, {"$set": {"tokens": new_tokens}})

    # Log the coupon usage
    coupon_usage = {"coupon_id": coupon["_id"], "user_id": user_id}
    db.coupon_usage.insert_one(coupon_usage)

    return f"Successfully added {coupon['tokens']} tokens."

    # Log History add token by user
def get_token_history(user_id):
    token_history = db.coupons.find({"user_id": user_id})
    return list(token_history)

def add_admin(user_id):
    admin = {"user_id": user_id}
    if not db.admins.find_one({"user_id": user_id}):
        db.admins.insert_one(admin)

def is_admin(user_id):
    return db.admins.find_one({"user_id": user_id}) is not None

def get_total_users():
    return users.count_documents({})

def get_total_tokens_used(start_date, end_date):
    start_date = datetime.strptime(start_date, "%d-%m-%Y")
    end_date = datetime.strptime(end_date, "%d-%m-%Y")
    
    chat_history = db.chat_history.find({"timestamp": {"$gte": start_date, "$lte": end_date}})
    total_tokens = sum([item["total_tokens"] for item in chat_history])
    
    return total_tokens
