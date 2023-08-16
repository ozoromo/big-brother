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
from app import socketio, login_manager, ws
from app.user import BigBrotherUser
from app.blueprints.login.forms import LoginForm, CameraLoginForm

# Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "FaceRecognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Logik"))
import FaceDetection
import Face_Recognition.FaceReco_class as LogikFaceRec


blueprint_login = Blueprint("blueprint_login", __name__)


@login_manager.user_loader
def load_user(user_id):
    loaded_user = ws.get_user_by_id(user_id)
    loaded_user.sync()
    return loaded_user


@blueprint_login.route("/loginstep")
def loginstep():
    # TODO: Why do we have a global user. What is this route for?
    flask_login.login_user(user["bbUser"])
    return render_template("validationauthenticated.html")


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

        user_uuid = ws.DB.getUser(form.name.data)
        bb_user = ws.get_user_by_id(user_uuid)
        login_attempt_time = ws.DB.login_user(user_uuid)

        user = {
            "username": form.name.data,
            "uuid": user_uuid,
        }
        np_image = convert_picture_stream_to_numpy_array(form.pic.data)
        cookie = request.cookies.get("session_uuid")
        result = ws.authenticatePicture(user, np_image, cookie)
        if result:
            # TODO: The inserted picture has to be somehow documented
            ws.DB.update_login(user_uuid, login_attempt_time, result)
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


@socketio.on("start_transfer_login", namespace="/webcamJS")
def webcamCommunication():
    cookie = request.cookies.get("session_uuid")
    ws.emptyQueue(cookie)

    emit("ack_transfer", {"foo": "bar"}, namespace="/webcamJS")

    ws.resetinvalidStreamCount(cookie)
    while not ws.getAuthorizedFlag(cookie) or not ws.getAuthorizedAbort(cookie):
        try:
            test_message(
                ws.getQueue(cookie).get(block=True, timeout=15)
            )
        except queue.Empty:
            print("Webcam Queue is Empty! Breaking!", file=sys.stdout)
            break

    ws.emptyQueue(cookie)

    ws.setAuthorizedFlag(cookie, False)
    ws.setAuthorizedAbort(cookie, False)


# Retrieving Image from Client javascript side, analyze it and send it back
# Socket source from: https://github.com/dxue2012/python-webcam-flask
# @socketio.on("input image", namespace="/webcamJS")
def test_message(input_):
    # TODO: Write down what exactly the message tests
    cookie = request.cookies.get("session_uuid")
    ws.setAuthorizedAbort(cookie, False)

    if ws.checkinvalidStreamCount(cookie):
        ws.resetinvalidStreamCount(cookie)
        ws.setAuthorizedAbort(cookie, True)
        # TODO: Why is anything emmited if the socketio-decorator is turned off?
        emit("redirect", {"url": "/rejection"})

    # CAUTION: test_message is called multiple times from the client
    # (for every image). Figure out how many pics are needed and then
    # close socket
    input_ = input_.split(",")[1]
    image_data = input_  # Do your magical Image processing here!!

    # OpenCV part decode and encode
    img = None
    try:
        img = imread(io.BytesIO(base64.b64decode(image_data)))
    except ValueError:
        emit("ready", {"image_data": "bar"}, namespace="/webcamJS")
        return

    cutImg = FaceDetection.cut_rectangle(copy.deepcopy(img))
    cv2_img = FaceDetection.make_rectangle(img)

    # TODO: What does this comment mean?
    # TODO: Authentication with cv2_img and users
    cv2.imwrite("reconstructed.jpg", cv2_img)
    retval, buffer = cv2.imencode(".jpg", cv2_img)
    b = base64.b64encode(buffer)
    b = b.decode()
    image_data = "data:image/jpeg;base64," + b

    user["isWorking"] = False

    cookie = request.cookies.get("session_uuid")
    # TODO: Eliminate magic numbers
    if len(cutImg) < len(img) and len(cutImg) > 50:
        res = ws.authenticatePicture(user, np.asarray(cutImg), cookie)
        if res:
            cookie = request.cookies.get("session_uuid")
            ws.setAuthorizedAbort(cookie, True)

            ws.DB.update_login(
                user["uuid"],
                user["login_attempt_time"],
                res
            )
            ws.DB.commit()

            emit("redirect", {"url": "/loginstep"})
            return
        else:
            ws.addinvalidStreamCount(cookie)
    else:
        ws.addinvalidStreamCount(cookie)
        if ws.checkinvalidStreamCount(cookie):
            cookie = request.cookies.get("session_uuid")
            ws.setAuthorizedAbort(cookie, True)
            emit("redirect", {"url": "/rejection"})

    emit("next_image", {"image_data": image_data}, namespace="/webcamJS")


@blueprint_login.route("/logincamera", methods=["GET", "POST"])
def logincamera():
    form = CameraLoginForm()

    if form.validate_on_submit():
        flash("Thanks for logging in")

        user_uuid = ws.DB.getUser(form.name.data)
        bb_user = ws.get_user_by_id(user_uuid),
        login_attempt_time = ws.DB.login_user(user_uuid)

        global user
        user = {
            "username": form.name.data,
            "isWorking": False,
            "uuid": user_uuid,
            "bbUser": bb_user,
            "login_attempt_time": login_attempt_time
        }
        data = {
            "username": form.name.data
        }

        # authentication and user login

        return render_template("webcamJS.html", title="Camera", data=data)

    return render_template("logincamera.html", title="Login with Camera", form=form)


# TODO: We don't need this!
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
    if request.method == "POST":
        data = request.get_json()
        if ("username" not in data) or ("image" not in data):
            return {"redirect": "/rejection"}

        username = data.get("username")
        img_url = data.get("image").split(",")

        # data url is split into "image type" and "actual data"
        if len(img_url) < 2:
            return {"redirect": "/rejection"}

        # decode image
        img_data = img_url[1]
        buffer = np.frombuffer(base64.b64decode(img_data), dtype=np.uint8)
        camera_img = cv2.imdecode(buffer, cv2.COLOR_BGR2RGB)

        # Verify user
        user_uuid = ws.DB.getUser(username)
        if user_uuid:
            user_enc = ws.DB.get_user_enc(user_uuid)
            print("User Enc: ", user_enc)

            if user_enc is None or len(user_enc) == 0:
                return {"redirect": "/rejection"}

            logik = LogikFaceRec.FaceReco()
            (results, dists) = logik.photo_to_photo(user_enc, camera_img)

            result = results[0]
            if not result:
                return {"redirect": "/rejection"}
            else:
                thisUser = BigBrotherUser(user_uuid, user["username"], ws.DB)
                flask_login.login_user(thisUser)
                user_data = {"username": username}
                return {"redirect": "/verifypicture", "data": user_data}
        else:
            return {"redirect": "/rejection"}
    return {"redirect": "/rejection"}
