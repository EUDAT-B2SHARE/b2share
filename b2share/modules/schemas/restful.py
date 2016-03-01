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

from flask import Blueprint, jsonify, request

from invenio_rest import ContentNegotiatedMethodView

from .api import Schema

blueprint = Blueprint(
    'b2share_schemas',
    __name__,
    url_prefix='/schemas'
)


def schema_to_json_serializer(data, code=200, headers=None):
    """Build a json flask response using the given data.
    :Returns: A flask response with json data.
    :Returns Type: :py:class:`flask.Response`
    """
    response = jsonify(data)
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response


class SchemaList(ContentNegotiatedMethodView):
    def __init__(self, *args, **kwargs):
        super(SchemaList, self).__init__(*args, **kwargs)
        self.serializers = {
            'text/html': schema_to_json_serializer,
            'application/json': schema_to_json_serializer,
        }

    def get(self, **kwargs):
        """
        Retrieve list of schemas based on list of schema ids
        """
        ids = request.args.getlist('schemaIDs[]')
        schemas = Schema.get_by_id_list(ids) if ids else Schema.get_all(**kwargs)
        return {'schemas': [s.model.json for s in schemas]}

    def post(self, **kwargs):
        """
        Create a new schema
        """
        return None


class SchemaItem(ContentNegotiatedMethodView):
    def __init__(self, *args, **kwargs):
        super(SchemaItem, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': schema_to_json_serializer,
        }

    def get(self, schema_id, **kwargs):
        """
        Get a schema
        """
        return Schema.get_by_id(schema_id).model.json

    def post(self, schema_id, **kwargs):
        """
        Create a new schema from an old one. It might be a new version.
        """
        return None


blueprint.add_url_rule('/', view_func=SchemaList .as_view('schema_list'))
blueprint.add_url_rule('/<uuid:schema_id>', view_func=SchemaItem .as_view('schema'))
