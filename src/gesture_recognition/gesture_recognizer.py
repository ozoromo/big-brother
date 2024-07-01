import os
import mediapipe as mp
#import numpy as np
import visualizer
import cv2
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class GestureRecognizer:
    def __init__(self):
        BaseOptions = mp.tasks.BaseOptions
        GestureRecognizer = mp.tasks.vision.GestureRecognizer
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
        VisionRunningMode = mp.tasks.vision.RunningMode
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands

        # initialize mediapipe
        options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path='./src/gesture_recognition/mp_hand_gesture/gesture_recognizer.task'),
        running_mode=VisionRunningMode.IMAGE)

        self.recognizer = GestureRecognizer.create_from_options(options)


    #def preprocess(self, img: np.ndarray) -> tuple[Tensor, tuple[int, int], tuple[int, int]]:
    #    pass

    def recognize(self, frame):
        """
        Receive a frame, preprocess it and return 
        """
        # Flip the frame vertically
        frame = cv2.flip(frame, 1)
        
        #x, y, c = frame.shape

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        frame_timestamp_ms = int(time.time() * 1000)
        res = self.recognizer.recognize(mp_image)
       
        return visualizer.annotate_image_with_gesture_and_landmarks(frame, res)
        
        
        #return frame, class_name
  
