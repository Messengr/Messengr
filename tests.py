import os

os.environ["DATABASE_URL"] = "sqlite:////tmp/test.db"
os.environ["APP_SETTINGS"] = "config.TestingConfig"

import app as SecureMessenger
import unittest

import models

user_alice = {
    'username' : 'alice',
    'password' : 'testpass1234',
    'public_key' : '3zaXNLdZvashITmql64jBotAiusoX4iaFnHv4ubxh+nV5UhtvMac1rKRmM5loAeIlDB7n9ZlMNJPl298/Hd43A==',
    'secret_key' : 'IDhMGp6hRzWH6xh/+uIn7RVD1ye71ZvkuJPSK8IcU74='
}

user_bob = {
    'username' : 'bob',
    'password' : 'testpass1234',
    'public_key' : '0XOaiEAOzkB7eZfIkaAKlrhh0vE6IMV9G8XtBn72ZIjGEDfxiJlHm0CRbonjYKrHEL6jUT3WVmqpdvWNSvrsKg==',
    'secret_key' : '09RGnoJcKJH3+ILWzv/MKatoOdLQZnJNPRDafSCOLlM='
}

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        SecureMessenger.app.config['TESTING'] = True
        self.app = SecureMessenger.app.test_client()

    def tearDown(self):
        os.close(SecureMessenger.app.config['DB_FD'])
        os.unlink(SecureMessenger.app.config['DATABASE_FILE'])
        
    def create_account(self, username, password, public_key):
        return self.app.post('/user/create', data=dict(
            username=username,
            password=password,
            public_key=public_key
        ), follow_redirects=True)
        
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)
    
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

class LoginTestCase(BaseTestCase):
    def test_login_logout(self):
        ## Test Unauthenticated
        rv = self.login('test', 'test')
        self.assertIn("Error: Invalid username and/or password", rv.data)
        self.assertEqual(rv.status_code, 200)
        
        ## Test create account and authenticated login
        rv = self.create_account(user_alice["username"], user_alice["password"], user_alice["public_key"])
        self.assertIn(user_alice["username"], rv.data)
        self.assertEqual(rv.status_code, 200)
        
        rv = self.login(user_alice["username"], user_alice["password"])
        self.assertIn(user_alice["username"], rv.data)
        self.assertEqual(rv.status_code, 200)
        
        rv = self.logout()
        self.assertIn("Login", rv.data)
        self.assertEqual(rv.status_code, 200)
        
#class ChatTestCase(BaseTestCase):
#    def test_chat(self):
#        ## Test create account and authenticated login
#        rv = self.create_account(user_alice["username"], user_alice["password"], user_alice["public_key"])
#        self.assertIn(user_alice["username"], rv.data)
#        self.assertEqual(rv.status_code, 200)
    
if __name__ == '__main__':
    unittest.main()