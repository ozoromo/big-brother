import os
import sys
import io

from flask import (render_template, request, Blueprint, url_for, send_from_directory, redirect)
import flask_login
from flask_socketio import emit
import cv2
from PIL import Image, UnidentifiedImageError
import numpy as np
import base64

# Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "gesture_recognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "database_management"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "eduVid"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "gesture_recognition/user_scripts"))
from app.blueprints.logic.forms import VideoUploadForm
from app import application, socketio

from gesture_recognizer import GestureRecognizer
import question_answering.qa_algo_core as qa

from base_database import BaseDatabase
from lua_sandbox_runner import run_lua_in_sandbox

from base_database import BaseDatabase

db = BaseDatabase()

logic = Blueprint("logic", __name__)
gesture = GestureRecognizer()

GESTURE_ACTIONS = {
    "like": ["yes", "like", "help", "good", "hungry"],
    "rock": ["Good Morning/Afternoon/Evening", "How are you?", "Thank you", "Please", "Hello"],
    "closed_fist": ["I", "You", "it", "she/he", "they"],
    "call": ["be", "eat", "do", "have", "go"],
    "ok": ["What", "Where", "When", "Which", "Who"],
    "dislike": ["no", "hate", "sorry", "Delete All", "Delete 1"],
    "italy": ["spaghetti", "pizza", "lasagna", "mamma mia", "i love italy"]
}

Gesture_Script_Map = {
    'like': 'standart_like',
    'rock': 'standart_rock',
    'closed_fist': 'standart_closed_first',
    'call': 'standart_call',
    'ok ': 'standart_ok',
    'dislike': 'standart_dislike',
    'italy': 'standart_italy',    
    'one' : 'hello_welt', 
    'piece' : 'hello_welt',
    'three' : 'hello_welt', 
    'four' : 'hello_welt',
    'highfive' : 'hello_welt'
}

# Gesture to Action 
@logic.route("/gestureReco")
@flask_login.login_required
def gestureReco():
    return render_template("gestureReco_actions.html")

@socketio.on("gesture_recognition", namespace="/gesture_recognition")
def recognizing_gestures(data):
    try:
        img_url = data.get("image")
        if not img_url:
            print("Error: No image data found in request.")
            return
        
        img_data_parts = img_url.split(",")
        if len(img_data_parts) != 2:
            print("Error: Image data is not in the expected base64 format.")
            return

        img_str = img_data_parts[1]
        try:
            img_data = base64.b64decode(img_str)
        except Exception as e:
            print(f"Error decoding base64 image data: {e}")
            return
        
        try:
            pil_img = Image.open(io.BytesIO(img_data))
            np_img = np.array(pil_img)
        except UnidentifiedImageError as e:
            print(f"Error: Unable to identify image. {e}")
            return
        except Exception as e:
            print(f"Error loading image into PIL: {e}")
            return

        np_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)

        try:
            annotated_image, class_name = gesture.recognize(np_img)
        except Exception as e:
            print(f"Error during gesture recognition: {e}")
            return

        actions = GESTURE_ACTIONS.get(class_name, [])

        annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        cv2.putText(annotated_image, class_name, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        pil_annotated_img = Image.fromarray(annotated_image)

        buffered = io.BytesIO()
        pil_annotated_img.save(buffered, format="JPEG")
        response_data_url = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

        emit("ack_gesture_recognition", {"image": response_data_url, "gesture": class_name, "actions": actions})

    except Exception as e:
        print(f"Error in recognizing_gestures: {e}")

@logic.route('/action_control', methods=['GET', 'POST'])
def action_control():
    if request.method == 'POST':
        for gesture in Gesture_Script_Map.keys():
            selected_script_id = request.form.get(gesture)
            Gesture_Script_Map[gesture] = selected_script_id
        return redirect(url_for('logic.action_control'))
    #['standart_like', 'standart_rock', 'standart_closed_first', 'standart_call', 'standart_ok', 'standart_dislike', 'standart_italy']
    user_id = request.args.get("usr", default=None, type=str)
    accessible_scripts = db.get_accessible_scripts(user_id)  # Assume 'user1' for now
    return render_template('action_control.html', gesture_script_map=Gesture_Script_Map, accessible_scripts=accessible_scripts)

@logic.route('/upload_script', methods=['POST'])
def upload_script(): 
    script_name = request.form.get('script_name')
    script_file = request.files.get('script_file')
    is_private = request.form.get('is_private') == 'on'
    username = 'user1'  # Assume 'user1' for now

    if script_file and script_file.filename.endswith('.lua'):
        script_content = script_file.read().decode('utf-8')
        # Save the new script
        db.save_lua_script(username, script_name, script_content, is_private)
        return redirect(url_for('logic.action_control'))
    else:
        return "Invalid file type. Only Lua files are allowed.", 400
    
@app.route('/logic/execute_gesture_action', methods=['POST'])
def execute_gesture_action():
    data = request.get_json()
    gesture = data.get('gesture')
    
    # Example: Mapping gestures to Lua scripts
    gesture_script_map = {
        'one': 'script_one.lua',
        'peace': 'script_peace.lua',
        'three': 'script_three.lua',
        # Add mappings for other gestures...
    }

    script = gesture_script_map.get(gesture)
    
    if script:
        # Execute the Lua script (example implementation)
        try:
            result = execute_lua_script(script)
            return jsonify(result=result)
        except Exception as e:
            return jsonify(error=str(e)), 500
    else:
        return jsonify(error="No script found for gesture"), 400

def execute_lua_script(script):
    # Implement the logic to execute the Lua script and return the result
    # This is a placeholder function
    return "Result from " + script
    
# Gesture to Text Conversion
@logic.route("/gestureReco_text")
@flask_login.login_required
def gestureReco_text():
    return render_template("gestureReco_text.html")


@socketio.on("gesture_recognition_text", namespace="/gesture_recognition_text")
def recognizing_gestures_text(data):
    try:
        img_url = data.get("image")
        if not img_url:
            print("Error: No image data found in request.")
            return
        
        img_data_parts = img_url.split(",")
        if len(img_data_parts) != 2:
            print("Error: Image data is not in the expected base64 format.")
            return

        img_str = img_data_parts[1]
        try:
            img_data = base64.b64decode(img_str)
        except Exception as e:
            print(f"Error decoding base64 image data: {e}")
            return
        
        try:
            pil_img = Image.open(io.BytesIO(img_data))
            np_img = np.array(pil_img)
        except UnidentifiedImageError as e:
            print(f"Error: Unable to identify image. {e}")
            return
        except Exception as e:
            print(f"Error loading image into PIL: {e}")
            return

        np_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)

        try:
            annotated_image, class_name = gesture.recognize(np_img)
        except Exception as e:
            print(f"Error during gesture recognition: {e}")
            return

        actions = GESTURE_ACTIONS.get(class_name, [])

        annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        cv2.putText(annotated_image, class_name, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        pil_annotated_img = Image.fromarray(annotated_image)

        buffered = io.BytesIO()
        pil_annotated_img.save(buffered, format="JPEG")
        response_data_url = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

        emit("ack_gesture_recognition_text", {"image": response_data_url, "gesture": class_name, "actions": actions})

    except Exception as e:
        print(f"Error in recognizing_gestures: {e}")



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