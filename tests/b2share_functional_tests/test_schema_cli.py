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
import test
import pytest
from click.testing import CliRunner
from flask_cli import ScriptInfo

from b2share.modules.schemas.cli import schemas as schemas_cmd
from data.testschema import test_schema

@pytest.mark.parametrize('app', [({
    'config': {'PREFERRED_URL_SCHEME': 'https'}
}), ({
    'config': {'PREFERRED_URL_SCHEME': 'http'}
})],
    indirect=['app'])

def test_set_schema_cmd(app, test_communities):
    """Test the `schemas set_schema` CLI command."""
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info: app)
        comm_name = test_communities.popitem()[0]
        print(test_schema)
        # Run 'set schema' command
        with runner.isolated_filesystem():
            f = open("schema.json","w")
            f.write(json.dumps(json.loads(test_schema)))
            f.close()
            result = runner.invoke(schemas_cmd, ['set_schema',comm_name,'schema.json'], obj=script_info)
            print(result)
            assert result.exit_code == 0