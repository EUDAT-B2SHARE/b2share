# -*- coding: utf-8 -*-

"""B2SHARE WSGI API configuration."""

from .factory import create_app as b2share_api

# B2SHARE API application.
api = b2share_api()