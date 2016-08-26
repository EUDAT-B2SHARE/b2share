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

"""Helper functions for B2Share Schemas module."""

import json
import re
import os
from functools import lru_cache
from urllib.error import URLError
from urllib.request import urlopen

from flask import current_app
from invenio_db import db
from jsonschema import validate
import chardet
import jsonschema

from doschema.validation import JSONSchemaValidator

from .errors import InvalidJSONSchemaError, RootSchemaDoesNotExistError, \
    RootSchemaAlreadyExistsError


@lru_cache(maxsize=1000)
def resolve_json(url):
    """Load the given URL as a JSON."""
    resource = urlopen(url)
    encoding = resource.headers.get_content_charset()
    schema_bytes = resource.read()
    if encoding is None:
        encoding = chardet.detect(schema_bytes)['encoding']
    json_schema = json.loads(schema_bytes.decode(encoding))
    return json_schema


def validate_json_schema(new_json_schema, prev_schemas):
    """Check that a JSON Schema matches its "$schema" and is backward
    compatible.

    Args:
        new_json_schema: json_schema to be created.
        prev_schemas: list of previous versions of a schema.

    """
    if '$schema' not in new_json_schema:
        raise InvalidJSONSchemaError('Missing "$schema" field in JSON Schema')
    if new_json_schema['$schema'] != 'http://json-schema.org/draft-04/schema#':
        # FIXME: later we should accept other json-schema versions too
        # but we have to make sure that the root-schema, block-schema and
        # community-schema are compatible
        raise InvalidJSONSchemaError(
            '"$schema" field can only be '
            '"http://json-schema.org/draft-04/schema#"')
    try:
        super_schema = resolve_json(new_json_schema['$schema'])

        schema_validator = JSONSchemaValidator(
            resolver_factory=lambda *args,
            **kwargs: current_app.extensions[
                'invenio-records'
            ].ref_resolver_cls.from_schema(new_json_schema)
        )

        for prev_schema in prev_schemas:
            schema_validator.validate(json.loads(prev_schema), 'prevs')
        schema_validator.validate(new_json_schema, 'current schema')
    except URLError as e:
        raise InvalidJSONSchemaError('Invalid "$schema" URL.') from e
    jsonschema.validate(new_json_schema, super_schema)


def resolve_schemas_ref(source):
    """Resolve all references to Block Schemas and replace them with URLs.

    Every instance of
    '$BLOCK_SCHEMA_VERSION_URL[<block_schema_id>::<block_schema_version>]'
    will be replaced with the corresponding URL.

    Args:
        source (str): the source string to transform.

    Returns:
        str: a copy of source with the references replaced.
    """
    from .serializers import block_schema_version_self_link
    from .api import BlockSchema

    def block_schema_version_match(match):
        schema_id = match.group(1)
        schema_version = match.group(2)
        block_schema = BlockSchema.get_block_schema(schema_id)
        # FIXME use EPIC links
        return block_schema_version_self_link(
            block_schema.versions[int(schema_version)],
            _external=True
        )

    return re.sub(
        r'\$BLOCK_SCHEMA_VERSION_URL\[([^\]:]+)::([^\]:]+)\]',
        block_schema_version_match,
        source
    )


root_schema_config_schema = {
    'type': 'object',
    'properties': {
        'version': {'type': 'integer'},
        'json_schema': {'type': 'object'}
    },
    'required': ['version', 'json_schema'],
    'additionalProperties': False,
}


def load_root_schemas(cli=False, verbose=False):
    """Load root schemas in the database.

    Args:
        verbose (bool): enable verbose messages if :param:`cli` is True.
        cli (bool): enable click messages.
    """
    import click
    from .api import RootSchema
    current_dir = os.path.dirname(os.path.realpath(__file__))
    root_schemas_dir = os.path.join(current_dir, 'root_schemas')
    if cli:
        click.secho('LOADING root schemas from "{}".'
                    .format(root_schemas_dir), fg='yellow', bold=True)
    configs_count = 0
    for filename in sorted(os.listdir(root_schemas_dir)):
        if os.path.splitext(filename)[1] == '.json':
            if cli and verbose:
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
                    if cli and verbose:
                        raise RootSchemaAlreadyExistsError(
                            'Already loaded Root JSON Schema '
                            'version {0} does not match the one in file "{1}".'
                            .format(version,
                                    os.path.join(root_schemas_dir, filename)),
                        )
                if cli and verbose:
                    click.echo(' => SCHEMA ALREADY LOADED.')
            except RootSchemaDoesNotExistError:
                if cli and verbose:
                    click.echo(' => LOADING root schema version {0}.'
                               .format(version, filename))
                configs_count += 1
                RootSchema.create_new_version(version, json_schema)
                db.session.commit()
            except Exception:
                click.echo()
                raise
    if cli:
        click.secho('LOADED {} schemas'.format(configs_count), fg='green')
