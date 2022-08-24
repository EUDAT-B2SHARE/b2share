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

"""Test B2Share Ownership cli module."""
import click
from click.testing import CliRunner

from sqlalchemy import true
from flask.cli import ScriptInfo

import b2share.modules.management.ownership.cli as ownership_cli
from b2share_unit_tests.helpers import create_user
from b2share.modules.management.ownership.cli import find_version_master

from invenio_records_files.api import Record


def test_record_ownership_list_cli(app,test_records):
            
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    for record in test_records:
        result = runner.invoke(ownership_cli.list, [record.pid], obj=script_info)
        if result.exit_code != 0:
            print(result.output)
        assert result.exit_code == 0

def test_record_ownership_add_cli(app,test_records):
            
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)
    with app.app_context():
        new_owner = create_user('new_owner')
        for record in test_records:
            result = runner.invoke(ownership_cli.add, [record.pid, new_owner.email], obj=script_info)
            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0

            version_master = find_version_master(record.pid)
            all_record_versions = version_master.children.all()
            all_records=[Record.get_record(single_pid.object_uuid) for single_pid in all_record_versions]
            for record_v in all_records:
                assert new_owner.id in record_v['_deposit']['owners']
                assert len(record_v['_deposit']['owners']) == 2


def test_record_ownership_reset_cli(app,test_records):
            
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)
    with app.app_context():
        unique_owner = create_user('unique_owner')
        for record in test_records:
            result = runner.invoke(ownership_cli.reset, [record.pid, unique_owner.email, "--yes-i-know"], obj=script_info)
            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0

            version_master = find_version_master(record.pid)
            all_record_versions = version_master.children.all()
            all_records=[Record.get_record(single_pid.object_uuid) for single_pid in all_record_versions]
            for record_v in all_records:
                assert unique_owner.id in record_v['_deposit']['owners']
                assert len(record_v['_deposit']['owners']) == 1

def test_record_ownership_remove_cli(app,test_records):
            
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)
    with app.app_context():
        new_owner = create_user('new_owner')
        
        for record in test_records:
            result = runner.invoke(ownership_cli.add, [record.pid, new_owner.email], obj=script_info)
            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0
            
            version_master = find_version_master(record.pid)
            all_record_versions = version_master.children.all()
            all_records=[Record.get_record(single_pid.object_uuid) for single_pid in all_record_versions]
            for record_v in all_records:
                assert new_owner.id in record_v['_deposit']['owners']
                assert len(record_v['_deposit']['owners']) == 2

            result = runner.invoke(ownership_cli.remove, [record.pid, new_owner.email], obj=script_info)
            if result.exit_code != 0:
                print(result.output)
            assert result.exit_code == 0

            version_master = find_version_master(record.pid)
            all_record_versions = version_master.children.all()
            all_records=[Record.get_record(single_pid.object_uuid) for single_pid in all_record_versions]
            for record_v in all_records:
                assert new_owner.id not in record_v['_deposit']['owners']
                assert len(record_v['_deposit']['owners']) == 1
