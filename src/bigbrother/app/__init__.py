import os
import logging
from sys import stdout

from flask import Flask
import flask_login
from flask_socketio import SocketIO
from engineio.payload import Payload

from app.websiteSystem import websiteSystem
from app.utils import formatSeconds
from config import Config


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

ws = websiteSystem()

Payload.max_decode_packets = 1000
socketio = SocketIO(application)


# This has to be at the bottom in order to avoid cyclic dependencies
from app.blueprints.main.routes import main
from app.blueprints.logic.routes import logic
from app.blueprints.users.routes import users
from app.blueprints.login.routes import blueprint_login

application.register_blueprint(main)
application.register_blueprint(logic)
application.register_blueprint(users)
application.register_blueprint(blueprint_login)
