# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN, SurfSara
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

"""B2Share Communities module Command Line Interface."""

from __future__ import absolute_import

import os
from os.path import isfile

import click
from flask.cli import with_appcontext

from invenio_db import db

from .api import Community, CommunityDoesNotExistError, \
    CommunityPolicyDoesNotExistError, CommunityPolicyInvalidValueError

@click.group()
def communities():
    """communities management commands."""


def _validate_community_parameters(name=None, description=None, logo=None):
    """Validate community parameters and update them if needed."""
    if name is not None and len(name) > 80:
        raise click.BadParameter(""""NAME parameter is longer than the 80
        character maximum""")
    if description is not None and len(description) > 2000:
        raise click.BadParameter("""DESCRIPTION parameter is longer than the
        2000 character maximum""")

    if logo is not None:
        webui_path = os.environ.get('B2SHARE_UI_PATH', 'webui/app')
        img_path = os.path.abspath(os.path.join(webui_path, 'img/communities'))
        if not os.path.isabs(logo):
            logo = os.path.join(img_path, logo)
        if not logo.startswith(img_path) or not isfile(logo):
            raise click.BadParameter(""""LOGO should be the filename of an
            image file existing in the B2SHARE_UI_PATH/img/communities/
            directory.""")
        logo = '/' + os.path.relpath(logo, webui_path)
    return (name, description, logo)


@communities.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.argument('name')
@click.argument('description')
@click.argument('logo')
def create(verbose, name, description, logo):
    """Create a community in the database. Name can be 255 characters long.
     Description is a text of maximally 1024 characters enclosed in
    parentheses. The logo parameter should be a valid path to a logo file
    relative to B2SHARE_UI_PATH/img/communities directory """
    name, description, logo = _validate_community_parameters(name, description,
                                                             logo)
    try:
        Community.get(name=name)
        #if it does not yield the CommunityDoesNotExistError then:
        raise click.BadParameter("There already is a community with name %s"
                                 % name)
    except CommunityDoesNotExistError:
        pass
    community = Community.create_community(name=name,
                                           description=description, logo=logo)
    db.session.commit()
    if verbose:
        click.echo("Community created with %d" % community.id)

@communities.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
def list(verbose):
    """List all communities in this instances' database"""
    communities = Community.get_all()
    for c in communities:
        click.echo("%s\t%s\t%s\t%s" % (c.name[0:15], c.id, c.description[0:31], c.logo))


@communities.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('--name')
@click.option('--description')
@click.option('--logo')
@click.option('--clear_fields', is_flag=True, default=False,
              help='if set edit nullifies unspecified value options')
@click.argument('id')
def edit(verbose, id, name, description, logo, clear_fields):
    """Edit data of the specified community."""
    try:
        community = Community.get(id=id)
    except:
        raise click.BadParameter("No community with id %s" % id)
    if not(name or description or logo):
        raise click.ClickException("""At least one of name, description or
        id must be specified""")

    name, description, logo = _validate_community_parameters(name, description,
                                                             logo)
    data = {}
    if name:
        if name != community.name:
            try:
                Community.get(name=name)
                raise click.BadParameter("""You are trying to
                change the name of the community but another community
                already exists with that name.""")
            except CommunityDoesNotExistError:
                pass
        data['name'] = name
    if description:
        data['description'] = description
    if logo:
        data['logo'] = logo
    updated_community = community.update(data, clear_fields)
    db.session.commit()
    click.echo("Community %s updated: name= %s description=%s logo=%s" %
               (updated_community.id, updated_community.name,
                updated_community.description, updated_community.logo))


@communities.command()
@with_appcontext
@click.argument('community')
@click.argument('json_file', required=False, default=None)
@click.option('--no-block', required=False, is_flag=True)
@click.option('--root-schema', required=False, default=None, type=int)
def set_schema(community, json_file, root_schema, no_block):
    """Set the community block schema and/or root schema version.
    If a root schema version is given, but no JSON file, the latest known block schema will be used (if present)."""
    from b2share.modules.schemas.cli import update_or_set_community_schema, update_or_set_community_root_schema
    if json_file or no_block:
        update_or_set_community_schema(community, json_file, root_schema, no_block)
    elif root_schema:
        update_or_set_community_root_schema(community, root_schema)
    else:
        raise click.BadParameter("Need at least a JSON file, block flag or root schema version")


@communities.group()
@with_appcontext
def roles():
    """Manage community roles"""

@roles.command('list')
@with_appcontext
@click.argument('community', required=False)
def community_roles_list(community=None):
    """List all communities' roles"""

    def list_item(comm):
        click.secho("%s\t%s\t\t%s\t%s" % (
            comm.id,
            comm.name,
            comm.admin_role,
            comm.member_role
        ))

    click.secho("ID\t\t\t\t\tNAME\t\tROLES")
    if not community:
        for c in Community.get_all():
            list_item(c)
    else:
        list_item(Community.get(community))


@communities.group()
@with_appcontext
def policies():
    """Manage community policies"""

@policies.command('list')
@with_appcontext
@click.argument('community', required=False)
def community_policies_list(community=None):
    """List all communities' policy values"""

    def list_item(comm):
        click.secho("%s\t%s\t\t%s\t%s" % (
            comm.id,
            comm.name,
            comm.publication_workflow,
            comm.restricted_submission
        ))

    click.secho("ID\t\t\t\t\tNAME\t\tWORKFLOW\tMEMBERS-ONLY")
    if not community:
        for c in Community.get_all():
            list_item(c)
    else:
        list_item(Community.get(community))


@policies.command('set')
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.argument('community')
@click.argument('policy')
@click.argument('value', required=False)
@click.option('--enable', 'enable', flag_value=True)
@click.option('--disable', 'enable', flag_value=False, default=True)
def community_policies_set(verbose, community, policy, enable=None, value=None):
    """Enable/disable/set the value for a given community and policy."""

    from .policies import PolicyValuesMapping, PolicyToggleValues

    # if a value is omitted, use the enable flag and use its value
    if value is None:
        if not enable is None:
            value = enable
        else:
            raise click.BadParameter("No value given or use --enable or --disable flag")

    try:
        comm = Community.get(id=community)
        comm.policy(policy, value)
    except CommunityDoesNotExistError:
        raise click.BadParameter("No such community with ID %s" % community)
    except CommunityPolicyDoesNotExistError:
        raise click.BadParameter("No such community policy '%s', choose from: '%s'" % (policy, "', '".join(PolicyValuesMapping.keys())))
    except CommunityPolicyInvalidValueError:
        if PolicyValuesMapping[policy] == PolicyToggleValues:
            raise click.BadParameter("Invalid value '%s' for policy '%s', use --enable or --disable flag" % (value, policy))
        else:
            raise click.BadParameter("Invalid value '%s' for policy '%s', choose from: '%s'" % (value, policy, "', '".join([str(x) for x in PolicyValuesMapping[policy]])))

    db.session.commit()
    if verbose:
        click.echo("Community policy '%s' updated" % policy)
>>>>>>> 19031bc32 (Add community policy update CLI command)
