# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.

"""
    b2share.views
    -------------------------------
    B2Share interface.
"""

from __future__ import print_function
from flask import Blueprint

blueprint = Blueprint('b2share', __name__, url_prefix='/',
                      template_folder='templates', static_folder='static')

