# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""B2Share Files views."""

from __future__ import absolute_import

from flask import Blueprint, abort, request, jsonify

from invenio_rest import ContentNegotiatedMethodView
from b2handle.handleclient import EUDATHandleClient


blueprint = Blueprint(
    'handle',
    __name__,
)


class B2HandleRetriever(ContentNegotiatedMethodView):
    """Class for handling the b2handle record retrieval."""
    view_name = 'b2handle_retriever'

    def __init__(self, **kwargs):

        default_media_type = 'application/json'

        super(B2HandleRetriever, self).__init__(
            serializers={
                default_media_type: lambda response: jsonify(response)
            },
            default_method_media_type={
                'GET': default_media_type,
            },
            default_media_type=default_media_type,
            **kwargs
        )

    def get(self, prefix, file_pid, **kwargs):
        eudat_handle_client = EUDATHandleClient()
        return eudat_handle_client.retrieve_handle_record(prefix + "/" + file_pid)


blueprint.add_url_rule('/handle/<prefix>/<file_pid>',
                       view_func=B2HandleRetriever.as_view(
                           B2HandleRetriever.view_name))
