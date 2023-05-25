# Documentation
We are still trying to write the documentation. We will split it up soon so that it 
has a structure that is more readable.

## Frontend-Group
- Run Code:
- Watch these two videos to install flask on VS Code:
- Install Python 3.10.2: https://www.youtube.com/watch?v=uxZuFm5tmhM
-> IMPORTANT: we need Python 3.10.2 to download all the packages
- Install Flask on VS Code: https://www.youtube.com/watch?v=S8aFNcYpSfI 
- Last step on video ist to let the code run -> dont work
- Install Visual c++: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170
-> for Package dlib-binary
- Write on the same terminal, while in your env (environment): pip install ..\..\requirements.txt
- Write: python -m flask --app .\app\__init__.py --debug run
- If doesnt run install the package it requires (one line above you input): pip install ... and again write the code above to let it run
- commands for packages you could need:
- PIL: pip install pillow opencv-python opencv-contrib-python
- Opencv-python: pip install opencv-python opencv-contrib-python
- wtforms: pip install wtforms==2.3.3
- Flask_SocketIO= pip install Flask_SocketIO==4.3.1
-  routes, structures, functionalities, explanation 
## Logik-Group

## Database-Group
### MongoDB Ressources
- Getting Started:
    - Introduction into how it works: 
      https://www.mongodb.com/docs/manual/tutorial/getting-started/
    - Setting atlas up: https://www.mongodb.com/docs/atlas/getting-started/ 
    - Using database (as Video): https://www.youtube.com/watch?v=ofme2o29ngU
      -> Similar to first link
- With Python (and pymongo):
    - Introductory: https://www.youtube.com/watch?v=rE\_bJl2GAY8
    - Reading more about it: 
        - Very short tutorial: https://www.mongodb.com/docs/drivers/pymongo/
        - https://pymongo.readthedocs.io/en/stable/
          -> https://pymongo.readthedocs.io/en/stable/tutorial.html
- Handling very big files: MongoDB doesn't allow you to store files that
are larger than 16MB. In order to store them you would need GridFs. 
There are some useful resources:
    - Overview: https://www.youtube.com/watch?v=GDUbWNJLPnc
    - Documentation: https://www.mongodb.com/docs/manual/core/gridfs/
    - With pymongo: 
        - Introduction: https://pymongo.readthedocs.io/en/stable/examples/gridfs.html
        - Read more: https://pymongo.readthedocs.io/en/stable/api/gridfs/index.html#module-gridfs
- Design: 
    - https://www.youtube.com/watch?v=leNCfU5SYR8
    - Schema Design Patterns: https://www.mongodb.com/blog/post/building-with-patterns-a-summary
    - How not to design - Anti-patterns: https://www.youtube.com/watch?v=8CZs-0it9r4&list=PL4RCxklHWZ9uluV0YBxeuwpEa0FWdmCRy

### MongoDB Example code
We store the images and videos as binary data in the fields of the documents. Here is some example code:
- Store images: Own example (without GridFS)
    ```python
    import pymongo
    from pymongo import MongoClient
    import base64

    def conv_image_to_bin(image):
        with open(image, "rb") as f:
            image_enc = base64.b64encode(f.read())

        return image_enc

    # image is the binary data from DB
    def conv_bin_to_image(image):
        image = base64.b64decode(image)
        f = 'stored.png'
        with open(f, 'wb') as f:
            f.write(image)

    cluster = MongoClient("...")
    db = cluster["..."]; collection = db["..."]

    # seding: id: some id; filenameOfImage: In local directory
    send = {
        "_id": id
        "image": conv_image_to_bin(filenameOfImage) # binary data of image
    }
    collection.insert_one(send)

    # getting image: store: path where I want to store image
    got = collection.find_one({"_id": 0})
    conv_bin_to_image(store)
    ```
- Store with GridFS: Es assume the functions above have already
been declared
    ```python
    import pymongo
    from pymongo import MongoClient
    import base64

    # declare functions

    cluster = MongoClient("")
    db = cluster["..."]
    collection = db["..."]

    fs = gridfs.GridFS(db)
    a = fs.put(
        conv_image_to_bin("image/path.png"), 
        _id = 0, 
        filename="Sylphid snacking.png"
    )
    print(a) # 0
    conv_bin_to_image(fs.get(a).read())
    ```

## Tool stack
- Programming language: [Python](https://docs.python.org/3/)
- Frontend: [Flask](https://flask.palletsprojects.com/en/2.2.x/) Docker
- FaceRecognition and other ML-libraries: 
    - [openCV](https://pypi.org/project/opencv-python/)
    - [OpenFace](https://cmusatyalab.github.io/openface/)
    - [PyTorch](https://pytorch.org/)
    - [TensorFlow](https://www.tensorflow.org/learn)
- Database: [MongoDB](https://www.mongodb.com/)
