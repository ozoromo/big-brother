import os
import sys

import numpy as np
import matplotlib as mpl
import cv2

import wireUtils
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database_management.picture_database import PictureDatabase

def recogFace(im_data):

    imgs_test_raw = [im_data[0]]
    imgs_test = []

    user_uuid = im_data[1]

    for img in imgs_test_raw:
        try:
            imgs_test.append(cv2.cvtColor(
                cv2.resize(img, dsize=(98,116), interpolation=cv2.INTER_CUBIC),
                cv2.COLOR_BGR2GRAY))
        except cv2.error as e:
            print(e)
            print("[Warning] Returning Wire Algo")
            return

    print("Loading train Images...")
    curDir = os.path.dirname(os.path.abspath(__file__))
    # TODO: Find out why the training data is hardcoded in here! Shouldn't some sort
    # of database be used???
    imgs_train, dim_x, dim_y, uuids = wireUtils.load_images(f"{curDir}/../../../res/data/train/", user_uuid, ".png")

    print("Training...")
    flat_images = wireUtils.setup_data_matrix(imgs_train)
    pcs, sv, mean_data  = wireUtils.calculate_pca(flat_images )
    cutoff_threshold = 0.8
    k = wireUtils.accumulated_energy(sv, cutoff_threshold)

    # cut off number of pcs if desired
    pcs = pcs[0:k,:]
    # compute coefficients of input in eigenbasis
    print("Projecting...")
    coeffs_train = wireUtils.project_faces(pcs, imgs_train, mean_data)
    print("Identifying...")
    scores, imgs_test, coeffs_test = wireUtils.identify_faces(coeffs_train, pcs, mean_data,imgs_test)

    usernames = []
    for i in range(scores.shape[1]):
        j = np.argmin(scores[:, i])
        recognisedImageScore = np.min(scores[:, i])
        print("Index : {} Score : {}".format(j,round(recognisedImageScore,4)))
        if recognisedImageScore > 0.4:

            print("Score needs to be under 0.4!")
            return []
        DB = PictureDatabase()
        usernames.append(DB.get_user_with_id(user_uuid))
    return usernames
