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

# Dealing with images
from imageio import imread
from PIL import Image
import cv2
import cv2.misc


# Own libraries
# GUI and frontend libraries
from app import socketio, login_manager, ws
from app.user import BigBrotherUser
from app.login.forms import SignInForm, CameraForm

# Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "FaceRecognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "Logik"))
import FaceDetection
import Face_Recognition.FaceReco_class as LogikFaceRec


blueprint_login = Blueprint("blueprint_login", __name__)


@login_manager.user_loader
def load_user(user_id):
    print("loading user:", user_id, file=sys.stdout)

    if type(user_id) == tuple:
        user_id = user_id[0]

    loadedUser = None
    for bbUser in ws.BigBrotherUserList:
        if bbUser.uuid == user_id:
            loadedUser = bbUser
            bbUser.sync()
            print("{} is Admin: {}".format(bbUser.name, bbUser.admin))
    return loadedUser


@blueprint_login.route("/loginstep")
def loginstep():
    flask_login.login_user(user["bbUser"])
    return render_template("validationauthenticated.html")


@blueprint_login.route("/login", methods=["GET", "POST"])
def login():
    form = SignInForm(request.form)

    rejectionDict = {
        "reason": "Unknown",
        "redirect": "login",
        "redirectPretty": "Zurück zur Anmeldung",
    }

    # We need to check if "Sign In" or "Open Camera" got pressed
    # Activates when Sign in Button is pressed
    if request.method == "POST" and form.validate():
        flash("Thanks for logging in")

        user = {
            "username": form.name.data,
            "pic": request.files.get("pic", None)
        }

        # Verify user
        # Checks if username is in Database and fetches uuid
        user_uuid = ws.DB.getUser(user["username"])

        if user_uuid:
            user["uuid"] = user_uuid
            storage = user["pic"]

            if storage is None or not storage.content_type.startswith("image/"):
                rejectionDict["reason"] = "Image Not uploaded!"
                return render_template("rejection.html", rejectionDict=rejectionDict, title="Sign In", form=form)

            # Save Picture
            cookie = request.cookies.get("session_uuid")

            im_bytes = storage.stream.read()
            image = Image.open(io.BytesIO(im_bytes))
            array = np.array(image)

            image.close()
            storage.close()

            result = ws.authenticatePicture(user, array, cookie)
            if result:
                thisUser = BigBrotherUser(user_uuid, user["username"], ws.DB)
                flask_login.login_user(thisUser)

                return render_template("validationauthenticated.html", user=user)

            else:
                return render_template("rejection.html", rejectionDict=rejectionDict, title="Sign In", form=form)
        else:
            print("'{}' not found!".format(user["username"]), file=sys.stdout)
            rejectionDict["reason"] = "'{}' not found!".format(user["username"])
            return render_template("rejection.html", rejectionDict=rejectionDict, title="Sign In", form=form)

    return render_template("login.html", title="Sign In", form=form)


@socketio.on("input_image_login", namespace="/webcamJS")
def queueImage_login(input_):
    cookie = request.cookies.get("session_uuid")
    queueObj = ws.getQueue(cookie)
    if queueObj.qsize() < 5:
        queueObj.put(input_)

    input_ = input_.split(",")[1]
    image_data = input_  # Do your magical Image processing here!!

    # user is global, use it with cv2_img for authentication
    # OpenCV part decode and encode
    img = None
    try:
        img = imread(io.BytesIO(base64.b64decode(image_data)))
    except ValueError:
        emit("ready", {"image_data": "bar"}, namespace="/webcamJS")
        return
    cv2_img = FaceDetection.make_rectangle(img)
    cv2.imwrite("reconstructed_display.jpg", cv2_img)

    retval, buffer = cv2.imencode(".jpg", cv2_img)
    b = base64.b64encode(buffer)
    b = b.decode()
    image_data = "data:image/jpeg;base64," + b

    emit("display_image", {"image_data": image_data}, namespace="/webcamJS")


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
    cookie = request.cookies.get("session_uuid")
    ws.setAuthorizedAbort(cookie, False)

    if ws.checkinvalidStreamCount(cookie):
        ws.resetinvalidStreamCount(cookie)
        ws.setAuthorizedAbort(cookie, True)
        emit("redirect", {"url": "/rejection"})

    print("Testing...")

    # CAUTION: test_message is called multiple times from the client (for every image).
    # Figure out how many pics are needed and then close socket
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

    # TODO: Authentication with cv2_img and users
    cv2.imwrite("reconstructed.jpg", cv2_img)
    retval, buffer = cv2.imencode(".jpg", cv2_img)
    b = base64.b64encode(buffer)
    b = b.decode()
    image_data = "data:image/jpeg;base64," + b

    user["isWorking"] = False

    cookie = request.cookies.get("session_uuid")
    if len(cutImg) < len(img) and len(cutImg) > 50:
        res = ws.authenticatePicture(user, np.asarray(cutImg), cookie)
        if res:
            cookie = request.cookies.get("session_uuid")
            ws.setAuthorizedAbort(cookie, True)

            ws.DB.update_login(
                user_uuid=user["uuid"],
                time=user["login_attempt_time"],
                inserted_pic_uuid=res
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
    form = CameraForm(request.form)
    rejectionDict = {
        "reason": "Unknown",
        "redirect": "login",
        "redirectPretty": "Zurück zur Anmeldung",
    }

    # We need to check if "Sign In" or "Open Camera" got pressed
    # Activates when Sign in Button is pressed
    if request.method == "POST" and form.validate():
        flash("Thanks for logging in")

        # Fetch Username
        global user
        user_uuid = ws.DB.getUser(form.name.data)

        if not user_uuid:
            print("'{}' not found!".format(form.name.data), file=sys.stdout)
            rejectionDict["reason"] = "'{}' not found!".format(form.name.data)
            return render_template("rejection.html", rejectionDict=rejectionDict, title="Sign In", form=form)

        bbUser = None

        for user in ws.BigBrotherUserList:
            if user.uuid == user_uuid:
                bbUser = user
                break

        user = {
            "username": form.name.data,
            "isWorking": False,
            "uuid": user_uuid,
            "bbUser": bbUser
        }
        data = {
            "username": form.name.data
        }

        # TODO: Figure out whether the commented out line is important or not!
        # user["login_attempt_time"] = ws.DB.login_user(uuid_id=user_uuid)

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

    # POST request gets send from main.js in the sendSnapshot() function.
    if request.method == "POST":
        data = request.get_json()
        # json data needs to have the encoded image & username
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

            # if successfull login but page does not change !
            result = results[0]
            if not result:
                return {"redirect": "/rejection"}
            else:
                thisUser = BigBrotherUser(user_uuid, user["username"], ws.DB)
                flask_login.login_user(thisUser)

                user_data = {"username": username}

                # back to base?
                return {"redirect": "/verifypicture", "data": user_data}
        else:
            return {"redirect": "/rejection"}

    return {"redirect": "/rejection"}
