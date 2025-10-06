# database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['knowledge_db']

documents_collection = db['documents']          # store metadata + text
conversations_collection = db['conversations']  # store user conversation history
users_collection = db['users']                  # store user authentication data