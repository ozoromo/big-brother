import sys
import os

import numpy as np
import cv2

from face_recognition_strategies.strategies.base_strategy import BaseStrategy
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "face_recog", "ultra_light_and_openface"))
import FaceDetection

class OpenfaceStrategy(BaseStrategy):
    def execute(self, training_data, testing_data):
        """
        Executes the openface strategy.

        Arguments:
        training_data -- List of images to train with.
        testing_data -- A single test image.

        Return:
        Returns True if the test data matches with the training data and False
        otherwise.
        """
        try:
            return FaceDetection.authorize_user(training_data, testing_data)
        except Exception:
            print("openface Algo failed")
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
            float32_im = np.float32(im.astype("uint8"))
            im_RGB = cv2.cvtColor(
                (float32_im / 256).astype("uint8"), 
                cv2.COLOR_BGR2RGB
            )
            processed_training_data.append(im_RGB)

        processed_testing_data = cv2.resize(
            testing_data.astype("uint8"),
            dsize=(max_shape[1], max_shape[0]),
            interpolation=cv2.INTER_CUBIC
        )
        return (processed_testing_data, processed_testing_data)
