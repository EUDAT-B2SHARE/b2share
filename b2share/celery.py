# -*- coding: utf-8 -*-

"""mysite base Invenio configuration."""

from __future__ import absolute_import, print_function

from flask_celeryext import create_celery_app

# # Temporary step (ensures celery tasks is discovered)
from invenio_records.tasks import *

from .factory import create_app

celery = create_celery_app(create_app())
