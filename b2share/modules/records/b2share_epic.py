import httplib2
from simplejson import dumps as jsondumps
from werkzeug.exceptions import abort
from flask import current_app
from urllib.parse import urljoin, urlparse

from .errors import EpicPIDError


def createHandle(location, checksum=None, suffix=''):
    """ Create a new handle for a file.

    Parameters:
        location: The location (URL) of the file.
        checksum: Optional parameter, store the checksum of the file as well.
        suffix: The suffix of the handle. Default: ''.
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
    if suffix != '':
        uri += "/" + suffix.lstrip(prefix + "/")

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

    try:
        response, content = http.request(
            uri, method='POST', headers=hdrs, body=new_handle_json)
    except Exception as e:
        current_app.logger.debug(e)
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
