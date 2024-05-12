import os
import sys
import uuid

import numpy as np

from face_recognition_strategies.context import FaceRecognitionContext
from face_recognition_strategies.strategies.cv2_strategy import Cv2Strategy
from face_recognition_strategies.strategies.openface_strategy import OpenfaceStrategy
from face_recognition_strategies.strategies.principle_component_analysis_strategy import PCAStrategy

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
from database_management.picture_database import PictureDatabase

def authenticate_picture(user_uuid: uuid.UUID, picture: np.ndarray):
    """
    Authenticates picture from a certain user.

    Arguments:
    user_uuid -- This is the user_uuid of the user that you want to authenticate.
    WARNING: We assume that the user with the given uuid already exists!

    Return:
    Returns True if the user has been authenticated and False otherwise.
    """
    DB = PictureDatabase()
    username = DB.get_user_with_id(user_uuid)
    training_data, _ = DB.get_pictures(user_uuid=user_uuid)

    face_recognition_context = FaceRecognitionContext(Cv2Strategy())

    face_recognition_context.set_strategy(Cv2Strategy())
    cv_result = face_recognition_context.execute_strategy(
        training_data, picture
    )

    face_recognition_context.set_strategy(OpenfaceStrategy())
    openface_result = face_recognition_context.execute_strategy(
        training_data, picture
    )

    face_recognition_context.set_strategy(PCAStrategy(user_uuid))
    pca_result = face_recognition_context.execute_strategy(
        training_data, picture
    )

    # algorithm is weighted
    algo_score = int(cv_result) * 60 + int(openface_result) * 20 + int(pca_result) * 20
    THRESHHOLD_FOR_WEIGHTED_SCORE = 40
    return algo_score >= THRESHHOLD_FOR_WEIGHTED_SCORE
