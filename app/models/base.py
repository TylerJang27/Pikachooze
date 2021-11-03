from flask_login import LoginManager
from flask_babel import Babel
from sqlalchemy.ext.declarative import declarative_base

login = LoginManager()
login.login_view = 'users.login'
babel = Babel()
Base = declarative_base()