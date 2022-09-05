import os
import cloudinary as Cloud
from dotenv import load_dotenv

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    CLOUD_NAME:os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUD_API_KEY: os.environ.get('CLOUDINARY_API_KEY')
    CLOUD_API_SECRET: os.environ.get('CLOUDINARY_API_SECRET')
    SECRET_KEY = os.environ.get('SECRET_KEY') or ''
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', ''))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    KOTKOT_MAIL_SUBJECT_PREFIX = '[Kotkot]'
    KOTKOT_MAIL_SENDER = 'Kotkot Admin <>'
    KOTKOT_ADMIN = os.environ.get('KOTKOT_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_NAME = os.getenv('LOCAL_DB_NAME')
    DB_SOURCE = os.getenv('LOCAL_DB_SOURCE')
    DB_USERNAME = os.getenv('LOCAL_DB_USERNAME')
    DB_PASSWORD = os.getenv('LOCAL_DB_PASSWORD')
    REMOTE_NAME = os.getenv('REMOTE_NAME')
    REMOTE_SOURCE = os.getenv('REMOTE_SOURCE')
    REMOTE_USERNAME = os.getenv('REMOTE_USERNAME')
    REMOTE_PASSWORD = os.getenv('REMOTE_PASSWORD')
    REMOTE_URI = os.getenv('REMOTE_URI')
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class KotkotConfig(Config):
    DB_NAME = Config.DB_NAME
    DB_SOURCE = Config.DB_SOURCE
    DB_USERNAME = Config.DB_USERNAME
    DB_PASSWORD = Config.DB_PASSWORD
    REMOTE_NAME = Config.REMOTE_NAME
    REMOTE_SOURCE = Config.REMOTE_SOURCE
    REMOTE_USERNAME = Config.REMOTE_USERNAME
    REMOTE_PASSWORD = Config.REMOTE_PASSWORD
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '' + DB_SOURCE + '' + DB_NAME
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + REMOTE_USERNAME + ':' + REMOTE_PASSWORD + '' + REMOTE_SOURCE + '' + REMOTE_NAME
    SQLALCHEMY_DATABASE_URI = Config.REMOTE_URI
    SQLALCHEMY_ECHO = True
    
    KOTKOT_MAIL_SUBJECT_PREFIX = '[Kotkot]'
    KOTKOT_MAIL_SENDER = 'Kotkot Admin <>'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'kotkot' : KotkotConfig,
    'default': KotkotConfig
}
