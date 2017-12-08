# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN, University of Tübingen.
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

"""B2SHARE Handle API."""

import httplib2
from simplejson import dumps as jsondumps
from werkzeug.exceptions import abort
from flask import current_app
from datetime import datetime
from urllib.parse import urljoin, urlparse

from .errors import EpicPIDError


def create_handle(handle_client, handle_prefix, location,
                  checksum=None, fixed=False):
    """Create a new handle for a file, using the B2HANDLE library."""

    try:
        eudat_entries = {
            'EUDAT/FIXED_CONTENT': str(fixed),
            'EUDAT/PROFILE_VERSION': str(1),
        }
        if checksum:
            eudat_entries['EUDAT/CHECKSUM'] = str(checksum)
            eudat_entries['EUDAT/CHECKSUM_TIMESTAMP'] = datetime.now().isoformat()
        handle = handle_client.generate_and_register_handle(
            prefix=handle_prefix, location=location, checksum=checksum,
            **eudat_entries)
    except Exception as e:
        msg = "Handle System PID creation error: {}".format(e)
        current_app.logger.error(msg)
        raise EpicPIDError(msg) from e

    current_app.logger.info("Created Handle System PID: {}".format(handle))

    base_url = current_app.config.get('CFG_HANDLE_SYSTEM_BASEURL')
    return urljoin(base_url, handle)


def create_fake_handle(location):
    """Create a fake handle. """

    uuid = location.split('/')[-1] # record id
    handle = '0000/{}'.format(uuid)

    current_app.logger.info("Created fake handle PID: {}".format(handle))

    base_url = current_app.config.get('CFG_HANDLE_SYSTEM_BASEURL')
    return urljoin(base_url, handle)


def check_eudat_entries_in_handle_pid(handle_client, handle_prefix, handle,
        fixed=False, checksum=None, checksum_timestamp_iso=None, update=False):
    """Checks and update the mandatory EUDAT entries in a Handle PID."""

    if not handle_client:
        current_app.logger.error("check_eudat_entries_to_handle_pid only "
            "works if the handle API is used; please define "
            "PID_HANDLE_CREDENTIALS in the configuration file.")
        return

    prefix = current_app.config.get('CFG_HANDLE_SYSTEM_BASEURL')
    if not prefix.endswith('/'):
        prefix += '/'

    if handle.startswith(prefix):
        handle = handle[len(prefix):]

    try:
        old_values = handle_client.retrieve_handle_record(handle=handle)
    except Exception as e:
        msg = "Handle System PID retrieval error for handle {}:\n\t{}".format(
                handle, e)
        current_app.logger.error(msg)
        raise EpicPIDError(msg) from e

    assert old_values
    assert old_values.get('URL')
    if old_values.get('CHECKSUM') and checksum:
        assert old_values.get('CHECKSUM') == checksum

    new_values = {}
    if not old_values.get('EUDAT/FIXED_CONTENT'):
        new_values['EUDAT/FIXED_CONTENT'] = str(fixed)
    if not old_values.get('EUDAT/PROFILE_VERSION'):
        new_values['EUDAT/PROFILE_VERSION'] = str(1)
    if not old_values.get('CHECKSUM') and checksum:
        new_values['CHECKSUM'] = checksum
    if not old_values.get('EUDAT/CHECKSUM') and checksum:
        new_values['EUDAT/CHECKSUM'] = checksum
    if not old_values.get('EUDAT/CHECKSUM_TIMESTAMP') and checksum_timestamp_iso:
        new_values['EUDAT/CHECKSUM_TIMESTAMP'] = checksum_timestamp_iso

    if update:
        try:
            handle_client.modify_handle_value(handle=handle, **new_values)
        except Exception as e:
            msg = "Handle System PID modification error for handle {}:\n\t{}".format(
                handle, e)
            current_app.logger.error(msg)
            raise EpicPIDError(msg) from e

    return new_values


def create_epic_handle(location, checksum=None):
    """Create a new handle for a file.

    Parameters:
        location: The location (URL) of the file.
        checksum: Optional parameter, store the checksum of the file as well.
    Returns:
        the URI of the new handle, raises a 503 exception if an error occurred.
    """

    # httplib2.debuglevel = 4

    # Ensure all these are strings
    username = str(current_app.config.get('CFG_EPIC_USERNAME'))
    password = str(current_app.config.get('CFG_EPIC_PASSWORD'))
    baseurl = str(current_app.config.get('CFG_EPIC_BASEURL'))
    prefix = str(current_app.config.get('CFG_EPIC_PREFIX'))

    # If the proxy and proxy ports are set in the invenio-local.conf file
    # read them and set the proxy. If not, do nothing.
    try:
        proxy = current_app.config.get('CFG_SITE_PROXY')
        proxy_port = current_app.config.get('CFG_SITE_PROXYPORT')
    except:
        proxy = None
        proxy_port = 80

    if proxy is not None:
        import socks
        http = httplib2.Http(
            proxy_info=httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP,
                                          proxy, proxy_port))
    else:
        http = httplib2.Http()

    http.add_credentials(username, password)

    if not (prefix.endswith('/')):
        prefix += '/'
    if baseurl.endswith('/'):
        uri = baseurl + prefix
    else:
        uri = baseurl + '/' + prefix

    # for a PUT, add 'If-None-Match': '*' to the header
    hdrs = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    if checksum:
        new_handle_json = jsondumps([{'type': 'URL',
                                      'parsed_data': location},
                                     {'type': 'CHECKSUM',
                                      'parsed_data': checksum}])
    else:
        new_handle_json = jsondumps([{'type': 'URL',
                                      'parsed_data': location}])

    current_app.logger.debug("EPIC PID json: " + new_handle_json)

    if current_app.config.get('TESTING', False) or current_app.config.get('FAKE_EPIC_PID', False):
        # special case for unit/functional testing: it's useful to get a PID,
        # which otherwise will not get allocated due to missing credentials;
        # this also speeds up testing just a bit, by avoiding HTTP requests
        uuid = location.split('/')[-1] # record id
        fake_pid_url = 'http://example.com/epic/handle/0000/{}'.format(uuid)
        class FakeResponse(dict):
            status=201
        response = FakeResponse(location=fake_pid_url)
    else:
        try:
            response, content = http.request(
                uri, method='POST', headers=hdrs, body=new_handle_json)
        except Exception as e:
            raise EpicPIDError("EPIC PID Exception") from e

    current_app.logger.debug("EPIC PID Request completed")

    if response.status != 201:
        msg = "EPIC PID Not Created: Response status: {}".format(response.status)
        current_app.logger.debug(msg)
        raise EpicPIDError(msg)

    # get the handle as returned by EPIC
    hdl = response['location']
    pid = '/'.join(urlparse(hdl).path.split('/')[3:])

    CFG_HANDLE_SYSTEM_BASEURL = current_app.config.get(
        'CFG_HANDLE_SYSTEM_BASEURL')
    return urljoin(CFG_HANDLE_SYSTEM_BASEURL, pid)
