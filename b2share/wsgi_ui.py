# -*- coding: utf-8 -*-

"""B2SHARE WSGI UI configuration."""

from .factory import create_app as b2share_ui

# B2SHARE UI application.
ui = b2share_ui()
