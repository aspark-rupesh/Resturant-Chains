from pymongo import MongoClient

MONGO_URL="mongodb://localhost:27017"
DATABASE_NAME = 'rupesh_resturant_chain'

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]


def reset_database(db):
    # Check if collections exist
    collections = db.list_collection_names()

    if collections:
        print("Dropping existing collections...")
        # Drop all collections
        for collection_name in collections:
            db[collection_name].drop()
        print("Collections dropped.")