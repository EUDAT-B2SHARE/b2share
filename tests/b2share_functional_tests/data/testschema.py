test_schema = """{
    "description": "This is the blueprint of the metadata block specific for a unit test community",
    "additionalProperties": false,
    "type": "object",
    "properties": {
        "some_field": {
            "description": "The only field in this schema",
            "title": "Field nr 1",
            "type": "string"
        }
    },
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "EISCAT Metadata"
}"""
