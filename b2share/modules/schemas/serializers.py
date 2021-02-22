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

"""B2Share schemas module's serializers."""

from __future__ import absolute_import

import json

from flask import jsonify, url_for


def block_schema_version_self_link(block_schema_version, **kwargs):
    """Create self link to a given block_schema_version.

    Args:
        block_schema_version (:class:`b2share.modules.schemas.api:BlockSchemaVersion`):
            block schema version to which the generated link will point.

        **kwargs: additional parameters given to flask.url_for.

    :Returns:
        str: link pointing to the given block_schema_version.
    """  # noqa
    return url_for(
        'b2share_schemas.block_schema_versions_item',
        schema_id=block_schema_version.block_schema.id,
        schema_version_nb=block_schema_version.version,
        **kwargs)


def block_schema_version_json_schema_link(block_schema_version, **kwargs):
    return '{}#/json_schema'.format(
        block_schema_version_self_link(block_schema_version, **kwargs))


def block_schema_version_to_dict(block_schema_version):
    """Serializes block schema version to dict.

    Args:
        block_schema_version
            (:class:`b2share.modules.schemas.api:BlockSchemaVersion`):
            block schema version that will be serialized.

    Returns:
        dict: serialized BlockSchemaVersion.
    """
    return dict(
        id=block_schema_version.block_schema.id,
        version=block_schema_version.version,
        json_schema=json.loads(block_schema_version.json_schema),
    )


def block_schema_version_to_json_serializer(block_schema_version, code=200,
                                            headers=None):
    """Serializes block schema version to json response.

    Args:
        block_schema_version
            (:class:`b2share.modules.schemas.api:BlockSchemaVersion`):
            block schema version that will be serialized.

        code: http response status.

        headers: additional http response headers.

    Returns:
        Response: serialized response from BlockSchemaVersion.
    """
    response = jsonify(block_schema_version_to_dict(block_schema_version))
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response


def community_schema_self_link(community_schema, **kwargs):
    """Create self link to a given community schema.

    Args:
        community_schema (:class:`b2share.modules.schemas.api:CommunitySchema`):
            community schema version to which the generated link will point.

        **kwargs: additional parameters given to flask.url_for.

    Returns:
        str: link pointing to the given community schema.
    """  # noqa
    return url_for(
        'b2share_schemas.community_schema_item',
        community_id=community_schema.community,
        schema_version_nb=community_schema.version,
        **kwargs)


def community_schemas_self_link(community_schema, **kwargs):
    """Create self link to the community schemas listing.

    Args:
        community_schema (:class:`b2share.modules.schemas.api:CommunitySchema`):
            community schema version to which the generated link will point.

        **kwargs: additional parameters given to flask.url_for.

    Returns:
        str: link pointing to the given community schema.
    """  # noqa
    return url_for(
        'b2share_schemas.community_schema_list',
        community_id=community_schema.community,
        **kwargs)


def community_schema_json_schemas_link(community_schema, **kwargs):
    """Build the URL to the community's publication JSON Schemas."""
    return '{}'.format(
        community_schemas_self_link(community_schema, **kwargs))


def community_schema_json_schema_link(community_schema, **kwargs):
    """Build the URL to the community's publication JSON Schema."""
    return '{}#/json_schema'.format(
        community_schema_self_link(community_schema, **kwargs))


def community_schema_draft_json_schema_link(community_schema, **kwargs):
    """Build the URL to the community's draft JSON Schema."""
    return '{}#/draft_json_schema'.format(
        community_schema_self_link(community_schema, **kwargs))


def community_schema_to_dict(community_schema):
    return dict(
        community=community_schema.community,
        version=community_schema.version,
        json_schema=community_schema.build_json_schema(),
        draft_json_schema={
            "$schema": "http://json-schema.org/draft-04/schema#",
            "$ref": community_schema_json_schema_link(community_schema,
                                                      _external=True)
        },
        links={
            'self': community_schema_self_link(community_schema,
                                               _external=True)
        }
    )


def community_schema_to_json_serializer(community_schema, code=200,
                                        headers=None):
    response = jsonify(community_schema_to_dict(community_schema))
    response.status_code = code
    response.set_etag(str(community_schema.released.utcfromtimestamp(0)))
    if headers is not None:
        response.headers.extend(headers)
    return response


def community_schemas_list_to_json_serializer(schemas, code=200,
                                        headers=None):
    response = jsonify(list(map(lambda x: community_schema_to_dict(x), schemas)))
    response.status_code = code
    response.set_etag(str(schemas[0].released.utcfromtimestamp(0)))
    if headers is not None:
        response.headers.extend(headers)
    return response


def block_schema_to_dict(schema):
    """Serializes block schema to dict.

    Args:
        schema: block schema to serialize into dict.

    Returns:
        dict: dict from BlockSchema.
     """
    return dict(
        schema_id=str(schema.id),
        name=schema.name
    )


def block_schema_to_json_serializer(schema, code=200, headers=None):
    """Serializes block schema to json response.

    Args:
        schema: block schema to serialize into json response.
        code: http response code.
        headers: additional http response headers.

    Returns:
        Response: response from list of BlockSchemas.
     """
    response = jsonify(block_schema_to_dict(schema))
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response


def schemas_list_to_dict(schemas):
    """Serializes schemas list to dict.

    Args:
        schemas: list of BlockSchemas.

    Returns:
        dict: dict with list of BlockSchema.
     """
    return dict(
        schemas=list(map(block_schema_to_dict, schemas))
    )


def schemas_list_to_json_serializer(schemas, code=200, headers=None):
    """Serializes schema list to json response.

    Args:
        schemas: list of block schemas.
        code: http response code.
        headers: additional http response headers.

    Returns:
        Response: response from list of BlockSchemas.
     """
    response = jsonify(schemas_list_to_dict(schemas))
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response
