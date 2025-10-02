import json
import jsonschema
from jsonschema import RefResolver

# 스키마 파일 경로
main_schema_path = 'schemas/main_schema.json'
person_schema_path = 'schemas/person_schema.json'
address_schema_path = 'schemas/address_schema.json'

# 스키마 파일 로드
with open(main_schema_path) as f:
    main_schema = json.load(f)

with open(person_schema_path) as f:
    person_schema = json.load(f)

with open(address_schema_path) as f:
    address_schema = json.load(f)

# 참조 해결자 생성
resolver = RefResolver.from_schema(main_schema, store={
    main_schema['$id']: main_schema,
    person_schema['$id']: person_schema,
    address_schema['$id']: address_schema,
})

# JSON 데이터 예제
json_data = {
    "person": {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "address": {
            "street_address": "123 Main St",
            "city": "Anytown",
            "state": "CA"
        }
    }
}

# JSON 데이터 검증
try:
    jsonschema.validate(instance=json_data, schema=main_schema, resolver=resolver)
    print("JSON 데이터가 유효합니다.")
except jsonschema.exceptions.ValidationError as e:
    print("JSON 데이터가 유효하지 않습니다:", e.message)