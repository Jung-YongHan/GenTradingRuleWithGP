
from bulltrader.utils.mongodb import MongoDBHandler
import bulltrader.GlobalProperties as global_prop

import bt4.common.ReportSupport


mongo_host = "localhost"
mongo_port = "27017"
mongo_id = "bulltrader"
mongo_pw = "qnfxmfpdlej12!"

mongo = MongoDBHandler(mongo_host, mongo_port)

database = 'quote'
collection = 'test'

###########################
## Insert and Find
mongo.insert_item_one(collection, {"text": "Hello Python22222"})
#
# many_data = [{"text": "Hello Python2",'t2':'aaaa','t3':'aaaa'},
# 			 {"text": "Hello Python3",'t2':'aaaa2','t3':'aaaa2'}]
# mongo.insert_item_many(many_data, database, collection)
#
# cursor = mongo.find_item(None, database, collection)
#
# for list in cursor:
# 	print('find', list["text"])
# cursor.close()


#####################################################################################
#
# def delete_item_one(mongo, condition=None, db_name=None, collection_name=None):
#     result = mongo[db_name][collection_name].delete_one(condition)
#     return result
#
# def delete_item_many(mongo, condition=None, db_name=None, collection_name=None):
#     result = mongo[db_name][collection_name].delete_many(condition)
#     return result
#
# delete_item_one(mongo, {"text": "Hello Python"}, "autotrader", "test")
# delete_item_many(mongo, {}, "autotrader", "test") ## delete
# print('done')
#
# #####################################################################################
# def update_item_one(mongo, condition=None, update_value=None, db_name=None, collection_name=None):
#     result = mongo[db_name][collection_name].update_one(filter=condition, update=update_value)
#     return result
#
#
# def update_item_many(mongo, condition=None, update_value=None, db_name=None, collection_name=None):
#     result = mongo[db_name][collection_name].update_many(filter=condition, update=update_value)
#     return result
#
#
# update_item_one(mongo, {"text": "Hello Python"}, {"$set": {"text": "Hello Kotlin"}}, "autotrader", "test")
# #####################################################################################
#
# def text_search(mongo, text=None, db_name=None, collection_name=None):
#     result = mongo[db_name][collection_name].find({"$text": {"$search": text}})
#     return result
#
# cursor = text_search(mongo, "Hello", "test", "test")
# for list in cursor:
# 	print(list)