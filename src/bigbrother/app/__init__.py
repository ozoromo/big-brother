
import os
import logging
from sys import stdout

from flask import Flask
from flask_socketio import SocketIO
import flask_login

from app.websiteSystem import websiteSystem
from config import Config


def formatSeconds(seconds):
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return 'Invalid input'

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = int(seconds % 60)

    formatted_time_parts = []

    if hours > 0:
        formatted_time_parts.append(f"{hours}h")

    if minutes > 0:
        formatted_time_parts.append(f"{minutes}m")

    if remaining_seconds > 0:
        formatted_time_parts.append(f"{remaining_seconds}s")

    return "".join(formatted_time_parts)


print("Starting BigBrother")

application = Flask(__name__)
application.config.from_object(Config)

application.logger.addHandler(logging.StreamHandler(stdout))
application.config['SECRET_KEY'] = 'secret!'
application.config['DEBUG'] = True
application.config['UPLOAD_FOLDER'] = application.instance_path
application.config['LOCALDEBUG'] = None
# TODO: Review implementation
application.config['TMP_VIDEO_FOLDER'] = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')), 'eduVid', 'tmp')
application.jinja_env.globals.update(formatSeconds=formatSeconds)

login_manager = flask_login.LoginManager()
login_manager.init_app(application)

ws = websiteSystem()

if os.environ.get('LOCALDEBUG') == "True":
    application.config['LOCALDEBUG'] = True
else:
    application.config['LOCALDEBUG'] = False
socketio = SocketIO(application)

# This has to be at the bottom in order to avoid cyclic dependencies
from app.main.routes import main
from app.logic.routes import logic
from app.users.routes import users
from app.login.routes import blueprint_login

application.register_blueprint(main)
application.register_blueprint(logic)
application.register_blueprint(users)
application.register_blueprint(blueprint_login)
