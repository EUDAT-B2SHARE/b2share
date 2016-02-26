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

from __future__ import absolute_import

from flask import url_for

from .default_schemas import schema_basic
from .validate import validate_metadata_schema

# TODO:
#   - schemas change to new schemas with new ids
#   - deprecate a schema in favour of a new one

# a schema belongs to a community, but can be also used by another community


SCHEMA_URI_PREFIX = 'http://b2share.eudat.eu/schemas/'

class SchemaRegistry(object):
    schemas = []
    @classmethod
    def get_basic_schema(cls):
        """Returns the basic Schema object, common for all communities"""
        return SchemaRegistry.schemas[0]

    @classmethod
    def get_by_id(cls, schema_id):
        """Returns a Schema object, based on its id"""
        schema_id = str(schema_id)
        for s in SchemaRegistry.schemas:
            if s.get_id() == schema_id:
                return s
        return None

    @classmethod
    def get_by_id_list(cls, schema_id_list):
        """Returns a Schema object, based on its id"""
        schema_id_list = [str(s) for s in schema_id_list]
        return [s for s in SchemaRegistry.schemas if s.get_id() in schema_id_list]

    @classmethod
    def get_by_community_id(cls, community_id):
        """Returns a list of Schema objects that belong to a community"""
        return [s for s in SchemaRegistry.schemas if s.get_community_id() == community_id]

    @classmethod
    def get_all(cls, start=0, stop=20):
        """Returns all schema objects"""
        return SchemaRegistry.schemas[start:stop]

    @classmethod
    def create_schema(cls, json_schema, community_id):
        import uuid
        schema_id = str(uuid.uuid4())
        schema_url = "{}{}".format(SCHEMA_URI_PREFIX, schema_id) # FIXME: use url_for?
        json_schema.update({
            'id': schema_url,
            '$schema': "http://json-schema.org/draft-04/schema#",
        })
        validate_metadata_schema(json_schema)
        schema = Schema(schema_id, community_id, json_schema)
        SchemaRegistry.schemas.append(schema)
        return schema


class Schema(dict):
    """ A Schema object is a shallow object encapsulating a jsonschema object.
        A Schema cannot be ever deleted"""
    def __init__(self, schema_id, community_id, json_schema):
        super(Schema, self).__init__(self)
        self.update({
            "id": schema_id,
            "community_id": community_id,
            "block_schema": True,
            "status": "draft",
            "recommended_successor": None,
            "schema": json_schema,
        })

    def get_id(self):
        """Returns the id of the schema"""
        return self.get('id')

    def get_community_id(self):
        return self.get('community_id')


def init():
    SchemaRegistry.create_schema(schema_basic, None)

init() # FIXME: save schemas to database and remove this line
