# -*- coding: utf-8 -*-
# This file is part of B2SHARE.
# Copyright (C) 2015 CERN.
#
# B2SHARE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2SHARE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2SHARE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Tests for checksumming b2share deposits"""

from invenio.ext.restful.utils import APITestCase
from invenio.base.globals import cfg
from invenio.ext.sqlalchemy import db

from flask import url_for

import logging
import os.path
import shutil
import subprocess
import tempfile

from urlparse import urlparse


class B2ShareAPITestCase(APITestCase):
    """Unit test case helping test B2Share REST API."""

    def setUp(self):
        """Generic tests initalization"""
        # only log warnings
        self.app.logger.setLevel(logging.WARNING)
        # display log messages on the console
        self.app.logger.addHandler(logging.StreamHandler())

    # Record
    def get_records(self, page_offset=None, page_size=None, safe=False):
        """call GET /api/records"""
        req = self.get(endpoint='b2deposit.listrecords',
                       urlargs={
                           'page_offset': page_offset,
                           'page_size': page_size,
                       })
        if safe:
            self.assertEqual(req.status_code, 200,
                             "GET /api/records returned code \
                             {0}".format(req.status_code))
        return req

    def get_records_by_domain(self, domain, page_offset=None, page_size=None,
                              safe=False):
        """call GET /api/records/<domain_name>"""
        req = self.get(endpoint='b2deposit.listrecordsbydomain',
                       urlargs={
                           'domain_name': domain,
                           'page_offset': page_offset,
                           'page_size': page_size,
                       })
        if safe:
            self.assertEqual(req.status_code, 200,
                             "GET /api/records/<domain_name> returned code \
                             {0}".format(req.status_code))
        return req

    def get_record(self, record_id, safe=False):
        """call GET /api/record/<record_id>"""
        req = self.get(endpoint='b2deposit.recordres',
                       urlargs={'record_id': int(record_id)})
        if safe:
            self.assertEqual(req.status_code, 200,
                             "GET /api/records/<record_id> returned code \
                             {0}".format(req.status_code))
            self.assertEqual(req.json.get('record_id'), record_id)
        return req

    # Deposition
    def create_deposition(self, safe=False):
        """call POST /api/depositions"""
        req = self.post(endpoint='b2deposit.listdepositions')
        if safe:
            self.assertEqual(req.status_code, 201,
                             "POST /api/depositions returned code \
                             {0}".format(req.status_code))
        return req

    def upload_deposition_file(self, deposit_id, file_path=None,
                               file_stream=None, file_name=None, safe=False):
        """call POST /api/deposition/<deposit_id>/files

        :Parameters:
            - `deposit_id` (str) - deposition id.
            - `file_path` (str) - file whose content and name will be sent.
            - `file_stream` (stream) - if set, it will be sent as file's
            content.
            - `file_name` (string) - file name, mandatory if file_stream is
            used.
            - `safe` (bool) - enable validation of request success.
        """
        def send_stream(stream):
            return self.post(endpoint='b2deposit.depositionfiles',
                             urlargs={'deposit_id': deposit_id},
                             is_json=False,
                             data={'file': (file_stream, file_name)})

        if file_path is not None:
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as file_stream:
                req = send_stream(file_stream)
        elif file_stream is not None:
            if file_name is None:
                raise ValueError('file_name is mandatory when file_stream is\
                                 used')
            req = send_stream(file_stream)
        else:
            raise ValueError('file_stream or file_path must be set')
        # check if the request succeeded
        if safe:
            self.assertEqual(req.status_code, 200,
                             "POST /api/deposition/<deposit_id>/files \
                             returned code {0}".format(req.status_code))
        return req

    def get_deposition_files(self, deposit_id, safe=False):
        """call GET /api/deposition/<deposit_id>/files"""
        req = self.get(endpoint='b2deposit.depositionfiles',
                       urlargs={'deposit_id': deposit_id})
        if safe:
            self.assertEqual(req.status_code, 200,
                             "GET /api/deposition/<deposit_id>/files returned code \
                             {0}".format(req.status_code))
        return req

    def commit_deposition(self, deposit_id, metadata_json, safe=False):
        """call POST /api/deposition/<deposit_id>/commit"""
        req = self.post(endpoint='b2deposit.depositioncommit',
                        urlargs={'deposit_id': deposit_id},
                        is_json=True, data=metadata_json)

        if req.status_code == 201:
            record_id = req.json["record_id"]
            self.process_record(record_id)

        if safe:
            self.assertEqual(req.status_code, 201,
                             "POST /api/deposition/<deposit_id>/commit returned \
                             code {0}".format(req.status_code))
        return req

    #
    # Helpers
    #
    def create_and_login_user(self, user_nickname=None, user_password=None):
        """Create test user and log him in."""
        from invenio.modules.accounts.models import User
        self.user_nickname = user_nickname or "tester"
        self.user_password = user_password or "tester"
        # remove the user if he exists
        self.user = User.query.filter(
            User.nickname == self.user_nickname).first()
        if self.user:
            try:
                db.session.delete(self.user)
                db.session.commit()
            except:
                db.session.rollback()
                raise
        # create the user
        email = "{}@b2share.com".format(self.user_nickname)
        self.user = User(
            email=email, nickname=self.user_nickname
        )
        self.user.password = self.user_password
        try:
            db.session.add(self.user)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        from invenio.ext.login import login_user
        from flask.ext.login import current_user
        login_user(self.user.id)
        current_user.reload()
        self.assertEqual(current_user.get_id(), self.user.id)
        self.safe_login_web_user(self.user_nickname, self.user_password)
        return self.user.id

    def safe_login_web_user(self, username, password):
        """Log in as a given user using the web frontend, not the REST API and
        check that the login succeeded."""
        self.create_oauth_token(self.user.id, scopes=[])
        response = self.client.post(url_for('webaccount.login'),
                                    base_url=cfg["CFG_SITE_SECURE_URL"],
                                    data=dict(nickname=username,
                                              password=password),
                                    follow_redirects=False)
        # check that the login succeeded. i.e we are redirected on another page
        # and it is not the login page FIXME: improve this
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(urlparse(response.location).path,
                            url_for('webaccount.login'))

    def add_current_user_to_group(self, usergroup_name):
        from invenio.modules.accounts.models import User, Usergroup, UserUsergroup
        from flask.ext.login import current_user
        user = User.query.get(current_user.get_id())
        ug = Usergroup.query.filter(Usergroup.name == usergroup_name).one()
        ug.join(user, status=UserUsergroup.USER_STATUS['MEMBER'])
        current_user.reload()

    def remove_current_user_from_group(self, usergroup_name):
        from invenio.modules.accounts.models import User, Usergroup
        from flask.ext.login import current_user
        user = User.query.get(current_user.get_id())
        ug = Usergroup.query.filter(Usergroup.name == usergroup_name).one()
        ug.leave(user)
        current_user.reload()

    def remove_user(self):
        """Logout and remove test user."""
        try:
            self.remove_oauth_token()
        except:
            self.app.logger.exception("Caught an error while removing oauth token")

        try:
            self.logout()
        except:
            self.app.logger.exception("Caught an error while logging out")

        if self.user:
            try:
                db.session.delete(self.user)
                db.session.commit()
            except:
                db.session.rollback()
                raise

    def get_record_file_content(self, record_id, file_name):
        """Retrieve a given file's content

        The user must be authenticated through the web frontend as the
        access_token cannot be used.
        :Parameters:
            - `recid` (str) - record id
            - `file_name` (str) - name of the file to retrieve
        """
        file_request = self.client.get(
            url_for('record.file', recid=record_id, filename=file_name),
            base_url=cfg["CFG_SITE_SECURE_URL"]
        )
        self.assertEqual(file_request.status_code, 200)
        return file_request.get_data()

    def get_internal_record(self, recid):
        """Retrieve a given record without using B2Deposit."""
        from invenio.modules.records.api import get_record
        return get_record(recid)

    def process_record(self, recid):
        """Runs all bib* tasks needed to be able to access the record"""
        # run all 'webdeposit' pending tasks
        # FIXME it would be cleaner if we could just execute the added task,
        # but we can't because we don't save the task ID => TODO
        self.run_tasks('webdeposit')  # first run for bibupload
        self.run_command(["bibindex", "-v0", "-u", "webdeposit",
                          "-i", str(recid)])
        self.run_command(["webcoll", "-v0", "-q", "-u", "webdeposit"])
        self.run_tasks('webdeposit')  # second run for the new tasks

    def run_command(self, command):
        """Run a command in a subprocess.

        It prints the subprocess's stdout and stderr at debug level if the
        return code is 0. This method waits for the subprocess to end before
        returning.

        :Parameters:
            - `command` (list): the command as given to popen
        """
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        # extract subprocess's standard output and error
        proc_stdout, proc_stderr = proc.communicate()
        # check if the command failed
        if proc.returncode:
            # print stdout
            self.app.logger.info(proc_stdout)
            # print stderr
            self.app.logger.error(proc_stderr)
            raise Exception("command {0} failed with code {1}"
                            .format(str(command), proc.returncode))
        else:
            # print subprocess's stdout and stderr at debug level
            # print stdout
            self.app.logger.debug(proc_stdout)
            # print stderr
            self.app.logger.debug(proc_stderr)

    # NOTE: this is comming from
    # zenodo/modules/deposit/testsuite/test_zenodo_api.py
    def run_task_id(self, task_id):
        """ Run a bibsched task."""
        from invenio.modules.scheduler.models import SchTASK
        CFG_BINDIR = self.app.config['CFG_BINDIR']

        bibtask = SchTASK.query.filter(SchTASK.id == task_id).first()
        assert bibtask is not None
        assert bibtask.status == 'WAITING'
        self.run_command([CFG_BINDIR + "/" + bibtask.proc, str(task_id)])

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
    Context manager which creates a temporary directory using
    tempfile.mkdtemp() and deletes it when exiting.

    This class is available in python +v3.2 as tempfile.TemporaryDirectory.
    """
    def __enter__(self):
        self.dir_name = tempfile.mkdtemp()
        return self.dir_name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.dir_name)


def create_file(folder_path, file_name, content):
    path = os.path.join(folder_path, file_name)
    with open(path, 'w') as file_desc:
        file_desc.write(content)
    return path

# use either the existing class from tempfile or, if it does not exist, the one
# we just created.
TemporaryDirectory = getattr(tempfile, 'TemporaryDirectory',
                             TemporaryDirectory)
