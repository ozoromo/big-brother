import os

import tensorflow as tf
from tensorflow.keras.models import load_model

import cv2
import numpy as np
import mediapipe as mp
import torch
import yaml
from PIL import Image
import albumentations as Alb
from albumentations.pytorch import ToTensorV2
from omegaconf import DictConfig, OmegaConf
from torch import Tensor
from torchvision import models, transforms
import torch.nn.functional as F

COLOR = (0, 255, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX

path = os.path.dirname(os.path.abspath(__file__))

yaml_path = os.path.abspath(os.path.join(path, 'mp_hand_gesture/ResNext50.yaml'))
with open(yaml_path, 'r') as file:
    config = yaml.safe_load(file)

# Initialize the model
model_name = config['model']['name']
if model_name == 'ResNext50':
    model = models.resnext50_32x4d(pretrained=config['model']['pretrained'])
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, len(config['dataset']['targets']))  # Number of classes

# Load the state dictionary
state_dict_path = os.path.abspath(os.path.join(path, 'mp_hand_gesture/ResNext50.pth'))
state_dict = torch.load(state_dict_path, map_location=torch.device('cpu'))
model_state_dict = state_dict.get('MODEL_STATE', state_dict)
missing_keys, unexpected_keys = model.load_state_dict(model_state_dict, strict=False)
print(f"Missing keys: {missing_keys}")
print(f"Unexpected keys: {unexpected_keys}")

# Set the model to evaluation mode
model.eval()

class GestureRecognizer:
    def __init__(self):
        # initialize mediapipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=0, static_image_mode=False, max_num_hands=2, min_detection_confidence=0.6
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        self.model = model
        self.transform = self.get_transform_for_inf()
        self.class_names = config['dataset']['targets']
        
        for i in range(0,10):
            print(self.class_names)

    def preprocess(self, img: np.ndarray) -> tuple[Tensor, tuple[int, int], tuple[int, int]]:
        """
        Preproc image for model input
        Parameters
        ----------
        img: np.ndarray
            input image
        transform :
            albumentation transforms
        """
        transform = self.transform
        height, width = img.shape[0], img.shape[1]
        transformed_image = transform(image=img)
        processed_image = transformed_image["image"] / 255.0
        processed_image = processed_image.unsqueeze(0)
        return processed_image, (width, height)

    @staticmethod
    def get_transform_for_inf():
        """
        Create list of transforms from config
        """
        transform_config = OmegaConf.load(yaml_path).test_transforms
        
        transforms_list = [getattr(Alb, key)(**params) for key, params in transform_config.items()]
        transforms_list.append(ToTensorV2())
        return Alb.Compose(transforms_list)

    def recognize(self, frame):
        """
        Receive a frame, preprocess it and return 
        """
        # Flip the frame vertically
        frame = cv2.flip(frame, 1)
        
        x, y, c = frame.shape


        # DETECT HAND KEYPOINTS
        framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Get hand landmark prediction
        result = self.hands.process(framergb)

        class_name = ""


        # post process the result
        if result.multi_hand_landmarks:
            landmarks = []
            for handslms in result.multi_hand_landmarks:
                #hand_bbox = self._get_hand_bbox(handslms, x, y)
                #hand_img = frame[hand_bbox[1]:hand_bbox[3], hand_bbox[0]:hand_bbox[2]]
                #hand_img = Image.fromarray(hand_img)

                input_tensor = self.preprocess(frame)
                with torch.no_grad():
                    prediction = self.model(input_tensor[0])
                class_id = torch.argmax(prediction, dim=1).item()
                class_name = self.class_names[class_id]

                for i in range(0,100):
                    print(f"Class id: {class_id}, class name: {class_name}")
                # Drawing landmarks on frames
                self.mp_draw.draw_landmarks(frame, handslms, self.mp_hands.HAND_CONNECTIONS)
        
        return frame, class_name
    
    def _get_hand_bbox(self, hand_landmarks, img_width, img_height):
        x_min, y_min = img_width, img_height
        x_max = y_max = 0
        for lm in hand_landmarks.landmark:
            x, y = int(lm.x * img_width), int(lm.y * img_height)
            if x < x_min:
                x_min = x
            if y < y_min:
                y_min = y
            if x > x_max:
                x_max = x
            if y > y_max:
                y_max = y
        return [x_min, y_min, x_max, y_max]


