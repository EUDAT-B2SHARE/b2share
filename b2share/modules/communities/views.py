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

"""B2Share Communities REST API"""

from __future__ import absolute_import

from functools import wraps

from flask import Blueprint, abort, current_app, make_response, request, \
                  jsonify, url_for
from invenio_db import db
from invenio_rest import ContentNegotiatedMethodView
from invenio_rest.decorators import require_content_types
from jsonpatch import InvalidJsonPatch, JsonPatchConflict, JsonPatchException
from werkzeug.exceptions import HTTPException
from werkzeug.local import LocalProxy

from .api import Community
from .errors import CommunityDeletedError, CommunityDoesNotExistError, \
    InvalidCommunityError
from .permissions import communities_create_all_permission, \
    delete_permission_factory, read_permission_factory, \
    update_permission_factory
from .serializers import community_to_json_serializer, \
    search_to_json_serializer, community_self_link
from b2share.utils import is_valid_uuid

current_communities = LocalProxy(
    lambda: current_app.extensions['b2share-communities'])

blueprint = Blueprint(
    'b2share_communities',
    __name__,
    url_prefix='/communities'
)


def pass_community(f):
    """Decorator to retrieve a community."""
    @wraps(f)
    def inner(self, community_id, *args, **kwargs):
        try:
            if is_valid_uuid(community_id):
                community = Community.get(id=community_id)
            else:
                community = Community.get(name=community_id)
        except (CommunityDoesNotExistError):
            abort(404)
        except (CommunityDeletedError):
            abort(410)

        return f(self, community=community, *args, **kwargs)
    return inner


def verify_community_permission(permission_factory, community):
    """Check that the current user has the required permissions on community.

    Args:
        permission_factory: permission factory used to check permissions.
        community: community whose access is limited.
    """
    # Note, cannot be done in one line due overloading of boolean
    # operations permission object.
    if not permission_factory(community).can():
        from flask_login import current_user
        if not current_user.is_authenticated:
            abort(401)
        abort(403)


def need_community_permission(permission_factory):
    """Decorator checking that the user has the required community permissions.

    Args:
        factory_name: name of the factory to retrieve.
    """
    def need_community_permission_builder(f):
        @wraps(f)
        def need_community_permission_decorator(self, community, *args,
                                                **kwargs):
            verify_community_permission(permission_factory, community)
            return f(self, community=community, *args, **kwargs)
        return need_community_permission_decorator
    return need_community_permission_builder


def _generic_search_result(item_array):
    self_link = url_for('b2share_communities.communities_list', _external=True)
    return {
        'hits': {
            'hits':item_array,
            'total':len(item_array)
        },
        'links':{
            'self': self_link,
        }
    }


class CommunityListResource(ContentNegotiatedMethodView):

    view_name = 'communities_list'

    def __init__(self, **kwargs):
        """Constructor."""
        super(CommunityListResource, self).__init__(
            method_serializers={
                'GET': {
                    'application/json': search_to_json_serializer,
                },
                'POST': {
                    'application/json': community_to_json_serializer,
                },
            },
            default_method_media_type={
                'GET': 'application/json',
                'POST': 'application/json',
            },
            default_media_type='application/json',
            **kwargs)

    def get(self):
        """Retrieve a list of communities."""
        # TODO: change this to a search function, not just a list of communities
        from .serializers import community_to_dict
        start = request.args.get('start') or 0
        stop = request.args.get('stop') or 100
        community_list = Community.get_all(start, stop)
        community_dict_list = [community_to_dict(c) for c in community_list]
        response_dict = _generic_search_result(community_dict_list)
        response = jsonify(response_dict)
        # TODO: set etag
        return response

    # def post(self):
    #     """Create a new community."""
    #     if request.content_type != 'application/json':
    #         abort(415)
    #     data = request.get_json()
    #     if data is None:
    #         return abort(400)
    #     # check user permissions
    #     if (not current_communities.rest_access_control_disabled and
    #             not communities_create_all_permission.can()):
    #         from flask_login import current_user
    #         if not current_user.is_authenticated:
    #             abort(401)
    #         abort(403)

    #     try:
    #         community = Community.create_community(**data)
    #         response = self.make_response(
    #             community=community,
    #             code=201,
    #         )
    #         # set the header's Location field.
    #         response.headers['Location'] = community_self_link(community)
    #         db.session.commit()
    #         return response
    #     except InvalidCommunityError as e1:
    #         try:
    #             db.session.rollback()
    #         except Exception as e2:
    #             raise e2 from e1
    #         abort(400)
    #     except Exception as e1:
    #         try:
    #             db.session.rollback()
    #         except Exception as e2:
    #             raise e2 from e1
    #         if isinstance(e1, HTTPException):
    #             raise e1
    #         current_app.logger.exception('Failed to create record.')
    #         abort(500)


class CommunityResource(ContentNegotiatedMethodView):

    view_name = 'communities_item'

    def __init__(self, **kwargs):
        """Constructor."""
        super(CommunityResource, self).__init__(
            serializers={
                'application/json': community_to_json_serializer,
            },
            method_serializers={
                'DELETE': {'*/*': lambda *args: make_response(*args), },
            },
            default_method_media_type={
                'GET': 'application/json',
                'PUT': 'application/json',
                'DELETE': '*/*',
                'PATCH': 'application/json',
            },
            default_media_type='application/json',
            **kwargs)

    # @pass_community
    # @need_community_permission(delete_permission_factory)
    # def delete(self, community, **kwargs):
    #     """Delete a community."""
    #     # check the ETAG
    #     self.check_etag(str(community.updated))
    #     try:
    #         community.delete()
    #         db.session.commit()
    #     except Exception as e1:
    #         current_app.logger.exception('Failed to create record.')
    #         try:
    #             db.session.rollback()
    #         except Exception as e2:
    #             raise e2 from e1
    #         abort(500)
    #     return '', 204

    @pass_community
    @need_community_permission(read_permission_factory)
    def get(self, community, **kwargs):
        """Get a community's metadata."""
        # check the ETAG
        self.check_etag(str(community.updated))
        return community

    # @require_content_types('application/json-patch+json', 'application/json')
    # @pass_community
    # @need_community_permission(update_permission_factory)
    # def patch(self, community, **kwargs):
    #     """Patch a community."""
    #     # check the ETAG
    #     self.check_etag(str(community.updated))

    #     data = request.get_json(force=True)
    #     if data is None:
    #         abort(400)
    #     try:
    #         if 'application/json' == request.content_type:
    #             community.update(data)
    #         else:
    #             community = community.patch(data)
    #         db.session.commit()
    #         return community
    #     except (JsonPatchConflict):
    #         abort(409)
    #     except (JsonPatchException, InvalidJsonPatch):
    #         abort(400)
    #     except InvalidCommunityError:
    #         db.session.rollback()
    #         abort(400)
    #     except Exception as e1:
    #         current_app.logger.exception('Failed to patch record.')
    #         try:
    #             db.session.rollback()
    #         except Exception as e2:
    #             raise e2 from e1
    #         abort(500)

    # @require_content_types('application/json')
    # @pass_community
    # @need_community_permission(update_permission_factory)
    # def put(self, community, **kwargs):
    #     """Put a community."""
    #     # check the ETAG
    #     self.check_etag(str(community.updated))

    #     data = request.get_json(force=True)
    #     if data is None:
    #         abort(400)
    #     try:
    #         community.update(data, clear_fields=True)
    #         db.session.commit()
    #         return community
    #     except InvalidCommunityError:
    #         db.session.rollback()
    #         abort(400)
    #     except Exception as e1:
    #         current_app.logger.exception('Failed to patch record.')
    #         try:
    #             db.session.rollback()
    #         except Exception as e2:
    #             raise e2 from e1
    #         abort(500)

blueprint.add_url_rule('/',
                       view_func=CommunityListResource
                       .as_view(CommunityListResource.view_name))
blueprint.add_url_rule('/<community_id>',
                       view_func=CommunityResource
                       .as_view(CommunityResource.view_name))
