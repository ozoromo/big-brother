# Documentation

## Frontend-Group
### Functionality
- Two ways of registration users
  - With username + 3 pictures
  - With username + video
- Three ways of signing in
  - With username + a picture
  - With username + video (live face)
  - With username + video (live gesture)
...
  
- EduVid:
  - User uploads Video in .mp4
  - speech recognition performed to obtain transcription
  - then transcription preparation
    - detailed process description
    - context extraction
  - User questions
    - is basis for answers
  - return Timestamps
    - indicate video moments
    - correspond to displayed answers

- GestureRec:
  - 

- FaceRec:
  - recognise face of registered user
  - face for login via photo or video (live face)
  - In case of large deviation of the face -> login fails
  - otherwise success

### Project structure & Routes
- HTML files
    - algorithms.html:
      - information about our algorithm
    - base.html:
      - 
    - create.html:
      -> registration with 3 photos + username
    - eduVid.html:
      - only uploading a video at the moment + name of the video
    - eduVidPlayer.html:
    - gestureReco.html:
      - login with gesture
      - needed for photo of certain gesture
      - connecting to gestureRecognition.js
    - index.html:
    - login.html:
    - logincamera.html:
    - rejection.html:
      - if certain process fails error message appears
    - team23.html:
      - the internship team of SS23
    - team21.html: 
      - the internship team of 2021
    - test.html:
    - userpage.html:
    - validationauthenticated.html:
      - appears when sign in was successful
    - validationsignup.html:
      - appears when sign up was successful
    - webcam.html:
      - 
    - webcamJS.html:
      - connection to main.js

- JS files
    - eduVid.js:
      - 
    - gestureRecognition.js:
      - taking photo for ... with certain gesture
    - main.js: 
      - live Camera for login
      - taking photo for login via face recognition


- PY Files
    - __init__.py:
      - is used to execute the code
      - contains all routes & their functionalities
    - user_manager.py:
      - manages the users of the websites
    - user.py:
      - keeps the information about user
    - utils.py:

# Tutorials
- [Introduction to our database](tutorials/introduction_to_our_database.md)
- [Introduction to eduVid](tutorials/introduction_to_eduVid.md)
- [Explanation of face recognition lib](tutorials/explanation_of_face_recognition_lib)

# Examples
- [Basic video management](examples/DBM/DatabaseManagement/videoInsertionRetrivalAndDeletion.py)
- [Basic eduVid](examples/eduVid/qa_usage.py)
- [Basic gesture recognition workflow](examples/gesture_recognition/example_gesture_recognizer.py)

# API Documentation
The API documentation can be found in [here](API%20Documentation/README.md).
Install `mkdocs` with `pip install mkdocs` and execute `mkdocs serve` in 
this folder (`<github-repo-root>/docs/`) in order to have better navigation 
for the documentation.

## Maintainance/Generation
In order to generate the API Documentation we use
[pydoc-markdown](https://pypi.org/project/pydoc-markdown/). In order to compile
go to the [generator](.generator)-directory and call:
```
pydoc-markdown
```
in the command window. If you add files or functions make sure that they 
are also visible in the API Documentation after using `pydoc-markdown`. 
If not you might modify the 
[pydoc-markdown.yml](.generator/pydoc-markdown.yml)-file:
- Perhaps you need to add a new path in `search\_path` or
- Add a new `title`, `name` or `contents` in the `pages`-section to make
it work.

