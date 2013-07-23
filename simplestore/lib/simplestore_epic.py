#!/usr/bin/env python

import httplib2
#import socks
from simplejson import loads as jsonloads 
from simplejson import dumps as jsondumps
from xml.dom import minidom

from invenio.config import CFG_EPIC_USERNAME
from invenio.config import CFG_EPIC_PASSWORD
from invenio.config import CFG_EPIC_BASEURL
from invenio.config import CFG_EPIC_PREFIX
from invenio.config import CFG_SITE_PROXY
from invenio.config import CFG_SITE_PROXYPORT

import uuid
import sys

"""
httplib2
download from http://code.google.com/p/httplib2
python setup.py install

simplejson
download from http://pypi.python.org/pypi/simplejson/
python setup.py install

ubuntu: apt-get install python-httplib2 python-simplejson
"""



def _debugMsg(debug, method,msg):
    """Internal: Print a debug message if debug is enabled."""
    if debug: 
        print "[",method,"]",msg

def createHandle(location,checksum=None,suffix=''):
    """Create a new handle for a file.

    Parameters:
    location: The location (URL) of the file.
    checksum: Optional parameter, store the checksum of the file as well.
    suffix: The suffix of the handle. Default: ''.
    Returns the URI of the new handle, None if an error occurred.

    """
    
    # True - print out disgnostics
    debug = True
    
    # Comment out this line when it all works!
    httplib2.debuglevel = 4
    
    username = CFG_EPIC_USERNAME
    password = CFG_EPIC_PASSWORD
    baseurl = CFG_EPIC_BASEURL
    prefix = CFG_EPIC_PREFIX

    # Our  'username' and 'prefix' is currently a number not a string - is this right?
    if isinstance(username, basestring) == False: username = str(username)
    if isinstance(password, basestring) == False: password = str(password)
    if isinstance(prefix, basestring) == False: prefix = str(prefix)

    proxy = CFG_SITE_PROXY
    proxyPort = CFG_SITE_PROXYPORT
    
    if proxy != '':
        import socks
        if isinstance(proxyPort, int) == False: proxyPort = 8080
        _debugMsg(debug, 'createHandleWithLocation',"Proxy: " + proxy)
        _debugMsg(debug, 'createHandleWithLocation',"Proxy port: " + str(proxyPort))
        #http = httplib2.Http(proxy_info = httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, proxy, proxyPort), disable_ssl_certificate_validation=True)
        http = httplib2.Http(proxy_info = httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, proxy, proxyPort))
        
    http.add_credentials(username, password)

    _debugMsg(debug, 'createHandleWithLocation',"Location: " + location)
    _debugMsg(debug, 'createHandleWithLocation',"Username: " + username)
    _debugMsg(debug, 'createHandleWithLocation',"Password: " + password)   
    
    if prefix.endswith('/') == False:
        prefix += '/'
    if baseurl.endswith('/'):
        uri = baseurl + prefix
    else:
        uri = baseurl + '/' + prefix
    if suffix != '': uri += "/" + suffix.lstrip(prefix+"/")
    _debugMsg(debug, 'createHandleWithLocation',"URI " + uri)
    
    # This appears to be the correct header for a PUT
    #hdrs = {'If-None-Match': '*','Content-Type':'application/json'}
    hdrs = {'Content-Type':'application/json', 'Accept': 'application/json'}
    
    if checksum:
        new_handle_json = jsondumps([{'type':'URL','parsed_data':location}, {'type':'CHECKSUM','parsed_data': checksum}])
    else:
        new_handle_json = jsondumps([{'type':'URL','parsed_data':location}])
        
    _debugMsg(debug, 'createHandleWithLocation',"json: " + new_handle_json)         

    try:
      response, content = http.request(uri,method='POST',headers=hdrs,body=new_handle_json)
    except:
        _debugMsg(debug, 'createHandleWithLocation', "An Exception occurred during Creation of " + uri)
        return None
    else:
        _debugMsg(debug, 'createHandleWithLocation', "Request completed")
    
    if response.status != 201:
        _debugMsg(debug, 'createHandleWithLocation', "Not Created: Response status: "+str(response.status))
        if response.status == 400:
            _debugMsg('createHandleWithLocation', 'body json:' + new_handle_json)
       	
    """
    make sure to only return the handle and strip off the baseuri if it is included
    """
    hdl = response['location']
    _debugMsg(debug,'hdl', hdl)
    if hdl.startswith(uri):
        hdl = hdl[len(uri):len(hdl)]
    elif hdl.startswith(uri + '/'):
        hdl = hdl[len(uri + '/'):len(hdl)]
  	
    _debugMsg(debug, 'final hdl', hdl)

    return hdl