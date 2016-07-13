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

"""B2Share Deposit Link factory."""

from flask import url_for, g
from b2share.modules.records.providers import RecordUUIDProvider


def deposit_links_factory(pid):
    """Factory for record links generation."""
    deposit_endpoint = 'b2share_deposit_rest.{0}_item'.format(pid.pid_type)
    record_endpoint = 'b2share_records_rest.{0}_item'.format(
        RecordUUIDProvider.pid_type
    )
    links = dict(
        self=url_for(deposit_endpoint, pid_value=pid.pid_value,
                     _external=True),
        publication=url_for(record_endpoint, pid_value=pid.pid_value,
                            _external=True)
    )

    def _url(name, **kwargs):
        """URL builder."""
        endpoint = 'b2share_deposit_rest.{0}_{1}'.format(pid.pid_type, name)
        return url_for(endpoint, pid_value=pid.pid_value, _external=True,
                       **kwargs)

    if hasattr(g, 'record'):
        record = g.record
        # FIXME: index the record bucket with the bucket so that we can
        # add the "files" link
        if record.files is not None:
            links['files'] = url_for('invenio_files_rest.bucket_api',
                                     bucket_id=record.files.bucket.id,
                                     _external=True)
    return links
