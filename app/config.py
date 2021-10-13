import os
from flask_login import LoginManager
from flask_babel import Babel
from sqlalchemy.ext.declarative import declarative_base

login = LoginManager()
login.login_view = 'users.login'
babel = Babel()
Base = declarative_base()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@localhost/{}'\
        .format(os.environ.get('DB_USER'),
                os.environ.get('DB_PASSWORD'),
                os.environ.get('DB_NAME'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
