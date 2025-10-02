import json
from fastjsonschema import RefResolver
import jsonschema
import requests
from jsonschema import validate, RefResolver, Draft7Validator
import bt4.GlobalProperties as global_prop

class JSonSchemaValidator:
    def __init__(self):
        pass

    def validate(self, tr_request_json):
        is_remote = global_prop.json_schema_exec_remote
        is_remote_str = "Remote JSON Schema" if is_remote else "Local JSON Schema"
        print(f"## Execute trade request(JSON) validation based on {is_remote_str}.")
        resolver, main_schema = self.create_resolver(global_prop.json_schema_exec_remote)
        json_data = tr_request_json

        try :
            jsonschema.validate(instance = json_data, schema = main_schema, resolver = resolver)
            print("## The given trade request(JSON) is valid.")
            return True
        except jsonschema.exceptions.ValidationError as e :
            print("## The given trade request(JSON) is not valid:")
            print(e)
            return False

    def create_resolver(self, is_support_remote ):
        if is_support_remote:
            def load_remote_schema(url) :
                response = requests.get(url)
                response.raise_for_status()
                return response.json()

            main_schema_url = global_prop.main_schema_url
            vars_schema_url = global_prop.vars_schema_url
            strategy_schema_url = global_prop.strategy_schema_url
            systems_schema_url = global_prop.systems_schema_url

            main_schema = load_remote_schema(main_schema_url)
            vars_schema = load_remote_schema(vars_schema_url)
            strategy_schema = load_remote_schema(strategy_schema_url)
            systems_schema = load_remote_schema(systems_schema_url)

            schemas = {
                main_schema_url     : main_schema,
                vars_schema_url     : vars_schema,
                strategy_schema_url : strategy_schema,
                systems_schema_url  : systems_schema
            }

            # RefResolver 생성
            return RefResolver(base_uri = main_schema_url, referrer = main_schema, store = schemas), main_schema
        else:
            # 스키마 파일 경로
            main_schema_path = global_prop.main_schema_path
            strategy_schema_path = global_prop.strategy_schema_path
            vars_schema_path = global_prop.vars_schema_path
            systems_schema_path = global_prop.systems_schema_path

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
            return RefResolver.from_schema(main_schema, store = {
                main_schema['$id']     : main_schema,
                strategy_schema['$id'] : strategy_schema,
                vars_schema['$id']     : vars_schema,
                systems_schema['$id']  : systems_schema
                }), main_schema