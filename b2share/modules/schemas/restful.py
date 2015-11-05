# -*- coding: utf-8 -*-

"""B2Share Communities REST API"""

from __future__ import absolute_import

from flask import Blueprint, jsonify

from invenio_rest import ContentNegotiatedMethodView


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
    # TODO: set location to seld
    # response.headers['location'] = ...
    # TODO: set etag
    # response.set_etag(...)
    return response

class SchemaList(ContentNegotiatedMethodView):

    view_name = 'schemas_list'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(SchemaList, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': schema_to_json_serializer,
        }

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


class Schema(ContentNegotiatedMethodView):

    view_name = 'schema_item'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(Schema, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': schema_to_json_serializer,
        }

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


blueprint.add_url_rule('/',
                       view_func=SchemaList
                       .as_view(SchemaList.view_name))
blueprint.add_url_rule('/<int:schema_id>',
                       view_func=Schema
                       .as_view(Schema.view_name))
