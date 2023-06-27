import cv2
import face_recognition
import FaceReco_class
'''
def photo_to_photo(img1, img2):
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

    face_Loc_img1 = face_recognition.face_locations(img1)[0]
    encodeimg1 = face_recognition.face_encodings(img1)[0]
    cv2.rectangle(img1, (face_Loc_img1[3], face_Loc_img1[0]), (face_Loc_img1[1], face_Loc_img1[2]), (255, 0, 255), 2)

    face_Loc_img2 = face_recognition.face_locations(img2)[0]
    encodeimg2 = face_recognition.face_encodings(img2)[0]
    cv2.rectangle(img2, (face_Loc_img2[3], face_Loc_img2[0]), (face_Loc_img2[1], face_Loc_img2[2]), (255, 0, 255), 2)

    results = face_recognition.compare_faces([encodeimg1], encodeimg2)  # true/false
    faceDis = face_recognition.face_distance([encodeimg1], encodeimg2)  # distance between two photos, measure of comparsion in range [0,1]

    print(results, faceDis)     # true if the same person on two photos/false if not
    cv2.putText(img2, f'{results} {round(faceDis[0], 2)}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('img1', img1)
    cv2.imshow('img2', img2)
    cv2.waitKey(0)
'''

f = FaceReco_class.FaceReco()
img2 = face_recognition.load_image_file('ImagesAttendance/Elon Musk.jpg') # image from camera
img1 = face_recognition.load_image_file('ImagesAttendance/Elon Musk.jpg') # image from DB

image_encoding = face_recognition.face_encodings(img1)
f.photo_to_photo(image_encoding[0], img2)

