# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016, University of Tuebingen, CERN.
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

"""B2Share access policies."""


import pytz

from dateutil.parser import parse as dateutil_parse
from datetime import datetime, timezone


def allow_public_file_metadata(record_metadata):
    '''Metadata about a record's files, i.e. file names can be
        serialized or indexed if BOTH:
            1. the record is open_access, and
            2. the record embargo date (if any) has expired
    '''
    if record_metadata.get('open_access') is True:
        if not is_under_embargo(record_metadata):
            return True
    return False


def is_under_embargo(record_metadata):
    embargo_date_string = record_metadata.get('embargo_date')
    if not embargo_date_string:
        # no embargo date set
        return False
    embargo_date = dateutil_parse(embargo_date_string)
    # assume UTC for naive datetime objects
    if embargo_date.tzinfo is None or embargo_date.tzinfo.utcoffset(embargo_date) is None:
        embargo_date = embargo_date.replace(tzinfo=pytz.UTC)
    return datetime.now(timezone.utc) < embargo_date
