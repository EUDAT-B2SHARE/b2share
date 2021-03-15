# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""Statistics event preprocessors."""


def skip_deposit(doc):
    """Check if event is coming from deposit file and skip."""
    from invenio_records_files.models import RecordsBuckets
    from invenio_records.models import RecordMetadata
    from b2share.modules.records.utils import is_deposit

    rb = RecordsBuckets.query.filter_by(bucket_id=doc['bucket_id']).first()
    record = RecordMetadata.query.filter_by(id=rb.record_id).first()
    if is_deposit(record):
        return None
    return doc
