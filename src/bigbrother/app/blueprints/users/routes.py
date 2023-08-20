# Standard libraries
import os
import io
import sys
import base64
import copy
import queue
import uuid


# Third party
# Flask
from flask import render_template, request, flash, Blueprint
from flask_login import login_required, logout_user

# Math
import numpy as np
import face_recognition

# Dealing with images
from imageio import imread
from PIL import Image
import cv2
import cv2.misc


# Own libraries
# GUI and frontend libraries
from app import application, picture_database, user_manager
from app.user import BigBrotherUser
from app.blueprints.users.forms import CameraSignUpForm, SignUpForm
from app.blueprints.users.utils import register_user


users = Blueprint("users", __name__)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("index.html", title="Home")


@users.route("/deleteuser")
@login_required
def deleteuser():
    logout_user()
    user_uuid = uuid.UUID(request.args.get("usr", default=1, type=str))
    picture_database.deleteUserWithId(user_uuid)
    return render_template("index.html", title="Home")


@users.route("/rejection")
def rejection():
    rejectionDict = {
        "reason": "Unknown",
        "redirect": "create",
        "redirectPretty": "Back to registration",
    }
    return render_template("rejection.html", rejectionDict=rejectionDict,
                           title="Reject")


# TODO: What is this used for?
@users.route("/validationsignup")
def validationsignup():
    user_uuid = picture_database.getUser(user)
    if user_uuid:
        picture_database.BigBrotherUserList.append(
            BigBrotherUser(user_uuid, user, picture_database)
       )
        return render_template("validationsignup.html", name=user)

    return render_template("index.html",
                           BigBrotherUserList=user_manager.BigBrotherUserList)


@users.route("/userpage")
def userpage():
    display_uuid = request.args.get("usr", default=None, type=str)
    display_user = None
    if display_uuid:
        display_user = user_manager.get_user_by_id(display_uuid)
    return render_template("userpage.html",
                           BigBrotherUserList=user_manager.BigBrotherUserList,
                           displayUser=display_user)


@users.route("/create", methods=["GET", "POST"])
def create():
    form = SignUpForm()

    if form.validate_on_submit():
        rejectionDict = {
            "reason": "Unknown",
            "redirect": "create",
            "redirectPretty": "Back to registration",
        }
        user = {
            "username": form.name.data,
            "pic1": form.pic1.data,
            "pic2": form.pic2.data,
            "pic3": form.pic3.data
        }
        user_uuid = None

        pictures = [
            user["pic1"],
            user["pic2"],
            user["pic3"],
        ]

        user_uuid = picture_database.register_user(user["username"], None)
        image_index = 0
        encodings_saved = False
        for storage in pictures:
            image_index += 1
            # TODO: This should be removable. Ask egain!
            if (storage is None) or (not storage.content_type.startswith("image/")):
                rejectionDict["reason"] = f"Image {image_index} not provided"
                picture_database.deleteUserWithId(user_uuid)
                return render_template("rejection.html",
                                       rejectionDict=rejectionDict,
                                       title="Reject", form=form)

            im_bytes = storage.stream.read()
            image = Image.open(io.BytesIO(im_bytes))
            array = np.array(image)
            if not encodings_saved:
                try:
                    # TODO: Check for errors later
                    img = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
                    encodings = face_recognition.face_encodings(img)

                    picture_database.update_user_enc(user_uuid, encodings[0])
                    encodings_saved = True
                except:
                    # TODO: What exception does this cover? Specify the
                    # exception and handle it properly!
                    print("Error while calculating encodings")
            image.close()
            storage.close()

            # TODO: Avoid magic numbers: (98, 116)
            pic_resized = cv2.resize(
                array,
                dsize=(98, 116),
                interpolation=cv2.INTER_CUBIC
            )
            picture_database.insertTrainingPicture(
                np.asarray(pic_resized, dtype=np.float64),
                user_uuid
            )

        user_manager.BigBrotherUserList.append(
            BigBrotherUser(user_uuid, user["username"], picture_database)
        )

        return render_template("validationsignup.html", name=user["username"])

    return render_template("create.html", form=form)


@users.route("/webcamJS", methods=["GET", "POST"])
def webcamJS():
    return render_template("webcamJS.html", title="Camera")
