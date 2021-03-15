# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2015, 2016, University of Tuebingen, CERN.
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

"""EUDAT B2ACCESS OAuth configuration."""

import base64

from urllib.parse import urljoin

from flask import abort, current_app, redirect, request, \
    session, url_for
from flask_oauthlib.client import OAuthException, OAuthRemoteApp, \
    parse_response
from flask_oauthlib.utils import to_bytes
from flask_security import current_user
from invenio_oauthclient.handlers import response_token_setter, token_getter, \
    token_session_key
from invenio_oauthclient.proxies import current_oauthclient
from invenio_oauthclient.signals import account_info_received, \
    account_setup_received
from invenio_oauthclient.utils import oauth_authenticate, oauth_get_user, \
    oauth_link_external_id


def make_b2access_remote_app(base_url):
    access_token_url = urljoin(base_url, 'oauth2/token')
    authorize_url = urljoin(base_url, 'oauth2-as/oauth2-authz')
    tokeninfo_url = urljoin(base_url, 'oauth2/tokeninfo')
    userinfo_url = urljoin(base_url, 'oauth2/userinfo')
    return dict(
        title='B2Access',
        description='EUDAT B2Access authentication.',
        icon='',
        authorized_handler='b2share.modules.oauthclient.b2access:authorized_signup_handler',
        disconnect_handler='b2share.modules.oauthclient.b2access:disconnect_handler',
        signup_handler=dict(
            info='b2share.modules.oauthclient.b2access:account_info',
            setup='b2share.modules.oauthclient.b2access:account_setup',
            view='b2share.modules.oauthclient.b2access:signup_handler',
        ),
        remote_app='b2share.modules.oauthclient.b2access:B2AccessOAuthRemoteApp',
        params=dict(
            request_token_params={'scope': 'USER_PROFILE GENERATE_USER_CERTIFICATE'},
            base_url=base_url,
            request_token_url=None,
            access_token_url=access_token_url,
            access_token_method='POST',
            authorize_url=authorize_url,
            app_key='B2ACCESS_APP_CREDENTIALS',
        ),
        tokeninfo_url=tokeninfo_url,
        userinfo_url=userinfo_url,
        registration_url=base_url,
    )


class B2AccessOAuthRemoteApp(OAuthRemoteApp):
    """Custom OAuth remote app handling Basic HTTP Authentication (RFC2617)."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(B2AccessOAuthRemoteApp, self).__init__(*args, **kwargs)

    def my_http_request(self, uri, headers=None, data=None, method=None):
        '''
        Method for monkey patching 'flask_oauthlib.client.OAuth.http_request'
        This version allows for insecure SSL certificates
        '''
        from flask_oauthlib.client import prepare_request, http
        import ssl

        uri, headers, data, method = prepare_request(
            uri, headers, data, method
        )
        req = http.Request(uri, headers=headers, data=data)
        req.get_method = lambda: method.upper()
        try:
            resp = http.urlopen(req, context=ssl._create_unverified_context())
            content = resp.read()
            resp.close()
            return resp, content
        except http.HTTPError as resp:
            content = resp.read()
            resp.close()
            return resp, content

    def handle_oauth2_response(self, args):
        """Handles an oauth2 authorization response.

        This method overrides the one provided by OAuthRemoteApp in order to
        support Basic HTTP Authentication.
        """
        if self.access_token_method != 'POST':
            raise OAuthException(
                ('Unsupported access_token_method: {}. '
                 'Only POST is supported.').format(self.access_token_method)
            )

        client = self.make_client()
        remote_args = {
            'code': args.get('code'),
            'client_secret': self.consumer_secret,
            'redirect_uri': (
                session.get('%s_oauthredir' % self.name) or
                url_for('invenio_oauthclient.authorized',
                        remote_app=self.name, _external=True)
            ),
        }
        remote_args.update(self.access_token_params)
        # build the Basic HTTP Authentication code
        b2access_basic_auth = base64.b64encode(bytes("{0}:{1}".format(
            self.consumer_key, self.consumer_secret),
            'utf-8')).decode('ascii').replace('\n', '')

        body = client.prepare_request_body(**remote_args)

        resp, content = self.my_http_request(
            self.expand_url(self.access_token_url),
            # set the Authentication header
            headers={
                'Authorization': 'Basic {}'.format(b2access_basic_auth),
            },
            data=to_bytes(body, self.encoding),
            method=self.access_token_method,
        )

        data = parse_response(resp, content, content_type=self.content_type)
        if resp.code not in (200, 201):
            raise OAuthException(
                'Invalid response from %s' % self.name,
                type='invalid_response', data=data
            )
        return data


def authorized_signup_handler(resp, remote, *args, **kwargs):
    """Handle sign-in/up functionality.

    This is needed as we don't use Flask Forms (for now), thus the default
    function would fail.
    """
    # Remove any previously stored auto register session key
    session.pop(token_session_key(remote.name) + '_autoregister', None)

    # Store token in session
    # ----------------------
    # Set token in session - token object only returned if
    # current_user.is_autenticated().
    token = response_token_setter(remote, resp)
    handlers = current_oauthclient.signup_handlers[remote.name]

    # Sign-in/up user
    # ---------------
    if not current_user.is_authenticated:
        account_info = handlers['info'](resp)
        account_info_received.send(
            remote, token=token, response=resp, account_info=account_info
        )
        user = oauth_get_user(
            remote.consumer_key,
            account_info=account_info,
            access_token=token_getter(remote)[0],
        )
        if user is None:
            # Auto sign-up if user not found
            user = oauth_register(account_info)

        # Authenticate user
        if not oauth_authenticate(remote.consumer_key, user,
                                  require_existing_link=False):
            return current_app.login_manager.unauthorized()

        # Link account
        # ------------
        # Need to store token in database instead of only the session when
        # called first time.
        token = response_token_setter(remote, resp)

    # Setup account
    # -------------
    if not token.remote_account.extra_data:
        account_setup = handlers['setup'](token, resp)
        account_setup_received.send(
            remote, token=token, response=resp, account_setup=account_setup
        )

    return redirect('/')


def oauth_register(account_info):
    """Register new OAuth users.

    This is needed as we don't use Flask Forms (for now), thus the default
    function would fail.
    """
    from flask_security.registerable import register_user
    user_data = account_info.get("user")
    user_data['password'] = ''
    user = register_user(**user_data)
    # Create user <-> external id link.
    oauth_link_external_id(
        user, dict(
            id=str(account_info.get('external_id')),
            method=account_info.get('external_method')
        )
    )
    return user


def disconnect_handler(remote, *args, **kwargs):
    """Handle unlinking of remote account.

    Disconnecting B2Access accounts is disabled.
    """
    return abort(404)


def signup_handler(remote, *args, **kwargs):
    """Handle extra signup information.

    This is disabled for B2Share.
    """
    return abort(404)


def account_info(remote, resp):
    """Retrieve remote account information used to find local user. """
    from flask import current_app
    import json
    import ssl
    try:
        import urllib2 as http
    except ImportError:
        from urllib import request as http

    url = current_app.config['OAUTHCLIENT_REMOTE_APPS'][remote.name][
        'userinfo_url']
    headers = {'Authorization': 'Bearer %s' % (resp.get('access_token'),)}
    req = http.Request(url, headers=headers)
    response, content = None, None
    try:
        response = http.urlopen(req, context=ssl._create_unverified_context())
        content = response.read()
        response.close()
        dict_content = json.loads(content.decode('utf-8'))
        if dict_content.get('cn') is None:
            username = dict_content.get('userName')
        else:
            username = dict_content.get('cn')
        return dict(
            user=dict(
                email=dict_content.get('email'),
                # Fixme add this once we support user profiles
                # profile=dict(full_name=username)
            ),
            external_id=dict_content.get('unity:persistent'),
            external_method='B2ACCESS'
        )
    except http.HTTPError as response:
        content = response.read()
        response.close()
        current_app.logger.warning("Failed to get user info from Unity", exc_info=True)

    return {}


def account_setup(remote, token, resp):
    """ Perform additional setup after user have been logged in. """
    pass
