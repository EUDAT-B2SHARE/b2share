# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016, 2017, 2018 CERN.
#
# B2Share is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2Share is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2Share; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""Celery application factory."""

from __future__ import absolute_import, print_function

from flask_celeryext import create_celery_app
from invenio_celery import InvenioCelery
from invenio_queues import InvenioQueues
from invenio_search import InvenioSearch

from invenio_stats import InvenioStats

from .factory import create_app

celery = create_celery_app(create_app())

__all__ = ['celery']
