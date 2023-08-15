import sys

from flask_socketio import emit
import numpy as np

from app import ws


def register_user(username, pictures):
    user_uuid = None

    if not ws.DB.getUser(username):
        user_uuid = ws.DB.register_user(username)
        for pic in pictures:
            ws.DB.insertTrainingPicture(
                np.asarray(pic, dtype=np.float64), user_uuid
            )
    else:
        # TODO: Put some message on the web page instead of terminal
        # this makes it easier for the user to see what has been done wrong
        print("'{}' already exists!".format(username), file=sys.stdout)
        emit("redirect", {"url": "/rejection"})
    emit("redirect", {"url": "/validationsignup"})
