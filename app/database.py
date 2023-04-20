import os
from pymongo import MongoClient
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
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

def save_chat_history(user_id, question, answer):
    db = get_db()
    chat_history = {
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "timestamp": datetime.utcnow()
    }
    db.chat_history.insert_one(chat_history)

def get_chat_history(user_id):
    db = get_db()
    return list(db.chat_history.find({"user_id": user_id}).sort("timestamp", -1))

class Coupons(Base):
    __tablename__ = 'coupons'
    id = Column(Integer, primary_key=True)
    coupon_code = Column(String, unique=True)
    tokens = Column(Integer)

class CouponUsage(Base):
    __tablename__ = 'coupon_usage'
    id = Column(Integer, primary_key=True)
    coupon_id = Column(Integer, ForeignKey('coupons.id'))
    user_id = Column(String)
    
class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    tokens = Column(Integer, default=3000)

    def __repr__(self):
        return f"<User(id='{self.id}', tokens={self.tokens})>"