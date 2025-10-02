import unittest

import redis

import bt4.GlobalProperties as global_prop

class MyTestCase(unittest.TestCase) :
    def test_something(self) :

        quote_redis_ip = global_prop.QUOTE_REDIS_IP_ADDR
        redis_storage = redis.StrictRedis(host = quote_redis_ip, port = global_prop.REDIS_PORT, db = 0)

        # 키와 값을 설정
        key = 'my_key'
        initial_value = 'initial_value'
        new_value = 'new_value'

        # 초기 값 설정
        redis_storage.set(key, initial_value)
        print(f"Initial value set: {redis_storage.get(key).decode('utf-8')}")

        # 새로운 값으로 업데이트
        redis_storage.set(key, new_value)
        print(f"Updated value set: {redis_storage.get(key).decode('utf-8')}")


if __name__ == '__main__' :
    unittest.main()
