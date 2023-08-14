import os
import sys


from flask import (render_template, request, Blueprint, url_for,
                   send_from_directory)
import flask_login

import cv2
import cv2.misc


# Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Logik"))

from app.blueprints.logic.forms import VideoUploadForm, CameraForm
from app import application

import Gesture_Recognition.GestureReco_class as GestureRec


logic = Blueprint("logic", __name__)


@logic.route("/gestureReco", methods=["GET", "POST"])
def gestureReco():
    form = CameraForm()

    rejectionDict = {
        "reason": "Unknown",
        "redirect": "login",
        "redirectPretty": "Back to login",
    }

    if request.method == "GET":
        return render_template("gestureReco.html", form=form)

    if form.validate_on_submit():
        capture = cv2.VideoCapture(0)
        gesture = GestureRec.GestureReco()

        while True:
            _, frame = capture.read()
            frame, className = gesture.read_each_frame_from_webcam(frame)
            cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # Show the final output
            cv2.imshow("Output", frame)

            if cv2.waitKey(1) == ord("q"):
                break

        capture.release()
        cv2.destroyAllWindows()

        return render_template("gestureRecoJS.html", title="Camera")

    return render_template("rejection.html", rejectionDict=rejectionDict)


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
