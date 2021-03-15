# -*- coding: utf-8 -*-

"""B2SHARE base Invenio configuration."""

from __future__ import absolute_import, print_function

from invenio_base.app import create_cli

from .factory import create_app as b2share_cli

# B2SHARE CLI application.
cli = create_cli(create_app=b2share_cli)
