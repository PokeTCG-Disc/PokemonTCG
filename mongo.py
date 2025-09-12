import os
from pymongo import MongoClient

# Load variables from .env

# Get MongoDB URI from .env
uri = 'mongodb+srv://Sri-dev:<cSf07xnQpgphCEIf>@poketcg.d8tsjnu.mongodb.net/?retryWrites=true&w=majority&appName=poketcg'

# Connect to MongoDB
client = MongoClient(uri)

# Choose database & collection
db = client["my_database"]
collection = db["my_collection"]

# Insert test document
collection.insert_one({"name": "Alice", "age": 25})

# Fetch and print documents
for doc in collection.find():
    print(doc)
