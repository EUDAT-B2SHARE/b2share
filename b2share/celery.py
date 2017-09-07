# -*- coding: utf-8 -*-

"""mysite base Invenio configuration."""

from __future__ import absolute_import, print_function

from flask_celeryext import create_celery_app
from invenio_celery import InvenioCelery
from invenio_queues import InvenioQueues
from invenio_search import InvenioSearch

from invenio_stats import InvenioStats

from .factory import create_app

celery = create_celery_app(create_app())

__all__ = ['celery']
