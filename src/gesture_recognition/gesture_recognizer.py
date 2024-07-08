import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
from mediapipe.framework.formats import landmark_pb2

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class GestureRecognizer:
    def __init__(self):
        # Ensure the correct relative path to the gesture_recognizer.task file
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, 'exported_model', 'gesture_recognizer.task')
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(base_options=base_options)
        self.recognizer = vision.GestureRecognizer.create_from_options(options)

    def recognize(self, image):
        # Convert the image to the required format for Mediapipe
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(rgb_image))
        
        # Perform gesture recognition
        recognition_result = self.recognizer.recognize(mp_image)

        if not recognition_result.gestures:
            return image, "No gesture recognized"
        top_gesture = recognition_result.gestures[0][0]
        if top_gesture.score < 0.50:
            return image, "No gesture recognized"
        top_gesture = recognition_result.gestures[0][0]
        hand_landmarks_list = recognition_result.hand_landmarks

        # Annotate the image
        annotated_image = rgb_image.copy()
        for hand_landmarks in hand_landmarks_list:
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])
            mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks_proto,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

        # Convert the annotated image back to BGR for consistency with OpenCV
        annotated_image_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        return annotated_image_bgr, top_gesture.category_name