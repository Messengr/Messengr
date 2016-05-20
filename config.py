import os
import tempfile
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    CSRF_ENABLED = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    try:
        SECRET_KEY = os.environ['SECRET_KEY']
    except KeyError:
        SECRET_KEY = os.urandom(64)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test.db"
    SECRET_KEY = 'development-key'

class TestingConfig(Config):
    DEBUG = True
    temp_file = tempfile.mkstemp()
    DB_FD = temp_file[0]
    DATABASE_FILE = temp_file[1]
    SQLALCHEMY_DATABASE_URL = "sqlite:////" + temp_file[1]
    SECRET_KEY = 'testing-key'