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

"""B2Share Stats REST API"""

from __future__ import absolute_import

from flask import Blueprint, request,  jsonify, make_response

from invenio_rest import ContentNegotiatedMethodView
from invenio_oauth2server.decorators import require_api_auth
from b2share.modules.access.permissions import admin_only

from .api import get_quota, users_list


blueprint = Blueprint('b2share_statistics', __name__)

def switch_queries(value):
    actions = {
        'quota': get_quota,
        'users': users_list
        # add more keys and values as needed
    }
    try:
        return actions[value]()
    except KeyError:
        return None



class B2shareStatisticsCollection(ContentNegotiatedMethodView):
    """B2SHARE specific stats endpoint.
    
    This is not an extension to invenio-stats, but an independent
    endpoint in B2SHARE.
    """

    view_name = 'record_ownership'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(B2shareStatisticsCollection, self).__init__(
            default_method_media_type={
                'GET': 'application/json',
            },
            default_media_type='application/json', *args, **kwargs)

    #@require_api_auth()
    @admin_only.require(http_exception=403)
    def get(self):
        query_type=request.args.get('query',None)
        query_result=switch_queries(query_type)
        
        if query_result is not None:
                response={"query":query_type,
                        "response":query_result
                        }
                return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify({'Error': 'query arguments missing or not correct'}), 400)
        

blueprint.add_url_rule(
    '/collections/statistics',
    view_func=B2shareStatisticsCollection.as_view(
        B2shareStatisticsCollection.view_name
    )
)
