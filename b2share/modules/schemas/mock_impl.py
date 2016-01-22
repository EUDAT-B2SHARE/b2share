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
