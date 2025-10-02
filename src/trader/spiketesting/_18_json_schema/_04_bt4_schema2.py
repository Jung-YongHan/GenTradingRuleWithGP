import json
import jsonschema
from jsonschema import RefResolver

# 스키마 파일 경로
main_schema_path        = 'bt4_schema2/main_schema.json'
strategy_schema_path    = 'bt4_schema2/strategy_schema.json'
vars_schema_path        = 'bt4_schema2/vars_schema.json'
systems_schema_path        = 'bt4_schema2/systems_schema.json'


# 스키마 파일 로드
with open(main_schema_path) as f:
    main_schema = json.load(f)

with open(strategy_schema_path) as f:
    strategy_schema = json.load(f)

with open(vars_schema_path) as f:
    vars_schema = json.load(f)

with open(systems_schema_path) as f :
    systems_schema = json.load(f)


# 참조 해결자 생성
resolver = RefResolver.from_schema(main_schema, store={
    main_schema['$id']: main_schema,
    strategy_schema['$id']: strategy_schema,
    vars_schema['$id']: vars_schema,
    systems_schema['$id']: systems_schema
})

f = open(f"bt4_schema2/test_json.json", encoding = "UTF-8")
json_data = json.load(f)

# JSON 데이터 검증
try:
    jsonschema.validate(instance=json_data, schema=main_schema, resolver=resolver)
    print("JSON 데이터가 유효합니다.")
except jsonschema.exceptions.ValidationError as e:
    print("JSON 데이터가 유효하지 않습니다:")
    print(e)