# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""" Pre-configured remote application for enabling sign in/up with EUDAT Unity.
"""

REMOTE_APP = dict(
    title='Unity',
    description='EUDAT Unity authentication.',
    icon='fa fa-github',
    authorized_handler="invenio.modules.oauthclient.handlers:authorized_signup_handler",
    disconnect_handler="invenio.modules.oauthclient.handlers:disconnect_handler",
    signup_handler=dict(
        info="invenio.modules.oauthclient.contrib.unity:account_info",
        setup="invenio.modules.oauthclient.contrib.unity:account_setup",
        view="invenio.modules.oauthclient.handlers:signup_handler",
    ),
    params=dict(
            request_token_params={'scope': 'USER_PROFILE GENERATE_USER_CERTIFICATE'},
            base_url='https://eudat-aai.fz-juelich.de:8445/oauth-as',
            request_token_url=None,
            access_token_url= "https://eudat-aai.fz-juelich.de:8445/oauth-as/r/access_token/request",
            access_token_method='POST',
            authorize_url="https://eudat-aai.fz-juelich.de:8445/oauth-as/authorize",
            app_key="UNITY_APP_CREDENTIALS",
    )
)


def account_info(remote, resp):
    """ Retrieve remote account information used to find local user. """
    print ("resp")
    from pprint import pprint
    pprint(resp)
    # gh = github3.login(token=resp['access_token'])
    # ghuser = gh.user()
    return dict(email=None, nickname=None)


def account_setup(remote, token):
    """ Perform additional setup after user have been logged in. """
    pass
