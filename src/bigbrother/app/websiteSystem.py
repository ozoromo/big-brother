import os
import sys
import time
import queue


import numpy as np
import cv2


from app.user import BigBrotherUser

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "FaceRecognition", "haar_and_lbph"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "FaceRecognition", "WireFaceRecognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "FaceRecognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "DBM"))

import FaceDetection
from wireUtils import load_images as load_test_imgs
from modifiedFaceRecog import recogFace
from face_rec_main import train_add_faces, authorize_faces
from cv2RecogClass import cv2Recog

import DatabaseManagement as DBM


class websiteSystem:
    def __init__(self):
        self.createPictures = []
        self.authorizedFlag = False
        self.authorizedAbort = False
        self.emptypiccount = 0
        self.WEBCAM_IMAGE_QUEUE_LOGIN = queue.Queue()
        self.WEBCAM_IMAGE_QUEUE_CREATE = queue.Queue()

        self.WEBCAM_IMAGE_QUEUE_LOGIN_DICT = {}
        self.authorizedFlagDict = {}
        self.authorizedAbortDict = {}
        self.invalidStreamCount = {}

        self.DB = DBM.wire_DB()

        self.BigBrotherUserList = []
        userDict = self.DB.getUsers().items()
        userCount = len(userDict)
        counter = 0
        for key, value in self.DB.getUsers().items():
            self.BigBrotherUserList.append(BigBrotherUser(key, value, self.DB))
            counter += 1
            if round((counter / userCount) * 100) % 25 == 0:
                print("{}% finished...".format(round((counter / userCount) * 100)))

        def getBBUser(self, **kwargs):
            username = ""
            uuid = None
            isValidArgument = False

            # TODO: This can be done easier and cleaner with more modern python
            for key, value in kwargs.items():
                if key == "username":
                    if type(value) == str:
                        username = value
                        isValidArgument = True
                    else:
                        raise RuntimeException("invalid username! : {}".format(value))
                if key == "uuid":
                    if type(value) == uuid.UUID:
                        uuid = value
                        isValidArgument = True
                    elif type(value) == str:
                        uuid = uuid.UUID(value)
                        isValidArgument = True
                    else:
                        raise RuntimeException("invalid uuid! : {}".format(value))
            if not isValidArgument:
                raise RuntimeException("Invalid Arguments! : {}".format(kwargs.items()))

            for user in self.BigBrotherUserList:
                if user.uuid == uuid or user.username == username:
                    return user

            return None

    def setAuthorizedAbort(self, session_uuid, value):
        self.authorizedAbortDict[session_uuid] = value

    def setAuthorizedFlag(self, session_uuid, value):
        self.authorizedFlagDict[session_uuid] = value

    def setinvalidStreamCount(self, session_uuid, value):
        self.invalidStreamCount[session_uuid] = value

    def getinvalidStreamCount(self, session_uuid):
        if session_uuid not in self.invalidStreamCount.keys():
            self.invalidStreamCount[session_uuid] = False
        return self.invalidStreamCount[session_uuid]

    def addinvalidStreamCount(self, session_uuid):
        self.invalidStreamCount[session_uuid] = self.invalidStreamCount[session_uuid] + 1

    def resetinvalidStreamCount(self, session_uuid):
        self.invalidStreamCount[session_uuid] = 0

    def checkinvalidStreamCount(self, session_uuid):
        return self.invalidStreamCount[session_uuid] > 20

    def getAuthorizedAbort(self, session_uuid):
        if session_uuid not in self.authorizedAbortDict.keys():
            self.authorizedAbortDict[session_uuid] = False
        return self.authorizedAbortDict[session_uuid]

    def getAuthorizedFlag(self, session_uuid):
        if session_uuid not in self.authorizedFlagDict.keys():
            self.authorizedFlagDict[session_uuid] = False
        return self.authorizedFlagDict[session_uuid]

    def getQueue(self, session_uuid):
        if session_uuid in self.WEBCAM_IMAGE_QUEUE_LOGIN_DICT.keys():
            return self.WEBCAM_IMAGE_QUEUE_LOGIN_DICT[session_uuid]
        else:
            self.WEBCAM_IMAGE_QUEUE_LOGIN_DICT[session_uuid] = queue.Queue()
            return self.WEBCAM_IMAGE_QUEUE_LOGIN_DICT[session_uuid]

    def emptyQueue(self, session_uuid):
        self.WEBCAM_IMAGE_QUEUE_LOGIN_DICT[session_uuid] = queue.Queue()

    def authenticatePicture(self, user, pic, cookie):
        self.authorizedFlag = False
        self.setAuthorizedFlag(cookie, False)

        user_uuid = user["uuid"]

        print(user)
        # TODO: This if statement is definately too long. Make it more consise
        # by extracting functions
        if user_uuid:
            if type(user_uuid) == tuple:
                user_uuid = user_uuid[0]

            recogUsernames = recogFace([pic, user_uuid])

            # TODO: Review and remove if not necessary
            print("Running Query...", file=sys.stdout)
            t0 = time.time()
            print("UUID: ", user_uuid)
            imgs_raw, uuids = self.DB.getTrainingPictures(user_uuid=user_uuid)
            t1 = time.time()
            print("Took: {}s".format(t1-t0), file=sys.stdout)

            maxShape = (0, 0)
            for im in imgs_raw:
                if im.shape[0]*im.shape[1] > maxShape[0]*maxShape[1]:
                    maxShape = im.shape

            imgs_train = []
            resized_imgs = []
            for im in imgs_raw:
                im = cv2.resize(
                    im.astype("uint8"),
                    dsize=(maxShape[1], maxShape[0]),
                    interpolation=cv2.INTER_CUBIC
                )

                norm_im = cv2.normalize(
                    src=im.astype("uint8"), dst=None,
                    alpha=0, beta=255,
                    norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
                )
                imgs_train.append(norm_im)
                float32_im = np.float32(im.astype("uint8"))
                im_RGB = cv2.cvtColor((float32_im / 256).astype("uint8"), cv2.COLOR_BGR2RGB)
                resized_imgs.append(im_RGB)

            # TODO: Why is the temp_ID always set to 22?
            # use temporary integer ID to train a completely new model and check if it recognized the same person in authorisation login picture
            temp_ID = 22

            cv2Inst = cv2Recog()

            # TODO: The code below was commented out! WHY? Shouldn't we add training data?
            # cv2Inst.train_add_faces(temp_ID, imgs_train, save_model=False)

            # Authorize: check if the training pitures are the same person as the given login picture
            cv_result, dists = False, None
            pic = cv2.resize(
                pic.astype("uint8"),
                dsize=(maxShape[1], maxShape[0]),
                interpolation=cv2.INTER_CUBIC
            )

            cv_test_img = cv2.normalize(
                src=pic.astype("uint8"), dst=None,
                alpha=0, beta=255,
                norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
            )

            testDists = np.zeros(len(imgs_train))
            try:
                for train_im_index, train_im in enumerate(imgs_train):
                    testDists[train_im_index] = cv2Inst.dist_between_two_pics(train_im, cv_test_img)
                dists = np.min(testDists)
                cv_result = dists < 125
            except cv2.error:
                print("cv2 Algo failed!")
                pass

            # debug
            print(f"\nOpenCV result: \nmatch? {cv_result} \ndistances: {dists} \n")

            openface_result = False
            try:
                openface_result = FaceDetection.authorize_user(resized_imgs, pic)

                print(f"openface Algo result: {openface_result}")
            except Exception:
                print("openface Algo failed")

            # When Recognised goto validationauthenticated.html
            print(recogUsernames)
            wireMatch = user["username"] in recogUsernames

            # TODO: What do 60, 20 and 20 mean?
            algoScore = int(cv_result) * 60 + int(openface_result) * 20 + int(wireMatch) * 20

            # TODO: Why has 40 been chosen?
            if algoScore >= 40:
                print("User : '{}' recognised!".format(user["username"]), file=sys.stdout)
                print("AlgoScore : {}".format(algoScore))

                self.authorizedFlag = True
                self.setAuthorizedFlag(cookie, True)
                return self.DB.insertTrainingPicture(pic, user_uuid)
            else:
                # TODO: Why is authorizedFlag set to false while the other one authorized flag
                # is set to true?
                self.authorizedFlag = False
                self.setAuthorizedFlag(cookie, True)

                print("User : '{}' not recognised!".format(user["username"]), file=sys.stdout)
                print("AlgoScore : {}".format(algoScore))

                return False
        else:
            self.authorizedFlag = False
            self.setAuthorizedFlag(cookie, False)
            print("'{}' not found!".format(user["username"]), file=sys.stdout)
            return False
