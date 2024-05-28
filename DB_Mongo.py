from dataclasses import asdict
from pymongo import MongoClient

DATABASE_NAME = "JournalDB"
# collection = db["mycollection"]


# def mongo_connection(func, db_name=DATABASE_NAME):
#     def wrapper(*args, **kwargs):
#         with  as client:
#
#             result = func(db, *args, **kwargs)
#         # Return the result of the original function
#         return result
#     return wrapper


def add_entry(entry):
    with db["entries"] as entry_collection:
        entry_collection.insert_one(asdict(entry))
        return True


def add_doc(collection_name, doc):
    collection = db[collection_name]
    collection.insert_one(doc)
    return True


def update_doc_from(collection_name, original_doc, update_operation):
    return db[collection_name].update_one(original_doc, update_operation)


def get_docs_from(collection_name):
    return [doc for doc in db[collection_name].find()]


def get_docs_from_where(collection_name, query):
    return [doc for doc in db[collection_name].find(query)]


def get_doc_from_where(collection_name, query):
    return db[collection_name].find_one(query)


def print_all_collections():
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        for doc in collection.find():
            print(doc)


client = MongoClient("mongodb://localhost:27017/")
db = client[DATABASE_NAME]


