###############################################
#         Make THIS script executable         #
###############################################
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src", "face_recog", "haar_and_lbph"))

###############################################
#       The actual program starts here        #
###############################################
import cv2
import numpy as np
from cv2RecogClass import cv2Recog


# Example to use face_rec_main to:
#   - detect faces
#   - register faces (train the model to recognize them)
#   - and "authorize" users by checking if the model recognizes the same user as the given user_id


# global paths to images
img_path = "../../../../res/test_images/merkel.jpg"
img_path_2 = "../../../../res/test_images/merkel2.jpg"
img_path_test = "../../../../res/test_images/ronaldo.jpg"


def crop_face(cv2Recog, img):
    # fix_res changes resotion of the cropped face to standard size
    face = cv2Recog.detect_face(img, fix_res=True)
    # shows cropped face, press 0 to close window and continue execution
    cv2.imshow("", face)
    cv2.waitKey(0)

   
if __name__ == "__main__":
    img = cv2.imread(os.path.expanduser( img_path))
    img2 = cv2.imread(os.path.expanduser(img_path_2))
    img_test = cv2.imread(os.path.expanduser(img_path_test))

    cv2Recog = cv2Recog()

    #show cropped face of image press 0 to escape
    crop_face(cv2Recog, img)

    # train img and img2 to be the same person with id 10
    user_id = 10
    cv2Recog.train_add_faces(user_id, [img, img2])

    # check if test_imgs is the person with id user_id, should be false if img_test is different to the other 2
    test_imgs = [img_test]
    result, dists = cv2Recog.authorize_faces(user_id, test_imgs)

    print(f"The given pictures are user with id {user_id} : {result}")
    print(f"The distances of the given pictures to the trained user with ID {user_id} : {dists}")
    print(f"dist: {cv2Recog.dist_between_two_pics(img2, img_test, crop_to_face=True)}")
