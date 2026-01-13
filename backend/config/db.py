from pymongo import MongoClient
import os

client = None

def get_db():
    global client
    if client is None:
        client = MongoClient(os.getenv("MONGO_URI"))
    return client["voice_ai"]
