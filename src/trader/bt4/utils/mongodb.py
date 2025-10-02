from pymongo import MongoClient
from pymongo.cursor import CursorType
from bt4 import GlobalProperties
from bt4.utils.python_utils import SingletonInstance

import bt4.GlobalProperties as global_prop


mongo_host = "localhost"
mongo_port = "27017"
mongo_id = "bulltrader"
mongo_pw = "qnfxmfpdlej12!"
class MongoDBHandler(SingletonInstance):

    def __init__(self, db_name='autotrader'):
        self.id = mongo_id
        self.pw = mongo_pw

        self.host = mongo_host
        self.port = mongo_port
        mongo_url = f'mongodb://{self.id}:{self.pw}@{self.host}:{self.port}/'
        print(f'Try to connect to : {mongo_url}')
        self.db_name = db_name
        self.client = MongoClient(mongo_url)

        if self.db_name not in self.client.list_database_names():
            self.client[self.db_name]

    def create_collection(self, collection_name):
        if collection_name not in self.client[self.db_name].list_collection_names():
            self.client[self.db_name].create_collection(collection_name)

    def insert_item_one(self, collection_name, data):
        result = self.client[self.db_name][collection_name].insert_one(data).inserted_id
        return result

    def insert_item_many(self,collection_name, datas):
        result = self.client[self.db_name][collection_name].insert_many(datas).inserted_ids
        return result

    def find_item_one(self, collection_name, condition=None):
        result = self.client[self.db_name][collection_name].find_one(condition, {"_id": False})
        return result

    def find_item(self, collection_name, condition=None):
        result = self.client[self.db_name][collection_name].find(condition, {"_id": False}, no_cursor_timeout=True, cursor_type=CursorType.EXHAUST)
        return result

    def count_documents(self, collection_name, filter):
        return self.client[self.db_name][collection_name].count_documents(filter)

    def delete_item_one(self, collection_name, condition=None):
        result = self.client[self.db_name][collection_name].delete_one(condition)
        return result

    def delete_item_many(self, collection_name, condition=None):
        result = self.client[self.db_name][collection_name].delete_many(condition)
        return result

    def replace_item_one(self, collection_name, condition=None, update_value=None):
        result = self.client[self.db_name][collection_name].replace_one(filter=condition, replacement=update_value, upsert=True)
        return result

    def update_item_one(self, collection_name, condition=None, update_value=None):
        result = self.client[self.db_name][collection_name].update_one(filter=condition, update=update_value)
        return result

    def update_item_many(self, collection_name, condition=None, update_value=None):
        result = self.client[self.db_name][collection_name].update_many(filter=condition, update=update_value)
        return result

    def text_search(self, collection_name, text=None):
        result = self.client[self.db_name][collection_name].find({"$text": {"$search": text}})
        return result

    def close(self):
        self.client.close()