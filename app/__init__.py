from flask import Flask
from app.config import Config
from app.db import DB
from app.models.base import login, babel
import subprocess
from os import getcwd, path


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    create_path = path.join(getcwd(), app.config['SQL_CREATE_PATH'])
    process = subprocess.Popen(create_path, shell=True, stdout=subprocess.PIPE)
    process.wait()
    process.kill()

    app.db = DB(app)

    load_path = path.join(getcwd(), app.config['SQL_LOAD_PATH'])
    subprocess.call([load_path])

    login.init_app(app)
    babel.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    return app
