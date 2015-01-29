# -*- coding: utf-8 -*-
"""Unit Tests for B2share restapi"""

from invenio.base.wrappers import lazy_import
from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase
from cgi import parse_qs
from flask_oauthlib.utils import extract_params

from invenio.modules.oauth2server.provider import oauth2
from invenio.ext.sqlalchemy import db

from invenio.modules.oauth2server.models import Token, Client
from invenio.modules.accounts.models import User

from werkzeug.security import gen_salt
from flask import current_app

import requests, logging, os, json
# only log warnings (building requests)
logging.getLogger("requests").setLevel(logging.WARNING)
# logging.getLogger("requests").setLevel(logging.DEBUG)

class RestApi(object):
    """rest api wrapper class"""

    def __init__(self, url=None, access_token=None):
        self.host = url
        self.url = self.host + "/api"
        self.at = access_token

    def get_params(self):
        params = ""
        if self.at != None:
            params = "?access_token=" + self.at
        return params

    def get_records(self):
        params = self.get_params()
        r = requests.get(self.url + "/records/" + params)
        return r

    def create_deposition(self):
        params = self.get_params()
        r = requests.post(self.url + "/depositions/" + params)
        return r

    def get_by_uri(self, uri):
        params = self.get_params()
        r = requests.get(self.host + uri + params)
        return r

    def upload_deposition_files(self, uri, files):
        params = self.get_params()
        r = requests.post(self.host + uri + "/files" + params, files=files)
        return r

    def get_deposition_files(self, uri):
        params = self.get_params()
        r = requests.get(self.host + uri + "/files" + params)
        return r

    def commit_deposition(self, uri, metadata_json):
        params = self.get_params()
        data = json.dumps(metadata_json)
        headers = {'content-type': 'application/json'}
        r = requests.post(self.host + uri + "/commit" + params, data=data,
                          headers=headers)
        return r


    # def commit_deposition_files(self, uri):
    #     params = get_params()
    #     r = requests.post(self.host + uri + "/commit" + params)
    #     return r

class InitHelper(object):

    @staticmethod
    def init_user_token(test_case):
        # get user
        admin_user = User.query.filter_by(email='b2share@localhost').first()
        if admin_user == None:
            # TODO: create user here!
            admin_user = User(email="b2share@localhost", note="1", nickname="b2share", password="b2share")
            db.session.add(admin_user)
            db.session.commit()
        test_case.assertIsNotNone(admin_user)
        admin_user_id = admin_user.get_id()
        # get token
        token = Token.query.filter_by(user_id=admin_user_id).first()
        if token == None:
            # create client object
            client = Client(name="test_client", user_id=admin_user_id, is_internal=True,
                is_confidential=False)
            test_case.assertIsNotNone(client)
            client.gen_salt()
            db.session.add(client)
            # create login token
            access_token = gen_salt(current_app.config.get('OAUTH2_TOKEN_PERSONAL_SALT_LEN'))
            token = Token(client_id=client.client_id, user_id=admin_user_id,
                access_token=access_token, expires=None, is_personal=True,
                is_internal=True)
            db.session.add(token)
            db.session.commit()
        # verify info
        test_case.assertIsNotNone(token)
        test_case.assertTrue(len(token.access_token) == 60)
        test_case.access_token = token.access_token
        test_case.current_app_url = current_app.config.get('CFG_SITE_URL')

    @staticmethod
    def create_tmp_files(test_case, filename, content):
        path = os.path.dirname(__file__) + "/tmp_files/"
        fo = open(path + filename, "wb")
        fo.write(content)
        fo.close()
        assert os.path.isfile(path + filename)
        return ('files', (filename, open(path + filename, 'rb'), 'text/plain'))

    @staticmethod
    def delete_tmp_files(test_case, filename):
        path = os.path.dirname(__file__) + "/tmp_files/"
        os.remove(path + "/" + filename)
        assert not os.path.isfile(path + filename)


class TestB2depositRestapiConnect(InvenioTestCase):
    """Unit tests for restapi connecting"""

    def setUp(self):
        InitHelper.init_user_token(self)

    def test_connect_with_oauth(self):
        api = RestApi(url=self.current_app_url, access_token=self.access_token)
        r = api.get_records()
        # request deposit list
        self.assertEqual(r.status_code, 200)
        body_json = r.json()
        self.assertTrue(isinstance(body_json,list))
        # print body_json

    def test_connect_with_wrong_oauth(self):
        api = RestApi(url=self.current_app_url, access_token=
                      "kljlkjlksdfj")
        r = api.get_records()
        self.assertEqual(r.status_code, 401)
        body_json = r.json()
        self.assertTrue(isinstance(body_json, dict))
        self.assertTrue("status" in body_json)
        self.assertEqual(body_json['status'], 401)
        self.assertTrue("message" in body_json)
        self.assertEqual(body_json['message'], "Unauthorized")

    def test_connect_with_empty_oauth(self):
        api = RestApi(url=self.current_app_url, access_token="")
        r = api.get_records()
        self.assertEqual(r.status_code, 401)
        body_json = r.json()
        self.assertTrue(isinstance(body_json, dict))
        self.assertTrue("status" in body_json)
        self.assertEqual(body_json['status'], 401)
        self.assertTrue("message" in body_json)
        self.assertEqual(body_json['message'], "Unauthorized")

    def test_connect_without_oauth(self):
        api = RestApi(url=self.current_app_url)
        r = api.get_records()
        self.assertEqual(r.status_code, 401)
        body_json = r.json()
        self.assertTrue(isinstance(body_json, dict))
        self.assertTrue("status" in body_json)
        self.assertEqual(body_json['status'], 401)
        self.assertTrue("message" in body_json)
        self.assertEqual(body_json['message'], "Unauthorized")

    # TODO: add get token handle
    # def test_get_token(self):
    #     self.assertTrue(False)


class TestB2depositRestapiRecord(InvenioTestCase):
    """Unit tests for restapi record"""

    def setUp(self):
        InitHelper.init_user_token(self)

    def test_get_records(self):
        api = RestApi(url=self.current_app_url, access_token=self.access_token)
        r = api.get_records()
        # request deposit list
        self.assertEqual(r.status_code, 200)
        body_json = r.json()
        self.assertTrue(isinstance(body_json,list))
        # TODO: FIXME: self.assertTrue(len(body_json) == 0)

    def test_create_deposition_with_files_and_commit(self):
        api = RestApi(url=self.current_app_url, access_token=self.access_token)
        # create deposit
        record = api.create_deposition()
        # verify response
        self.assertTrue(record.status_code == 201)
        body_json = record.json()
        self.assertTrue(isinstance(body_json, dict))
        self.assertTrue('location' in body_json)
        self.assertTrue(body_json['location'].startswith("/api/deposition/"))
        # get created deposition (via location)
        location = body_json['location']
        record = api.get_by_uri(location)
        # verify response
        self.assertTrue(record.status_code == 200)
        body_json = record.json()
        self.assertTrue(isinstance(body_json, dict))
        self.assertTrue('message' in body_json)
        self.assertTrue(body_json['message'] == "valid deposition resource")
        self.assertTrue('locations' in body_json)
        self.assertTrue(len(body_json['locations']) == 2)
        self.assertTrue(location + "/files" in body_json['locations'])
        self.assertTrue(location + "/commit" in body_json['locations'])
        # upload single file
        files = []
        files.append(InitHelper.create_tmp_files(self, "testfile1", "test file 1"))
        deposit_files = api.upload_deposition_files(location, files)
        # verify response
        self.assertTrue(deposit_files.status_code == 200)
        body_json = deposit_files.json()
        self.assertTrue(isinstance(body_json, dict))
        self.assertTrue('files' in body_json)
        self.assertTrue(len(body_json['files']) == 1)
        self.assertEquals(body_json['files'][0]['name'], "testfile1")
        self.assertTrue('message' in body_json)
        self.assertTrue(body_json['message'] == "File(s) saved")
        # get uploaded deposition (via location)
        deposit_files = api.get_deposition_files(location)
        # verify response
        self.assertTrue(deposit_files.status_code == 200)
        body_json = deposit_files.json()
        self.assertTrue(isinstance(body_json, list))
        file1 = body_json[0]
        self.assertTrue('name' in file1)
        self.assertEquals(file1['name'], "testfile1")
        self.assertTrue('size' in file1)
        self.assertEquals(file1['size'], 11)
        # commit deposition (via location)
        metadata = {
            'domain': "generic",
            'title': 'Test File 1 via RestAPI',
            'description': "Test file 1 via RestAPI description.",
            'open_access': "true"
        }
        deposit_commit = api.commit_deposition(location, metadata)
        # verify response
        self.assertTrue(deposit_commit.status_code == 201)
        body_json = deposit_commit.json()
        self.assertTrue(isinstance(body_json, dict))
        self.assertTrue('message' in body_json)
        self.assertEquals(body_json['message'], "New record submitted for processing")
        self.assertTrue('location' in body_json)
        self.assertTrue(body_json['location'].startswith("/api/record/"))
        location = body_json['location']

        # # get record (via location)
        # record = api.get_by_uri(location)
        # print record
        # print record.json()

        # TODO: download file


    def test_commit_into_invalid_deposit(self):
        pass


    # def test_records_paginate(self):
    #     # TODO: implement!
    #     self.assertTrue(False)

    # def test_read_record_by_id(self):
    #     # TODO: implement!
    #     self.assertTrue(False)

    # def test_read_record_by_domain(self):
    #     # TODO: implement!
    #     self.assertTrue(False)



    # def test_update_record(self):
    #     # TODO: implement!
    #     self.assertTrue(False)

    # def test_delete_record(self):
    #     # TODO: implement!
    #     self.assertTrue(False)

TEST_SUITE = make_test_suite(
                TestB2depositRestapiConnect,
                TestB2depositRestapiRecord
            )

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
