# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
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

"""B2Share Schemas module Command Line Interface."""

from __future__ import absolute_import

import json
import os
import sys

import click
from flask_cli import with_appcontext
from invenio_db import db
from jsonschema import validate

from .api import RootSchema
from .errors import RootSchemaDoesNotExistError

root_schema_config_schema = {
    'type': 'object',
    'properties': {
        'version': {'type': 'integer'},
        'json_schema': {'type': 'object'}
    },
    'required': ['version', 'json_schema'],
    'additionalProperties': False,
}


@click.group()
def schemas():
    """Schemas management commands."""


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
def init(verbose):
    """CLI command loading Root Schema files in the database."""
    current_dir = os.path.dirname(os.path.realpath(__file__))
    root_schemas_dir = os.path.join(current_dir, 'root_schemas')
    # for schema_file in os.walk(root_schemas_dir):
    configs_count = 0
    click.secho('LOADING root schemas from "{}".'
                .format(root_schemas_dir), fg='yellow', bold=True)
    for filename in sorted(os.listdir(root_schemas_dir)):
        if os.path.splitext(filename)[1] == '.json':
            if verbose:
                click.echo('READING schema from "{}"'.format(filename),
                           nl=False)
            try:
                with open(os.path.join(root_schemas_dir,
                                       filename)) as json_file:
                    json_config = json.loads(json_file.read())
                validate(json_config, root_schema_config_schema)
                version = json_config['version']
                json_schema = json_config['json_schema']
                retrieved = RootSchema.get_root_schema(version)
                # check that the schema is the same
                if json.loads(retrieved.json_schema) != json_schema:
                    if verbose:
                        click.secho(
                            ' => Already loaded Root JSON Schema version '
                            '{0} does not match the one in file "{1}".'
                            .format(version,
                                    os.path.join(root_schemas_dir, filename)),
                            fg='red',
                            err=True)
                    sys.exit(1)
                if verbose:
                    click.echo(' => SCHEMA ALREADY LOADED.')
            except RootSchemaDoesNotExistError:
                if verbose:
                    click.echo(' => LOADING root schema version {0}.'
                               .format(version, filename))
                configs_count += 1
                RootSchema.create_new_version(version, json_schema)
                db.session.commit()
            except Exception:
                click.echo()
                raise
    click.secho('LOADED {} schemas'.format(configs_count), fg='green')
