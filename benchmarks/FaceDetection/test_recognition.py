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

    def encoding_to_encoding(self, image_encoding1, image_encoding2):
        '''
        We want to campare, if the photos match
        If it's the same person on two different photos
        If True: - the given photos are from same person
        If False: - the given photos includes different person
        Arguments:
            image_encoding1 = encoding of the first photo,
            image_encoding2 = encoding of the second photo
        '''
        results = face_recognition.compare_faces([image_encoding1], image_encoding2)
        faceDis = face_recognition.face_distance([image_encoding1], image_encoding2)

        return (results, faceDis)

    def _findEncodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList


def main(): 

    image_paths = ['test_images/Photo1.jpg', 'test_images/Photo2.jpg', 'test_images/Photo4.jpg']
    images = []
    
    # Load and check images
    for path in image_paths:
        image = cv2.imread(path)
        if image is None:
            print(f"Cannot open/read file: {path}. Please check the file path and integrity.")
            return
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert image to RGB
        images.append(image)

    face_encodings = []
    for image in images:

        try:
            encodings = face_recognition.face_encodings(image)
            if not encodings:
                print("No faces found on the given image.")
                return
            if len(encodings) > 1:
                print("Multiple faces detected in Image. Please choose a more clear photo")
                return
            face_encodings.append(encodings[0])
        except Exception as e:
            print("Error while calculating encodings:", e)
        
    if len(face_encodings) >= 2:
        for i in range(1, len(face_encodings)):
            logik = FaceReco()
            (results, dists) = logik.encoding_to_encoding(face_encodings[0], face_encodings[i])
            result = results[0]
            if not result:
                print("Faces in provided images do not match")
                return
    
    print("Recognition completed succesfully.")
    return


if __name__ == "__main__":
    main()