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


def indexer_receiver(sender, json=None, record=None, index=None,
                     **dummy_kwargs):
    """Connect to before_record_index signal to transform record for ES."""
    if not index.startswith('records'):
        return
    try:
        if '_files' in json:
            del json['_files']
        del json['_deposit']
        json['_created'] = pytz.utc.localize(record.created).isoformat()
        json['_updated'] = pytz.utc.localize(record.updated).isoformat()
        json['owners'] = record['_deposit']['owners']
        if record.files:
            json['_internal'] = {
                'files_bucket_id': str(record.files.bucket.id),
            }
    except Exception:
        raise
