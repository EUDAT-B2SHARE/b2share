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

"""Celery background tasks."""

import pytest
from datetime import datetime, timedelta

from b2share_unit_tests.helpers import (
    create_record, generate_record_data, subtest_file_bucket_permissions,
    create_user,
)
from b2share.modules.records.tasks import update_expired_embargos
# from invenio_records_files.api import Record
from invenio_db import db
from invenio_search import current_search
from invenio_files_rest.models import Bucket
from invenio_records_files.api import Record
from click.testing import CliRunner
from b2share.modules.records.cli import b2records
from flask_cli import ScriptInfo


@pytest.mark.parametrize('cli_cmd', [True, False])
def test_update_expired_embargo(app, test_communities, login_user, cli_cmd):
    """Test record embargo update."""

    uploaded_files = {
        'myfile1.dat': b'contents1',
        'myfile2.dat': b'contents2'
    }
    with app.app_context():
        creator = create_user('creator')
        non_creator = create_user('non-creator')

        # create a record with a finishing embargo
        released_record_data = generate_record_data(
            open_access=False,
            embargo_date=datetime.utcnow().isoformat(),
        )
        _, _, released_record = create_record(
            released_record_data, creator, files=uploaded_files
        )
        released_record_id = released_record.id

        # create a record with anot finished embargo
        closed_record_data = generate_record_data(
            open_access=False,
            # embargo finishes tomorrow
            embargo_date=(datetime.utcnow() + timedelta(days=1)).isoformat(),
        )
        _, _, closed_record = create_record(
            closed_record_data, creator, files=uploaded_files
        )
        closed_record_id = closed_record.id

        db.session.commit()
        # refresh index to make records searchable
        current_search._client.indices.refresh()

    def check_embargo(record_id, is_embargoed):
        with app.app_context():
            with app.test_client() as client:
                login_user(non_creator, client)
                # test open_access field in record's metadata
                record = Record.get_record(record_id)
                assert record['open_access'] != is_embargoed
                # test record's file access
                subtest_file_bucket_permissions(
                    client, record.files.bucket,
                    access_level=None if is_embargoed else 'read',
                    is_authenticated=True
                )

    # check that both records are under embargo
    check_embargo(released_record_id, is_embargoed=True)
    check_embargo(closed_record_id, is_embargoed=True)

    with app.app_context():
        if not cli_cmd:
            update_expired_embargos.delay()
        else:
            script_info = ScriptInfo(create_app=lambda info: app)
            runner = CliRunner()
            result = runner.invoke(b2records, ['update_expired_embargoes'], obj=script_info)
            assert result.exit_code == 0

        # refresh index to make records searchable
        current_search._client.indices.refresh()

    # check that only the released record is not under embargo
    check_embargo(released_record_id, is_embargoed=False)
    check_embargo(closed_record_id, is_embargoed=True)
