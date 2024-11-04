# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""B2Share Files views."""

from __future__ import absolute_import


from invenio_files_rest.views import (
    ObjectResource,
    invalid_subresource_validator,
    need_permissions
)
from invenio_files_rest.serializer import json_serializer
from invenio_files_rest.models import ObjectVersion
from webargs import fields

from invenio_files_rest.tasks import remove_file_data
from invenio_db import db



class B2ShareObjectResource(ObjectResource):
    """Object item resource for B2SHARE.

    Adds capability to enable user to download of a file with a JWT token,
    without explicitly giving this user permission to file.
    Enables to sharing of restricted files or files from draft records
    to anonymous (i.e. not logged in) users.
    """

    view_name = 'b2share_files_rest_object_view'

    get_args = {
        'version_id': fields.UUID(
            location='query',
            load_from='versionId',
            missing=None,
        ),
        'upload_id': fields.UUID(
            location='query',
            load_from='uploadId',
            missing=None,
        ),
        'uploads': fields.Raw(
            location='query',
            validate=invalid_subresource_validator,
        ),
        'encoded_jwt': fields.Str(
            location='query',
            load_from='jwt',
            missing=None,
        ),
    }

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(B2ShareObjectResource, self).__init__(*args, **kwargs)


    @need_permissions(
        lambda self, bucket, obj, *args: obj,
        'object-delete',
        hidden=False,  # Because get_object permission check has already run
    )
    def delete_object(self, bucket, obj, version_id):
        """Delete an existing object.

        :param bucket: The bucket (instance or id) to get the object from.
        :param obj: A :class:`invenio_files_rest.models.ObjectVersion`
            instance.
        :param version_id: The version ID.
        :returns: A Flask response.
        """
        if version_id is None:
            # Create a delete marker.
            with db.session.begin_nested():
                ObjectVersion.delete(bucket, obj.key)
            db.session.commit()
        else:
            # Permanently delete specific object version.
            # check_permission(
            #    current_permission_factory(bucket, 'object-delete-version'),
            #    hidden=False,
            #)
            obj.remove()
            db.session.commit()
            if obj.file_id:
                remove_file_data.delay(str(obj.file_id))

        return self.make_response('', 204)


object_view_object_resources = B2ShareObjectResource.as_view(
    'b2share_object_api',
    serializers={
        'application/json': json_serializer,
    }
)