import os

base_dir = os.path.abspath(os.path.dirname(__file__))
sqlite_local_base = 'sqlite:///../'
database_name = 'api.db'


class BaseConfig:
    """
    Base application configuration.
    """

    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_strong_key')
    BCRYPT_HASH_PREFIX = 14
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTH_TOKEN_EXPIRY_DAYS = 30
    AUTH_TOKEN_EXPIRY_SECONDS = 600


class DevelopmentConfig(BaseConfig):
    """
    Development application configuration.
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', sqlite_local_base + database_name)
    BCRYPT_HASH_PREFIX = 4
    AUTH_TOKEN_EXPIRY_DAYS = 1
    AUTH_TOKEN_EXPIRY_SECONDS = 30000


class TestingConfig(BaseConfig):
    """
    Testing application configuration.
    """

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL_TEST', sqlite_local_base + database_name + "_test")
    BCRYPT_HASH_PREFIX = 4
    AUTH_TOKEN_EXPIRY_DAYS = 0
    AUTH_TOKEN_EXPIRY_SECONDS = 3
    AUTH_TOKEN_EXPIRATION_TIME_DURING_TESTS = 5


class ProductionConfig(BaseConfig):
    """
    Production application configuration.
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', sqlite_local_base + database_name)
    BCRYPT_HASH_PREFIX = 13
    AUTH_TOKEN_EXPIRY_DAYS = 30
    AUTH_TOKEN_EXPIRY_SECONDS = 600
