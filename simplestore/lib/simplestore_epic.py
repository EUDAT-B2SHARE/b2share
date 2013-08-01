import httplib2
from simplejson import dumps as jsondumps
from werkzeug.exceptions import HTTPException, BadRequest

from invenio.config import CFG_EPIC_USERNAME
from invenio.config import CFG_EPIC_PASSWORD
from invenio.config import CFG_EPIC_BASEURL
from invenio.config import CFG_EPIC_PREFIX

def _debugMsg(debug, method, msg):
    # Internal: Print a debug message if debug is enabled.
    if debug: 
        print "[",method,"]",msg

def createHandle(location,checksum=None,suffix=''):
    # Create a new handle for a file.
    #
    # Parameters:
    # location: The location (URL) of the file.
    # checksum: Optional parameter, store the checksum of the file as well.
    # suffix: The suffix of the handle. Default: ''.
    # Returns the URI of the new handle, None if an error occurred.
    
    # True - print out disgnostics
    debug = True
    
    # Comment out this line when it all works!
    httplib2.debuglevel = 4
    
    # Ensure all these are strings
    username = str(CFG_EPIC_USERNAME)
    password = str(CFG_EPIC_PASSWORD)
    baseurl = str(CFG_EPIC_BASEURL)
    prefix = str(CFG_EPIC_PREFIX)

    _debugMsg(debug, 'createHandleWithLocation',"Location: " + location)
    _debugMsg(debug, 'createHandleWithLocation',"Username: " + username)
    _debugMsg(debug, 'createHandleWithLocation',"Password: " + password)   
        
    # If the proxy and proxy ports are set in the invenio-local.conf file
    # read them and set the proxy. If not, do nothing.
    try:
        from invenio.config import CFG_SITE_PROXY as proxy
        from invenio.config import CFG_SITE_PROXYPORT as proxyPort        
    except:
        _debugMsg(debug, 'createHandleWithLocation',"No Proxy set")
        proxy = ''
        proxyPort = 80
            
    if not (proxy==''):
        _debugMsg(debug, 'createHandleWithLocation',"Proxy: " + proxy)
        _debugMsg(debug, 'createHandleWithLocation',"Proxy port: " + str(proxyPort))
        if type(proxyPort) != int:
            raise HTTPException
        import socks

        # The original epic clint this code is based on included the 
        # disable_ssl_certificate_validation=True
        # parameter. It's not clear whether this is needed.
        http = httplib2.Http(proxy_info = httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, 
                             proxy, proxyPort))
    else:
        _debugMsg(debug, 'createHandleWithLocation',"Still no Proxy set")
        http = httplib2.Http()
        
    _debugMsg(debug, 'createHandleWithLocation',"Setting credentials")    
    http.add_credentials(username, password)
    _debugMsg(debug, 'createHandleWithLocation',"Set credentials") 

    
    if not (prefix.endswith('/')):
        prefix += '/'
    if baseurl.endswith('/'):
        uri = baseurl + prefix
    else:
        uri = baseurl + '/' + prefix
    if suffix != '':
    	  uri += "/" + suffix.lstrip(prefix+"/")
    _debugMsg(debug, 'createHandleWithLocation',"URI " + uri)
    
    # for a PUT, add 'If-None-Match': '*' to the header
    hdrs = {'Content-Type':'application/json', 'Accept': 'application/json'}
    
    if checksum:
        new_handle_json = jsondumps([{'type':'URL','parsed_data':location},
            {'type':'CHECKSUM','parsed_data': checksum}])
    else:
        new_handle_json = jsondumps([{'type':'URL','parsed_data':location}])
        
    _debugMsg(debug, 'createHandleWithLocation',"json: " + new_handle_json)         

    try:
        # Try to test the error handling with a an obvious error
        response, content = http.request(uri, method='PUT',
                headers=hdrs, body=new_handle_json)        
        #response, content = http.request(uri, method='POST',
        #        headers=hdrs, body=new_handle_json)
    except:
        _debugMsg(debug, 'createHandleWithLocation',
                  "An Exception occurred during Creation of " + uri)
        raise
    else:
        _debugMsg(debug, 'createHandleWithLocation', "Request completed")
    
    if response.status != 201:
        _debugMsg(debug, 'createHandleWithLocation',
                  "Not Created: Response status: "+str(response.status))
        raise HTTPException
       	
    # make sure to only return the handle and strip off the baseuri 
    # if it is included 
    hdl = response['location']
    _debugMsg(debug, 'hdl', hdl)
    if hdl.startswith(uri):
        hdl = hdl[len(uri):len(hdl)]
    elif hdl.startswith(uri + '/'):
        hdl = hdl[len(uri + '/'):len(hdl)]
  	
    _debugMsg(debug, 'final hdl', hdl)

    return hdl
    