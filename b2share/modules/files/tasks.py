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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Celery background tasks."""
import json
from celery import shared_task
from flask import current_app, url_for
from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_records_files.models import RecordsBuckets
from invenio_files_rest.models import FileInstance, ObjectVersion
from invenio_files_rest.tasks import schedule_checksum_verification
from invenio_mail.tasks import send_email
from sqlalchemy import or_


def failed_checksum_files_query():
    """Get all files that failed their previous checksum verification."""
    return FileInstance.query.filter(or_(FileInstance.last_check==None,
                                         FileInstance.last_check==False))


def _format_file_info(file_info):
    """Format file information."""
    return ('Record Id: {0}<br/> Bucket Id: {1}<br/> '
            'File key: {2}<br/> Path: {3}<br/> Previous'
            ' Checksum: {4}').format(
                str(file_info[0]), str(file_info[1]),
                str(file_info[2]), str(file_info[3]),
                str(file_info[4])
            )

def notify_admin():
    """Send email to admin with the info about checksum verification errors."""
    # Get all files that didn't match their checksums
    results = db.session.query(RecordsBuckets.record_id,
                               ObjectVersion.bucket_id,
                               ObjectVersion.key,
                               FileInstance.uri,
                               FileInstance.checksum).\
        filter(RecordsBuckets.bucket_id == ObjectVersion.bucket_id,
               ObjectVersion.file_id == FileInstance.id,
               FileInstance.last_check == False).all()
    # Get all files for which an error occurred while verifying their checksum
    error_count = FileInstance.query.filter_by(last_check=None).count()
    if error_count != 0:
        error_files = db.session.query(RecordsBuckets.record_id,
                                ObjectVersion.bucket_id,
                                ObjectVersion.key,
                                FileInstance.uri,
                                FileInstance.checksum).\
            filter(RecordsBuckets.bucket_id == ObjectVersion.bucket_id,
                ObjectVersion.file_id == FileInstance.id,
                FileInstance.last_check == None).limit(100).all()

    msg_content = ''
    if results:
        msg_content = '{0} "{1}" :<br/><br/> {2}<br/><br/>'.format(
            _('List of files with modified checksums on the B2SHARE server '),
            # We reuse JSONSCHEMAS_HOST because SERVER_NAME is not set
            current_app.config['JSONSCHEMAS_HOST'],
            '<br/><br/>'.join([_format_file_info(info) for info in results])
        )
    if error_count != 0:
        msg_content += ('{0}: {1}<br/><br/>{2}:<br/><br/>{3}<br/><br/>'.format(
            _('Number of files for which an error occurred during the '
              'checksum verification (other than a wrong checksum)'),
            str(error_count),
            _('Partial list of files with errors'),
            '<br/><br/>'.join([
                _format_file_info(info) for info in error_files
            ])
        ))
    if msg_content:
        msg_content += '-- <br>{0} "{1}"'.format(
            _('B2SHARE automatic task for server'),
            current_app.config['JSONSCHEMAS_HOST']
        )
        support = str(current_app.config.get('SUPPORT_EMAIL'))
        send_email(dict(
            subject=_('B2SHARE Checksum Verification Report'),
            sender=support,
            recipients=[support],
            html=msg_content,
            body=msg_content
        ))


@shared_task(ignore_result=True)
def schedule_failed_checksum_files(**kwargs):
    """Schedule files checksum check for files which failed their check.

    This happens when a previous scan scheduled by either of the tasks
    schedule_checksum_verification or schedule_failed_checksum_files
    failed with an exception.

    Exceptions can be raised for example if the filesystem is not available. It
    doesn't mean that the files are corrupted but the check should still run
    again.

    In general we want schedule_failed_checksum_files to run more often than
    schedule_checksum_verification as few files should fail their scan and
    when it happens we want to recheck them rapidly.

    This task also notifies B2SHARE_SUPPORT email of any errors.


   :param dict kwargs: parameter forwarded to schedule_checksum_verification.
    """
    assert 'files_query' not in  kwargs
    schedule_checksum_verification.s(
        files_query=failed_checksum_files_query,
        **kwargs
    ).apply()
    notify_admin()
