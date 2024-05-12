# Introduction to implementation of the web application
## Folder structure
The folder structure of the web\_application-folder is described in here.
There are two folders to discuss:

- `app`: This package implements the flask application and is called via the
`run.py`-script.
- `face_recognition_strategies`: This implements the algorithms in a
strategy pattern. This makes it easier to switch between differen algorithm
implementations.  
**NOTE**: In the future the pattern can also be used in the benchmark-tests.
It would be necessary to put the `face_recognition_strategies`-folder into
the `face_recog`-folder in order to have a more clear structure.

### app
We describe the folder structure and certain files, that are worth describing,
roughtly:

- `blueprints`: Used in order to structure the routes in the flask project
more clearly based on content. This is a concept provided by flask
(see documentation [here](https://flask.palletsprojects.com/en/2.3.x/blueprints/)).
The different folders inside of the blueprint folders are the blueprints that
are sorted based on their use-case:

    - `logic`: This is a section where the logic of the site is implemented that 
    pretains everything after the login. Video analysis and gesture recogntion
    is implemented in here.
    - `login`: You can find all the login routes in here. Because the login of
    users with different methods is a very big part of our project we decided to
    use a blueprint for it.
    - `main`: Those routes mostly only have information on them that can be
    accessed without having logged in.
    - `user`: This contains all the routes that has anything to do with user
    management except of login. This includes deleting user, looking at history
    of user, registering user...

- `templates`: The HTML-templates can be found in here. The use cases for the
pages are rather self explanatory when you look at the python code that uses those
templates.
- `static`: You can find css-files, js-files, and images in this folder.
- `__init__.py`: We initialize the global variables in here that we use in
our flask application. It's also important to mention that the blueprints have
to be included farther below in order to avoid dependency issues.

## Algorithm strategies

## Registration and login of user
We use an username and three images in order to register a user. The user
can then log in with a camera or a picture of themselfs. If they chose
to log in with a picture a different algorithm will be used than for the
login with the camera. Those can be seen in the code.

## EduVid
This functionality is accesible only if the user is logged in. You may then
upload a 

- file name,
- video,
- json file with timestamps and
- question you want the video content to answer

in order for the video to get analyzed. This may take quite a long time
depending on the length of the video. The json file describes the sections
of the video, meaning what the content of a video is starting from a certain
time (measured in seconds). This can be described with the following example:
```javascript
{
	"time-stamps": [
		{"Intro": 0.0},
		{"Core Idea": 10.0},
		{"Next Steps": 30.0},
		{"Advanced": 300.0},
		{"Conclusion": 500.0},
		{"Outro": 700.0}
	]
}
```
The functionalities are implemented with the EduVid-API. You can find a
tutorial in documentation.

