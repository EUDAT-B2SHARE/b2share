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

"""Test B2Share deposit cli module."""
from __future__ import absolute_import, print_function


from click.testing import CliRunner
from flask.cli import ScriptInfo
import pytest

import b2share.modules.deposit.cli as deposit_cli
from b2share.modules.deposit.api import Deposit


def test_deposit_delete(app, draft_deposits):
    """Test deposit remove of unpublished deposit."""
    data = draft_deposits[0]
    
    with app.app_context():
        # get the deposit, check if this exist
        deposit = Deposit.get_record(data.deposit_id)

    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)
    with app.app_context():
        #   delete the deposit
        result = runner.invoke(deposit_cli.delete, [str(deposit.id)], obj=script_info)
        if result.exit_code != 0:
           print(result.output)
        assert result.exit_code == 0

        # check if the deposit does not exist anymore. 
        # if does not fail the test fails!
        with pytest.raises(Exception):
            deposit=Deposit.get_record(data.deposit_id)
            
