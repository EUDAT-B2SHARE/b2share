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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Demonstration configuration."""

from __future__ import absolute_import, print_function


OAUTHCLIENT_REMOTE_APPS=dict(
    #: B2ACCESS Staging instance for the demo
    b2access=dict(
        title='B2Access',
        description='EUDAT B2Access authentication.',
        icon='',
        authorized_handler="invenio_oauthclient.handlers:authorized_signup_handler",
        disconnect_handler="invenio_oauthclient.handlers:disconnect_handler",
        signup_handler=dict(
            info="b2share.oauth.b2access:account_info",
            setup="b2share.oauth.b2access:account_setup",
            view="invenio_oauthclient.handlers:signup_handler",
        ),
        params=dict(
            request_token_params={'scope': 'USER_PROFILE GENERATE_USER_CERTIFICATE'},
            base_url='https://unity.eudat-aai.fz-juelich.de:8443/',
            request_token_url=None,
            access_token_url= "https://unity.eudat-aai.fz-juelich.de:8443/oauth2/token",
            access_token_method='POST',
            authorize_url="https://unity.eudat-aai.fz-juelich.de:8443/oauth2-as/oauth2-authz",
            app_key="B2ACCESS_APP_CREDENTIALS",
        ),
        tokeninfo_url = "https://unity.eudat-aai.fz-juelich.de:8443/oauth2/tokeninfo",
        userinfo_url = "https://unity.eudat-aai.fz-juelich.de:8443/oauth2/userinfo",
    )
)
