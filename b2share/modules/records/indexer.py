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

"""Record modification prior to indexing."""

import pytz
from b2share.modules.access.policies import allow_public_file_metadata
from invenio_records_files.models import RecordsBuckets


def indexer_receiver(sender, json=None, record=None, index=None,
                     **dummy_kwargs):
    """Connect to before_record_index signal to transform record for ES."""
    if not index.startswith('records'):
        return
    try:
        if '_files' in json:
            if not allow_public_file_metadata(json):
                for f in json['_files']:
                    del f['key']
        del json['_deposit']
        json['_created'] = pytz.utc.localize(record.created).isoformat()
        json['_updated'] = pytz.utc.localize(record.updated).isoformat()
        json['owners'] = record['_deposit']['owners']

        # insert the bucket id for link generation in search results
        record_buckets = RecordsBuckets.query.filter(
            RecordsBuckets.record_id == record.id).all()
        if record_buckets:
            json['_internal'] = {
                'files_bucket_id': str(record_buckets[0].bucket_id),
            }
    except Exception:
        raise
