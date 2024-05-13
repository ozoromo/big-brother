import os

import tensorflow as tf
from tensorflow.keras.models import load_model

import cv2
import numpy as np
import mediapipe as mp
import torch
from albumentations.pytorch import ToTensorV2

COLOR = (0, 255, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX


class GestureRecognizer:
    def __init__(self):
        # initialize mediapipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=0, static_image_mode=False, max_num_hands=2, min_detection_confidence=0.8
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.conf = OmegaConf.load()

        # initialize tensorflow
        # Load the gesture recognizer model

    def preprocess(img: np.ndarray, transform) -> Tuple[Tensor, Tuple[int, int], Tuple[int, int]]:
        """
        Preprocess the image before feeding it to the model.
        Parameters
        ----------
        img: np.ndarray
            input image
        transform :
            albumentation transforms
        """
        height, width = img.shape[0], img.shape[1]
        transformed_image = transform(image=img)
        processed_image = transformed_image["image"] / 255.0
        return processed_image, (width, height)


    def get_transform_for_inf(transform_config: DictConfig):
        transforms_list = [getattr(A, key)(**params) for key, params in transform_config.items()]
        transforms_list.append(ToTensorV2())
        return A.Compose(transforms_list)


    def recognize(self, frame):
        """
        Receive a frame, preprocess it and return 
        """

        processed_image, size = GestureRecognizer.preprocess(frame, transform)
                with torch.no_grad():
                    output = detector([processed_image])[0]
                boxes = output["boxes"][:num_hands]
                scores = output["scores"][:num_hands]
                labels = output["labels"][:num_hands]


        return frame, class_name

        x, y, c = frame.shape

        # Flip the frame vertically
        frame = cv2.flip(frame, 1)

        # DETECT HAND KEYPOINTS
        framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Get hand landmark prediction
        result = self.hands.process(framergb)

        class_name = ""

        # post process the result
        if result.multi_hand_landmarks:
            landmarks = []
            for handslms in result.multi_hand_landmarks:
                for lm in handslms.landmark:
                    # print(id, lm)
                    lmx = int(lm.x * x)
                    lmy = int(lm.y * y)

                    landmarks.append([lmx, lmy])

                # Drawing landmarks on frames
                self.mp_draw.draw_landmarks(frame, handslms, self.mp_hands.HAND_CONNECTIONS)

                # Predict gesture in Hand Gesture Recognition project
                prediction = self.model.predict([landmarks])
                class_id = np.argmax(prediction)
                class_name = self.class_names[class_id]


