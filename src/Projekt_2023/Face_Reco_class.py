"""
Big Brother Face Recognition Class
Recognize and compare faces (Photo-Video), (Photo-Photo)
"""

import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime

class Face_Reco:
    def photo_to_photo(self, img1, img2):
        '''
        We want to campare, if that's the right person
        If it's the same person on two different photos
        If True: - log in
        If False: - wrong person (no log in)

        Arguments:
            img1 = single photo already saved in DB
            img2 = single photo of a person (,who wants to log in)
        '''
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

        face_Loc_img1 = face_recognition.face_locations(img1)[0]
        encodeimg1 = face_recognition.face_encodings(img1)[0]

        face_Loc_img2 = face_recognition.face_locations(img2)[0]
        encodeimg2 = face_recognition.face_encodings(img2)[0]

        results = face_recognition.compare_faces([encodeimg1], encodeimg2)  #true/false
        #faceDis = face_recognition.face_distance([encodeimg1], encodeimg2)  #distance between two photos, measure of comparsion in range [0,1]
        return(results)

    def _findEncodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    """
    def photo_to_video(self, images, video):
        '''
        Args:
            images (list): List with images converted to cv2.imread (from DB)
            video (cv2.VideoCapture): Video from Webcam

        We want to campare person from camera, with all photos from DB
        If it's the same person (If True:) - log in
        If False: - wrong person (no log in)

        '''

        encodeListKnown = self._findEncodings(images)

        success, img = video.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace in encodesCurFrame:
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print(matches)
            # print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:


            results = face_recognition.compare_faces([matches[matchIndex]], encodesCurFrame)  # true/false
            # faceDis = face_recognition.face_distance([encodeimg1], encodeimg2)  #distance between two photos, measure of comparsion in range [0,1]
            return (results)
            """

    def photo_to_video(self, image, video):
        '''
        Args:
            image (cv2.imread):image for specified (selected user_id, we know from login, who wants to log in )
            converted to cv2.imread (from DB)
            video (cv2.VideoCapture): Video from Webcam

        We want to campare person from camera, with all photos from DB
        If it's the same person (If True:) - log in
        If False: - wrong person (no log in)

        '''
        encodeListKnown = self._findEncodings(image)

        success, img = video.read()
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

        # results = face_recognition.compare_faces([matches[matchIndex]], image)  # true/false
