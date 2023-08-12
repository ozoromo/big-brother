# Standard libraries
import os
import io
import sys
import base64
import copy
import queue


# Third party
# Flask
from flask import render_template, request, flash, Blueprint
from flask_socketio import emit
import flask_login

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
from app.users.forms import SignInForm, CameraForm, SignUpForm

# ML libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "FaceRecognition"))
import FaceDetection


users = Blueprint("users", __name__)


@users.route("/logout")
@flask_login.login_required
def logout():
    form = SignInForm(request.form)
    flask_login.logout_user()
    return render_template("index.html", title="Home", form=form)


@users.route("/deleteuser")
@flask_login.login_required
def deleteuser():
    form = SignInForm(request.form)
    flask_login.logout_user()
    display_uuid = request.args.get("usr", default=1, type=str)
    ws.DB.deleteUserWithId(display_uuid)
    return render_template("index.html", title="Home", form=form)


@users.route("/rejection")
def rejection():
    form = CameraForm()
    rejectionDict = {
        "reason": "Unknown",
        "redirect": "create",
        "redirectPretty": "Back to registration",
    }
    return render_template("rejection.html", rejectionDict=rejectionDict, title="Reject", form=form)


@users.route("/validationsignup")
def validationsignup():
    form = CameraForm()
    user_uuid = ws.DB.getUser(user)

    if user_uuid:
        ws.BigBrotherUserList.append(BigBrotherUser(user_uuid, user, ws.DB))
        print("Created UserObject '{}' with uuid: {}".format(user, user_uuid), file=sys.stdout)
        return render_template("validationsignup.html", name=user)

    return render_template("index.html", BigBrotherUserList=ws.BigBrotherUserList, form=form)


@users.route("/userpage")
def userpage():

    display_uuid = request.args.get("usr", default=1, type=str)
    displayUser = None
    for user in ws.BigBrotherUserList:
        if user.uuid == display_uuid:
            displayUser = user

    return render_template("userpage.html", BigBrotherUserList=ws.BigBrotherUserList, displayUser=displayUser)


@users.route("/create", methods=["GET", "POST"])
def create():
    form = SignUpForm(request.form)
    if request.method == "POST" and form.validate():
        rejectionDict = {
            "reason": "Unknown",
            "redirect": "create",
            "redirectPretty": "Back to registration",
        }
        user = {
            "username": form.name.data,
            "pic1": request.files.get("pic1", None),
            "pic2": request.files.get("pic2", None),
            "pic3": request.files.get("pic3", None),
        }
        user_uuid = None

        if not ws.DB.getUser(user["username"]):
            pictures = [
                user["pic1"],
                user["pic2"],
                user["pic3"],
            ]

            user_uuid = ws.DB.register_user(user["username"], None)
            i = 0
            encodings_saved = False
            for storage in pictures:
                i += 1
                if storage is None or not storage.content_type.startswith("image/"):
                    rejectionDict["reason"] = f"Image {i} not provided"
                    ws.DB.deleteUserWithId(user_uuid)
                    return render_template("rejection.html", rejectionDict=rejectionDict, title="Reject", form=form)

                im_bytes = storage.stream.read()
                image = Image.open(io.BytesIO(im_bytes))
                array = np.array(image)
                if not encodings_saved:
                    try:
                        img = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
                        encodings = face_recognition.face_encodings(img)

                        ws.DB.update_user_enc(user_uuid, encodings[0])
                        encodings_saved = True
                    except:
                        print("error while calculating encodings")
                image.close()
                storage.close()

                pic_resized = cv2.resize(array, dsize=(98, 116), interpolation=cv2.INTER_CUBIC)
                pic_uuid = ws.DB.insertTrainingPicture(np.asarray(pic_resized, dtype=np.float64), user_uuid)
                print("Inserted Picture for user_uuid: '{}' with pic_uuid: {}".format(user_uuid, pic_uuid), file=sys.stdout)

            ws.BigBrotherUserList.append(BigBrotherUser(user_uuid, user["username"], ws.DB))
            print("Created User '{}' with uuid: {}".format(user["username"], user_uuid), file=sys.stdout)
        else:
            print("'{}' already exists!".format(user["username"]), file=sys.stdout)
            rejectionDict["reason"] = "Benutzername '{}' nicht Verfügbar".format(user["username"])
            return render_template("rejection.html", rejectionDict=rejectionDict, title="Reject", form=form)

        return render_template("validationsignup.html", name=user["username"])
    else:
        flash("Error: All Fields are Required")

    return render_template("create.html", form=form)


@socketio.on("input_image_create", namespace="/createWithCamera")
def queueImage_create(input):
    print("Putting Image...")
    ws.WEBCAM_IMAGE_QUEUE_CREATE.put(input)


@socketio.on("start_transfer_create", namespace="/createWithCamera")
def webcamCommunication_create():
    emit("ack_transfer", {"foo": "bar"}, namespace="/createWithCamera")
    cookie = request.cookies.get("session_uuid")
    print("ack_transfer...")
    while not ws.authorizedFlag or not ws.authorizedAbort:
        try:
            create_with_image(ws.WEBCAM_IMAGE_QUEUE_CREATE.get(block=True, timeout=5))
        except queue.Empty:
            print("Webcam Queue is Empty! Breaking!", file=sys.stdout)
            break

    ws.WEBCAM_IMAGE_QUEUE_CREATE = queue.Queue()
    ws.authorizedAbort = False
    ws.authorizedFlag = False
    ws.resetinvalidStreamCount(cookie)


# TODO: Take a look at this and why it's so similar to the other routes in
# other modules

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

    print("Check : {} < 5, {} < {}, {} > 50".format(
          len(ws.createPictures), len(cutImg), len(img), len(cutImg)))
    print(len(ws.createPictures) < 5 and len(cutImg) < len(img) and len(cutImg) > 50)
    if len(ws.createPictures) < 5 and len(cutImg) < len(img) and len(cutImg) > 50:
        ws.createPictures.append(cutImg)
        if len(ws.createPictures) >= 5:
            cookie = request.cookies.get("session_uuid")
            ws.setAuthorizedAbort(cookie, True)
            registerUser(user, ws.createPictures)
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


# TODO: Take a look at what this is about
# TODO: If it is a test then you should export it
# Socket Server side for login
@socketio.on("connect", namespace="/webcamJS")
def test_connect_web():
    application.logger.info("client connected")


# TODO: Take a look at what this is about
# TODO: If it is a test then you should export it
# Socket Server side for registration
@socketio.on("connect", namespace="/createWithCamera")
def test_connect_camera():
    application.logger.info("client connected")


@socketio.on("disconnect", namespace="/createWithCamera")
def disconnected():
    cookie = request.cookies.get("session_uuid")
    ws.setAuthorizedAbort(cookie, True)
    ws.resetinvalidStreamCount(cookie)
    application.logger.info("Websocket client disconnected")


@users.route("/webcamJS", methods=["GET", "POST"])
def webcamJS():
    return render_template("webcamJS.html", title="Camera")


@users.route("/webcamCreate", methods=["GET", "POST"])
def webcamCreate():
    return render_template("webcamCreate.html", title="Camera")


@users.route("/createcamera", methods=["GET", "POST"])
def createcamera():
    form = CameraForm(request.form)

    ws.createPictures = []
    rejectionDict = {
        "reason": "Unknown",
        "redirect": "login",
        "redirectPretty": "Back to registration",
    }

    if request.method == "POST" and form.validate():
        flash("Thanks for signing up")

        global user
        username = form.name.data
        user_uuid = ws.DB.getUser(username)

        if user_uuid:
            print("'{}' found!".format(form.name.data), file=sys.stdout)
            rejectionDict["reason"] = "'{}' already found!".format(form.name.data)
            return render_template("rejection.html", rejectionDict=rejectionDict, title="Sign In", form=form)

        user = username

        return render_template("webcamCreate.html", title="Camera")

    return render_template("createcamera.html", title="Create an account", form=form)


def registerUser(username, pictures):
    user_uuid = None

    if not ws.DB.getUser(username):
        user_uuid = ws.DB.register_user(username)
        for pic in pictures:
            pic_uuid = ws.DB.insertTrainingPicture(np.asarray(pic, dtype=np.float64), user_uuid)
            print("Inserted Picture for user_uuid: '{}' with pic_uuid: {}".format(user_uuid, pic_uuid), file=sys.stdout)
    else:
        print("'{}' already exists!".format(username), file=sys.stdout)
        emit("redirect", {"url": "/rejection"})
    emit("redirect", {"url": "/validationsignup"})
    return
