# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask.ext.restful import Resource

class SchemaList(Resource):
    def get(self, **kwargs):
        """
        Retrieve list of schemas.
        """
        return None

    def post(self, **kwargs):
        """
        Create a new schema
        """
        return None


class Schema(Resource):
    def get(self, schema_id, **kwargs):
        """
        Get a schema
        """
        return None

    def post(self, schema_id, **kwargs):
        """
        Create a new schema from an old one. It might be a new version.
        """
        return None


def setup_app(app, api):
    api.add_resource(SchemaList, '/api/schemas')
    api.add_resource(Schema, '/api/schemas/<int:schema_id>')
