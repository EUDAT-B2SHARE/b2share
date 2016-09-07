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
from flask_cli import with_appcontext

from invenio_db import db

from .api import Community, CommunityDoesNotExistError


@click.group()
def communities():
    """communities management commands."""


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
    if len(name)>255:
        raise click.BadParameter(""""NAME parameter is longer than the 255 
        character maximum""")
    if len(description)>1024:
        raise click.BadParameter("""DESCRIPTION parameter is longer than the
        1024 character maximum""")
    if not isfile( os.path.join( 
                os.environ.get('B2SHARE_UI_PATH'), 
                'img/communities', logo)):
        raise click.BadParameter(""""LOGO should be a (relative) path to an
         existing image file under B2SHARE_UI_PATH/img/communities directory.
         """)
    try:
        Community.get(name=name)
        #if it does not yield the CommunityDoesNotExistError then:
        raise click.BadParameter("There already is a community with name %s" 
            % name)
    except CommunityDoesNotExistError as e:
        pass
    community = Community.create_community(name=name, 
        description=description, logo=logo)
    db.session.commit()
    if verbose:
        click.echo("Community created with %d" % community.id)
        
@communities.command()
@with_appcontext
@click.option('-v','--verbose', is_flag=True, default=False)
def list(verbose):
    """List all communities in this instances' database"""
    communities = Community.get_all()
    for c in communities:
        click.echo("%s\t%s\t%s\t%s" % (c.name[0:15], c.id, c.description[0:31], c.logo))


@communities.command()
@with_appcontext
@click.option('-v','--verbose', is_flag=True, default=False)
@click.option('--name')
@click.option('--description')
@click.option('--logo')
@click.option('--clear_fields',is_flag=True,
    default=False,help='if set edit nullifies unspecified value options')
@click.argument('id')
def edit(verbose, id, name, description, logo,clear_fields):
        """Edit data of the specified community."""
        try:
            community = Community.get(id=id)
        except:
           raise click.BadParameter("No community with id %s" % id)
        if not(name or description or logo):
            raise click.ClickException("""At least one of name, description or 
            id must be specified""")
        data = {}
        if name:
            if not(name==community.name):
                try:
                    Community.get(name=name)
                    raise click.BadParameterException("""You are trying to 
                    change the name of the community but another community 
                    already exists with that name.""")
                except CommunityDoesnNotExistError:
                    pass
            data['name']=name
        if description:
            data['description']=description
        if logo:
            data['logo']=logo
        updated_community = community.update(data, clear_fields)
        db.session.commit()
        click.echo("Community %s updated: name= %s description=%s logo=%s" % 
            (updated_community.id, updated_community.name, 
            updated_community.description, updated_community.logo))

