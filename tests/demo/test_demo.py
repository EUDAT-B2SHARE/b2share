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

"""Test B2Share demonstration module."""

from functools import partial

import os
import sys
from urllib.parse import urlparse

import pytest
from click.testing import CliRunner
from flask.cli import ScriptInfo
from invenio_pidstore.resolver import Resolver
from invenio_records import Record

from b2share.modules.schemas.cli import schemas as schemas_cmd
from b2share.modules.b2share_demo.cli import demo as demo_cmd


def test_demo_cmd_load(app):
    """Test the `load` CLI command."""
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info: app)

        # Run 'load' command
        with runner.isolated_filesystem():
            result = runner.invoke(schemas_cmd, ['init'], obj=script_info)
            assert result.exit_code == 0
            result = runner.invoke(demo_cmd, ['load_data'], obj=script_info)
            assert result.exit_code == 0
            result = runner.invoke(demo_cmd, ['load_config'], obj=script_info)
            # assert result.exit_code == 0
            # FIXME: check that the config is loaded

        resolver = Resolver(pid_type='b2rec', object_type='rec',
                            getter=partial(Record.get_record,
                                           with_deleted=True))
        # check that the loaded record exists
        resolved = resolver.resolve('a1c2ef96a1e446fa9bd7a2a46d2242d4')
        schema = resolved[1]['$schema']
        assert urlparse(schema).scheme == app.config['PREFERRED_URL_SCHEME']
