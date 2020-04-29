# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
#
# B2Share is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2Share is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2Share; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""B2SHARE"""


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
                    "unit": {"type": "string"},
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
