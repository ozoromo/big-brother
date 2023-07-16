# @Author: Julius U. Heller <thekalk>
# @Date:   2021-05-17T16:09:26+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: __init__.py
# @Last modified by:   Julius U. Heller
# @Last modified time: 2021-06-21T13:27:48+02:00
import os
import random
from sys import stdout
import sys
import click

sys.path.append(os.path.join(os.path.dirname(__file__),".."))
from flask import Flask, Response, render_template, request, session, make_response
from flask_socketio import SocketIO, emit
#from flask_login import LoginManager
import flask_login
from app.utils import base64_to_pil_image, pil_image_to_base64
from config import Config
from app.user import BigBrotherUser


import multiprocessing as mp
#from app.camera import Camera


#Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','WiReTest'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','FaceRecognition','haar_and_lbph'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','FaceRecognition'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','DBM'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','Logik'))
#from modifiedFaceRecog import recogFace
#from face_rec_main import train_add_faces, authorize_faces
#from main import load_images as load_test_imgs
import FaceDetection
import face_recognition
#from app import routes
import Face_Recognition.FaceReco_class as LogikFaceRec

from flask import render_template, flash, redirect, url_for

#kim: kommt bald weg
from app.forms import LoginForm, CreateForm, LoginCameraForm
#kim: neuer import
from app.forms import SignUpForm, SignInForm, CameraForm, VideoUploadForm

import ssl
from werkzeug.utils import secure_filename
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle
import uuid
import DatabaseManagement as DBM
import matplotlib as mpl
import cv2
import cv2.misc
import time
import logging
import base64
import io
import traceback
from imageio import imread
from PIL import Image
import copy
import websiteSystem
import queue
#from ..app import modifiedFaceRecog


#h2938366.stratoserver.net
print("Starting BigBrother")

application = Flask(__name__)
application.config.from_object(Config)

application.logger.addHandler(logging.StreamHandler(stdout))
application.config['SECRET_KEY'] = 'secret!'
application.config['DEBUG'] = True
application.config['UPLOAD_FOLDER'] = application.instance_path
application.config['LOCALDEBUG'] = None

login_manager = flask_login.LoginManager()
login_manager.init_app(application)

ws = websiteSystem.websiteSystem()



if os.environ.get('LOCALDEBUG') == "True":
    application.config['LOCALDEBUG'] = True
else:
    application.config['LOCALDEBUG'] = False
socketio = SocketIO(application)

#camera = Camera()

@application.route("/logout")
@flask_login.login_required
def logout():
    form = SignInForm(request.form)
    flask_login.logout_user()
    return render_template('index.html', title='Home',form=form)
    #return redirect(url_for('index'))
    
@application.route("/deleteuser")
@flask_login.login_required
def deleteuser():
    form = SignInForm(request.form)
    flask_login.logout_user()
    display_uuid = request.args.get('usr', default = 1, type = str)
    ws.DB.deleteUserWithId(display_uuid)
    return render_template('index.html', title='Home',form=form)

@login_manager.user_loader
def load_user(user_id):
    print("loading user:",user_id,file=sys.stdout)

    if type(user_id) == tuple:
        user_id = user_id[0]

    loadedUser = None
    # return BigBrotherUser(user_id,ws.DB.getUserWithId(user_id[0]))
    for bbUser in ws.BigBrotherUserList:
        if bbUser.uuid == user_id:
            loadedUser = bbUser
            bbUser.sync()
            print("{} is Admin: {}".format(bbUser.name,bbUser.admin))
    return loadedUser

@application.route("/loginstep")
def loginstep():

    flask_login.login_user(user['bbUser'])
    print("Loggin User : {}".format(user['bbUser'].name))

    return render_template("validationauthenticated.html")



@application.route("/rejection")
def rejection():

    form = CameraForm()
    rejectionDict = {

                        'reason' : 'Unknown',
                        'redirect' : 'create',
                        'redirectPretty' : 'Zurück zur Registrierung',
                    }
    return render_template('rejection.html',  rejectionDict = rejectionDict, title='Reject', form=form)

@application.route("/validationsignup")
def validationsignup():
    #print(application.config['LOCALDEBUG'])
    #Dummy Form
    form = CameraForm()

    user_uuid = ws.DB.getUser(user)

    if user_uuid:

        ws.BigBrotherUserList.append(BigBrotherUser(user_uuid,user,ws.DB))

        print("Created UserObject '{}' with uuid: {}".format(user,user_uuid),file=sys.stdout)

        return render_template('validationsignup.html', name=user)

    return render_template('index.html', BigBrotherUserList = ws.BigBrotherUserList,form = form)

@application.route("/team")
def team():
    return render_template("team.html")

@application.route("/team2")
def team2():
    return render_template("team_23.html")

@application.route("/algorithms")
def algorithms():
    return render_template("algorithms.html")

@application.route("/eduVid", methods=['GET','POST'])
@flask_login.login_required
def eduVid():
    form = VideoUploadForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            video = form.video.data
            
            #TODO: EduVid Implementation
            
            
        return 'Das Video wurde erfolgreich hochgeladen.'  
    return render_template("eduVid.html", form=form)

@application.route("/userpage")
def userpage():

    display_uuid = request.args.get('usr', default = 1, type = str)
    displayUser = None
    for user in ws.BigBrotherUserList:
        if user.uuid == display_uuid:
            displayUser = user

    return render_template("userpage.html", BigBrotherUserList = ws.BigBrotherUserList,displayUser=displayUser)


#@application.route('/index')
@application.route('/',methods=['GET', 'POST'])
def index():
    form = None
    if request.method == 'POST':
        #form = CameraForm()
        return logincamera()

    cookie = request.cookies.get('session_uuid')
    if not cookie:

        response = make_response(render_template('index.html', BigBrotherUserList = ws.BigBrotherUserList,form = form))
        uuid_ = uuid.uuid4()
        print("setting new uuid: ",uuid_)
        response.set_cookie('session_uuid', str(uuid_))


        return response
    return render_template('index.html', BigBrotherUserList = ws.BigBrotherUserList,form = form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = SignInForm(request.form)

    rejectionDict = {

                        'reason' : 'Unknown',
                        'redirect' : 'login',
                        'redirectPretty' : 'Zurück zur Anmeldung',
                    }


    # We need to check if 'Sign In' or 'Open Camera' got pressed
    # Activates when Sign in Button is pressed

    #print(request.method ,form.validate())
    #print(form.errors,file=sys.stdout)

    if request.method == 'POST' and form.validate():
        flash('Thanks for logging in')

        user = {
                    'username': form.name.data,
                    'pic' : request.files.get('pic', None)
                }

        #Verify user
        #Checks if username is in Database and fetches uuid
        user_uuid = ws.DB.getUser(user['username'])

        if user_uuid:

            # TODO: Take a look at why it was set to user_uuid[0]
            # user_uuid =uuid.UUID(user_uuid[0]) old code outputted a list
            #user_uuid = uuid.UUID(user_uuid)
            #Get Picture Path
            #print("test3",file=sys.stdout)
            #print("test4",file=sys.stdout)

            user['uuid'] = user_uuid
            storage = user['pic']

            #filename = secure_filename(pic.filename)
            #file_path = os.path.join(application.instance_path, filename)

            if storage is None or not storage.content_type.startswith('image/'):
                rejectionDict['reason'] = "Image Not uploaded!"
                return render_template('rejection.html',  rejectionDict = rejectionDict, title='Sign In', form=form)

            #Save Picture
            #print("test5",file=sys.stdout)
            #print("test6",file=sys.stdout)

            cookie = request.cookies.get('session_uuid')

            im_bytes = storage.stream.read()
            image = Image.open(io.BytesIO(im_bytes))
            array = np.array(image)

            image.close()
            storage.close()

            #(729, 1280, 3)
            result = ws.authenticatePicture(user, array, cookie)

            if result:

                thisUser = BigBrotherUser(user_uuid,user['username'],ws.DB)
                flask_login.login_user(thisUser)

                return render_template('validationauthenticated.html',  user=user)

            else:
                return render_template('rejection.html',  rejectionDict = rejectionDict, title='Sign In', form=form)
            
        else:
            print("'{}' not found!".format(user['username']),file=sys.stdout)
            rejectionDict['reason'] = "'{}' not found!".format(user['username'])
            return render_template('rejection.html', rejectionDict = rejectionDict,  title='Sign In', form=form)

    return render_template('login.html',  title='Sign In', form=form)


@application.route('/create', methods=['GET', 'POST'])
def create():
    #form = CreateForm()
    #form = SignUpForm()
    form = SignUpForm(request.form)
    #print(form.errors,file=sys.stdout)
    #print(request.method)
    #print(form.validate())
    #if form.validate_on_submit():
    if request.method == 'POST' and form.validate():
        #print("test2",file=sys.stdout)
        #flash('Thanks for logging in')

        rejectionDict = {

                            'reason' : 'Unknown',
                            'redirect' : 'create',
                            'redirectPretty' : 'Zurück zur Registrierung',
                        }

        #print("test6",file=sys.stdout)

        #print(request.files,file=sys.stdout)

        #print("test7",file=sys.stdout)
        user = {
                    'username': form.name.data,
                    'pic1' : request.files.get('pic1', None),
                    'pic2' : request.files.get('pic2', None),
                    'pic3' : request.files.get('pic3', None),
                }

        user_uuid = None
        #print(form.errors,file=sys.stdout)
        if not ws.DB.getUser(user['username']):
            #print("test3",file=sys.stdout)
            #print(user['username'],file=sys.stdout)

            #Get Picture Path
            #pic_1 = form.picturefront.data
            #pic_2 = form.pictureleft.data
            #pic_3 = form.pictureright.data

            pictures = [
                    user['pic1'],
                    user['pic2'],
                    user['pic3'],
                ]

            user_uuid = ws.DB.register_user(user['username'], None)
            i = 0
            encodings_saved = False
            for storage in pictures:
                i += 1
                if storage is None or not storage.content_type.startswith('image/'):
                    rejectionDict['reason'] = f"Image {i} not provided"
                    ws.DB.deleteUserWithId(user_uuid)
                    return render_template('rejection.html', rejectionDict=rejectionDict, title='Reject', form=form)

                #filename = secure_filename(pic.filename)
                #print(filename)
                #file_path = os.path.join(application.instance_path, filename)
                #pic.save(file_path)
                #pic_array = cv2.imread(file_path,0)

                im_bytes = storage.stream.read()
                image = Image.open(io.BytesIO(im_bytes))
                array = np.array(image)

                if not encodings_saved:
                    try:
                        img = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
                        encodings = face_recognition.face_encodings(img)
                        #print("encodings: ", encodings)

                        ws.DB.update_user_enc(user_uuid, encodings[0])
                        encodings_saved = True
                    except:
                        print("error while calculating encodings")

                image.close()
                storage.close()

                pic_resized = cv2.resize(array, dsize=(98, 116), interpolation=cv2.INTER_CUBIC)

                pic_uuid = ws.DB.insertTrainingPicture(np.asarray(pic_resized, dtype=np.float64),user_uuid)

                print("Inserted Picture for user_uuid: '{}' with pic_uuid: {}".format(user_uuid,pic_uuid),file=sys.stdout)

            ws.BigBrotherUserList.append(BigBrotherUser(user_uuid,user['username'],ws.DB))
            #else:
                #print("'{}' not found!".format(user['username']),file=sys.stdout)
                #return render_template('rejection.html',  title='Sign In', form=form)

            print("Created User '{}' with uuid: {}".format(user['username'],user_uuid),file=sys.stdout)

        else:
            print("'{}' already exists!".format(user['username']),file=sys.stdout)

            rejectionDict['reason'] = "Benutzername '{}' nicht Verfügbar".format(user['username'])

            return render_template('rejection.html',  rejectionDict = rejectionDict, title='Reject', form=form)


        return render_template('validationsignup.html', name=user['username'])
    else:
        flash('Error: All Fields are Required')
        #print("test5",file=sys.stdout)

    return render_template("create.html", form=form)

@socketio.on('input_image_create', namespace='/createWithCamera')
def queueImage_create(input):


    print("Putting Image...")
    ws.WEBCAM_IMAGE_QUEUE_CREATE.put(input)

@socketio.on('start_transfer_create', namespace='/createWithCamera')
def webcamCommunication_create():

    emit('ack_transfer', {'foo': 'bar'}, namespace='/createWithCamera')
    cookie = request.cookies.get('session_uuid')
    print("ack_transfer...")
    while not ws.authorizedFlag or not ws.authorizedAbort:
        try:
            create_with_image( ws.WEBCAM_IMAGE_QUEUE_CREATE.get(block=True, timeout=5) )
        except queue.Empty:
            print("Webcam Queue is Empty! Breaking!",file=sys.stdout)
            break

    ws.WEBCAM_IMAGE_QUEUE_CREATE = queue.Queue()
    ws.authorizedAbort = False
    ws.authorizedFlag = False
    ws.resetinvalidStreamCount(cookie)

@socketio.on('input_image_login', namespace='/webcamJS')
def queueImage_login(input):
    print("Putting Image...")
    cookie = request.cookies.get('session_uuid')
    print("Cookie: ",cookie)
    #ws.WEBCAM_IMAGE_QUEUE_LOGIN.put(input)
    queueObj = ws.getQueue(cookie)
    if queueObj.qsize() < 5:
        queueObj.put(input)

    input = input.split(",")[1]

    #camera.enqueue_input(input)
    image_data = input # Do your magical Image processing here!!

    #user is global (line 388), use it with cv2_img for authentication
    #OpenCV part decode and encode
    img = None
    try:

        img = imread(io.BytesIO(base64.b64decode(image_data)))

    except (ValueError) as e:
            print('Bad file')
            emit('ready', {'image_data': "bar"}, namespace='/webcamJS')
            return

    cv2_img = FaceDetection.make_rectangle(img)

    cv2.imwrite("reconstructed_display.jpg", cv2_img)

    retval, buffer = cv2.imencode('.jpg', cv2_img)

    b = base64.b64encode(buffer)

    b = b.decode()

    image_data = "data:image/jpeg;base64," + b

    emit('display_image', {'image_data': image_data}, namespace='/webcamJS')

@socketio.on('start_transfer_login', namespace='/webcamJS')
def webcamCommunication():

    cookie = request.cookies.get('session_uuid')
    ws.emptyQueue(cookie)

    emit('ack_transfer', {'foo': 'bar'}, namespace='/webcamJS')
    print("ack_transfer...")

    ws.resetinvalidStreamCount(cookie)
    #while not ws.authorizedFlag or not ws.authorizedAbort:
    while not ws.getAuthorizedFlag(cookie) or not ws.getAuthorizedAbort(cookie):
        try:
            #test_message( ws.WEBCAM_IMAGE_QUEUE_LOGIN.get(block=True, timeout=5) )
            test_message( ws.getQueue(cookie).get(block=True, timeout=15) )
        except queue.Empty:
            print("Webcam Queue is Empty! Breaking!",file=sys.stdout)
            break

    #ws.WEBCAM_IMAGE_QUEUE_LOGIN = queue.Queue()
    ws.emptyQueue(cookie)
    #ws.authorizedAbort = False
    #ws.authorizedFlag = False
    ws.setAuthorizedFlag(cookie,False)
    ws.setAuthorizedAbort(cookie,False)


#Retrieving Image from Client javascript side, analyze it and send it back
#Socket source from: https://github.com/dxue2012/python-webcam-flask
#@socketio.on('input image', namespace='/webcamJS')
def test_message(input):
    #form = LoginCameraForm()
    #user = {'username': form.username.data}
    #print(user)

    #ws.authorizedAbort = False
    cookie = request.cookies.get('session_uuid')
    ws.setAuthorizedAbort(cookie,False)

    #ws.setinvalidStreamCount(cookie,1)
    #ws.getinvalidStreamCount(cookie)
    if ws.checkinvalidStreamCount(cookie):
        ws.resetinvalidStreamCount(cookie)
        ws.setAuthorizedAbort(cookie,True)
        emit('redirect', {'url' : '/rejection'})


    print("Testing...")

    #CAUTION: test_message is called multiple times from the client (for every image).
    #Figure out how many pics are needed and then close socket

    #print("[SOCKET DEBUG] 1",file=sys.stdout)
    input = input.split(",")[1]

    #camera.enqueue_input(input)
    image_data = input # Do your magical Image processing here!!

    #user is global (line 388), use it with cv2_img for authentication
    #OpenCV part decode and encode
    img = None
    try:

        img = imread(io.BytesIO(base64.b64decode(image_data)))

    except (ValueError) as e:
            print('Bad file')
            emit('ready', {'image_data': "bar"}, namespace='/webcamJS')
            return


    cutImg = FaceDetection.cut_rectangle(copy.deepcopy(img))

    cv2_img = FaceDetection.make_rectangle(img)


    #TODO Authentication with cv2_img and users

    cv2.imwrite("reconstructed.jpg", cv2_img)

    retval, buffer = cv2.imencode('.jpg', cv2_img)

    b = base64.b64encode(buffer)

    b = b.decode()

    image_data = "data:image/jpeg;base64," + b

    #print("OUTPUT " + image_data)

    user["isWorking"] = False

    cookie = request.cookies.get('session_uuid')
    if len(cutImg) < len(img) and len(cutImg) > 50:
        res = ws.authenticatePicture(user,np.asarray(cutImg),cookie)

        print(res)

        if res:

            cookie = request.cookies.get('session_uuid')
            ws.setAuthorizedAbort(cookie,True)

            ws.DB.update_login(user_uuid=user['uuid'],
            time = user['login_attempt_time'],
            inserted_pic_uuid=res)
            ws.DB.commit()

            emit('redirect', {'url' : '/loginstep'})
            return
        else:
            ws.addinvalidStreamCount(cookie)
    else:
        print("redirect")
        ws.addinvalidStreamCount(cookie)
        if ws.checkinvalidStreamCount(cookie):
            #ws.authorizedAbort = True
            cookie = request.cookies.get('session_uuid')
            ws.setAuthorizedAbort(cookie,True)
            print("redirect2")
            emit('redirect', {'url' : '/rejection'})


    print("Next Image...")

    emit('next_image', {'image_data': image_data}, namespace='/webcamJS')

#Retrieving Image from Client javascript side, analyze it and send it back
#Socket source from: https://github.com/dxue2012/python-webcam-flask
#Used for Registration
@socketio.on('input image', namespace='/createWithCamera')
def create_with_image(input):

    #ws.authorizedAbort = False

    cookie = request.cookies.get('session_uuid')
    ws.setAuthorizedAbort(cookie,False)

    #Figure out how many pics are needed and then close socket

    input = input.split(",")[1]

    image_data = input # Do your magical Image processing here!!

    #user is global (line 388), use it with cv2_img for authentication
    #OpenCV part decode and encode
    img = imread(io.BytesIO(base64.b64decode(image_data)))

    cutImg = np.asarray(FaceDetection.cut_rectangle(copy.deepcopy(img)))

    cv2_img = FaceDetection.make_rectangle(img)

    cv2.imwrite("reconstructed.jpg", cv2_img)

    retval, buffer = cv2.imencode('.jpg', cv2_img)

    b = base64.b64encode(buffer)

    b = b.decode()

    image_data = "data:image/jpeg;base64," + b

    print("Check : {} < 5, {} < {}, {} > 50".format(len(ws.createPictures),len(cutImg),len(img),len(cutImg)))
    print(len(ws.createPictures) < 5 and len(cutImg) < len(img) and len(cutImg) > 50)
    if len(ws.createPictures) < 5 and len(cutImg) < len(img) and len(cutImg) > 50:


        ws.createPictures.append(cutImg)
        #mpl.pyplot.imshow(cutImg)
        #mpl.pyplot.show()

        if len(ws.createPictures) >= 5:

            #ws.authorizedAbort = True
            cookie = request.cookies.get('session_uuid')
            ws.setAuthorizedAbort(cookie,True)

            registerUser(user, ws.createPictures)

            emit('redirect', {'url' : '/validationsignup'})

        else:

            emit('out-image-event', {'image_data': image_data}, namespace='/createWithCamera')
    else:
        ws.addinvalidStreamCount(cookie)
        if ws.checkinvalidStreamCount(cookie):
            #ws.authorizedAbort = True
            cookie = request.cookies.get('session_uuid')
            ws.setAuthorizedAbort(cookie,True)
            emit('redirect', {'url' : '/rejection'})

    emit('out-image-event', {'image_data': image_data}, namespace='/createWithCamera')

#Socket Server side for login
@socketio.on('connect', namespace='/webcamJS')
def test_connect():
    application.logger.info("client connected")

#Socket Server side for registration
@socketio.on('connect', namespace='/createWithCamera')
def test_connect():
    application.logger.info("client connected")

@socketio.on("disconnect", namespace="/createWithCamera")
def disconnected():
    cookie = request.cookies.get('session_uuid')
    ws.setAuthorizedAbort(cookie,True)
    ws.resetinvalidStreamCount(cookie)
    application.logger.info("Websocket client disconnected")

@application.route('/webcamJS', methods=['GET', 'POST'])
def webcamJS():
    return render_template('webcamJS.html', title='Camera')

@application.route('/webcamCreate', methods=['GET', 'POST'])
def webcamCreate():
    return render_template('webcamCreate.html', title='Camera')

@application.route('/logincamera', methods=['GET', 'POST'])
def logincamera():
    #print("logincam",file=sys.stdout)
    form = CameraForm(request.form)

    rejectionDict = {

                    'reason' : 'Unknown',
                    'redirect' : 'login',
                    'redirectPretty' : 'Zurück zur Anmeldung',
    }
                    # We need to check if 'Sign In' or 'Open Camera' got pressed
                    # Activates when Sign in Button is pressed

    #kim: brauchen wir noch nen if request.method == 'POST': ?

    #if form.validate():
    if request.method == 'POST' and form.validate():

        flash('Thanks for logging in')

            #Fetch Username

        global user
        user_uuid = ws.DB.getUser(form.name.data)

        if not user_uuid:
            print("'{}' not found!".format(form.name.data),file=sys.stdout)
            rejectionDict['reason'] = "'{}' not found!".format(form.name.data)
            return render_template('rejection.html', rejectionDict = rejectionDict,  title='Sign In', form=form)

        bbUser = None

        for user in ws.BigBrotherUserList:
            #print(user_uuid,"=",user.uuid)
            if user.uuid == user_uuid:
                bbUser = user
                break

        user = {
            'username': form.name.data,
            'isWorking' : False,
            'uuid' : user_uuid,
            'bbUser': bbUser
        }

        data = {
            "username": form.name.data
        }

        #user['login_attempt_time'] = ws.DB.login_user(uuid_id=user_uuid)

        return render_template('webcamJS.html', title='Camera', data=data)

    return render_template('logincamera.html', title='Login with Camera', form = form)

@application.route('/createcamera', methods=['GET', 'POST'])
def createcamera():
    #print("logincam",file=sys.stdout)
    form = CameraForm(request.form)

    ws.createPictures = []

    rejectionDict = {

                    'reason' : 'Unknown',
                    'redirect' : 'login',
                    'redirectPretty' : 'Zurück zur Anmeldung',
    }

    if request.method == 'POST' and form.validate():

        flash('Thanks for signing up')

            #Fetch Username

        global user
        username = form.name.data
        user_uuid = ws.DB.getUser(username)

        if user_uuid:
            print("'{}' found!".format(form.name.data),file=sys.stdout)
            rejectionDict['reason'] = "'{}' already found!".format(form.name.data)
            return render_template('rejection.html', rejectionDict = rejectionDict,  title='Sign In', form=form)

        user = username

        return render_template('webcamCreate.html', title='Camera')

    return render_template('createcamera.html', title='Create an account', form = form)


@application.route('/verifypicture', methods=['POST'])
def verifyPicture():

    #POST request gets send from main.js in the sendSnapshot() function.

    if request.method == 'POST':

        data = request.get_json()

        #json data needs to have the encoded image & username

        if 'image' not in data:
            return {"redirect": "/rejection"} #, "data": rejection_data}

        if 'username' not in data:
            return {"redirect": "/rejection"} #, "data": rejection_data}

        username = data.get('username')
        img_url = data.get('image').split(',')

        #data url is split into 'image type' and 'actual data'
        if len(img_url) < 2:
            return {"redirect": "/rejection"} #, "data": rejection_data}

        #decode image
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

            #p2p function results are List<bool>, List<float>
            logik = LogikFaceRec.FaceReco()
            (results, dists) = logik.photo_to_photo(user_enc, camera_img)

            print("p2p results: ")
            print(results)
            print(dists)

            #if successfull login but page does not change !
            result = results[0]
            if result is None:
                return {"redirect": "/rejection"} #, "data": rejection_data}
                

                #TODO:
                #the json object returned will be used in main.js to switch to target page
                #this does not work with /validationauthenticated because its not a valid endpoint
                #that page gets usually shown under the /login endpoint with the photo login.
                #return render_template doesnt work here IDK why
                #but if you get render_template to work you need to remove the onload function in main.js 73

                #return render_template('validationauthenticated.html', user=user)
                #return render_template('validationauthenticated.html',  user=user) #, "data": userData}

            else:
                thisUser = BigBrotherUser(user_uuid, user['username'], ws.DB)
                flask_login.login_user(thisUser)

            
                userData = {
                    "name": username
                    
                }

                return {"redirect": "/validationauthenticated"}

        else:
            return {"redirect": "/rejection"} #, "data": rejection_data}

    return {"redirect": "/rejection"} #, "data": rejection_data}

def registerUser(username, pictures):
    user = {
                'username': username
            }
    user_uuid = None

    if not ws.DB.getUser(username):

        #pictures = [user['pic1'],user['pic2'],user['pic3']]

        user_uuid = ws.DB.register_user(username)

        for pic in pictures:


            pic_uuid = ws.DB.insertTrainingPicture(np.asarray(pic, dtype=np.float64),user_uuid)
            print("Inserted Picture for user_uuid: '{}' with pic_uuid: {}".format(user_uuid,pic_uuid),file=sys.stdout)

            #logTime = ws.DB.login_user(user_uuid=user_uuid)
            #ws.DB.update_login(user_uuid=user_uuid,
            #time = logTime,
            #inserted_pic_uuid=pic_uuid)
            #ws.DB.commit()
            #print("Logged picture with pic_uuid: {}".format(user_uuid,pic_uuid),file=sys.stdout)


    else:

            print("'{}' already exists!".format(username),file=sys.stdout)

            #rejectionDict['reason'] = "Benutzername '{}' nicht Verfügbar".format(username)

            #return render_template('rejection.html',  rejectionDict = rejectionDict, title='Reject', form=form)
            emit('redirect', {'url' : '/rejection'})

    #return render_template('validationsignup.html', name=user['username'])
    emit('redirect', {'url' : '/validationsignup'})
    return

"""
def isStreamEmpty():

    print("Empty: ",ws.emptypiccount)
    if ws.emptypiccount > 4:
        ws.emptypiccount = 0
        return True
    else:
        ws.emptypiccount = ws.emptypiccount + 1
        return False
"""

if __name__=='__main__':
    #
    # ENV Variable must be set!
    # Windows: set LOCALDEBUG=True/False
    # Linux: export LOCALDEBUG=True/False
    #
    #if app.config['LOCALDEBUG']:
     #   socketio.run(app)
    #else:
        #socketio.run(app, host='85.214.39.122', port='80', debug=True, ssl_context=('/etc/letsencrypt/live/h2938366.stratoserver.net/fullchain.pem','/etc/letsencrypt/live/h2938366.stratoserver.net/privkey.pem'))

        #socketio.run(app, host='0.0.0.0', port=80, debug=True)
#app.run()
        #app.run(host='85.214.39.122', port='80', ssl_context=('/etc/letsencrypt/live/h2938366.stratoserver.net/fullchain.pem','/etc/letsencrypt/live/h2938366.stratoserver.net/privkey.pem'))
        # socketio.run(application, host='h2938366.stratoserver.net', port='80', debug=True, ssl_context=('fullchain.pem','privkey.pem'))
        application.run(host='0.0.0.0', port=5000)
