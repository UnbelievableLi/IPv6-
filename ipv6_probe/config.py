import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'ipv6probekey'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    NUMBER_PER_PAGE = 50
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://probe:probingipv6@localhost/ipv6probe'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


config = {'default': DevelopmentConfig}
