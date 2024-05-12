'''
Detect and authorize faces in given images using opencv.

Detection is done by fast cascade filters by default. Can be changed to more accurate DNN Models
Authorization is done by comparing the given username with who the trained model recognized on the picture.
The model needs to be trained to recognize the correct labels/usernames, this can be done by adding newly registered faces with the train functions

Note: Expects images to be read using cv.imread. greyscale conversion is done automatically


---------------------------
useful functions to import
---------------------------

- authorize_faces(user_id, images, min_match_ratio=0.8, max_distance=60) -> (bool, np.ndarray)
    checks if the person on the images is considered a match to the username in atleast {min_match_ratio} percent of cases
    also returns np.ndarray with the distances of each picture from the trained person
    min_match_ratio means how many of the images have to be a correct match for the user to be authorized
    Distance is (euclidean?) in multidimensional space of face encodings - the greater the distance (further away) the less similar the faces and distance=0 is perfect match; not percentage

- detect_face(image, mode="crop") -> image
    finds the position of faces in the image and returns a image which
        - (mode="draw") has red rectangles around the faces
        - (mode="crop") is cropped the picture around the first face it found

- train_add_faces(user_id, images, save_model=True)) -> None
    trains the model that all the faces in [images] are the user with id user_id
    save_model = if the trained face recognition model should be written to file after training


'''

import cv2
import numpy as np
import os.path

class cv2Recog:

    def __init__(self):
        # _______ globals _______
        self.detector = self.init_detector()
        self.recognizer_path = os.path.join(os.path.dirname(__file__),"models", "recognizer.yml")
        self.recognizer = self.init_rec()

    # ________ setup of the models ________
    # detector is the model to find the postition of faces in images; currently uses cascade. this is not trained and can hence always use standard detector
    def init_detector(self):
        det = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_default.xml')
        return det


    #recognizer is the model trained on known faces, to recognize who is in a picture. this needs to be trained so loading a previous version may be necessary
    def init_rec(self):
        rec = cv2.face.LBPHFaceRecognizer_create(radius=4, neighbors=12)
        if os.path.exists(self.recognizer_path):
            rec.read(self.recognizer_path)

        return rec




    # ______ funcition defintions _______
    def img_pre(self, img):
        new_img = img
        #possible reformating, depending on given image
        '''try:
            new_img = np.array(new_img.convert("L"), "uint8")
        except:
            if type(new_img) != np.ndarray:
                if isinstance(new_img, Image.Image):  #PIL Image
                    new_img.convert("L") #converting to greyscale just in case
                    new_img = np.array(new_img, "uint8") #convert PIL to numpy array
                else:
                    raise TypeError(f"The given image has to be a numpy array or a PIL Image. Given Type was {type(img)}")'''

        #greyscale
        if len(new_img.shape) >= 3 and new_img.shape[2] == 3: #if it still has 3 color channels
            new_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)

        return  new_img



    def save_rec(self):
        self.recognizer.write(self.recognizer_path)


    def detect_face(self, image, mode="crop", fix_res=True):
        if self.detector == None:
            self.detector = self.init_detector()

        img = self.img_pre(image)

        positions = self.detector.detectMultiScale(img, 1.3, 5)
        final_img = img
        if mode == "crop" and len(positions) != 0:
            (x,y,w,h) = positions[0] #only first face in crop mode
            final_img = final_img[y:y+h, x:x+w]

            #downscale image resolution
            #this is after face detection, to maximize chance of finding a face in the image
            if fix_res:
                height = 150 #fixed height
                scale = height / float(final_img.shape[0])
                width = int(final_img.shape[1] * scale)
                dim = (width, height)
                final_img = cv2.resize(final_img, dim, interpolation = cv2.INTER_AREA)


        elif mode == "draw":
            for (x,y,w,h) in positions: #mark all faces in draw mode
                cv2.rectangle(final_img, (x,y), (x+y, y+h), (0,0,255), 2)


        #debug
        #cv2.imshow("", final_img)
        #cv2.waitKey(0)

        return final_img


    #def authorize_faces(self, user_id: int, images: list, min_match_ratio=0.70, max_distance=175, crop_to_face=True) -> bool:
    def authorize_faces(self, user_id: int, images: list, min_match_ratio=0.70, max_distance=175) -> bool:
        #init models if not done
        if self.detector == None:
            self.detector = self.init_self.detector()

        if self.recognizer == None:
            self.recognizer = self.init_rec()

        #bool array of matches: if recognizer prediction results == user_id && has distance of <= max_distance.
        matches = np.full(shape=(len(images),), fill_value=False, dtype=bool)
        dists = np.zeros(shape=(len(images),))

        for i, img in enumerate(images):
            #detect and crop faces, includes preprocessing

            face_img = self.img_pre(img)

            #check if {user_id} is recognized with atleast {max_distance} confidence values
            img_user_id, dist = self.recognizer.predict(face_img)

            dists[i] = dist
            #print(f'dist {dist} and img_user_id {img_user_id}')
            if dist <= max_distance and img_user_id == user_id:
                matches[i] = True


        #print(f'matches: {matches}')
        #calc ratio of matches
        ratio = np.sum(matches) / matches.shape[0]

        return ratio >= min_match_ratio, dists


    def train_add_faces(self, user_id, images, new_model=False, save_model=False, crop_to_face=False) -> None:
        if self.recognizer == None or new_model==True:
            self.recognizer = self.init_rec()

        processed_imgs = []
        for img in images:
            #preprocess images by cropping to face
            if crop_to_face:
                face = self.detect_face(img)
            else:
                face = self.img_pre(img)

            processed_imgs.append(face)

        #create vector of correct length with the user id
        #
        # Muss das eine Integer User Id sein? Könnten wir auch die UUIDs aus der Datenbank benutzen?
        # Oder Zumindest eine eindeutige Umwandlung von UUID in Interger ID programmieren?  --Julius
        id_vec = np.full(shape=(len(images),), fill_value=user_id)

        self.recognizer.update(processed_imgs, id_vec)

        if save_model == True:
            self.save_rec()


    def dist_between_two_pics(self, train_img, test_img, crop_to_face = False):
        #train model on the train image
        #always use a new model to get results for only these two images
        temp_user_id = 60
        self.train_add_faces(temp_user_id, [train_img], new_model=True, crop_to_face=crop_to_face)

        #test if the same person is recognized and if so, with what distance
        if crop_to_face:
            test_img = self.detect_face(test_img)
        else:
            test_img = self.img_pre(test_img)
        #cv2.imshow("",test_img)
        #cv2.waitKey(0)

        #check if {user_id} is recognized with atleast {max_distance} confidence values
        img_user_id, dist = self.recognizer.predict(test_img)

        if img_user_id != temp_user_id:
            raise ValueError("Could not recognize the given user in the test image and hence cannot calculate a distance")



        return dist



    # reset_model()
