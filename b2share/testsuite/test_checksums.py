# -*- coding: utf-8 -*-
"""Tests for checksumming b2share deposits"""

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase

import os, os.path, time, hashlib

from .helpers import B2ShareAPITestCase, TemporaryDirectory, create_file

from flask import current_app

class TestB2ShareChecksums(B2ShareAPITestCase):
    """Unit tests for stability of checksums, using the REST API"""

    def setUp(self):
        super(TestB2ShareChecksums, self).setUp()
        self.create_and_login_user()

    def tearDown(self):
        self.remove_user()

    def create_record(self, metadata, files):
        """create a deposition, add some files and commit the record."""
        current_app.config.update(PRESERVE_CONTEXT_ON_EXCEPTION = False)

        # create deposition object
        create_json = self.create_deposition(safe=True).json
        deposit_id = create_json['deposit_id']

        # upload files
        for f in files:
            self.upload_deposition_file(deposit_id, f, safe=True)

        # commit deposition
        commit_json = self.commit_deposition(deposit_id, metadata,
                                             safe=True).json
        record_id = commit_json['record_id']

        # get record
        request_get = self.get_record(record_id)
        if request_get.status_code != 200:
            time.sleep(10)
            request_get = self.get_record(record_id)
            if request_get.status_code != 200:
                self.fail('timeout while in the rest deposition')

        record_json = self.get_record(record_id, safe=True).json

        posted_files = set([os.path.basename(f) for f in files])
        deposited_files = set([f['name'] for f in record_json['files']])
        self.assertEquals(posted_files, deposited_files)
        return record_json

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

    def create_file(self, path, content):
        """
        Create a new file or truncate the existing one and print the given
        content in it.

        :param str path: path of the file to create.
        :param str content: content which will be written in the file.
        """
        with open(path, 'w') as file_desc:
            file_desc.write(content)
        return path

    def test_deposit_checksums(self):
        metadata1 = {
            'domain': "generic",
            'title': 'Checksum test',
            'description': "B2SHARE depositing checksum test via RestAPI",
            'open_access': "true"
        }

        # create a temporary directory
        with TemporaryDirectory() as tmp_dir:
            files1 = []
            files1.append(create_file(tmp_dir, "testfile1.txt", "test file 1"))
            files1.append(create_file(tmp_dir, "testfile2.txt", "test ünicödé-ø-å file"))

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
            files2.append(create_file(tmp_dir, "testfile3.txt", "yet another test file"))

            rec_diff = self.create_record(metadata1, files2)
            self.assertNotEquals(checksum, rec_diff['checksum'])


TEST_SUITE = make_test_suite(TestB2ShareChecksums)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
