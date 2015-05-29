# -*- coding: utf-8 -*-
"""Tests for checksumming b2share deposits"""

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase

import os, os.path, time, hashlib

from .helpers import B2ShareAPITestCase, TmpHelper

from flask import current_app

class TestB2ShareChecksums(B2ShareAPITestCase):
    """Unit tests for stability of checksums, using the REST API"""

    def setUp(self):
        self.create_and_login_user()

    def tearDown(self):
        self.remove_user()
        TmpHelper.delete_all_tmp_files()

    def create_record(self, metadata, files):
        """create a deposition, add some files and commit the record."""
        current_app.config.update(PRESERVE_CONTEXT_ON_EXCEPTION= False)
        # create deposition object
        request_create = self.create_deposition()
        print repr(request_create)
        self.assertTrue(request_create.status_code == 201)
        location = request_create.json['location']
        # FIXME: the api should return the deposition id. We should not have to
        # parse the uri
        deposit_id = location.split('/')[3]

        # upload files
        for f in files:
            request_upload = self.upload_deposition_file(
                deposit_id=deposit_id,
                file_stream=open(f,'rb'),
                file_name=os.path.basename(f)
            )
            self.assertTrue(request_upload.status_code == 200)

        # commit deposition
        request_commit = self.commit_deposition(deposit_id, metadata)
        self.assertTrue(request_commit.status_code == 201)
        location = request_commit.json['location']
        # FIXME: the api should return the record id. We should not have to
        # parse the uri
        record_id = location.split('/')[3]

        # get record
        request_get = self.get_record(record_id)
        if request_get.status_code != 200:
            self.fail('timeout while in the rest deposition')

        deposit_json = request_get.json['Deposit']
        posted_files = set([os.path.basename(f) for f in files])
        deposited_files = set([f['name'] for f in deposit_json['files']])
        self.assertEquals(posted_files, deposited_files)
        return deposit_json

    def compute_checksum(self, files):
        sha = hashlib.sha256()
        buffersize = 1024 * 1024
        for f in sorted(files):
            with open(f, 'rb', buffering=0) as fp:
                while True:
                    block = fp.read(buffersize)
                    if not block:
                        break
                    sha.update(block)
        return sha.hexdigest()

    def test_deposit_checksums(self):
        metadata1 = {
            'domain': "generic",
            'title': 'Checksum test',
            'description': "B2SHARE depositing checksum test via RestAPI",
            'open_access': "true"
        }

        files1 = []
        files1.append(TmpHelper.create_tmp_file("testfile1.txt", "test file 1"))
        files1.append(TmpHelper.create_tmp_file("testfile2.txt", "test ünicödé-ø-å file"))

        # precomputed sha256 sum:
        # $ ls -1 testfile*.txt | sort | xargs cat | shasum -a 256
        checksum = 'e6e06a09a8fdc6672563e177e7d2df4ae9ebd33df18f8d9cce564aae9d285c00'

        computed_checksum = self.compute_checksum(files1)
        self.assertEquals(checksum, computed_checksum)

        rec = self.create_record(metadata1, files1)
        self.assertEquals(checksum, rec['checksum'])

        rec_identical = self.create_record(metadata1, files1)
        self.assertEquals(checksum, rec_identical['checksum'])

        reversed_files = list(reversed(files1))
        rec_reversed = self.create_record(metadata1, reversed_files)
        self.assertEquals(checksum, rec_reversed['checksum'])

        metadata2 = {
            'domain': "Linguistics",
            'title': 'Checksum test 2',
            'description': "B2SHARE depositing checksum test via RestAPI",
            'open_access': "true",
            'language_code': 'eng',
            'ling_resource_type': ['Text']
        }

        rec_diffmeta = self.create_record(metadata2, files1)
        self.assertEquals(checksum, rec_diffmeta['checksum'])

        files2 = []
        files2.extend(files1)
        files2.append(TmpHelper.create_tmp_file("testfile3.txt", "yet another test file"))

        rec_diff = self.create_record(metadata1, files2)
        self.assertNotEquals(checksum, rec_diff['checksum'])


TEST_SUITE = make_test_suite(TestB2ShareChecksums)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
