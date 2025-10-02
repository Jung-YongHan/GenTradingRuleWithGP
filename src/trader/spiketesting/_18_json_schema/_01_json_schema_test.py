import json
import unittest

from spiketesting._18_json_schema.member_schema import member_schema


class MyTestCase(unittest.TestCase) :
    def test_json_schema_validate0(self) :
        from jsonschema import validate

        member1 = """{
            "name"                 : "홍길동xxxxxxxxxx",
            "cellphone_number"     : "010-1111-1111",
            "address"              : {"zip" : 12345, "detail_address" : "100번지"},
            "age"                  : 30,
            "weight"               : 70.5,
            "member_type_code"     : "VIP",
            "is_royal_member"      : true,
            "preferred_categories" : ["IT", "FOOD"]
        }"""
        loaded_json = json.loads(member1)
        print(validate(schema = member_schema, instance = loaded_json))


if __name__ == '__main__' :
    unittest.main()
