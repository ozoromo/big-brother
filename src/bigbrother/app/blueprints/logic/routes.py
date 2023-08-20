import os
import sys
import io


from flask import (render_template, request, Blueprint, url_for,
                   send_from_directory)
import flask_login
from flask_socketio import emit

import cv2
import cv2.misc
from PIL import Image
import numpy as np
import base64
import urllib


# Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "gesture_recognition"))

from app.blueprints.logic.forms import VideoUploadForm
from app import application, socketio

from gesture_recognizer import GestureRecognizer


logic = Blueprint("logic", __name__)
gesture = GestureRecognizer()


@logic.route("/gestureReco")
@flask_login.login_required
def gestureReco():
    return render_template("gestureReco.html")


@socketio.on("gesture_recognition", namespace="/gesture_recognition")
def recognizing_gestures(data):
    img_url = data["image"].split(",")
    if len(img_url) < 2:
        return
    
    response = urllib.request.urlopen(data["image"])
    buffer = io.BytesIO()
    buffer.write(response.file.read())
    pil_img = Image.open(io.BytesIO(buffer.getvalue()))
    buffer.close()
    np_img = np.asarray(pil_img)

    frame, className = gesture.recognize(np_img)
    frame = cv2.flip(frame, 1)
    cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    pil_img = Image.fromarray(frame.astype('uint8'), 'RGB')
    buffered = io.BytesIO()
    pil_img.save(buffered, format="JPEG")
    response_data_url = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

    emit("ack_gesture_recognition", {"image": response_data_url})


@logic.route("/videos/<filename>")
def serve_video(filename):
    return send_from_directory(application.config["TMP_VIDEO_FOLDER"], filename)


@logic.route("/eduVid", methods=["GET", "POST"])
@flask_login.login_required
def eduVid():
    form = VideoUploadForm()

    if form.validate_on_submit():
        name = form.name.data
        video = form.video.data

        # deletes every video file in tmp folder
        for vid_file in os.listdir(application.config["TMP_VIDEO_FOLDER"]):
            if vid_file.endswith(".md"):
                continue
            del_path = os.path.join(application.config["TMP_VIDEO_FOLDER"], vid_file)
            if os.path.isfile(del_path):
                os.remove(del_path)

        file_path = os.path.join(application.config["TMP_VIDEO_FOLDER"], video.filename)
        video.save(file_path)

        video_url = url_for("logic.serve_video", filename=video.filename)

        # TODO: get time stamps from logic
        # time stamps should be <label>:<time in seconds>
        video_info = {
            "title": name,
            "url": video_url,
            "time_stamps": [
                {"Intro": 0.0},
                {"Concept": 10.0},
                {"Conclusion": 180.0},
                {"Conclusion2": 210.0},
                {"Conclusion3": 300.0},
                {"Conclusion4": 492.0},
                {"Conclusion5": 688.0},
                {"Conclusion6": 700.0},
                {"Bye": 777.0},
                {"EOF": 7777.0}
            ]
        }
        return render_template("eduVidPlayer.html", video_info=video_info)

    return render_template("eduVid.html", form=form)
