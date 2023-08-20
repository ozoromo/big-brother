import sys
import os
import uuid

import numpy as np
import cv2

from face_recognition_strategies.strategies.base_strategy import BaseStrategy
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog", "wire_face_recognition"))
from wireUtils import load_images as load_test_imgs
from modifiedFaceRecog import recogFace
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "DBM"))
import DatabaseManagement as DBM

class PCAStrategy(BaseStrategy):
    def __init__(self, user_uuid):
        self.DB = DBM.wire_DB()
        self.set_user_uuid(user_uuid)
        self.username = self.DB.getUserWithId(user_uuid)

    def set_user_uuid(self, user_uuid):
        if type(user_uuid) == uuid.UUID:
            self.user_uuid = user_uuid
        else:
            raise ValueError

    def execute(self, training_data, testing_data):
        """
        Executes the openface strategy.

        Arguments:
        training_data -- List of images to train with.
        testing_data -- Single images to match with the training data.

        Return:
        Returns True if the test data matches with the training data and False
        otherwise.
        """
        recog_usernames = recogFace([testing_data, self.user_uuid])
        return self.username in recog_usernames

    def preprocess_data(self, training_data, testing_data):
        max_shape = (0, 0)
        for d in training_data:
            if d.shape[0]*d.shape[1] > max_shape[0]*max_shape[1]:
                max_shape = d.shape

        # TODO: Training data is worked with differently in the algorithm.
        # The algorithm accesses the database directly, which shouldn't be done

        processed_testing_data = cv2.resize(
            testing_data.astype("uint8"),
            dsize=(max_shape[1], max_shape[0]),
            interpolation=cv2.INTER_CUBIC
        )
        return ([], testing_data)
