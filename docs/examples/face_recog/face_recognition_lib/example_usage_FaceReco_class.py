###############################################
#         Make THIS script executable         #
###############################################
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src", "face_recog", "face_recognition_lib"))

###############################################
#       The actual program starts here        #
###############################################
import cv2
import face_recognition
import FaceReco_class

f = FaceReco_class.FaceReco()
testing_image = face_recognition.load_image_file("../../../../res/testImages/merkel.jpg")
training_image = face_recognition.load_image_file("../../../../res/testImages/merkel2.jpg") # image from DB

image_encoding = face_recognition.face_encodings(training_image)
print(f.photo_to_photo(image_encoding[0], testing_image))

