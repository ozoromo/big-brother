"""
Big Brother Face Recognition Class
Recognize and compare faces (Photo-Video), (Photo-Photo)
"""
import cv2
import face_recognition
import numpy as np
import os
#from datetime import datetime

class FaceReco:

    def photo_to_photo(self, image_encoding, img2):
        '''
        We want to campare, if that's the right person
        If it's the same person on two different photos
        If True: - log in
        If False: - wrong person (no log in)
        Arguments:
            #img1 = single photo already saved in DB
            image_encoding = encoding of the first photo,
            img2 = image from camera (who wants to log in)
        '''

        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        encodeimg2 = face_recognition.face_encodings(img2)[0]
        results = face_recognition.compare_faces([image_encoding], encodeimg2)  # true/false
        # faceDis = face_recognition.face_distance([encodeimg1], encodeimg2)  #distance between two photos, measure of comparsion in range [0,1]
        return (results)


    def _findEncodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList


'''
    def photo_to_video(self, image, img):    
        #Args:
            #image (cv2.imread):image for specified (selected user_id, we know from login, who wants to log in )
            #converted to cv2.imread (from DB)
            #video (cv2.VideoCapture): Video from Webcam

        #We want to campare person from camera, with all photos from DB
        #If it's the same person (If True:) - log in
        #If False: - wrong person (no log in)

        encodeListKnown = self._findEncodings(image)

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace in encodesCurFrame:
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                return True
            else:
                continue
        return False
'''

'''      
    def photo_to_video_box(self, image, img, classNames):
        
            #Args:
            #image (cv2.imread):image for specified (selected user_id, we know from login, who wants to log in )
            #converted to cv2.imread (from DB)
            #video (cv2.VideoCapture): Video from Webcam

        #We want to campare person from camera, with all photos from DB
        #If it's the same person (If True:) - log in
        #If False: - wrong person (no log in)
        
        
        encodeListKnown = self._findEncodings(image)

        # success, img = video.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                # print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                #markAttendance(name)
                return True
            else:
                continue
        return False
'''

'''
def photo_to_photo(self, image_encoding, img2):
    
    We want to campare, if that's the right person
    If it's the same person on two different photos
    If True: - log in
    If False: - wrong person (no log in)

    Arguments:
        #img1 = single photo already saved in DB
        image_encoding = encoding of the first photo,
        img2 = image from camera (who wants to log in)
    
    # img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

    # face_Loc_img1 = face_recognition.face_locations(img1)[0]
    # encodeimg1 = face_recognition.face_encodings(img1)[0]

    # face_Loc_img2 = face_recognition.face_locations(img2)[0]
    encodeimg2 = face_recognition.face_encodings(img2)[0]

    results = face_recognition.compare_faces([image_encoding], encodeimg2)  # true/false
    # faceDis = face_recognition.face_distance([encodeimg1], encodeimg2)  #distance between two photos, measure of comparsion in range [0,1]
    return (results)
'''
