# -*- coding: utf-8 -*-
"""Tests for checksumming b2share deposits"""

from invenio.ext.restful.utils import APITestCase
from invenio.ext.sqlalchemy import db

from werkzeug.security import gen_salt
from flask import current_app
from flask.ext import restful

import logging, os, json

import shutil
import tempfile

# only log warnings (building current_app)
logging.getLogger("current_app").setLevel(logging.WARNING)
# logging.getLogger("current_app").setLevel(logging.DEBUG)

class B2ShareAPITestCase(APITestCase):
    """Unit test case helping test B2Share REST API."""

    # Record
    def get_records(self):
        """call GET /api/records"""
        return self.get(endpoint='b2deposit.listrecords')

    def get_record(self, record_id):
        """call GET /api/record/<record_id>"""
        return self.get(endpoint='b2deposit.recordres',
                        urlargs={'record_id': int(record_id)})

    # Deposition
    def create_deposition(self):
        """call POST /api/depositions"""
        from invenio.b2share.modules.b2deposit.restful import ListDepositions
        return self.post(endpoint='b2deposit.listdepositions')

    def upload_deposition_file(self, deposit_id, file_stream, file_name):
        """call POST /api/deposition/<deposit_id>/files"""
        return self.post(endpoint='b2deposit.depositionfiles',
                         urlargs={'deposit_id': deposit_id},
                         is_json=False, data={'file':(file_stream, file_name)})

    def get_deposition_files(self, deposit_id):
        """call GET /api/deposition/<deposit_id>/files"""
        return self.get(endpoint='b2deposit.depositionfiles',
                          urlargs={'deposit_id': deposit_id})


    def commit_deposition(self, deposit_id, metadata_json):
        """call POST /api/deposition/<deposit_id>/commit"""
        result = self.post(endpoint='b2deposit.depositioncommit',
                           urlargs={ 'deposit_id': deposit_id },
                           is_json=True, data=metadata_json)

        # run all 'webdeposit' pending tasks
        # FIXME it would be cleaner if we could just execute the added task, but
        # we can't because we don't save the task ID => TODO
        self.run_tasks('webdeposit')
        return result

    # helpers
    def create_and_login_user(self):
        """Create test user and log him in."""
        from invenio.modules.accounts.models import User
        self.user = User(
            email='info@invenio-software.org', nickname='tester'
        )
        self.user.password = "tester"
        db.session.add(self.user)
        db.session.commit()
        self.create_oauth_token(self.user.id, scopes=[])

    def remove_user(self):
        """Remove test user."""
        self.remove_oauth_token()
        if self.user:
            db.session.delete(self.user)
            db.session.commit()


    # NOTE: this is comming from
    # zenodo/modules/deposit/testsuite/test_zenodo_api.py
    def run_task_id(self, task_id):
        """ Run a bibsched task."""
        import os
        from invenio.modules.scheduler.models import SchTASK
        CFG_BINDIR = self.app.config['CFG_BINDIR']

        bibtask = SchTASK.query.filter(SchTASK.id == task_id).first()
        assert bibtask is not None
        assert bibtask.status == 'WAITING'

        cmd = "%s/%s %s" % (CFG_BINDIR, bibtask.proc, task_id)
        assert not os.system(cmd)


    # NOTE: this is comming from
    # zenodo/modules/deposit/testsuite/test_zenodo_api.py
    def run_tasks(self, alias=None):
        """
        Run all background tasks matching parameters.
        """
        from invenio.modules.scheduler.models import SchTASK

        q = SchTASK.query
        if alias:
            q = q.filter(SchTASK.user == alias, SchTASK.status == 'WAITING')

        for r in q.all():
            self.run_task_id(r.id)


# TODO: this class does not have the parameters of the original
# tempfile.TemporaryDirectory
class TemporaryDirectory(object):
    """
    Context manager which creates a temporary directory using tempfile.mkdtemp()
    and deletes it when exiting.

    This class is available in python +v3.2 as tempfile.TemporaryDirectory.
    """
    def __enter__(self):
        self.dir_name = tempfile.mkdtemp()
        return self.dir_name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.dir_name)

# use either the existing class from tempfile or, if it does not exist, the one
# we just created.
TemporaryDirectory = getattr(tempfile, 'TemporaryDirectory',
                             TemporaryDirectory)

