# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN.
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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Record utils."""

from invenio_pidstore.models import PersistentIdentifier
from invenio_db import db

from .errors import UnknownRecordType


def _is_record_type(record_id, pid_type):
    """Verify if a record has a pid of the given type."""
    pids = PersistentIdentifier.query.filter(
        PersistentIdentifier.object_uuid == record_id).all()
    if pids:
        return pids[0].pid_type == pid_type
    else:
        raise UnknownRecordType('No PID found for record {}'.format(record_id))


def is_publication(record):
    """Check if a given record is a published record.

    Returns:
        bool: True if the record is a published record, else false.
    """
    return _is_record_type(record.id, 'b2share_record')


def is_deposit(record):
    """Check if a given record is a deposit record.

    Returns:
        bool: True if the record is a deposit record, else false.
    """
    return _is_record_type(record.id, 'b2share_deposit')
