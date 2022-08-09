# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
# Copyright (C) 2023 CSC
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

from invenio_stats.processors import EventsIndexer, anonymize_user, flag_robots
from invenio_stats.contrib.event_builders import build_file_unique_id

"""Statistics registrations."""

def register_events():
    """Register record-view events."""
    return [
        dict(
            event_type='b2share-file-download',
            templates='contrib/file_download',
            processor_class=EventsIndexer,
            processor_config=dict(
                preprocessors=[
                    flag_robots,
                    anonymize_user,
                    build_file_unique_id
                ])),
        dict(
            event_type='b2share-record-view',
            templates='contrib/record_view',
            processor_class=EventsIndexer)]
