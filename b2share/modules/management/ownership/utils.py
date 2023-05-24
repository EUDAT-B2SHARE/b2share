# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2023 CSC, EUDAT ltd.
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

"""Utility functions for B2SHARE ownership module"""

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.errors import PIDDoesNotExistError, PIDMissingObjectError
from invenio_accounts.models import User
from b2share.modules.records.api import B2ShareRecord

from .errors import UserAlreadyOwner

def get_record_by_pid(pid):
    """Get a record by a pid
    
    :param pid: Record b2rec PID
    :return:    B2ShareRecord object
    """
    pid = PersistentIdentifier.get('b2rec', pid)
    if not pid.object_uuid:
        raise PIDMissingObjectError(pid)
    return B2ShareRecord.get_record(pid.object_uuid)

def add_ownership_to_record(rec, user_id):
    """Add user as an owner of a record

    :param rec:        A B2ShareRecord object
    :param user_id:    Users id which to add
    :raise UserAlreadyOwner: When an user is already an owner of the record
    :raise Exception:        When something goes horribly wrong
    """
    if user_id not in rec['_deposit']['owners']:
        rec['_deposit']['owners'].append(user_id)
        try:
            rec = rec.commit()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(e)

    else:
        raise UserAlreadyOwner(rec['_deposit']['id'])
    
def find_version_master(pid):
    """Retrieve the PIDVersioning of a record PID.

    :params pid: record b2rec PID.
    """
    from b2share.modules.deposit.errors import RecordNotFoundVersioningError
    from b2share.modules.records.providers import RecordUUIDProvider
    try:
        child_pid = RecordUUIDProvider.get(pid).pid
        if child_pid.status == PIDStatus.DELETED:
            raise RecordNotFoundVersioningError()
    except PIDDoesNotExistError as e:
        raise RecordNotFoundVersioningError() from e

    return PIDVersioning(child=child_pid)

def check_user(user_email):
    """Check if user exists
    
    :param user_email: Email of the user to be searched
    :return: user object
    """
    return User.query.filter(User.email == user_email).one_or_none()

def remove_ownership(obj, user_id: int):
    if user_id in obj['_deposit']['owners']:
        if len(obj['_deposit']['owners']) > 1:
            try:
                obj['_deposit']['owners'].remove(user_id)
                obj = obj.commit()
                db.session.commit()
            except ValueError as e:
                db.session.rollback()
                raise ValueError() from e
        else:
            raise Exception("Record has to have at least one owner")
    else:
        raise Exception("User is not owner of the record")
