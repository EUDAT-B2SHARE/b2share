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

from flask import Blueprint, abort, request, jsonify
from flask_login import current_user
from flask_security.decorators import auth_required

from invenio_db import db
from invenio_rest import ContentNegotiatedMethodView
from invenio_oauth2server import current_oauth2server
from invenio_oauth2server.models import Token

from .serializers import (user_to_json_serializer,
                          token_to_json_serializer,
                          token_list_to_json_serializer)


blueprint = Blueprint(
    'b2share_users',
    __name__,
    url_prefix='/users'
)


class CurrentUser(ContentNegotiatedMethodView):

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(CurrentUser, self).__init__(
            default_method_media_type={
                'GET': 'application/json',
                'POST': 'application/json',
            },
            default_media_type='application/json',
            *args, **kwargs)

    def get(self, **kwargs):
        return user_to_json_serializer(current_user)


def _get_token(token_id, is_personal=True, is_internal=False):
    if not token_id:
        abort(400)
    token = Token.query.filter_by(
        id=token_id,
        user_id=current_user.get_id(),
        is_personal=is_personal,
        is_internal=is_internal,
    ).first()
    if token is None:
        abort(404)
    return token


class UserTokenList(ContentNegotiatedMethodView):

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(UserTokenList, self).__init__(
            default_method_media_type={
                'GET': 'application/json',
                'POST': 'application/json',
            },
            default_media_type='application/json',
            *args, **kwargs)

    @auth_required('token', 'session')
    def get(self, **kwargs):
        token_list = Token.query.filter_by(
            user_id=current_user.get_id(),
            is_personal=True,
            is_internal=False,
        ).all()
        return token_list_to_json_serializer(token_list)

    @auth_required('token', 'session')
    def post(self, **kwargs):
        token_name = request.get_json().get('token_name')
        if not token_name:
            abort(400)

        scopes = current_oauth2server.scope_choices()
        token = Token.create_personal(
            token_name, current_user.get_id(), scopes=[s[0] for s in scopes]
        )
        db.session.commit()
        return token_to_json_serializer(token, show_access_token=True, code=201)


class UserToken(ContentNegotiatedMethodView):

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(UserToken, self).__init__(
            default_method_media_type={
                'GET': 'application/json',
                'POST': 'application/json',
            },
            default_media_type='application/json',
            *args, **kwargs)


    @auth_required('token', 'session')
    def get(self, token_id, **kwargs):
        token = _get_token(token_id)
        return token_to_json_serializer(token)

    @auth_required('token', 'session')
    def delete(self, token_id, **kwargs):
        token = _get_token(token_id)
        db.session.delete(token)
        db.session.commit()
        return jsonify({}) # ok


blueprint.add_url_rule('/current', view_func=CurrentUser.as_view('current_user'))
blueprint.add_url_rule('/current/tokens', view_func=UserTokenList.as_view('user_token_list'))
blueprint.add_url_rule('/current/tokens/<token_id>', view_func=UserToken.as_view('user_token_item'))
