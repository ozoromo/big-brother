"""
Big Brother Face Recognition Class
Recognize and compare faces 'Photo-Photo'
"""
import cv2
import face_recognition
import numpy as np
import os


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
        encodings = face_recognition.face_encodings(img2)

        if len(encodings) == 0:
            return [False], [1]

        encodeimg2 = encodings[0]
        results = face_recognition.compare_faces([image_encoding], encodeimg2)  # true/false
        faceDis = face_recognition.face_distance([image_encoding], encodeimg2)  #distance between two photos, measure of comparsion in range [0,1], the closer to 0, the greater similarity
        return (results, faceDis)

    def encoding_to_encoding(self, image_encoding1, image_encoding2)
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
        results = face_recognition.compare_faces([image_encoding1], image_encoding2)
        faceDis = face_recognition.face_distance([image_encoding1], image_encoding2)



    def _findEncodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList
