import sys

from flask_socketio import emit
import numpy as np

from app import picture_database


def register_user(username, pictures):
    user_uuid = None

    if not picture_database.get_user(username):
        user_uuid = picture_database.register_user(username)
        for pic in pictures:
            picture_database.insert_picture(
                np.asarray(pic, dtype=np.float64), user_uuid
            )
    else:
        print("'{}' already exists!".format(username), file=sys.stdout)
        emit("redirect", {"url": "/rejection"})
    emit("redirect", {"url": "/validationsignup"})
