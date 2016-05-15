import os
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
    SQLALCHEMY_DATABASE_URI = "postgres:////tmp/test.db"
    SECRET_KEY = 'development-key'
