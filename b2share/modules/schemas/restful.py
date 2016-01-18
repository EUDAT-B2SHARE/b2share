# -*- coding: utf-8 -*-
# B2SHARE2

"""B2Share Communities REST API"""

from __future__ import absolute_import

from flask import Blueprint, jsonify

from invenio_rest import ContentNegotiatedMethodView

from .mock_impl import SchemaRegistry, Schema

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

    view_name = 'schema_list'

    def __init__(self, *args, **kwargs):
        super(SchemaList, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': schema_to_json_serializer,
        }

    def get(self, **kwargs):
        """
        Retrieve list of schemas.
        """
        allschemas = SchemaRegistry.get_all(**kwargs)
        print len(allschemas)
        return {'schemas': allschemas}

    def post(self, **kwargs):
        """
        Create a new schema
        """
        return None


class SchemaItem(ContentNegotiatedMethodView):

    view_name = 'schema_item'

    def __init__(self, *args, **kwargs):
        super(SchemaItem, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': schema_to_json_serializer,
        }

    def get(self, schema_id, **kwargs):
        """
        Get a schema
        """
        return SchemaRegistry.get_by_id(schema_id)

    def post(self, schema_id, **kwargs):
        """
        Create a new schema from an old one. It might be a new version.
        """
        return None


blueprint.add_url_rule('/',
                       view_func=SchemaList
                       .as_view(SchemaList.view_name))
blueprint.add_url_rule('/<int:schema_id>',
                       view_func=SchemaItem
                       .as_view(SchemaItem.view_name))
