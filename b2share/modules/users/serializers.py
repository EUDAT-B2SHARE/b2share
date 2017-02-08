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

from flask import jsonify


def _generic_search_result(item_array):
    return {
        'hits': {
            'hits':item_array,
            'total':len(item_array)
        },
        'links':{}
    }


def user_to_dict(user):
    """Build a json flask response using the given data.
    :Returns: A flask response with json data.
    :Returns Type: :py:class:`flask.Response`
    """
    data = {}
    if user.is_authenticated:
        roles = [{'id': r.id, 'description': r.description, 'name': r.name}
                 for r in user.roles]
        data = {
            'id': user.id,
            'name': user.email,
            'email': user.email,
            'roles': roles
        }
    return data

def user_to_json_serializer(user, code=200):
    data = user_to_dict(user)
    response = jsonify(data)
    response.status_code = code
    return response


def token_to_dict(token, show_access_token=False):
    token_dict = {
        'id':token.id,
        'name': token.client.name
    }
    if show_access_token:
        token_dict['access_token'] = token.access_token
    return token_dict


def token_to_json_serializer(token, show_access_token=False, code=200, headers=None):
    response = jsonify(token_to_dict(token, show_access_token=show_access_token))
    response.status_code = code
    return response


def token_list_to_json_serializer(token_list, code=200, headers=None):
    token_dict_list = [token_to_dict(t) for t in token_list]
    response = _generic_search_result(token_dict_list)
    response = jsonify(response)
    response.status_code = code
    return response
