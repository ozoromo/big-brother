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
import json


# Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "gesture_recognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "eduVid"))

from app.blueprints.logic.forms import VideoUploadForm
from app import application, socketio

from gesture_recognizer import GestureRecognizer
import question_answering.qa_algo_core as qa

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
        segment_file = request.files.get("segments")
        question = form.question.data

        segments_data = segment_file.stream.read()
        segments_json = json.loads(segments_data)
        segments = segments_json.get("time-stamps")

        if not os.path.isdir(application.config["TMP_VIDEO_FOLDER"]):
            os.makedirs(application.config["TMP_VIDEO_FOLDER"])

        # deletes every video file in tmp folder
        for vid_file in os.listdir(application.config["TMP_VIDEO_FOLDER"]):
            if vid_file.endswith(".md"):
                continue
            del_path = os.path.join(application.config["TMP_VIDEO_FOLDER"], vid_file)
            if os.path.isfile(del_path):
                os.remove(del_path)

        video_path = os.path.join(application.config["TMP_VIDEO_FOLDER"], video.filename)
        video.save(video_path)

        model_name = "timpal0l/mdeberta-v3-base-squad2"

        audio_file = os.path.join(application.config["TMP_VIDEO_FOLDER"], video.filename + "_audio.wav")
        _ = qa.HelperFN.extract_audio_from_mp4(video_path, audio_file)

        recog = qa.SpeechRecog(audio_file)
        context, tags = recog.transcribe()

        qa_result = qa.QAAlgo(model_name)
        answer = qa_result.answer_question(context, question)

        matching_segments = qa.HelperFN.find_matching_segments(tags, answer)
        merged_segments = qa.HelperFN.merge_overlapping_segments(matching_segments)

        if len(merged_segments) == 0:
            print("No segments found !")
            answer = "Es konnte keine passende Antwort gefunden werden"

        video_url = url_for("logic.serve_video", filename=video.filename)

        if segments is None:
            segments = []

        answer_segments = [{f"Answer{i}": begin} for i, (begin, _) in enumerate(merged_segments, start=1)]

        video_info = {
            "title": name,
            "url": video_url,
            "time_stamps": segments,
            "question": question,
            "answer": answer,
            "answer_time_stamps": answer_segments
        }

        print(video_info)

        return render_template("eduVidPlayer.html", video_info=video_info)

    return render_template("eduVid.html", form=form)
