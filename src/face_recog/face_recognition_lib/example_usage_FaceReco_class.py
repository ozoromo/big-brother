import cv2
import face_recognition
import FaceReco_class

f = FaceReco_class.FaceReco()
img2 = face_recognition.load_image_file('ImagesAttendance/Elon Musk.jpg') # image from camera
img1 = face_recognition.load_image_file('ImagesAttendance/Elon Musk.jpg') # image from DB

image_encoding = face_recognition.face_encodings(img1)
f.photo_to_photo(image_encoding[0], img2)

