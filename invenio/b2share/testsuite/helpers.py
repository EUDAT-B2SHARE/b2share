# -*- coding: utf-8 -*-
"""Tests for checksumming b2share deposits"""

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
        if not uri.startswith("/api"):
            uri = "/api%s" % uri
        params = self.get_params()
        r = requests.get(self.host + uri + params)
        return r

    # Deposition
    def upload_deposition_file(self, uri, file):
        params = self.get_params()
        r = requests.post(self.host + uri + "/files" + params,
                          files={'file':file})
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

class TmpHelper(object):
    @staticmethod
    def tmp_folder():
        return os.path.join(os.path.dirname(__file__), "tmp_files")

    @staticmethod
    def create_tmp_file(filename, content):
        folder = TmpHelper.tmp_folder()
        try:
            os.mkdir(folder)
        except Exception:
            pass
        path = os.path.join(folder, filename)
        fo = open(path, "wb")
        fo.write(content)
        fo.close()
        assert os.path.isfile(path)
        return path

    @staticmethod
    def delete_tmp_files(filename):
        path = os.path.join(TmpHelper.tmp_folder(), filename)
        os.remove(path)
        assert not os.path.isfile(path)

    @staticmethod
    def delete_all_tmp_files():
        import shutil
        shutil.rmtree(TmpHelper.tmp_folder())
