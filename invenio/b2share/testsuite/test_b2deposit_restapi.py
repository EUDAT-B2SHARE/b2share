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

import requests, logging
logging.getLogger("requests").setLevel(logging.WARNING)


class RestApi(object):
    """rest api wrapper class"""

    def __init__(self, url=None, access_token=None):
        self.url = url + "/api"
        self.at = access_token

    def get_deposits(self):
        try:
            r = requests.get(self.url + "/depositions/?access_token=" + self.at)
            return r
        except:
            print "server not found at: `" + self.url + "`"
        return None

class InitHelper(object):

    @staticmethod
    def init_user_token(test_case):
        # get user
        admin_user = User.query.filter_by(email='admin@localhost').first()
        if admin_user == None:
            # TODO: create user here!
            admin_user = User(email="admin@localhost", note="1", nickname="admin", password="admin")
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
    def init_records(test_case):
        pass


class TestB2depositRestapiConnect(InvenioTestCase):
    """Unit tests for restapi connecting"""

    def setUp(self):
        InitHelper.init_user_token(self)

    def test_connect_with_oauth(self):
        api = RestApi(url=self.current_app_url, access_token=self.access_token)
        r = api.get_deposits()
        # request deposit list
        self.assertEqual(r.status_code, 200)
        body_json = r.json()
        self.assertTrue(isinstance(body_json,list))
        print body_json

    # TODO: add get token handle
    # def test_get_token(self):
    #     self.assertTrue(False)


class TestB2depositRestapiRecord(InvenioTestCase):
    """Unit tests for restapi record"""

    def setUp(self):
        InitHelper.init_user_token(self)
        InitHelper.init_records(self)

    def test_records(self):
        api = RestApi(url=self.current_app_url, access_token=self.access_token)
        r = api.get_deposits()
        # request deposit list
        self.assertEqual(r.status_code, 200)
        body_json = r.json()
        self.assertTrue(isinstance(body_json,list))



    def test_records_paginate(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_read_record_by_id(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_read_record_by_domain(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_create_record(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_update_record(self):
        # TODO: implement!
        self.assertTrue(False)

    def test_delete_record(self):
        # TODO: implement!
        self.assertTrue(False)

TEST_SUITE = make_test_suite(
                TestB2depositRestapiConnect,
                TestB2depositRestapiRecord
            )

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
