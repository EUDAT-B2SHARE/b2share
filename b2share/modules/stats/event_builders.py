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

"""Statistics event builders."""

import datetime
from invenio_stats.utils import get_user
from b2share.modules.records.utils import is_deposit

def get_id(rec):
    pid = ''
    for i in rec.get("_pid", []):
        if i.get('type') == 'b2rec':
            pid = i.get('value')
    return pid

def record_view_event_builder(event, sender_app, pid=None, record=None,
                              **kwargs):
    """Build a record-view event."""
    if not record:
        return event
    if is_deposit(record):
        return None
    event.update(dict(
        # When:
        timestamp=datetime.datetime.utcnow().isoformat(),
        # What:
        record_id=str(get_id(record)),
        pid_type=pid.pid_type,
        pid_value=str(pid.pid_value),
        unique_id = '{0}_{1}'.format(pid.pid_type, pid.pid_value),
        community=record['community'],
        # Who:
        **get_user()
    ))
    return event
