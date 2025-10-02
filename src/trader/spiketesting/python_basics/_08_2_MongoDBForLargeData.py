import unittest

from bulltrader.utils.mongodb import MongoDBHandler
from datetime import datetime as dt


mongo_host = "localhost"
mongo_port = "27017"
mongo_id = "bulltrader"
mongo_pw = "qnfxmfpdlej12!"

database = 'autotrader'

mongo = MongoDBHandler.instance()

collection = 'quote'

document1 = {
            # "time": "2021-09-03T21:45:00",
            "time": dt.strptime("2021-09-03T21:45:00", "%Y-%m-%dT%H:%M:%S"),
            "KRW-BTC":
                {
                    "market":"KRW-BTC",
                    "candle_date_time_utc":"2021-09-03T12:45:00",
                    "candle_date_time_kst":"2021-09-03T21:45:00",
                    "opening_price":58814000.00000000,
                    "high_price":58832000.00000000,
                    "low_price":58802000.00000000,
                    "trade_price":58808000.00000000,
                    "timestamp":1630673109086,
                    "candle_acc_trade_price":138916815.64222000,
                    "candle_acc_trade_volume":2.36205068,
                    "unit":1
                },
            "KRW-ADA":
                {
                    "market": "KRW-ADA",
                    "candle_date_time_utc": "2021-09-03T12:45:00",
                    "candle_date_time_kst": "2021-09-03T21:45:00",
                    "opening_price": 3460.00000000,
                    "high_price": 3460.00000000,
                    "low_price": 3455.00000000,
                    "trade_price": 3460.00000000,
                    "timestamp": 1630673111320,
                    "candle_acc_trade_price": 131387086.80204690,
                    "candle_acc_trade_volume": 38021.14427835,
                    "unit": 1
                }
        }

document2 = {
    # "time": "2021-09-03T12:46:00",
    "time" : dt.strptime("2021-09-03T21:46:00", "%Y-%m-%dT%H:%M:%S"),
    "KRW-BTC":
        {
            "market":"KRW-BTC",
            "candle_date_time_utc":"2021-09-03T12:46:00",
            "candle_date_time_kst":"2021-09-03T21:46:00",
            "opening_price":58778000.00000000,
            "high_price":58801000.00000000,
            "low_price":58778000.00000000,
            "trade_price":58800000.00000000,
            "timestamp":1630673169414,
            "candle_acc_trade_price":77393601.58854000,
            "candle_acc_trade_volume":1.31622995,
            "unit":1
        },
    "KRW-ADA":
        {
            "market":"KRW-ADA",
            "candle_date_time_utc":"2021-09-03T12:46:00",
            "candle_date_time_kst":"2021-09-03T21:46:00",
            "opening_price":3455.00000000,
            "high_price":3455.00000000,
            "low_price":3450.00000000,
            "trade_price":3450.00000000,
            "timestamp":1630673170824,
            "candle_acc_trade_price":29311604.66276475,
            "candle_acc_trade_volume":8493.50205684,
            "unit":1
        }
}


document3 = {
    # "time": "2021-09-03T12:46:00",
    "time" : dt.strptime("2021-09-03T21:47:00", "%Y-%m-%dT%H:%M:%S"),
    "KRW-BTC":
        {"market":"KRW-BTC","candle_date_time_utc":"2021-09-03T12:47:00","candle_date_time_kst":"2021-09-03T21:47:00","opening_price":58789000.00000000,"high_price":58795000.00000000,"low_price":58781000.00000000,"trade_price":58788000.00000000,"timestamp":1630673229223,"candle_acc_trade_price":64816364.50515000,"candle_acc_trade_volume":1.10252373,"unit":1},
    "KRW-ETH":
        {"market":"KRW-ETH","candle_date_time_utc":"2021-09-03T12:47:00","candle_date_time_kst":"2021-09-03T21:47:00","opening_price":81270.00000000,"high_price":81280.00000000,"low_price":81260.00000000,"trade_price":81270.00000000,"timestamp":1630673230316,"candle_acc_trade_price":88095079.96987440,"candle_acc_trade_volume":1083.96033476,"unit":1},
}

document4 = {
    # "time": "2021-09-03T12:46:00",
    "time" : dt.strptime("2021-09-03T21:48:00", "%Y-%m-%dT%H:%M:%S"),
    "KRW-BTC":
        {"market":"KRW-BTC","candle_date_time_utc":"2021-09-03T12:48:00","candle_date_time_kst":"2021-09-03T21:48:00","opening_price":58798000.00000000,"high_price":58799000.00000000,"low_price":58797000.00000000,"trade_price":58798000.00000000,"timestamp":1630673289281,"candle_acc_trade_price":83763915.15939000,"candle_acc_trade_volume":1.42460701,"unit":1},
    "KRW-ETH":
        {"market":"KRW-ETH","candle_date_time_utc":"2021-09-03T12:48:00","candle_date_time_kst":"2021-09-03T21:48:00","opening_price":81360.00000000,"high_price":81370.00000000,"low_price":81360.00000000,"trade_price":81370.00000000,"timestamp":1630673290750,"candle_acc_trade_price":35804945.90152890,"candle_acc_trade_volume":440.07079642,"unit":1},
    "KRW-EOS":
        {"market":"KRW-EOS","candle_date_time_utc":"2021-09-03T12:48:00","candle_date_time_kst":"2021-09-03T21:48:00","opening_price":6320.00000000,"high_price":6320.00000000,"low_price":6320.00000000,"trade_price":6320.00000000,"timestamp":1630673289564,"candle_acc_trade_price":1888261.93634880,"candle_acc_trade_volume":298.77562284,"unit":1}
}

class MyTestCase(unittest.TestCase):

    def test_update_many_item(self):
        filter = {'time': dt.strptime("2021-09-03T21:45:00", "%Y-%m-%dT%H:%M:%S")}

        print('Before Update #####################################################')
        count_docs = mongo.count_documents(collection, filter)
        print('count_docs:', count_docs)
        if count_docs == 0:
            result = mongo.insert_item_one(collection, document1)

        cursor = mongo.find_item(collection, filter)
        for data in cursor:
            for key in data:
                print(f'key:{key} - value : {data[key]}')
        cursor.close()

        need_to_be_updated_key = "KRW-ETC"
        need_to_be_updated_value = {"market":"KRW-ETC","candle_date_time_utc":"2021-09-03T12:47:00","candle_date_time_kst":"2021-09-03T21:45:00","opening_price":81270.00000000,"high_price":81280.00000000,"low_price":81260.00000000,"trade_price":81270.00000000,"timestamp":1630673230316,"candle_acc_trade_price":88095079.96987440,"candle_acc_trade_volume":1083.96033476,"unit":1}
        count_docs = mongo.count_documents(collection, filter)
        print('count_docs:',count_docs)
        if count_docs > 0:
            cursor = mongo.find_item(collection, filter)
            for data in cursor:
                data[need_to_be_updated_key] = need_to_be_updated_value
                mongo.replace_item_one(collection, filter, data)
            cursor.close()

        print('After Update #####################################################')
        cursor = mongo.find_item(collection, filter)
        for data in cursor:
            for key in data:
                print(f'key:{key} - value : {data[key]}')
        cursor.close()

        # result = mongo.delete_item_one(collection, {'time': dt.strptime("2021-09-03T21:45:00", "%Y-%m-%dT%H:%M:%S")})
        # print('delete:', result)


    # @unittest.skip("Tested")
    def test_insert_find_many_item(self):
        # result = mongo.delete_item_many(collection, [{'time': dt.strptime("2021-09-03T21:45:00", "%Y-%m-%dT%H:%M:%S")},
        #                                              {'time': dt.strptime("2021-09-03T21:46:00", "%Y-%m-%dT%H:%M:%S")},
        #                                              {'time': dt.strptime("2021-09-03T21:47:00", "%Y-%m-%dT%H:%M:%S")},
        #                                              {'time': dt.strptime("2021-09-03T21:48:00", "%Y-%m-%dT%H:%M:%S")}])
        # print('delete:', result)
        #
        result = mongo.insert_item_one(collection, document1)
        print('insert_item_one:', result)
        result = mongo.insert_item_one(collection, document2)
        print('insert_item_one:', result)
        result = mongo.insert_item_one(collection, document3)
        print('insert_item_one:', result)
        result = mongo.insert_item_one(collection, document4)
        print('insert_item_one:', result)

        # cursor = mongo.find_item(collection, {'time': dt.strptime("2021-09-03T21:45:00", "%Y-%m-%dT%H:%M:%S")})
        cursor = mongo.find_item(collection,{'time': {
            '$gte': dt.strptime("2021-09-03T21:45:00", "%Y-%m-%dT%H:%M:%S"),
            '$lte': dt.strptime("2021-09-03T21:48:00", "%Y-%m-%dT%H:%M:%S")
        }})

        for data in cursor:
            for key in data:
                print(f'key:{key} - value : {data[key]}')
        cursor.close()


    @unittest.skip("Tested")
    def test_insert_find_one_item(self):
        result = mongo.delete_item_one(collection, {'time': dt.strptime("2021-09-03T21:45:00", "%Y-%m-%dT%H:%M:%S")})
        print('delete:', result)

        result = mongo.insert_item_one(collection, document1)
        print('insert_item_one:', result)

        cursor = mongo.find_item(collection, {'time': dt.strptime("2021-09-03T21:45:00", "%Y-%m-%dT%H:%M:%S")})
        for data in cursor:
            for key in data:
                print(f'key:{key} - value : {data[key]}')
        cursor.close()


if __name__ == '__main__':
    unittest.main()
