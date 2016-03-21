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
from functools import lru_cache
from urllib.error import URLError
from urllib.request import urlopen

import chardet
import jsonschema

from .errors import InvalidJSONSchemaError


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


def validate_json_schema(json_schema):
    """Check that a JSON Schema matches its "$schema"."""
    if '$schema' not in json_schema:
        raise InvalidJSONSchemaError('Missing "$schema" field in JSON Schema')
    if json_schema['$schema'] != 'http://json-schema.org/draft-04/schema#':
        # FIXME: later we should accept other json-schema versions too
        # but we have to make sure that the root-schema, block-schema and
        # community-schema are compatible
        raise InvalidJSONSchemaError(
            '"$schema" field can only be '
            '"http://json-schema.org/draft-04/schema#"')
    try:
        super_schema = resolve_json(json_schema['$schema'])
    except URLError as e:
        raise InvalidJSONSchemaError('Invalid "$schema" URL.') from e
    jsonschema.validate(json_schema, super_schema)


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
            block_schema.versions[int(schema_version)]
        )

    return re.sub(
        r'\$BLOCK_SCHEMA_VERSION_URL\[([^\]:]+)::([^\]:]+)\]',
        block_schema_version_match,
        source
    )
