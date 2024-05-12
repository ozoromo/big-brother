import os

import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model


class GestureRecognizer:
    def __init__(self):
        # initialize mediapipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

        # initialize tensorflow
        # Load the gesture recognizer model

        path = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.abspath(os.path.join(path, 'mp_hand_gesture'))
        self.model = load_model(model_dir)

        gesture_dir = os.path.abspath(os.path.join(path, 'gesture.names'))

        # Load class names
        with open(gesture_dir, 'r') as f:
            self.class_names = f.read().split('\n')

    def recognize(self, frame):
        """
        Receive a frame, then return the frame with the recognized hand gesture highlighted as well as the name of the gesture.
        """
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
        return frame, class_name
