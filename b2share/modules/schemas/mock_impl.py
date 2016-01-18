# -*- coding: utf-8 -*-
# B2SHARE2


from __future__ import absolute_import
from .api import SchemaRegistryInterface, SchemaInterface
from .default_schemas import schema_basic
from .validate import validate_metadata_schema

SCHEMA_URI_PREFIX = 'http://b2share.eudat.eu/schemas/'

class Schema(SchemaInterface, dict):
    def __init__(self, json_schema):
        dict.__init__(self)
        self.update(json_schema)

    def get_id(self):
        sid = self.get('id')
        if sid.startswith(SCHEMA_URI_PREFIX):
            return sid[len(SCHEMA_URI_PREFIX):]
        return sid

    def get_community_id(self):
        return self.get('community_id')


class SchemaRegistry(SchemaRegistryInterface):
    schemas = []

    @staticmethod
    def get_basic_schema():
        return SchemaRegistry.schemas[0]

    @staticmethod
    def get_by_id(schema_id):
        schema_id = str(schema_id)
        for s in SchemaRegistry.schemas:
            if s.get_id() == schema_id:
                return s
        return None

    @staticmethod
    def get_by_community_id(community_id):
        return [s for s in SchemaRegistry.schemas if s.get_community_id() == community_id]

    @staticmethod
    def get_all(start=0, stop=20):
        return SchemaRegistry.schemas[start:stop]

    @staticmethod
    def _add(json_schema):
        schema_id = len(SchemaRegistry.schemas)
        json_schema['id'] = '{}{}'.format(SCHEMA_URI_PREFIX, schema_id)
        validate_metadata_schema(json_schema)
        schema = Schema(json_schema)
        SchemaRegistry.schemas.append(schema)
        return schema

SchemaRegistry._add(schema_basic)
