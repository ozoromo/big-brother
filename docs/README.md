# Documentation
In this documentation you can find [tutorials](##tutorials) and [examples](#examples)
of the code that has been implemented in this project. The tutorials section
details some of the thought process and design decisions when implementing this
project and the examples give concrete code examples on how you might want to use
the code. You can directly execute the code in the folder in which you find them.

## General folder stucture
In this section we briefly explain how the folders in the root directory are
for. And perhaps where you might be able to find more detailed explanations:
- `benchmarks`: This folder contains all the benchmark tests.
- `docs`: This folder contains all the documentation. You won't find any
documentation outside of this folder. We decided that, because documenting
sub-projects (like face recognition, resture recognition, ...) in it's own
folder could get quite messy if the project gets bigger.
- `res`: All the resources like images or videos that is used (perhaps) multiple
parts of our project can be found here. This folder shouldn't contain code, but
rather data that is used throuout the project.
- `src`: Code that has been implemented during the project can be found here.
Because the folder structure in here might be a little unclear we are going to
clarify it in the following:
    - `database_management`: This contains various database access
    functionalities that can be used.
    - `eduVid`: The implementation of video analysis is contained within this
    folder. Below there is a tutorial that explains this folder in more detail.
    - `face_recog`: This folder contains all face recognition strategies that
    have been implemented. Various face recognition strategies have been
    implemented during the life-time of this project. You can find more
    detailed information on those algorithms in the [tutorials](##tutorials)
    section.
    - `gesture_recognition`: The gesture recognition algorithm is implemented
    in here. Feel free to implement more gesture recognition algorithms. More
    detailed information in the [tutorials](##tutorials) section.
    - `web_application`: This is the flask abpplication. The other projects in
    this projects are implemented in here in order to make those 
    implementations accessible to a user.

## Tutorials
- [Introduction to implementation of the web application](tutorials/introduction_to_implementation_of_the_web_application.md)
- [Introduction to our database](tutorials/introduction_to_our_database.md)
- [Introduction to eduVid](tutorials/introduction_to_eduVid.md)
- [Explanation of face recognition strategy: face recognition lib](tutorials/explanation_of_face_recognition_lib)
- [Explanation of face recognition strategy: ultra\_light\_and\_openface](tutorials/explanation_of_ultra_light_and_openface.md)

## Examples
- [Basic video management in database](examples/database_management/example_vdideo_insertion_retrival_and_deletion.py)
- [Basic eduVid](examples/eduVid/qa_usage.py)
- [Basic gesture recognition workflow](examples/gesture_recognition/example_gesture_recognizer.py)
- Face recognition:
    - [Basic usage of face\_recognition\_lib](examples/face_recog/face_recognition_lib/example_usage_FaceReco_class.py)
    - [Basic usage of haar\_and\_lbph](examples/face_recog/haar_and_lbph/example_cv2_recog.py)

## API Documentation
The API documentation can be found in [here](API%20Documentation/README.md).
Install `mkdocs` with `pip install mkdocs` and execute `mkdocs serve` in 
this folder (`<github-repo-root>/docs/`) in order to have better navigation 
for the documentation.

### Maintainance/Generation
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

