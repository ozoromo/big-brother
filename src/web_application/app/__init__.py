import os
import sys
from sys import stdout
import logging

from flask import Flask
import flask_login
from flask_socketio import SocketIO
from engineio.payload import Payload

from app.utils import formatSeconds
from config import Config

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database_management.picture_database import PictureDatabase

application = Flask(__name__)
application.config.from_object(Config)

application.logger.addHandler(logging.StreamHandler(stdout))
application.config["SECRET_KEY"] = "secret!"
application.config["DEBUG"] = True
application.config["UPLOAD_FOLDER"] = application.instance_path
application.config["LOCALDEBUG"] = (os.environ.get("LOCALDEBUG") == "True")
application.config["TMP_VIDEO_FOLDER"] = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), 'eduVid', 'tmp')
application.jinja_env.globals.update(formatSeconds=formatSeconds)

login_manager = flask_login.LoginManager()
login_manager.init_app(application)

picture_database = PictureDatabase()

Payload.max_decode_packets = 1000
socketio = SocketIO(application)


# NOTE: The following code is meant to be at the bottom in order to avoid cyclic dependencies
from app.user_manager import UserManager
user_manager = UserManager()


from app.blueprints.main.routes import main
from app.blueprints.logic.routes import logic
from app.blueprints.users.routes import users
from app.blueprints.login.routes import blueprint_login

application.register_blueprint(main)
application.register_blueprint(logic)
application.register_blueprint(users)
application.register_blueprint(blueprint_login)
