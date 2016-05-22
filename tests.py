import os

os.environ["DATABASE_URL"] = "testdb"
os.environ["APP_SETTINGS"] = "config.DevelopmentConfig"

import app as SecureMessenger
import unittest
import tempfile
import json

import models

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, SecureMessenger.app.config['DATABASE'] = tempfile.mkstemp()
        SecureMessenger.app.config['TESTING'] = True
        self.app = SecureMessenger.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(SecureMessenger.app.config['DATABASE'])
        
    def create_account(self, username, password, public_key, user_data):
        return self.app.post('/user/create', data=dict(
            username=username,
            password=password,
            public_key=public_key,
            user_data=user_data)
        )
        
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password)
        )
    
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

class LoginTestCase(BaseTestCase):
    def test_login_unauthenticated(self):
        rv = self.login('test', 'test')
        self.assertIn("Invalid username and/or password", json.loads(rv.data)['error'])
        self.assertEqual(rv.status_code, 200)

        
if __name__ == '__main__':
    unittest.main()