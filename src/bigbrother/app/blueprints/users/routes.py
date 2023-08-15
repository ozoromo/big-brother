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
from flask_socketio import emit
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
from app import application, socketio, ws
from app.user import BigBrotherUser
from app.blueprints.users.forms import CameraSignUpForm, SignUpForm
from app.blueprints.users.utils import register_user

# ML libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "FaceRecognition"))
import FaceDetection


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
    ws.DB.deleteUserWithId(user_uuid)
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
    user_uuid = ws.DB.getUser(user)
    if user_uuid:
        ws.BigBrotherUserList.append(BigBrotherUser(user_uuid, user, ws.DB))
        return render_template("validationsignup.html", name=user)

    return render_template("index.html",
                           BigBrotherUserList=ws.BigBrotherUserList)


@users.route("/userpage")
def userpage():
    display_uuid = request.args.get("usr", default=None, type=str)
    display_user = None
    if display_uuid:
        display_user = ws.get_user_by_id(display_uuid)
    return render_template("userpage.html",
                           BigBrotherUserList=ws.BigBrotherUserList,
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

        user_uuid = ws.DB.register_user(user["username"], None)
        image_index = 0
        encodings_saved = False
        for storage in pictures:
            image_index += 1
            # TODO: This should be removable. Ask egain!
            if (storage is None) or (not storage.content_type.startswith("image/")):
                rejectionDict["reason"] = f"Image {image_index} not provided"
                ws.DB.deleteUserWithId(user_uuid)
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

                    ws.DB.update_user_enc(user_uuid, encodings[0])
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
            ws.DB.insertTrainingPicture(
                np.asarray(pic_resized, dtype=np.float64),
                user_uuid
            )

        ws.BigBrotherUserList.append(
            BigBrotherUser(user_uuid, user["username"], ws.DB)
        )

        return render_template("validationsignup.html", name=user["username"])

    return render_template("create.html", form=form)


@users.route("/webcamJS", methods=["GET", "POST"])
def webcamJS():
    return render_template("webcamJS.html", title="Camera")


@users.route("/webcamCreate", methods=["GET", "POST"])
def webcamCreate():
    return render_template("webcamCreate.html", title="Camera")


@users.route("/createcamera", methods=["GET", "POST"])
def createcamera():
    form = CameraSignUpForm()

    ws.createPictures = []
    if form.validate_on_submit():
        flash("Thanks for signing up")

        global user
        user = form.name.data

        # TODO: The signup still needs to get implemented.

        return render_template("webcamCreate.html", title="Camera")
    return render_template("createcamera.html", title="Create an account", form=form)


@socketio.on("disconnect", namespace="/createWithCamera")
def disconnected():
    cookie = request.cookies.get("session_uuid")
    ws.setAuthorizedAbort(cookie, True)
    ws.resetinvalidStreamCount(cookie)
    application.logger.info("Websocket client disconnected")


# TODO: Take a look at this and why it's so similar to the other routes in
# other modules
# TODO: Find out that this does. The emmiting line in createWithCamera.js
# is commented out!
# TODO: What is the input_?

# Retrieving Image from Client javascript side, analyze it and send it back
# Socket source from: https://github.com/dxue2012/python-webcam-flask
# Used for Registration
@socketio.on("input image", namespace="/createWithCamera")
def create_with_image(input_):
    cookie = request.cookies.get("session_uuid")
    ws.setAuthorizedAbort(cookie, False)

    # Figure out how many pics are needed and then close socket
    input_ = input_.split(",")[1]

    image_data = input_  # Do your magical Image processing here!!

    # user is global, use it with cv2_img for authentication
    # OpenCV part decode and encode
    img = imread(io.BytesIO(base64.b64decode(image_data)))
    cutImg = np.asarray(FaceDetection.cut_rectangle(copy.deepcopy(img)))
    cv2_img = FaceDetection.make_rectangle(img)
    cv2.imwrite("reconstructed.jpg", cv2_img)
    retval, buffer = cv2.imencode(".jpg", cv2_img)
    b = base64.b64encode(buffer)
    b = b.decode()
    image_data = "data:image/jpeg;base64," + b

    # TODO: What do those magic number mean?
    if len(ws.createPictures) < 5 and len(cutImg) < len(img) and len(cutImg) > 50:
        ws.createPictures.append(cutImg)
        if len(ws.createPictures) >= 5:
            cookie = request.cookies.get("session_uuid")
            ws.setAuthorizedAbort(cookie, True)
            register_user(user, ws.createPictures)
            emit("redirect", {"url": "/validationsignup"})
        else:
            emit("out-image-event", {"image_data": image_data}, namespace="/createWithCamera")
    else:
        ws.addinvalidStreamCount(cookie)
        if ws.checkinvalidStreamCount(cookie):
            cookie = request.cookies.get("session_uuid")
            ws.setAuthorizedAbort(cookie, True)
            emit("redirect", {"url": "/rejection"})
    emit("out-image-event", {"image_data": image_data}, namespace="/createWithCamera")


@socketio.on("input_image_create", namespace="/createWithCamera")
def queueImage_create(input):
    ws.WEBCAM_IMAGE_QUEUE_CREATE.put(input)


@socketio.on("start_transfer_create", namespace="/createWithCamera")
def webcamCommunication_create():
    emit("ack_transfer", {"foo": "bar"}, namespace="/createWithCamera")
    cookie = request.cookies.get("session_uuid")
    # TODO: Check for infinite loop.
    while (not ws.authorizedFlag) or (not ws.authorizedAbort):
        try:
            create_with_image(ws.WEBCAM_IMAGE_QUEUE_CREATE.get(block=True, timeout=5))
        except queue.Empty:
            print("Webcam Queue is Empty! Breaking!", file=sys.stdout)
            break

    ws.WEBCAM_IMAGE_QUEUE_CREATE = queue.Queue()
    # TODO: Find out what the flags are for they don't seem to do anything.
    # Sometimes they are commented out and sometimes commented in (in the same
    # context)
    ws.authorizedAbort = False
    ws.authorizedFlag = False
    ws.resetinvalidStreamCount(cookie)
