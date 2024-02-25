from pymongo import MongoClient

MONGO_URL="mongodb://localhost:27017"
DATABASE_NAME = 'final_resturant_chain'

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]