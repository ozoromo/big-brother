# @Author: Julius U. Heller <thekalk>
# @Date:   2021-05-19T19:15:24+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: modifiedFaceRecog.py
# @Last modified by:   Julius U. Heller
# @Last modified time: 2021-06-20T14:45:34+02:00



import main
import numpy as np
import matplotlib as mpl
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','DBM'))
import DatabaseManagement
import cv2


# def recogFace(returnQueue,im_data):
def recogFace(im_data):
    #im_data:
    #im_data[0] = image path
    #im_data[1] = user uuid

    #imgs_test_raw = [np.asarray(cv2.imread(im_data[0]), dtype=np.float64)]
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
    imgs_train, dim_x, dim_y, uuids = main.load_images(f"{curDir}/data/train/", user_uuid, ".png")

    print("Training...")
    flat_images = main.setup_data_matrix(imgs_train)
    pcs, sv, mean_data  = main.calculate_pca(flat_images )
    cutoff_threshold = 0.8
    k = main.accumulated_energy(sv, cutoff_threshold)

    # cut off number of pcs if desired
    pcs = pcs[0:k,:]
    # compute coefficients of input in eigenbasis
    print("Projecting...")
    coeffs_train = main.project_faces(pcs, imgs_train, mean_data)
    print("Identifying...")
    scores, imgs_test, coeffs_test = main.identify_faces(coeffs_train, pcs, mean_data,imgs_test)

    usernames = []
    for i in range(scores.shape[1]):
        j = np.argmin(scores[:, i])
        recognisedImageScore = np.min(scores[:, i])
        print("Index : {} Score : {}".format(j,round(recognisedImageScore,4)))
        if recognisedImageScore > 0.4:

            print("Score needs to be under 0.4!")
            return []
        DB = DatabaseManagement.wire_DB()
        usernames.append(DB.getUserWithId(user_uuid))
    return usernames
