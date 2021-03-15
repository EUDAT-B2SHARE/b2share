# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 EUDAT.
#
# B2SHARE_MAIN is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""MODULE MAIN for EUDAT Collaborative Data Infrastructure."""

# TODO: This is an example file. Remove it if you do not need it, including
# the templates and static folders as well as the test case.

from flask import Blueprint, render_template
from flask_babelex import gettext as _

blueprint = Blueprint(
    'b2share_main',
    __name__,
    template_folder='templates',
    static_folder='static',
)

@blueprint.route('/help', defaults={'path': ''})
@blueprint.route('/help/', defaults={'path': ''})
@blueprint.route('/help/<path:path>')
@blueprint.route('/communities', defaults={'path': ''})
@blueprint.route('/communities/', defaults={'path': ''})
@blueprint.route('/communities/<path:path>')
@blueprint.route('/user', defaults={'path': ''})
@blueprint.route('/user/', defaults={'path': ''})
@blueprint.route('/user/<path:path>')
@blueprint.route('/records', defaults={'path': ''})
@blueprint.route('/records/', defaults={'path': ''})
@blueprint.route('/records/<path:path>')
@blueprint.route('/search', defaults={'path': ''})
@blueprint.route('/search/', defaults={'path': ''})
@blueprint.route('/search/<path:path>')
@blueprint.route("/")

def index(path=''):
    """Render a basic view."""
    return render_template(
        "b2share_main/page.html",
        module_name=_('B2SHARE_MAIN'))
