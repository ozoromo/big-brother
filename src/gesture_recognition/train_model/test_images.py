# STEP 1: Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from visualizer import display_batch_of_images_with_gestures_and_hand_landmarks 

# STEP 2: Create an GestureRecognizer object.
base_options = python.BaseOptions(model_asset_path='exported_model/gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options)
recognizer = vision.GestureRecognizer.create_from_options(options)
images = []
results = []
IMAGE_FILENAMES = ['data_test/new_model/1.jpg','data_test/new_model/2.jpg','data_test/new_model/call.jpg','data_test/new_model/fist.jpg',
                   'data_test/new_model/none.jpg','data_test/new_model/ok.jpg','data_test/new_model/stop.jpg']
for image_file_name in IMAGE_FILENAMES:
  # STEP 3: Load the input image.
  image = mp.Image.create_from_file(image_file_name)

  # STEP 4: Recognize gestures in the input image.
  recognition_result = recognizer.recognize(image)

  # STEP 5: Process the result. In this case, visualize it.
  images.append(image)
  top_gesture = recognition_result.gestures[0][0]
  hand_landmarks = recognition_result.hand_landmarks
  results.append((top_gesture, hand_landmarks))

display_batch_of_images_with_gestures_and_hand_landmarks(images, results)