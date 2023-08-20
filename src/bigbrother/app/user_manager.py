import os
import sys
import time
import queue
import uuid
import typing


import numpy as np
import cv2


from app.user import BigBrotherUser

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog", "haar_and_lbph"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog", "wire_face_recognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog", "ultra_light_and_openface"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "DBM"))

import FaceDetection
from wireUtils import load_images as load_test_imgs
from modifiedFaceRecog import recogFace
from face_rec_main import train_add_faces, authorize_faces
from cv2RecogClass import cv2Recog

from face_recognition_strategies.context import FaceRecognitionContext
from face_recognition_strategies.strategies.cv2_strategy import Cv2Strategy
from face_recognition_strategies.strategies.openface_strategy import OpenfaceStrategy
from face_recognition_strategies.strategies.principle_component_analysis_strategy import PCAStrategy

import DatabaseManagement as DBM


class UserManager:
    """
    This class manages the users of the websites.

    It manages the user and keeps information about them that needs to get
    accessed in other conponents of the frontend. This is used with the
    login maanger of flask in order to keep track of sessions.
    """
    def __init__(self):
        DB = DBM.wire_DB()

        # Keeps track of the users and their session keys
        self.BigBrotherUserList = []
        userDict = DB.getUsers().items()
        for key, value in DB.getUsers().items():
            self.BigBrotherUserList.append(BigBrotherUser(key, value, DB))

    def get_user_by_id(self, user_uuid: uuid.UUID) -> typing.Optional[BigBrotherUser]:
        """
        Searches and returns the a user with a certain id.

        Arguments:
        user_uuid -- The ID of the user that you are trying to search.

        Return:
        Returns the user with the give ID. Returns None if the user
        with the ID doesn't exist.

        Exception:
        TypeError -- Gets risen if the type of the arguments is incorrect.
        """
        if type(user_uuid) != uuid.UUID:
            raise TypeError

        # TODO: Implement a more efficient way of searching
        for user in self.BigBrotherUserList:
            if user.uuid == user_uuid:
                return user
        return None
