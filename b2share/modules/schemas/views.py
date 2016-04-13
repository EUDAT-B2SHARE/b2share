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

from flask import Blueprint, abort
from invenio_rest import ContentNegotiatedMethodView
from b2share.modules.communities.views import pass_community

from .api import BlockSchema, CommunitySchema
from .errors import BlockSchemaDoesNotExistError, \
    CommunitySchemaDoesNotExistError
from .serializers import block_schema_version_to_json_serializer, \
    community_schema_to_json_serializer

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
            block_schema_version = block_schema.versions[schema_version_nb]
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
            default_method_media_type={
                'GET': 'application/json',
                'PATCH': 'application/json',
            },
            default_media_type='application/json',
            **kwargs
        )

    @pass_block_schema
    @pass_block_schema_version
    def get(self, block_schema, block_schema_version):
        return block_schema_version


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


blueprint.add_url_rule(
    '/schemas/<string:schema_id>/versions/<int:schema_version_nb>',
    view_func=BlockSchemaVersionResource
    .as_view(BlockSchemaVersionResource.view_name))

blueprint.add_url_rule(
    '/communities/<string:community_id>/schemas/<string:schema_version_nb>',
    view_func=CommunitySchemaResource
    .as_view(CommunitySchemaResource.view_name))
