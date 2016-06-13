"""Utilities for B2share deposit."""

from flask import request
from werkzeug.local import LocalProxy
from werkzeug.routing import PathConverter


def file_id_to_key(value):
    """Convert file UUID to value if in request context."""
    from invenio_files_rest.models import ObjectVersion

    _, record = request.view_args['pid_value'].data
    if value in record.files:
        return value

    object_version = ObjectVersion.query.filter_by(
        bucket_id=record.files.bucket.id, file_id=value
    ).first()
    if object_version:
        return object_version.key
    return value


class FileKeyConverter(PathConverter):
    """Convert file UUID for key."""

    def to_python(self, value):
        """Lazily convert value from UUID to key if need be."""
        return LocalProxy(lambda: file_id_to_key(value))
