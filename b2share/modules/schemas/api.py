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

"""B2Share Schemas module programmatic API."""

from __future__ import absolute_import

import json, copy

import sqlalchemy
from invenio_db import db
from sqlalchemy.orm.exc import NoResultFound

from b2share.modules.communities import Community
from b2share.modules.schemas.helpers import validate_json_schema

from jsonpatch import apply_patch
from .errors import BlockSchemaDoesNotExistError, BlockSchemaIsDeprecated, \
    CommunitySchemaDoesNotExistError, InvalidBlockSchemaError, \
    InvalidJSONSchemaError, InvalidRootSchemaError, \
    RootSchemaDoesNotExistError, InvalidSchemaVersionError,\
    SchemaVersionExistsError


class Schema(object):
    @staticmethod
    def _resolveLocalReferences(schema, defs):
        def getRef(ref):
            if not ref.startswith("#"):
                raise InvalidRootSchemaError('Only local references supported')
            return defs.get(ref.split('/')[-1])

        r = {}
        for k, v in schema.items():
            if k == '$ref':
                r.update(Schema._resolveLocalReferences(getRef(v), defs))
            elif isinstance(v, dict):
                r[k] = Schema._resolveLocalReferences(v, defs)
            else:
                r[k] = v

        return r


class RootSchema(Schema):
    """Record root Schema API.

    Root schemas are maintined by EUDAT. Their list is fixed and always
    backward compatible.
    """

    def __init__(self, model):
        """Constructor.

        Args:
            model (:class:`b2share.modules.schemas.models.RootSchemaVersion`):
                root schema database model.
        """
        self.model = model

    @classmethod
    def create_new_version(cls, version, json_schema, options={}):
        """Load a new root schema version.

        Args:
            version (int): version number of this schema. Versions are known
                in advance and are the same for all B2Share instances. This is
                more of a security check as the version MUST follow the last
                loaded one.
            json_schema (dict): the JSON Schema corresponding to this version.

        Raises:
            :class:`b2share.modules.schemas.errors.InvalidRootSchemaError`:
                If the root schema version is invalid.
            :class:`b2share.modules.schemas.errors.InvalidJSONSchemaError`:
                The given JSON Schema is not valid.
        """
        from .models import RootSchemaVersion
        if not isinstance(json_schema, dict):
            raise InvalidJSONSchemaError('json_schema must be a dict')

        previous_root_schemas = _fetch_all_query_pages(
            RootSchemaVersion.query.filter(
                RootSchemaVersion.version < version
            ).order_by(RootSchemaVersion.version.asc())
        )
        prev_schemas = map(lambda x: x.json_schema, previous_root_schemas)

        if 'definitions' in json_schema:
            json_schema = Schema._resolveLocalReferences(json_schema, json_schema['definitions'])

        validate_json_schema(json_schema, prev_schemas, options)

        with db.session.begin_nested():
            # Force the given version to follow the previous one.
            # Root schema versions are not random and should be hard-coded.
            # This is just to make sure that a version was not skipped.
            last_version = db.session.query(
                sqlalchemy.func.max(
                    RootSchemaVersion.version).label('last_version')
            ).one().last_version
            if last_version is None:
                if version != 0:
                    raise InvalidRootSchemaError('First version should '
                                                 'be 0.')
            elif last_version + 1 != version:
                raise InvalidRootSchemaError('Given version does not '
                                             'follow the previous one.')
            # Create the root schema.
            model = RootSchemaVersion(
                json_schema=json.dumps(json_schema),
                version=version)
            root_schema = cls(model)
            db.session.add(model)
            return root_schema

    @classmethod
    def update_existing_version(cls, version, json_schema, options={}):
        """Update an existing root schema version.

        Args:
            version (int): version number of this schema. Versions are known
                in advance and are the same for all B2Share instances. This is
                more of a security check as the version MUST follow the last
                loaded one.
            json_schema (dict): the JSON Schema corresponding to this version.

        Raises:
            :class:`b2share.modules.schemas.errors.InvalidRootSchemaError`:
                If the root schema version is invalid.
            :class:`b2share.modules.schemas.errors.RootSchemaDoesNotExistError`:
                If the root schema version does not exist.
            :class:`b2share.modules.schemas.errors.InvalidJSONSchemaError`:
                The given JSON Schema is not valid.
        """
        from .models import RootSchemaVersion
        if not isinstance(json_schema, dict):
            raise InvalidJSONSchemaError('json_schema must be a dict')

        existing_schema = RootSchemaVersion.query.filter(
                RootSchemaVersion.version == version
            ).one()

        if existing_schema is None:
            raise RootSchemaDoesNotExistError("Root schema version {0} intended for update does not exist.".format(version))

        # resolve references if definitions present
        if 'definitions' in json_schema:
            json_schema = Schema._resolveLocalReferences(json_schema, json_schema['definitions'])

        validate_json_schema(json_schema, [existing_schema.json_schema], options)

        with db.session.begin_nested():
            # Update the root schema.
            model = RootSchemaVersion(
                json_schema=json.dumps(json_schema),
                version=version)
            root_schema = cls(model)
            db.session.merge(model)
            return root_schema

    @classmethod
    def get_root_schema(cls, version):
        """Retrieve a given root schema version.

        Args:
            version (int): the version to retrieve.

        Returns:
            :class:`b2share.modules.schemas.errors.RootSchema`: The requested
                root schema.

        Raises:
            :class:`b2share.modules.schemas.errors.RootSchemaDoesNotExistError`:
                If the root schema version does not exist.
        """  # noqa
        from .models import RootSchemaVersion
        try:
            model = RootSchemaVersion.query.filter(
                RootSchemaVersion.version == version).one()
            return cls(model)
        except NoResultFound as e:
            raise RootSchemaDoesNotExistError(id) from e

    @property
    def version(self):
        """Retrieve this root schema's version."""
        return self.model.version

    @property
    def json_schema(self):
        """Retrieve this root schema's JSON Schema."""
        return self.model.json_schema


class BlockSchema(object):
    """Record block Schema API."""

    def __init__(self, model):
        """
        Args:
            model (:class:`b2share.modules.schemas.models.BlockSchema`):
                block schema database model.
        """
        self.model = model

    @classmethod
    def get_block_schema(cls, schema_id):
        from .models import BlockSchema as BlockSchemaModel
        try:
            model = BlockSchemaModel.query.filter(
                BlockSchemaModel.id == schema_id).one()
            return cls(model)
        except NoResultFound as e:
            raise BlockSchemaDoesNotExistError() from e

    @classmethod
    def get_all_block_schemas(cls, community_id=None, name=None):
        from .models import BlockSchema as BlockSchemaModel
        try:
            filters = []
            if community_id is not None:
                filters.append(BlockSchemaModel.community == community_id)
            if name is not None:
                filters.append(BlockSchemaModel.name == name)

            return [cls(model) for model in BlockSchemaModel.query.filter(
                *filters).order_by(BlockSchemaModel.created).all()]
        except NoResultFound as e:
            raise BlockSchemaDoesNotExistError() from e

    @classmethod
    def create_block_schema(cls, community_id, name, id_=None):
        """Create a new block schema.

        Args:
            community_id (UUID): id of the community maintaining this
        """
        from .models import BlockSchema as BlockSchemaModel
        try:
            with db.session.begin_nested():
                kwargs = {}
                if id_ is not None:
                    kwargs['id'] = id_
                model = BlockSchemaModel(
                    community=community_id, name=name, **kwargs)
                block_schema = cls(model)
                db.session.add(model)
        except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.DataError) as e:
            raise InvalidBlockSchemaError() from e
        return block_schema

    def update(self, data, clear_fields=False):
        """Update multiple fields of the schema at the same time.
        If the update fails, none of the schema's fields are modified.
        Args:
            data (dict): it replaces the given values.
            clear_fields (bool): if True, set not specified fields to None.
        Returns:
            :class:`BlockSchema`: self
        Raises:
            b2share.modules.schemas.InvalidBlockSchemaError: The
                schema update failed because the resulting schema is
                not valid.
        """
        try:
            with db.session.begin_nested():
                if clear_fields:
                    for field in ['name']:
                        setattr(self.model, field, data.get(field, None))
                else:
                    for key, value in data.items():
                        setattr(self.model, key, value)
                db.session.merge(self.model)
        except sqlalchemy.exc.IntegrityError as e:
            raise InvalidBlockSchemaError() from e
        return self

    def patch(self, patch):
        """Update the schema's metadata with a json-patch.
        Args:
            patch (dict): json-patch which can modify the following fields:
                name, description, logo.
        Returns:
            :class:`BlockSchema`: self
        Raises:
            jsonpatch.JsonPatchConflict: the json patch conflicts on the
                block schema.
            jsonpatch.InvalidJsonPatch: the json patch is invalid.
            b2share.modules.block_schemas.errors.InvalidBlockSchemaError: The
                block schema patch failed because the resulting block schema is
                not valid.
        """
        data = apply_patch({'name': self.model.name}, patch, True)
        self.update(data)
        return self

    def create_version(self, json_schema, version_number=None):
        """Create a new version of this schema and release it.

        Args:
            json_schema (dict): the json_schema to use for this new version.

        Returns:
            :class:`b2share.modules.schemas.models.BlockSchemaVersion`:
                The new block schema version.

        Raises:
            :class:`b2share.modules.schemas.errors.InvalidJSONSchemaError`:
                The given JSON Schema is not valid.

        """
        from .models import BlockSchemaVersion as BlockSchemaVersionModel

        if self.deprecated:
            raise BlockSchemaIsDeprecated()
        if not isinstance(json_schema, dict):
            raise InvalidJSONSchemaError('json_schema must be a dict')

        previous_block_schema_versions = _fetch_all_query_pages(
            BlockSchemaVersionModel.query.filter(
                BlockSchemaVersionModel.block_schema == self.model.id,
                # BlockSchemaVersionModel.version < version_number
            ).order_by(BlockSchemaVersionModel.version.asc())
        )
        prev_schemas = map(lambda x: x.json_schema,
                           previous_block_schema_versions)

        validate_json_schema(json_schema, prev_schemas)
        # FIXME: validate the json-schema
        with db.session.begin_nested():
            last_version = db.session.query(
                sqlalchemy.func.max(BlockSchemaVersionModel.version)
                .label('last_version')
            ).filter(
                BlockSchemaVersionModel.block_schema == self.model.id
            ).one().last_version

            new_version = (last_version + 1 if last_version is not None
                           else 0)
            if version_number and new_version < version_number:
                raise InvalidSchemaVersionError(last_version)
            elif version_number and new_version > version_number:
                raise SchemaVersionExistsError(last_version)

            model = BlockSchemaVersionModel(
                block_schema=self.model.id,
                # we specify the separators in order to avoir whitespaces
                json_schema=json.dumps(json_schema, separators=(',', ':')),
                version=new_version)
            db.session.add(model)
        return BlockSchemaVersion(model, self)

    @property
    def id(self):
        """Retrieve the ID of this Block Schema."""
        return self.model.id

    @property
    def name(self):
        """Retrieve the name of this Block Schema."""
        return self.model.name

    @name.setter
    def name(self, value):
        """Set the name of this Block Schema."""
        try:
            with db.session.begin_nested():
                self.model.name = value
        except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.DataError) as e:
            raise InvalidBlockSchemaError() from e

    @property
    def community(self):
        """Retrieve the ID of the community maintaining of this Block Schema.
        """
        return self.model.community

    @community.setter
    def community(self, community_id):
        """Set the ID of the community maintaining of this Block Schema.

        Raises:
            :class:`b2share.modules.communities.errors.CommunityDoesNotExistError`:
                if the community does not exist.
            :class:`b2share.modules.schemas.errors.InvalidBlockSchemaError`:
                if another conflict occured.
        """  # noqa
        try:
            with db.session.begin_nested():
                self.model.community = community_id
                db.session.merge(self.model)
        except sqlalchemy.exc.IntegrityError as e:
            # this will raise CommunityDoesNotExistError if necessary
            Community.get(community_id)
            # else raise a generic exception
            raise InvalidBlockSchemaError() from e

    @property
    def deprecated(self):
        """Retrieve the deprecation status of this Block Schema.

        A schema marked as deprecated is not maintained anymore.

        Returns:
            bool: True if the schema is deprecated, else False.
        """
        return self.model.deprecated

    @deprecated.setter
    def deprecated(self, value):
        """Set the deprecation status of this Block Schema.

        Args:
            value (bool): the new deprecation status.
        """
        with db.session.begin_nested():
            self.model.deprecated = value
            db.session.merge(self.model)

    @property
    def versions(self):
        """Retrieve the complete list of released block schema versions.

        Returns:
            :class:`b2share.modules.schemas.models.BlockSchemaVersionsIterator`:
                An iterator on released block schema versions.
        """  # noqa
        return BlockSchemaVersionsIterator(self)

    @property
    def updated(self):
        """Retrieve the updated field value of this Block Schema."""
        return self.model.updated


class BlockSchemaVersionsIterator(object):
    """Iterator for Block Schema Versions.

    SQL Queries are performed for each method call. Thus repeated calls will
    be inconsistent if new Block Schema Versions are added.
    """

    def __init__(self, block_schema):
        """Initialize iterator."""
        self._it = None
        self.block_schema = block_schema

    def __len__(self):
        """Get number of versions."""
        from .models import BlockSchemaVersion as BlockSchemaVersionModel
        return db.session.query(
            sqlalchemy.func.count(BlockSchemaVersionModel.version)
            .label('count')
        ).filter(
            BlockSchemaVersionModel.block_schema == self.block_schema.id,
        ).one().count

    def __iter__(self):
        """Get iterator."""
        from .models import BlockSchemaVersion as BlockSchemaVersionModel
        self._it = iter(BlockSchemaVersionModel.query.filter(
            BlockSchemaVersionModel.block_schema == self.block_schema.id,
        ).order_by(BlockSchemaVersionModel.version.asc()).all())
        return self

    def __next__(self):
        """Get next version item."""
        return BlockSchemaVersion(next(self._it), self.block_schema)

    def __getitem__(self, version):
        """Get a specific version."""
        from .models import BlockSchemaVersion as BlockSchemaVersionModel
        try:
            model = BlockSchemaVersionModel.query.filter(
                BlockSchemaVersionModel.block_schema == self.block_schema.id,
                BlockSchemaVersionModel.version == version).one()
        except NoResultFound:
            raise IndexError('No version {0} for block schema {1}'.format(
                version, self.block_schema.id))
        return BlockSchemaVersion(model, self.block_schema)

    def __contains__(self, version):
        """Test if a version exists."""
        try:
            self[version]
            return True
        except IndexError:
            return False


class BlockSchemaVersion(object):
    """API for the Block Schema Versions."""

    def __init__(self, model, block_schema):
        """
        Args:
            model (:class:`b2share.modules.schemas.models.BlockSchemaVersion`):
                block schema version database model.
            block_schema (:class:`b2share.modules.schemas.api.BlockSchema`):
                the parent block schema.
        """
        super(BlockSchemaVersion, self).__init__()
        self.model = model
        self.block_schema = block_schema

    @property
    def version(self):
        """Retrieve the version number of this Block Schema Version."""
        return self.model.version

    @property
    def released(self):
        """Retrieve the release date of this Block Schema Version."""
        return self.model.released

    @property
    def json_schema(self):
        """Retrieve the JSON Schema of this Block Schema Version."""
        return self.model.json_schema


class CommunitySchema(object):
    """Community Schema API.

    Each Community has only one schema, which can have multiple versions. All
    released versions are immutable.

    The last released Community schema is used to validate all the new records
    submitted to this Community.
    """

    def __init__(self, model):
        """
        Args:
            model (:class:`b2share.modules.schemas.models.CommunitySchemaVersion`):
                Community schema version database model.
        """  # noqa
        self.model = model

    @classmethod
    def get_community_schema(cls, community_id, version=None):
        """Retrieve the requested version of a community schema.

        Args:
            community_id (ID): community id.
            version (int): version of the schema to retrieve. If None, the last
                version will be retrieved.

        Returns:
            :class:`b2share.modules.schemas.api.CommunitySchema`: the
                requested Community schema.
        Raises:
            :class:`b2share.modules.schemas.errors.CommunitySchemaDoesNotExistError`:
                the requested community schema does not exist.

        """  # noqa
        from .models import CommunitySchemaVersion
        try:
            with db.session.begin_nested():
                if version is not None:
                    model = CommunitySchemaVersion.query.filter(
                        CommunitySchemaVersion.community == str(community_id),
                        CommunitySchemaVersion.version == version
                    ).one()
                else:
                    model = CommunitySchemaVersion.query.filter(
                        CommunitySchemaVersion.community == str(community_id)
                    ).order_by(
                        CommunitySchemaVersion.version.desc()
                    ).limit(1).one()
                return cls(model)
        except NoResultFound as e:
            raise CommunitySchemaDoesNotExistError(str(community_id)) from e

    @classmethod
    def create_version(cls, community_id, community_schema,
                       root_schema_version=None):
        """Create a new schema draft for the given community.

        Args:
            community_id (UUID): ID of the community whose schema is create.
            community_schema (dict): loaded JSON Schema validating the
                community specific metadata.
            root_schema_version (int): version of the root schema used by this
                community schema. If set to None, the root_schema of the last
                version is used, if there is no previous version
                (new community), the last root_schema is used.

        Returns:
            :class:`b2share.modules.schemas.api.CommunitySchema`: the
                new Community schema.
        """
        from .models import CommunitySchemaVersion

        previous_community_schemas = _fetch_all_query_pages(
            CommunitySchemaVersion.query.filter(
                CommunitySchemaVersion.community == community_id
            ).order_by(CommunitySchemaVersion.version.asc())
        )

        prev_schemas = map(lambda x: x.community_schema,
                           previous_community_schemas)
        validate_json_schema(community_schema, prev_schemas)

        with db.session.begin_nested():
            if len(previous_community_schemas) > 0:
                last_schema = previous_community_schemas[-1]

                new_version = last_schema.version + 1
                if root_schema_version is None:
                    root_schema_version = last_schema.root_schema
            else:
                if root_schema_version is None:
                    # there is no schema yet, the community is new.
                    # Use the last RootSchema.
                    from .models import RootSchemaVersion
                    try:
                        root_schema_version = RootSchemaVersion.query.order_by(
                            RootSchemaVersion.version).limit(1).one().version
                    except NoResultFound as e:
                        raise RootSchemaDoesNotExistError from e
                new_version = 0

            model = CommunitySchemaVersion(
                community=community_id,
                root_schema=root_schema_version,
                community_schema=json.dumps(community_schema,
                                            # avoid default whitespaces
                                            separators=(',', ':')),
                version=new_version)
            db.session.add(model)
        return cls(model)

    def build_json_schema(self):
        """Build the JSON Schema corresponding to this Community schema.

        Each Block Schema and the Root Schema should also refuse any additional
        properties in order to avoid conflicts.
        """
        # The root schema already defines the "community_specific" field but
        # Doesn't define what it contains. This way it can forbid any
        # additional field at the root level while enabling the later
        # definition of the "community_specific" field content.
        root_schema = RootSchema.get_root_schema(self.model.root_schema)
        result = {"allOf": [
            # Combine root schema and community specific schema.
            json.loads(root_schema.json_schema),
            {
                'type': 'object',
                'properties': {
                    'community_specific':
                    json.loads(self.model.community_schema)
                },
            }
        ]}
        return result

    @property
    def community(self):
        """Retrieve the community maintaining of this Community Schema."""
        return self.model.community

    @property
    def version(self):
        """Retrieve the version number of this Community Schema."""
        return self.model.version

    @property
    def released(self):
        """Retrieve the release date of this Community Schema Version."""
        return self.model.released

    @property
    def root_schema(self):
        """Retrieve the root schema version used by this community schema."""
        return self.model.root_schema

    @property
    def community_schema(self):
        """Retrieve the community specific JSON Schema."""
        return self.model.community_schema


def _fetch_all_query_pages(query, per_page=500):
    """Paginate query results and return an iterable object."""
    result = []
    iterator = query.paginate(page=1, per_page=500, error_out=False)
    while True:
        result.extend(iterator.items)
        if not iterator.has_next:
            break
        iterator = iterator.next(error_out=False)
    return result
