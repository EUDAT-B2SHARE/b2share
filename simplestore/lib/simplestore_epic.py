import httplib2
from simplejson import dumps as jsondumps
from werkzeug.exceptions import HTTPException, BadRequest, abort
from flask import current_app

from invenio.config import CFG_EPIC_USERNAME
from invenio.config import CFG_EPIC_PASSWORD
from invenio.config import CFG_EPIC_BASEURL
from invenio.config import CFG_EPIC_PREFIX


def createHandle(location,checksum=None,suffix=''):
    # Create a new handle for a file.
    #
    # Parameters:
    # location: The location (URL) of the file.
    # checksum: Optional parameter, store the checksum of the file as well.
    # suffix: The suffix of the handle. Default: ''.
    # Returns the URI of the new handle, None if an error occurred.
    
    # True - print out disgnostics
    debug = False
    
    # Comment out this line when it all works!
    httplib2.debuglevel = 4
    
    # Ensure all these are strings
    username = str(CFG_EPIC_USERNAME)
    password = str(CFG_EPIC_PASSWORD)
    baseurl = str(CFG_EPIC_BASEURL)
    prefix = str(CFG_EPIC_PREFIX)

    # If the proxy and proxy ports are set in the invenio-local.conf file
    # read them and set the proxy. If not, do nothing.
    try:
        from invenio.config import CFG_SITE_PROXY as proxy
        from invenio.config import CFG_SITE_PROXYPORT as proxyPort        
    except ImportError:
        proxy = None
        proxyPort = 80
            
    if proxy is not None:
        import socks

        # The original epic clint this code is based on included the 
        # disable_ssl_certificate_validation=True
        # parameter. It's not clear whether this is needed.
        http = httplib2.Http(proxy_info = httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, 
                             proxy, proxyPort))
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
    	  uri += "/" + suffix.lstrip(prefix+"/")
    
    # for a PUT, add 'If-None-Match': '*' to the header
    hdrs = {'Content-Type':'application/json', 'Accept': 'application/json'}
    
    if checksum:
        new_handle_json = jsondumps([{'type':'URL','parsed_data':location},
            {'type':'CHECKSUM','parsed_data': checksum}])
    else:
        new_handle_json = jsondumps([{'type':'URL','parsed_data':location}])

    current_app.logger.debug("json: " + new_handle_json)         

    try:
        response, content = http.request(uri, method='POST',
                headers=hdrs, body=new_handle_json)
    except:
        dbgmsg = "An Exception occurred during Creation of " + uri
        current_app.logger.debug(dbgmsg)
        abort(503)
    else:
        current_app.logger.debug("Request completed")

    if response.status != 201:
        current_app.logger.debug(
                  "Not Created: Response status: "+str(response.status))
        abort(response.status)

    # make sure to only return the handle and strip off the baseuri 
    # if it is included 
    hdl = response['location']
    if hdl.startswith(uri):
        hdl = hdl[len(uri):len(hdl)]
    elif hdl.startswith(uri + '/'):
        hdl = hdl[len(uri + '/'):len(hdl)]

    return hdl
    
