# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
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

from flask import Blueprint, jsonify, current_app

from invenio_rest import ContentNegotiatedMethodView

from b2share import __version__


blueprint = Blueprint('b2share_apiroot', __name__, url_prefix='/')


class ApiRoot(ContentNegotiatedMethodView):

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(ApiRoot, self).__init__(
            default_method_media_type={'GET': 'application/json'},
            default_media_type='application/json', *args, **kwargs)

    def get(self, **kwargs):
        b2access = current_app.config.get('OAUTHCLIENT_REMOTE_APPS', {}).get(
            'b2access', {})
        help_links = current_app.config.get('HELP_LINKS')
        data = {
            'version': __version__,
            'site_function': current_app.config.get('SITE_FUNCTION', ''),
            'training_site_link': current_app.config.get('TRAINING_SITE_LINK', ''),
            'b2access_registration_link': b2access.get('registration_url'),
            'b2note_url': current_app.config.get('B2NOTE_URL'),
            'terms_of_use_link': current_app.config.get('TERMS_OF_USE_LINK'),
            'help_links': {
                'issues': help_links.get('issues', ''),
                'user-guide': help_links.get('user-guide', ''),
                'rest-api': help_links.get('rest-api', ''),
                'search': help_links.get('search', '')
            }
        }
        response = jsonify(data)
        return response


blueprint.add_url_rule('/', view_func=ApiRoot.as_view('info'))
