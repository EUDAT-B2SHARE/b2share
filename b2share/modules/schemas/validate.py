# -*- coding: utf-8 -*-
# B2SHARE2
"""
B2SHARE
"""


from __future__ import absolute_import

import jsonschema

# metaschema is a restricted definition of the official jsonschema metaschema
# see https://github.com/json-schema/json-schema/blob/master/draft-04/schema
# the restricted metaschema must be used to validate community schemas
restricted_metaschema = {
    "id": "http://b2share.eudat.eu/schemas/restricted_metaschema",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "B2SHARE restricted metaschema",
    "description": """In B2SHARE, a community creates json schemas that define
                        the structure of metadata blocks. These json schemas
                        cannot be of any general jsonschema form, but can only
                        declare json objects containing simple properties which
                        are at most arrays of primitive types.""",
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "$schema": {"type": "string", "format":"uri"},
        "community_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "type": {"enum": ["object"]},
        "properties": {
            "type": "object",
            "properties": {}, # no required properties
            "additionalProperties": {
                "type": "object",
                "properties": {
                    # the properties which are defined must have this structure
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "type": {
                        "enum": ["boolean", "integer", "number", "string", "array"]
                    },
                    "default": {},
                    "maximum": {"type": "number"},
                    "minimum": {"type": "number"},
                    "enum":  {"$ref": "#/definitions/stringArray"},
                    "format": {
                        "enum": ["email", "date-time", "uri"]
                    },
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "enum": ["boolean", "integer", "number", "string"]
                            },
                            "enum":  {"$ref": "#/definitions/stringArray"},
                        }
                    },
                    "maxItems": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "minItems": {
                        "type": "integer",
                        "minimum": 0,
                        "default": 0
                    },
                    "uniqueItems": {
                        "type": "boolean",
                        "default": False
                    },
                },
                "required": ["title", "description", "type"]
            }
        },
        "required": {"$ref": "#/definitions/stringArray"},
        "additionalProperties": {"enum": [False]},
        "b2share": {
            "type": "object",
            "properties": {
                "plugins": {"type": "object"},
                "mapping": {"type": "object"},
            }
        }
    },
    "required": ["$schema", "title", "description", "type",
                 "properties", "additionalProperties"],
    "additionalProperties": False,
    "definitions": {
        "stringArray": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "uniqueItems": True,
        },
    },
}

jsonschema.Draft4Validator.check_schema(restricted_metaschema)
metaschema_validator = jsonschema.Draft4Validator(restricted_metaschema)

def validate_metadata_schema(schema):
    """ The schema param must be a json/dict object.
        The function raises an error if the schema is invalid"""
    jsonschema.Draft4Validator.check_schema(schema)
    metaschema_validator.validate(schema)
