# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 SurfSara, University of Tübingen
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

"""Test B2Share records cli module."""

from __future__ import absolute_import, print_function

from unittest.mock import patch, DEFAULT
from click.testing import CliRunner
from flask.cli import ScriptInfo

import b2share.modules.records.cli as records_cli

headers = [('Content-Type', 'application/json'),
           ('Accept', 'application/json')]
patch_headers = [('Content-Type', 'application/json-patch+json'),
                 ('Accept', 'application/json')]

def test_record_doi_cli(app, test_community, test_records, login_user):
    """Test checking a record's DOI using CLI commands."""
    with app.app_context():
        _test_record_doi_cli(app, test_community, test_records)

@patch.multiple('b2share.modules.records.cli',
                _datacite_doi_reference=DEFAULT,
                _datacite_register_doi=DEFAULT)
def _test_record_doi_cli(app, test_community, test_records,
                         _datacite_doi_reference, _datacite_register_doi):
    _datacite_doi_reference.return_value = None

    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    doi_prefix = app.config['PIDSTORE_DATACITE_DOI_PREFIX'] + "/b2share."

    def call_doi_cli_command(args):
        nonlocal _datacite_doi_reference
        nonlocal _datacite_register_doi
        _datacite_doi_reference.reset_mock()
        _datacite_register_doi.reset_mock()
        result = runner.invoke(records_cli.check_dois, args, obj=script_info)
        if result.exit_code != 0:
            print(result.output)
        assert result.exit_code == 0

    # Run 'check_record_doi' command for all each record in turn
    for record in test_records:
        doi = doi_prefix + record.pid
        call_doi_cli_command(['-r', record.pid])
        _datacite_doi_reference.assert_called_with(doi)
        _datacite_register_doi.assert_not_called()

        call_doi_cli_command(['-r', record.pid, '-u'])
        _datacite_doi_reference.assert_called_with(doi)
        assert _datacite_register_doi.call_args[0][1].endswith(record.pid)


    # Run 'check_record_doi' command for all records
    call_doi_cli_command(['-a'])
    for i, record in enumerate(test_records):
        assert _datacite_doi_reference.call_args_list[i][0] == (doi_prefix + record.pid,)
    _datacite_register_doi.assert_not_called()

    call_doi_cli_command(['-a', '-u'])
    for i, record in enumerate(test_records):
        assert _datacite_doi_reference.call_args_list[i][0] == (doi_prefix + record.pid,)
        assert _datacite_register_doi.call_args_list[i][0][1].endswith(record.pid)
