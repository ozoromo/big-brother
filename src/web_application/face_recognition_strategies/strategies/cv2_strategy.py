import sys
import os

import numpy as np
import cv2

from face_recognition_strategies.strategies.base_strategy import BaseStrategy
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..","face_recog", "haar_and_lbph"))
from cv2RecogClass import cv2Recog

class Cv2Strategy(BaseStrategy):
    def execute(self, training_data, testing_data):
        """
        Executes the cv2 strategy.

        Arguments:
        training_data -- List of images to train with.
        testing_data -- Single image that should compared with the training data.

        Return:
        Returns True if the test data matches with the training data and False
        otherwise.
        """
        recognizer = cv2Recog()
        temp_id = 22  # random temporary id
        recognizer.train_add_faces(temp_id, training_data, save_model=False)

        dists = np.zeros(len(training_data))
        try:
            for train_index, train_im in enumerate(training_data):
                dists[train_index] = recognizer.dist_between_two_pics(
                    train_im, testing_data
                )
            dist = np.min(dists)
            return dist < 125
        except cv2.error:
            print("cv2 Algo failed!")
            return False

    def preprocess_data(self, training_data, testing_data):
        max_shape = (0, 0)
        for im in training_data:
            if im.shape[0]*im.shape[1] > max_shape[0]*max_shape[1]:
                max_shape = im.shape

        processed_training_data = []
        for im in training_data:
            im = cv2.resize(
                im.astype("uint8"),
                dsize=(max_shape[1], max_shape[0]),
                interpolation=cv2.INTER_CUBIC
            )
            norm_im = cv2.normalize(
                src=im.astype("uint8"), dst=None,
                alpha=0, beta=255,
                norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
            )
            processed_training_data.append(norm_im)

        resized_testing_data = cv2.resize(
            testing_data.astype("uint8"),
            dsize=(max_shape[1], max_shape[0]),
            interpolation=cv2.INTER_CUBIC
        )
        processed_testing_data = cv2.normalize(
            src=resized_testing_data.astype("uint8"), dst=None,
            alpha=0, beta=255,
            norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
        )

        return (processed_training_data, processed_testing_data)
