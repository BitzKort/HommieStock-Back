from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("MONGO_DB_URL")

connection = MongoClient(db_url, server_api = ServerApi('1'))

database = connection.HommiesStock

collections = database.list_collection_names()