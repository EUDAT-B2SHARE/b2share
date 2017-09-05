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

"""Test B2Share schema cli module."""
from __future__ import absolute_import, print_function

import os
import json
import pytest
from click.testing import CliRunner
from flask.cli import ScriptInfo

from b2share.modules.communities.cli import communities as communities_cmd
from b2share.modules.communities.helpers import get_community_by_name_or_id


def test_communities_group_cli(app, test_communities):
    """Test the `communities` CLI command group."""
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info: app)
        # Run 'communities' command
        result = runner.invoke(communities_cmd, [], obj=script_info)
        assert result.exit_code == 0

def test_communities_list(app, test_communities):
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info: app)
        result = runner.invoke(communities_cmd, ["list"], obj=script_info)
        assert len(result.output)>0

def test_create_community(app, test_communities):
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info:app)
        result = runner.invoke(
            communities_cmd,
            ["create",
                "COMM_NAME",
                "Description comm",
                "bbmri.png"],
            obj=script_info)
        assert result.exit_code == 0
        retrieved_comm = get_community_by_name_or_id("COMM_NAME")
        assert retrieved_comm.name=='COMM_NAME'

def test_create_community2(app, test_communities):
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info:app)
        result = runner.invoke(
            communities_cmd,
            ["create"],
            obj=script_info)
        assert result.exit_code != 0

def test_edit_community(app, test_communities):
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info:app)
        result = runner.invoke(
            communities_cmd,
            ["edit",
                "cccccccc-1111-1111-1111-111111111111",
                "--name",
                "NEW_NAME2"],
            obj=script_info)
        result = runner.invoke(communities_cmd, ["list"], obj=script_info)
        retrieved_comm = get_community_by_name_or_id("NEW_NAME2")
        assert retrieved_comm.name=='NEW_NAME2'

def test_edit_community2(app, test_communities):
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info:app)
        result = runner.invoke(
            communities_cmd,
            ["edit",
                "community_does_not_exist",
                "--name",
                "NEW_NAME2"],
            obj=script_info)
        assert result.exit_code != 0

def test_community_workflow(app, test_communities):
    with app.app_context():
        runner = CliRunner()
        script_info = ScriptInfo(create_app=lambda info:app)
        result = runner.invoke(
            communities_cmd,
            ["edit",
            "cccccccc-1111-1111-1111-111111111111",
            "publication_workflow",
            "review_and_publish"],
            obj=script_info)
    

