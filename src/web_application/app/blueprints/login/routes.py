# Standard libraries
import os
import io
import sys
import base64
import copy
import queue
import uuid
import urllib


# Third party
# Flask
from flask import render_template, request, flash, Blueprint
import flask_login

import werkzeug

# Math
import numpy as np

# Dealing with images
from imageio import imread
from PIL import Image
import cv2
import cv2.misc


# Own libraries
# GUI and frontend libraries
from app import login_manager, user_manager, picture_database
from app.user import BigBrotherUser
from app.blueprints.login.forms import LoginForm, CameraLoginForm
from app.blueprints.login.utils import authenticate_picture

# Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "face_recog"))
import FaceDetection
import face_recognition_lib.FaceReco_class as LogikFaceRec


blueprint_login = Blueprint("blueprint_login", __name__)


@login_manager.user_loader
def load_user(user_id):
    loaded_user = user_manager.get_user_by_id(user_id)
    loaded_user.sync()
    return loaded_user


def convert_picture_stream_to_numpy_array(pic: werkzeug.datastructures.FileStorage):
    """
    Converts picture to numpy array.

    The pictures that come from the forms are of type werkzeug.datastructures.
    FileStorage. This function converts the pictures from the forms into a
    numpy image.

    """
    im_bytes = pic.stream.read()
    image = Image.open(io.BytesIO(im_bytes))
    np_image = np.array(image)
    image.close()
    pic.close()
    return np_image


# TODO: Restructure to correct the abstraction levels.
@blueprint_login.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        flash("Thanks for logging in")

        user_uuid = picture_database.get_user(form.name.data)
        bb_user = user_manager.get_user_by_id(user_uuid)
        login_attempt_time = picture_database.login_user(user_uuid)

        np_picture = convert_picture_stream_to_numpy_array(form.pic.data)
        if authenticate_picture(user_uuid, np_picture):
            pic_uuid = picture_database.insert_picture(
                np_picture, user_uuid
            )
            picture_database.update_login(
                user_uuid, login_attempt_time, pic_uuid
            )
            flask_login.login_user(bb_user)
            return render_template("validationauthenticated.html")
        else:
            return render_template(
                "rejection.html",
                rejectionDict={
                    "reason": "Unknown",
                    "redirect": "login",
                    "redirectPretty": "Back to login",
                },
                title="Login",
                form=form
            )
    return render_template("login.html", title="Login", form=form)


@blueprint_login.route("/logincamera", methods=["GET", "POST"])
def logincamera():
    form = CameraLoginForm()

    if form.validate_on_submit():
        flash("Thanks for logging in")

        user_uuid = picture_database.get_user(form.name.data)
        bb_user = user_manager.get_user_by_id(user_uuid),
        login_attempt_time = picture_database.login_user(user_uuid)

        data = {
            "username": form.name.data
        }

        # authentication and user login is done with javascript and the 
        # "/verifypicture" route
        return render_template("webcamJS.html", title="Camera", data=data)

    return render_template("logincamera.html", title="Login with Camera", form=form)


@blueprint_login.route("/verifypicture", methods=["GET", "POST"])
def verifyPicture():
    if request.method == "GET":
        if "username" not in request.args:
            rejectionDict = {
                "reason": "Unknown",
                "redirect": "/",
                "redirectPretty": "Nothing to verify",
            }
            return render_template("rejection.html", rejectionDict=rejectionDict)

        username = request.args.get("username")
        user_data = {
            "name": username,
            "username": username
        }
        return render_template("validationauthenticated.html", user=user_data)
    elif request.method == "POST":
        data = request.get_json()
        if ("username" not in data) or ("image" not in data):
            return {"redirect": "/rejection"}

        username = data.get("username")

        # decode image
        response = urllib.request.urlopen(data.get("image"))
        buffer = io.BytesIO()
        buffer.write(response.file.read())
        pil_img = Image.open(io.BytesIO(buffer.getvalue()))
        buffer.close()
        camera_img = np.asarray(pil_img)

        # Verify user
        user_uuid = picture_database.get_user(username)
        if user_uuid:
            user_enc = picture_database.get_user_enc(user_uuid)

            if user_enc is None or len(user_enc) == 0:
                return {"redirect": "/rejection"}

            bb_user = user_manager.get_user_by_id(user_uuid)
            login_attempt_time = picture_database.login_user(user_uuid)

            logik = LogikFaceRec.FaceReco()
            (results, dists) = logik.photo_to_photo(user_enc, camera_img)
            result = results[0]
            if result:
                pic_uuid = picture_database.insert_picture(
                    camera_img, user_uuid
                )
                picture_database.update_login(
                    user_uuid, login_attempt_time, pic_uuid
                )
                flask_login.login_user(bb_user)
                user_data = {"username": username}
                return {"redirect": "/verifypicture", "data": user_data}
            else:
                return {"redirect": "/rejection"}
        else:
            return {"redirect": "/rejection"}
    return {"redirect": "/rejection"}
