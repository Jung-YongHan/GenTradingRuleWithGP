import json
import unittest

import jsonschema
from fastjsonschema import RefResolver

from bt4.model.storage_mgr import StrategyStorage


class MyTestCase(unittest.TestCase) :
    def test_local_json_schema(self) :
        # 스키마 파일 경로
        main_schema_path = '../../bt4_json_schema/v1/main_schema_local.json'
        strategy_schema_path = '../../bt4_json_schema/v1/strategy_schema.json'
        vars_schema_path = '../../bt4_json_schema/v1/vars_schema.json'
        systems_schema_path = '../../bt4_json_schema/v1/systems_schema.json'

        # 스키마 파일 로드
        with open(main_schema_path) as f :
            main_schema = json.load(f)

        with open(strategy_schema_path) as f :
            strategy_schema = json.load(f)

        with open(vars_schema_path) as f :
            vars_schema = json.load(f)

        with open(systems_schema_path) as f :
            systems_schema = json.load(f)

        # 참조 해결자 생성
        resolver = RefResolver.from_schema(main_schema, store = {
            main_schema['$id']     : main_schema,
            strategy_schema['$id'] : strategy_schema,
            vars_schema['$id']     : vars_schema,
            systems_schema['$id']  : systems_schema
        })

        f = open(f"json_schema_test.json", encoding = "UTF-8")
        json_data = json.load(f)

        # JSON 데이터 검증
        try :
            jsonschema.validate(instance = json_data, schema = main_schema, resolver = resolver)
            print("JSON 데이터가 유효합니다.")
        except jsonschema.exceptions.ValidationError as e :
            print("JSON 데이터가 유효하지 않습니다:")
            print(e)

    def test_remote_json_schema(self) :
        import requests
        from jsonschema import RefResolver

        def load_remote_schema(url) :
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        # 기본 스키마와 참조할 스키마들의 URL
        main_schema_url = 'http://ssel.asuscomm.com:9080/v1/main_schema_remote.json'
        vars_schema_url = 'http://ssel.asuscomm.com:9080/v1/vars_schema.json'
        strategy_schema_url = 'http://ssel.asuscomm.com:9080/v1/strategy_schema.json'
        systems_schema_url = "http://ssel.asuscomm.com:9080/v1/systems_schema.json"

        # 스키마 로드
        main_schema = load_remote_schema(main_schema_url)
        vars_schema = load_remote_schema(vars_schema_url)
        strategy_schema = load_remote_schema(strategy_schema_url)
        systems_schema = load_remote_schema(systems_schema_url)

        # 모든 스키마를 저장할 딕셔너리
        schemas = {
            main_schema_url   : main_schema,
            vars_schema_url : vars_schema,
            strategy_schema_url : strategy_schema,
            systems_schema_url : systems_schema
        }

        # RefResolver 생성
        # tid = 383
        tid = 405
        resolver = RefResolver(base_uri = main_schema_url, referrer = main_schema, store = schemas)

        # f = open(f"json_schema_test.json", encoding = "UTF-8")
        # json_data = json.load(f)
        # f.close()

        bt_request = StrategyStorage.instance().load_backtesting_request(tid)
        json_data = bt_request.cfg_stgy_rules_json
        # JSON 데이터 검증
        try :
            jsonschema.validate(instance = json_data, schema = main_schema, resolver = resolver)
            print("JSON 데이터가 유효합니다.")
        except jsonschema.exceptions.ValidationError as e :
            print("JSON 데이터가 유효하지 않습니다:")
            print(e)

    def test_remote_schema(self):
        import requests
        from jsonschema import validate, RefResolver, ValidationError

        # 원격 스키마 파일 URL
        main_schema_url = "http://ssel.asuscomm.com:9080/main_schema2.json"
        address_schema_url = "http://ssel.asuscomm.com:9080/address_schema2.json"

        # 스키마 로드 함수
        def load_schema(url) :
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        # 스키마 로드
        main_schema = load_schema(main_schema_url)
        address_schema = load_schema(address_schema_url)

        # 참조 해결자 설정
        resolver = RefResolver(base_uri = main_schema_url, referrer = main_schema)
        resolver.store[address_schema_url] = address_schema

        # 검증할 데이터 예제
        example_data = {
            "id"               : "123",
            "name"             : "John Doe",
            "billing_address"  : {
                "street"     : "123 Billing St",
                "city"       : "Billtown",
                "postalCode" : "12345"
            },
            "shipping_address" : {
                "street"     : "456 Shipping Ave",
                "city"       : "Shipcity",
                "postalCode" : "67890"
            }
        }

        # 데이터 검증
        try :
            validate(instance = example_data, schema = main_schema, resolver = resolver)
            print("JSON data is valid")
        except ValidationError as e :
            print(f"JSON data is invalid: {e.message}")
if __name__ == '__main__' :
    unittest.main()
