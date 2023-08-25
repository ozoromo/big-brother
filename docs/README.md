# Documentation
We are still trying to write the documentation. We will split it up soon so that it 
has a structure that is more readable.

## Frontend-Group
### Deployment
- The project is deployed over Coolify (coolify.adastruct.com) | For username & password contact Mr. D. Foucard
- Build over Docker, Docker file is in project folder
- Main Branch of git-repository gets deployed
- URL: "https://bigbrother.adastruct.com" | Port & Exposed Port: 5000

### Start project
- We used VSCode (https://code.visualstudio.com/)
- Download Python & Flask:
    - Watch these two videos to install flask on VS Code:
    - Install Python 3.10.2: https://www.youtube.com/watch?v=uxZuFm5tmhM
    - IMPORTANT: we need Python 3.10.2 to download all the packages
    - Install Flask on VS Code: https://www.youtube.com/watch?v=S8aFNcYpSfI 
    - Last step on video is to let the code run -> dont work
- Install Visual c++ Redistributables: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170
-> for Package dlib-binary

- Start a virtual environment: "env\scripts\activate" | Type "deactivate" to get out of the virtual environment
-> IMPORTANT: gitignore the env (environment) to avoid committing it to main (create a file named .gitignore)
- Upgrade pip: "python -m pip install --upgrade pip"
- Write on the same terminal, while in your env (environment): pip install ..\..\requirements.txt | If this doesnt work, install them one by one with "python pip install -m [name]"
-> Requirements & versions are written in the requirements.txt file, which is in the project folder | If no versions are mentioned, use current versions (Date: 30.07.2023)
- Type "python -m flask --app .\app\__init__.py --debug run" to start the app
- Open your browser and type in the URL/IP in your terminal

(Over Docker)
- It's possible to start the app over docker
- Install Docker Desktop over "https://www.docker.com/" and run it | Additionaly add the docker plugin in VSCode
- Type: "docker build -t [container name] ." to build the container
- Type: "docker run -p 127.0.0.1:5000 [container name]" to run the container
- Open your browser and type in "127.0.0.1:5000"

### Functionality
- Two ways of registration users
  -> With username + 3 pictures
  -> With username + video
- Three ways of signing in
  -> With username + a picture
  -> With username + video (live face)
  -> With username + video (live gesture)
...
  
- EduVid:

- FaceRec:
  -> recognise face of registered user
  -> face for login via photo or video (live face)
  -> In case of large deviation of the face -> login fails
  -> otherwise success

### Project structure & Routes
- HTML files
    - algorithms.html:
      -> information about our algorithm
    - base.html:
      -> 
    - create.html:
      -> registration with 3 photos + username
    - eduVid.html:
      -> only uploading a video at the moment + name of the video
    - eduVidPlayer.html:
    - gestureReco.html:
      -> login with gesture
      -> needed for photo of certain gesture
      -> connecting to gestureRecognition.js
    - index.html:
    - login.html:
    - logincamera.html:
    - rejection.html:
      -> if certain process fails error message appears
    - team23.html:
      -> the internship team of SS23
    - team21.html: 
      -> the internship team of 2021
    - test.html:
    - userpage.html:
    - validationauthenticated.html:
      -> appears when sign in was successful
    - validationsignup.html:
      -> appears when sign up was successful
    - webcam.html:
      ->
    - webcamJS.html:
      -> connection to main.js

- JS files
    - createWithCamera.js:
      -> taking photo for registration (not used)
    - gestureRecognition.js:
      -> taking photo for login with certain gesture
    - main.js: 
      -> taking photo for login via face recognition

- PY Files
    - __init__.py:
      -> is used to execute the code
      -> contains all routes & their functionalities
    - user_manager.py:
      -> manages the users of the websites
    - user.py:
      -> keeps the information about user
    - utils.py:


## Logik-Group
## Face-recognition
The purpose of "Face-recognition" is to determine whether two images show the same person. 
- During the work we based on article and two youtube videos:
    - https://medium.com/@ageitgey/machine-learning-is-fun-part-4-modern-face-recognition-with-deep-learning-c3cffc121d78   
    - https://www.youtube.com/watch?v=iBomaK2ARyI
    - https://www.youtube.com/watch?v=sz25xxF_AVE
### FaceReco_class
If there is the same person in two images, the program returns the Boolean value "TRUE", otherwise "FALSE".
- Download
    - Python Version: 3.11   
    - https://visualstudio.microsoft.com/downloads/
    - Packages
        - cmake
        - dlib
        - face-recognition
        - numpy
        - opencv-python
          
- Explanation of code 
    - The function takes three parameters: self, image_encoding (encoding of a photo saved in the database), and img2 (image captured from a camera).
    - We start with converting img2 to the RGB color space, using the OpenCV library. 
    - Then we use face_recognition library to compute encodings for img2 (these encodings are numerical representations of the facial features )
    - If no face encodings are detected in the img2, the function returns "False"-value.
    - If at least one face encoding is detected in the img2, we compare the facial encoding of img2 with the image_encoding (encoding from database) using the face_recognition.compare_faces function.
    - This function determines whether the two face encodings belong to the same person.
    - We calculate face distance using the face_recognition.face_distance function. This distance is a measure of similarity between the two facial encodings. A smaller value indicates a greater similarity between the faces.
    - Method returns the results list (with True or False indicating if it's the same person)
      
- More inforamtions
    - We wrote this code with threads, hoping to optimise program, but eventually gave up on this idea - right server did the job
       
### encodings_class
This code is designed to encode raw face images into encodings that can be used with the face_recognition module. It processes images stored in a directory called "toBeEncoded" and creates suitable encoding files in a directory called "encodings". 
It also removes the original image files after encoding.

- Packages
    - such as for faceReco_class

- What exactly is face encoding?
    - A face encoding is basically a way to represent the face using a set of 128 computer-generated measurements. Two different                 pictures of the same person would have similar encoding and two different people would have totally different encoding.
    - For face encoding we use in our code variable encode, which is a numerical representation of the features and characteristics of a         person's face that is extracted and computed by the face_recognition library. The specific type of encode in terms of Python data          types is a 1-dimensional NumPy array. These values from NumPy-array represent the facial features in a way that allows for efficient       comparison and matching. 

- Explanation of code
    - Code retrieves a list of filenames(images) from the "toBeEncoded" folder using the os.listdir() function.
    - A loop iterates through each image file in the "toBeEncoded" folder:
    - Image is read using cv2.imread(). The data about image is appended to the images list.
      The class name is extracted from the filename using os.path.splitext() and appended to the classNames list.
    - A function findEncodings(images, classNames) is defined to loop through the images, their class names and call the findEncoding() function for each of them.
    - The findEncoding(img, name, idx) function takes an image, class name, and index as parameters. The image is converted to RGB color space using cv2.cvtColor().
    The facial encoding of the image is computed using face_recognition.face_encodings().
    - The addToEncodings() function is called to save the encoding to a file in the "encodings" folder. The original image file is removed from "toBeEncoded" folder using os.remove().

- Problems
    - The problem may arise when more than one face is recognized in a single photo. It may happen then that the calculated encodings are        not for the person who wants to log in/register, but for example for the face  on the t-shirt of the person logging in. 
      
### example_usage_FaceReco_class
A code named example_usage_FaceReco_class is basically just an example of using a previously written FaceReco_class.

## Tool stack
- Programming language: [Python](https://docs.python.org/3/)
- Frontend: [Flask](https://flask.palletsprojects.com/en/2.2.x/) Docker
- FaceRecognition and other ML-libraries: 
    - [openCV](https://pypi.org/project/opencv-python/)
    - [OpenFace](https://cmusatyalab.github.io/openface/)
    - [PyTorch](https://pytorch.org/)
    - [TensorFlow](https://www.tensorflow.org/learn)
- Database: [MongoDB](https://www.mongodb.com/)

# Tutorials
- [Introduction to our database](tutorials/introduction_to_our_database.md)
- [Introduction to eduVid](tutorials/introduction_to_eduVid.md)

# Examples
## DatabaseManagement
- [Basic video management](examples/DBM/DatabaseManagement/videoInsertionRetrivalAndDeletion.py)
- [Basic eduVid](examples/eduVid/qa_usage.py)

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

