from pymongo import MongoClient

from settings import DB_NAME

mongo_client = MongoClient()
db = mongo_client[DB_NAME]
