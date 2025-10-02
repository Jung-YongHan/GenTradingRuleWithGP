member_schema = {
    "title": "회원",
    "version": 1,
    "type": "object",
    "properties": {
        "name": {"type": "string",  "minLength": 1, "maxLength": 10}, # 성명(1~10자리 허용)
        "cellphone_number": {"type": "string", "pattern": "^\d{3}-\d{3,4}-\d{4}$"},
        "address": { # 주소
            "type": "object",
            "properties": {
                "zip": {"type": "integer"}, # 우편번호
                "detail_address": {"type": "string"} # 상세주소
            }
        },
        # 숫자 범위 지정, x ≥ minimum, x > exclusiveMinimum, x ≤ maximum, x < exclusiveMaximum
        "age": {"type": "integer", "minimum": 1, "exclusiveMaximum": 200}, # 나이(1~199), 정수
        "weight": {"type": "number", "minimum": 1}, # 몸무게(1~), 정수 or 소수 ex. 70, 71.5
        "member_type_code": {"type": "string", "enum": ["VVIP", "VIP", "NORMAL"]}, # 멤버타입코드
        "is_royal_member": {"type": "boolean" }, # 로얄멤버여부
        "preferred_categories": {"type": "array", "items": {"type": "string"}} # 선호카테고리배열
    },
    "required": ["name", "cellphone_number"] # 성명과 핸드폰번호를 필수프로퍼티로 정의
}