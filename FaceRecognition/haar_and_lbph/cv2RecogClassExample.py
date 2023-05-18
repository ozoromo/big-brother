import numpy as np
import cv2
from cv2RecogClass import cv2Recog
import os

#Example to use face_rec_main to:
#   detect faces
#   register faces (train the model to recognize them)
#   and "authorize" users by checking if the model recognizes the same user as the given user_id

#trained IDs 
#chad smith : 10

#-- global paths to images
img_path = '~/Downloads/th.jpeg' # change paths here
img_path_2 = '~/Downloads/th-2.jpeg'
img_path_test = '~/Downloads/Mark-Benecke-400x601.jpg' #different person from img_path and img_path2



def crop_face(cv2Recog, img):

    #shows cropped face, press 0 to close window and continue execution
    face = cv2Recog.detect_face(img, fix_res=True) #fix_res changes resotion of the cropped face to standard size
    cv2.imshow("", face)
    cv2.waitKey(0)

   
if __name__ == "__main__":

    img = cv2.imread(os.path.expanduser( img_path))
    img_2 = cv2.imread(os.path.expanduser(img_path_2))
    img_test = cv2.imread(os.path.expanduser(img_path_test))

    cv2Recog = cv2Recog()


    #show cropped face of img
    crop_face(cv2Recog, img) #press 0 to escape

    #train img and img2 to be the same person with id 10
    cv2Recog.train_add_faces(10, [img, img_2])

    #check if test_imgs is the person with id user_id, should be false if img_test is different to the other 2
    test_imgs = [img_test]
    user_id = 10
    result, dists = cv2Recog.authorize_faces(user_id, test_imgs)
    print(f'The given pictures are user with id {user_id} : {result} \nThe distances of the given pictures to the trained user with ID {user_id} : {dists}')

    print(f"dist: {cv2Recog.dist_between_two_pics(img_2, img_test, crop_to_face=True)}")