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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2Share schemas module's REST API."""

from __future__ import absolute_import

from functools import wraps

from flask import Blueprint, abort, request, current_app
from invenio_rest import ContentNegotiatedMethodView
from b2share.modules.communities.views import pass_community
from b2share.modules.schemas.errors import InvalidBlockSchemaError, \
    InvalidSchemaVersionError, SchemaVersionExistsError
from jsonpatch import JsonPatchConflict, JsonPatchException, \
    InvalidJsonPatch

from .api import BlockSchema, CommunitySchema
from .errors import BlockSchemaDoesNotExistError, \
    CommunitySchemaDoesNotExistError
from .serializers import block_schema_version_to_json_serializer, \
    block_schema_to_dict, \
    community_schema_to_json_serializer, \
    block_schema_to_json_serializer, schemas_list_to_json_serializer, \
    community_schema_list_to_json_serializer
from invenio_db import db
from webargs import fields
from webargs.flaskparser import use_kwargs


blueprint = Blueprint(
    'b2share_schemas',
    __name__,
)


def pass_block_schema(f):
    """Decorator retrieving a block schema."""

    @wraps(f)
    def inner(self, schema_id, *args, **kwargs):
        try:
            block_schema = BlockSchema.get_block_schema(
                schema_id=schema_id)
        except BlockSchemaDoesNotExistError:
            abort(404)
        return f(self, block_schema=block_schema, *args, **kwargs)

    return inner


def pass_block_schema_version(f):
    """Decorator retrieving a block schema version."""

    @wraps(f)
    def inner(self, block_schema, schema_version_nb, *args, **kwargs):
        try:
            if schema_version_nb == 'last':
                block_schema_version = block_schema.versions[
                    len(block_schema.versions) - 1
                ]
            elif schema_version_nb.isdigit():
                version_nb = int(schema_version_nb)
                block_schema_version = block_schema.versions[schema_version_nb]
            else:
                abort(400)
        except IndexError:
            abort(404)
        return f(self, block_schema=block_schema,
                 block_schema_version=block_schema_version, *args, **kwargs)

    return inner


class BlockSchemaVersionResource(ContentNegotiatedMethodView):
    view_name = 'block_schema_versions_item'

    def __init__(self, **kwargs):
        """Constructor."""
        super(BlockSchemaVersionResource, self).__init__(
            serializers={
                'application/json': block_schema_version_to_json_serializer,
            },
            default_media_type='application/json',
            **kwargs
        )

    @pass_block_schema
    @pass_block_schema_version
    def get(self, block_schema, block_schema_version):
        self.check_etag(str(block_schema_version.released))
        return block_schema_version

    def put(self, schema_id, schema_version_nb):
        """Create a new version of the schema."""
        block_schema = BlockSchema.get_block_schema(schema_id)

        data = request.get_json()
        if data is None:
            return abort(400)

        try:
            schema = block_schema.create_version(
                data['json_schema'],
                int(schema_version_nb)
            )
        except InvalidSchemaVersionError as e:
            abort(400, str(e))
        except SchemaVersionExistsError as e:
            abort(409, str(e))
        return self.make_response(
            block_schema_version=schema,
            code=201,
        )


def pass_community_schema(f):
    """Decorator retrieving a community schema."""

    @wraps(f)
    def inner(self, community_id, schema_version_nb, *args, **kwargs):
        try:
            if schema_version_nb.isdigit():
                version_nb = int(schema_version_nb)
                community_schema = CommunitySchema.get_community_schema(
                    community_id=community_id,
                    version=version_nb
                )
            else:
                if schema_version_nb == 'last':
                    community_schema = CommunitySchema.get_community_schema(
                        community_id=community_id
                    )
                else:
                    abort(400)
        except CommunitySchemaDoesNotExistError:
            abort(404)
        return f(self, community_schema=community_schema, *args, **kwargs)

    return inner


class CommunitySchemaResource(ContentNegotiatedMethodView):
    view_name = 'community_schema_item'

    def __init__(self, **kwargs):
        """Constructor."""
        super(CommunitySchemaResource, self).__init__(
            serializers={
                'application/json':
                    community_schema_to_json_serializer,
            },
            default_method_media_type={
                'GET': 'application/json',
                'PATCH': 'application/json',
            },
            default_media_type='application/json',
            **kwargs
        )

    @pass_community_schema
    def get(self, community_schema):
        return community_schema

    def put(self, community_id, schema_version_nb):
        """Create a new version of the schema."""
        data = request.get_json()
        if data is None:
            return abort(400)

        try:
            community_schema_version = CommunitySchema.create_version(
                community_id,
                data['json_schema'],
                None,
                int(schema_version_nb)
            )
        except InvalidSchemaVersionError as e:
            abort(400, str(e))
        except SchemaVersionExistsError as e:
            abort(409, str(e))
        return self.make_response(
            community_schema=community_schema_version,
            code=201,
        )


class CommunitySchemaListResource(ContentNegotiatedMethodView):
    view_name = 'community_schema_list'

    def __init__(self, **kwargs):
        """Constructor."""
        super(CommunitySchemaListResource, self).__init__(
            serializers={
                'application/json':
                    community_schema_list_to_json_serializer,
            },
            default_media_type='application/json',
            **kwargs
        )

    def get(self):
        """Get a list of all schemas."""
        community_schemas = CommunitySchema.get_all_community_schemas()
        return self.make_response(
            community_schemas=community_schemas,
            code=200
        )


class BlockSchemaListResource(ContentNegotiatedMethodView):
    view_name = 'block_schema_list'

    def __init__(self, **kwargs):
        """Constructor."""
        super(BlockSchemaListResource, self).__init__(
            method_serializers={
                'GET': {
                    'application/json': schemas_list_to_json_serializer,
                },
                'POST': {
                    'application/json': block_schema_to_json_serializer,
                }
            },
            default_media_type='application/json',
            **kwargs
        )

    def get(self):
        """Get a list of all schemas."""
        community_id = request.args['community_id']
        schemas = BlockSchema.get_all_block_schemas(community_id=community_id)
        return self.make_response(
            schemas=schemas,
            code=200
        )

    def post(self):
        """Create a new schema."""
        if request.content_type != 'application/json':
            abort(415)
        data = request.get_json()
        if data is None:
            return abort(400)

        schema = BlockSchema.create_block_schema(**data)
        return self.make_response(
            schema=schema,
            code=201,
        )


class BlockSchemaResource(ContentNegotiatedMethodView):
    view_name = 'block_schema_item'

    def __init__(self, **kwargs):
        """Constructor."""
        super(BlockSchemaResource, self).__init__(
            serializers={
                'application/json': block_schema_to_json_serializer
            },
            default_media_type='application/json',
            **kwargs
        )

    def get(self, schema_id):
        """Get a schema."""
        schema = BlockSchema.get_block_schema(schema_id)
        self.check_etag(str(schema.updated))

        return self.make_response(
            schema=schema,
            code=200
        )

    def patch(self, schema_id):
        """Patch a schema."""
        data = request.get_json(force=True)
        if data is None:
            abort(400)

        block_schema = BlockSchema.get_block_schema(schema_id)
        self.check_etag(str(block_schema.updated))

        try:
            if 'application/json' == request.content_type:
                block_schema.update(data)
            else:
                block_schema = block_schema.patch(data)
            db.session.commit()
            return self.make_response(
                schema=block_schema,
                code=200
            )
        except (JsonPatchConflict):
            abort(409)
        except (JsonPatchException):
            abort(400)
        except InvalidBlockSchemaError:
            db.session.rollback()
            abort(400)
        except Exception as e1:
            current_app.logger.exception('Failed to patch record.')
            try:
                db.session.rollback()
            except Exception as e2:
                raise e2 from e1
            abort(500)


blueprint.add_url_rule(
    '/schemas/<string:schema_id>/versions/<string:schema_version_nb>',
    view_func=BlockSchemaVersionResource
        .as_view(BlockSchemaVersionResource.view_name))


blueprint.add_url_rule(
    '/communities/<string:community_id>/schemas/<string:schema_version_nb>',
    view_func=CommunitySchemaResource
        .as_view(CommunitySchemaResource.view_name))


blueprint.add_url_rule(
    '/schemas/<string:schema_id>',
    view_func=BlockSchemaResource
        .as_view(BlockSchemaResource.view_name))

blueprint.add_url_rule(
    '/schemas',
    view_func=BlockSchemaListResource
        .as_view(BlockSchemaListResource.view_name))

blueprint.add_url_rule(
    '/communities/schemas',
    view_func=CommunitySchemaListResource
        .as_view(CommunitySchemaListResource.view_name))
