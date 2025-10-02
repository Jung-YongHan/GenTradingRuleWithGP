import json
import os
from os.path import dirname, join

import jsonschema
from jsonschema import RefResolver

from bt4.resource_path_mgr import RPath
from bt4_cfg_stgy_rules.CfgStgyRuleLoader import CfgStgyRuleLoader

# 스키마 파일 경로
main_schema_path = 'bt4_schema/main_schema.json'
common_schema_path = 'bt4_schema/common_schema.json'
strategy_schema_path = 'bt4_schema/strategy_schema.json'
systems_schema_path = 'bt4_schema/systems_schema.json'

# 스키마 파일 로드
with open(main_schema_path) as f:
    main_schema = json.load(f)

with open(common_schema_path) as f:
    common_schema = json.load(f)

with open(strategy_schema_path) as f:
    strategy_schema = json.load(f)

with open(systems_schema_path) as f:
    systems_schema = json.load(f)

# 참조 해결자 생성
resolver = RefResolver.from_schema(main_schema, store={
    main_schema['$id']: main_schema,
    common_schema['$id']: common_schema,
    strategy_schema['$id']: strategy_schema,
    systems_schema['$id']: systems_schema,
})

stgy_json_name = "schema_test_ws_day_hdg_vol_vwap"
cfg_stgy_rules = CfgStgyRuleLoader().load(f"{stgy_json_name}.json")
json_data = cfg_stgy_rules

# JSON 데이터 검증
try:
    jsonschema.validate(instance=json_data, schema=main_schema, resolver=resolver)
    print("JSON 데이터가 유효합니다.")
except jsonschema.exceptions.ValidationError as e:
    print("JSON 데이터가 유효하지 않습니다:", e.message)