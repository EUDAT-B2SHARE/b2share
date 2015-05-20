# -*- coding: utf-8 -*-
"""Tests for checksumming b2share deposits"""

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase
import os, os.path, time, hashlib
from .helpers import InitHelper, TmpHelper, RestApi


class TestB2ShareChecksums(InvenioTestCase):
    """Unit tests for stability of checksums, using the REST API"""

    def setUp(self):
        InitHelper.init_user_token(self)

    def tearDown(self):
        TmpHelper.delete_all_tmp_files()

    def create_record(self, api, metadata, files):
        # create deposition object
        request_create = api.create_deposition()
        self.assertTrue(request_create.status_code == 201)
        location = request_create.json()['location']

        # upload files
        for f in files:
            postfile = (os.path.basename(f), open(f, 'rb'), 'text/plain')
            request_upload = api.upload_deposition_file(location, postfile)
            self.assertTrue(request_upload.status_code == 200)

        # commit deposition
        request_commit = api.commit_deposition(location, metadata)
        self.assertTrue(request_commit.status_code == 201)
        location = request_commit.json()['location']

        # get record (via location) and wait for it to be made
        request_get = None
        for i in range(0, 10):
            time.sleep(5)
            request_get = api.get_by_uri(location)
            if request_get.status_code == 200:
                break
            self.assertEquals(request_get.status_code, 404)
        else:
            self.fail('timeout while in the rest deposition')

        deposit_json = request_get.json()['Deposit']
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
        api = RestApi(url=self.current_app_url, access_token=self.access_token)

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

        rec = self.create_record(api, metadata1, files1)
        self.assertEquals(checksum, rec['checksum'])

        rec_identical = self.create_record(api, metadata1, files1)
        self.assertEquals(checksum, rec_identical['checksum'])

        reversed_files = list(reversed(files1))
        rec_reversed = self.create_record(api, metadata1, reversed_files)
        self.assertEquals(checksum, rec_reversed['checksum'])

        metadata2 = {
            'domain': "Linguistics",
            'title': 'Checksum test 2',
            'description': "B2SHARE depositing checksum test via RestAPI",
            'open_access': "true",
            'language_code': 'eng',
            'ling_resource_type': ['Text']
        }

        rec_diffmeta = self.create_record(api, metadata2, files1)
        self.assertEquals(checksum, rec_diffmeta['checksum'])

        files2 = []
        files2.extend(files1)
        files2.append(TmpHelper.create_tmp_file("testfile3.txt", "yet another test file"))

        rec_diff = self.create_record(api, metadata1, files2)
        self.assertNotEquals(checksum, rec_diff['checksum'])


TEST_SUITE = make_test_suite(TestB2ShareChecksums)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
