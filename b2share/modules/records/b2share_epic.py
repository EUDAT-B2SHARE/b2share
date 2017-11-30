import httplib2
from simplejson import dumps as jsondumps
from werkzeug.exceptions import abort
from flask import current_app
from datetime import datetime
from urllib.parse import urljoin, urlparse
from b2handle.handleclient import EUDATHandleClient

from .errors import EpicPIDError


handle_client = None
handle_prefix = None


def init_handle_client(app):
    global handle_client, handle_prefix
    credentials = app.config.get('PID_HANDLE_CREDENTIALS')
    if not credentials:
        # assume EPIC API
        return
    handle_prefix = credentials.get('prefix')
    handle_client = EUDATHandleClient(**credentials)


def createHandle(location, checksum=None, fixed=False):
    """ Create a new handle for a file, using the B2HANDLE library. """

    if current_app.config.get('TESTING', False) or current_app.config.get('FAKE_EPIC_PID', False):
        # special case for unit/functional testing: it's useful to get a PID,
        # which otherwise will not get allocated due to missing credentials;
        # this also speeds up testing just a bit, by avoiding HTTP requests
        uuid = location.split('/')[-1] # record id
        handle = '0000/{}'.format(uuid)
    elif not handle_client:
        # assume EPIC API
        return _createEpicHandle(location, checksum)
    else:
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

    CFG_HANDLE_SYSTEM_BASEURL = current_app.config.get(
        'CFG_HANDLE_SYSTEM_BASEURL')
    return urljoin(CFG_HANDLE_SYSTEM_BASEURL, handle)


def _createEpicHandle(location, checksum=None):
    """ Create a new handle for a file.

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
