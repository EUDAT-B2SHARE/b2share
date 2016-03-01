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

import sqlalchemy
from invenio_db import db
from sqlalchemy.orm.exc import NoResultFound

import uuid

from .models import Schema as SchemaMeta
from .default_schemas import make_community_schema
from .validate import validate_block_schema, validate_community_schema

# TODO:
#   - schemas change to new schemas with new ids
#   - deprecate a schema in favour of a new one

# a schema belongs to a community, but can be also used by another community


SCHEMA_URI_PREFIX = 'http://b2share.eudat.eu/schemas/'

class Schema(object):
    @classmethod
    def get_by_id(cls, schema_id):
        """Returns a Schema object, based on its id"""
        schema_id = str(schema_id)
        schemas = [Schema(x) for x in SchemaMeta.query.all()]
        for s in schemas:
            if s.get_id() == schema_id:
                return s
        return None

    @classmethod
    def get_by_id_list(cls, schema_id_list):
        """Returns a Schema object, based on its id"""
        schema_id_list = [str(s) for s in schema_id_list]
        schemas = [Schema(x) for x in SchemaMeta.query.all()]
        return [s for s in schemas if s.get_id() in schema_id_list]

    @classmethod
    def get_by_community_id(cls, community_id):
        """Returns a list of Schema objects that belong to a community"""
        schemas = [Schema(x) for x in SchemaMeta.query.all()]
        return [s for s in schemas if s.get_community_id() == community_id]

    @classmethod
    def get_community_schema(cls, community_id):
        """Returns the Schema object that is currently used to validate
           the records of a community"""
        schemas = [Schema(x) for x in SchemaMeta.query.all()]
        return [s for s in schemas if s.get_community_id() == community_id]

    @classmethod
    def get_all(cls, start=0, stop=20):
        """Returns all schema objects"""
        schemas = SchemaMeta.query.order_by(SchemaMeta.created).limit(stop)[start:]
        return [Schema(x) for x in schemas]

    def __init__(self, model):
        self.model = model

    def get_id(self):
        """Returns the id of the schema"""
        return self.model.json.get('id')

    def get_community_id(self):
        return self.model.json.get('community_id')

    @classmethod
    def create_schema(cls, community_id, json_schema, block_schema):
        schema_id = str(uuid.uuid4())
        community_id = str(community_id)
        schema_url = "{}{}".format(SCHEMA_URI_PREFIX, schema_id) # FIXME: use url_for?
        json_schema.update({
            'id': schema_url,
            '$schema': "http://json-schema.org/draft-04/schema#",
        })

        if block_schema:
            validate_block_schema(json_schema)
        else:
            validate_community_schema(json_schema)

        json = {
            "id": schema_id,
            "community_id": community_id,
            "block_schema": block_schema,
            "status": "draft",
            "recommended_successor": None,
            "schema": json_schema,
        }

        with db.session.begin_nested():
            model = SchemaMeta(id=schema_id, json=json)
            db.session.add(model)
            return cls(model)
