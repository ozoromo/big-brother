# @Author: Julius U. Heller <thekalk>
# @Date:   2021-05-19T19:15:24+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: main.py
# @Last modified by:   thekalk
# @Last modified time: 2021-06-14T16:59:31+02:00



import numpy as np
import lib
import matplotlib as mpl
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..','DBM'))
import DatabaseManagement
import uuid
import cv2

####################################################################################################
# Exercise 1: Power Iteration

def power_iteration(M: np.ndarray, epsilon: float = -1.0) -> (np.ndarray, list):
    """
    Compute largest eigenvector of matrix M using power iteration. It is assumed that the
    largest eigenvalue of M, in magnitude, is well separated.

    Arguments:
    M: matrix, assumed to have a well separated largest eigenvalue
    epsilon: epsilon used for convergence (default: 10 * machine precision)

    Return:
    vector: eigenvector associated with largest eigenvalue
    residuals : residual for each iteration step

    Raised Exceptions:
    ValueError: if matrix is not square

    Forbidden:
    numpy.linalg.eig, numpy.linalg.eigh, numpy.linalg.svd
    """
    if M.shape[0] != M.shape[1]:
        raise ValueError("Matrix not nxn")

    # TODO: set epsilon to default value if not set by user
    if epsilon == -1.0:
        epsilon = np.finfo(np.float32).eps

    # TODO: normalized random vector of proper size to initialize iteration
    #vector = np.zeros(1)
    vector = np.random.rand(M.shape[0])
    #vector = M @ vector

    # Initialize residual list and residual of current eigenvector estimate
    residuals = []
    residual = 2.0 * epsilon

    # Perform power iteration
    while residual > epsilon:

        # TODO: implement power iteration
        x = vector
        z = M @ vector
        vector = z / np.linalg.norm(z)
        #print(vector)
        residual = np.linalg.norm(x - vector)
        residuals.append(residual)


    return vector, residuals


####################################################################################################
# Exercise 2: Eigenfaces

def insertTrainImages(path: str):

    print("start")
    DB = DatabaseManagement.wire_DB('h2938366.stratoserver.net')

    images = []

    # TODO read each image in path as numpy.ndarray and append to images
    # Useful functions: lib.list_directory(), matplotlib.image.imread(), numpy.asarray()
    table_name = ""
    if path == "./data/train/":
        table_name = "backend.wire_train"
    else:
        table_name = "backend.wire_test"

    img_str_list = lib.list_directory(path)

    for img_str in sorted(img_str_list):

        if img_str[-3:] != "png":

            #raise ValueError("Incorrect Data Type")

            continue

        im_path = path + img_str

        image = np.asarray(mpl.image.imread(im_path), dtype=np.float64)

        user_uuid = None

        try:

            user_uuid = DB.register_user(img_str[0:2])
            print("Created User : {} with uuid : {} ".format(img_str[0:2],user_uuid))

        except DatabaseManagement.UsernameExists:

            users = DB.getUsers()

            for u_uuid in users:

                if users[u_uuid] == img_str[0:2]:
                    user_uuid = u_uuid

        if not user_uuid:
            raise BaseException("No user id given")

        if type(user_uuid) == str:
            user_uuid = uuid.UUID(user_uuid)

        pic_uuid = DB.insertTrainingPicture(image,user_uuid)
        print("inserted : {}\nwith uuid : {}\nand user uuid : {}\n\n\n".format(img_str,pic_uuid,user_uuid))
    DB.closeGraceful()










def load_images(path: str,user_uuid : uuid.UUID, file_ending: str=".png") -> (list, int, int):
    """
    Load all images in path with matplotlib that have given file_ending

    Arguments:
    path: path of directory containing image files that can be assumed to have all the same dimensions
    file_ending: string that image files have to end with, if not->ignore file

    Return:
    images: list of images (each image as numpy.ndarray and dtype=float64)
    dimension_x: size of images in x direction
    dimension_y: size of images in y direction
    """
    #print("Starting DB Download")
    #Database

    images = []

    # TODO read each image in path as numpy.ndarray and append to images
    # Useful functions: lib.list_directory(), matplotlib.image.imread(), numpy.asarray()
    #img_str_list = lib.list_directory(path)

    DB = DatabaseManagement.wire_DB()
    uuids = []

    if path == "./data/train/":

        images,uuids = DB.getTrainingPictures(user_uuid=user_uuid)


        for image_index, image in enumerate(images):
            images[image_index] = cv2.cvtColor(np.float32(cv2.resize(image, dsize=(98,116), interpolation=cv2.INTER_CUBIC)),cv2.COLOR_BGR2GRAY)
        #images,uuids = DB.getTrainingPictures("""user_uuid,pic_data""","""""".format(user_uuid))
        #print(images)

        #for img_str in sorted(img_str_list):

            #if img_str[-3:] != "png":

                #raise ValueError("Incorrect Data Type")

                #continue

            #im_path = path + img_str

            #images.append(np.asarray(mpl.image.imread(im_path), dtype=np.float64))
            #images.append(mpl.image.imread(im_path))
        DB.closeGraceful()



    else:

        img_str_list = lib.list_directory(path)

        for img_str in sorted(img_str_list):

            if img_str[-3:] != "png":

                #raise ValueError("Incorrect Data Type")

                continue

            im_path = path + img_str

            images.append(np.asarray(mpl.image.imread(im_path), dtype=np.float64))
            #images.append(mpl.image.imread(im_path))


    #print(images)

    #TODO: Nur png durchlassen

    # TODO set dimensions according to first image in images
    #print(type(images[0]))
    dimension_y = images[0].shape[0]
    dimension_x = images[0].shape[1]

    #print("Fin DB Download")

    return images, dimension_x, dimension_y, uuids


def setup_data_matrix(images: list) -> np.ndarray:
    """
    Create data matrix out of list of 2D data sets.

    Arguments:
    images: list of 2D images (assumed to be all homogeneous of the same size and type np.ndarray)

    Return:
    D: data matrix that contains the flattened images as rows
    """
    # TODO: initialize data matrix with proper size and data type
    image_nbr = len(images)
    #print(type(images[0]))
    im_s = images[0].shape
    D = np.zeros((image_nbr, im_s[0] * im_s[1]))



    # TODO: add flattened images to data matrix


    for img_index, img in enumerate(images):
        #img = img.reshape(im_s[0] * im_s[1])
        #print(img)
        for row_index, row in enumerate(img):
            #c = row_index * im_s[1]
            #D[img_index][c] = img

            for val_index,val in enumerate(row):

                data_offset = row_index * im_s[1]
                data_index = data_offset + val_index
                try:
                    D[img_index][data_index] = val
                except Exception:
                    #print(type(val))
                    D[img_index][data_index] = (val[0] + val[1] + val[2]) / 3


    """
    for img_index, img in enumerate(images):
        print(im_s[0])
        print(im_s[1])
        print(img.shape[0])
        print(img.shape[1])

        print(im_s[0] * im_s[1])
        print(img.shape[0] * img.shape[1])

        #D[img_index] = img.reshape(im_s[0] * im_s[1])
        D[img_index] += img.reshape(img.shape[0] * img.shape[1])
    """


    return D


def calculate_pca(D: np.ndarray) -> (np.ndarray, np.ndarray, np.ndarray):
    """
    Perform principal component analysis for given data matrix.

    Arguments:
    D: data matrix of size m x n where m is the number of observations and n the number of variables

    Return:
    pcs: matrix containing principal components as rows
    svals: singular values associated with principle components
    mean_data: mean that was subtracted from data
    """

    # TODO: subtract mean from data / center data at origin
    #print(D)
    #print(D.shape)
    ds = D.shape
    mean_data = np.zeros(ds[1])

    """
    for k in range(ds[0]):

        mean_data = np.zeros(ds[0] * ds[1])

        for n in range(ds[1]):

            mean_data[n] += D[k][n]

        mean_data /= ds[0]
    """
    for n in range(ds[1]):

        for k in range(ds[0]):

            mean_data[n] += D[k][n]

    mean_data /= ds[0]

    D -= mean_data

    # TODO: compute left and right singular vectors and singular values
    # Useful functions: numpy.linalg.svd(..., full_matrices=False)
    #svals, pcs = [np.ones((1, 1))] * 2
    lvals,svals , pcs = np.linalg.svd(D, full_matrices=False)

    return pcs, svals, mean_data


def accumulated_energy(singular_values: np.ndarray, threshold: float = 0.8) -> int:
    """
    Compute index k so that threshold percent of magnitude of singular values is contained in
    first k singular vectors.

    Arguments:
    singular_values: vector containing singular values
    threshold: threshold for determining k (default = 0.8)

    Return:
    k: threshold index
    """

    # TODO: Normalize singular value magnitudes

    norm_sing = singular_values / np.linalg.norm(singular_values)

    k = 0
    # TODO: Determine k that first k singular values make up threshold percent of magnitude

    total = 0

    for val in norm_sing:
        total += val

    percent = 0
    progress = 0
    while percent < threshold and progress <= total:

        progress += norm_sing[k]
        percent = progress / total

        k += 1

    #print(k)
    return k


def project_faces(pcs: np.ndarray, images: list, mean_data: np.ndarray) -> np.ndarray:
    """
    Project given image set into basis.

    Arguments:
    pcs: matrix containing principal components / eigenfunctions as rows
    images: original input images from which pcs were created
    mean_data: mean data that was subtracted before computation of SVD/PCA

    Return:
    coefficients: basis function coefficients for input images, each row contains coefficients of one image
    """

    # TODO: initialize coefficients array with proper size
    coefficients = np.zeros((len(images), pcs.shape[0]))

    #mpl.pyplot.imshow(images[0], cmap="Greys_r")
    #mpl.pyplot.show()

    # TODO: iterate over images and project each normalized image into principal component basis
    images = setup_data_matrix(images)

    #mpl.pyplot.imshow(images[0].reshape(116,98), cmap="Greys_r")
    #mpl.pyplot.show()


    #
    #Normalize
    #

    for img_index, img in enumerate(images):
        images[img_index] = images[img_index] - mean_data

    #mpl.pyplot.imshow(images[0].reshape(116,98), cmap="Greys_r")
    #mpl.pyplot.show()


    for img_index, img in enumerate(images):
        for row_index, row in enumerate(pcs):
            coefficients[img_index][row_index] = np.dot(row,img)

    #mpl.pyplot.imshow(coefficients, cmap="Greys_r")
    #mpl.pyplot.show()

    return coefficients


def identify_faces(coeffs_train: np.ndarray, pcs: np.ndarray, mean_data: np.ndarray, imgs_test) -> (
np.ndarray, list, np.ndarray):
    """
    Perform face recognition for test images assumed to contain faces.

    For each image coefficients in the test data set the closest match in the training data set is calculated.
    The distance between images is given by the angle between their coefficient vectors.

    Arguments:
    coeffs_train: coefficients for training images, each image is represented in a row
    path_test: path to test image data

    Return:
    scores: Matrix with correlation between all train and test images, train images in rows, test images in columns
    imgs_test: list of test images
    coeffs_test: Eigenface coefficient of test images
    """

    # TODO: load test data set
    #print(imgs_test)
    # TODO: project test data set into eigenbasis
    #coeffs_test = np.zeros(coeffs_train.shape)
    #coeffs_test = np.zeros((len(imgs_test),))
    #coeffs_test = project_faces(pcs, imgs_test, mean_data)

    d_matrix = setup_data_matrix(imgs_test)
    test_pcs, test_sval, test_mean = calculate_pca(d_matrix)
    coeffs_test = project_faces(pcs,imgs_test,mean_data)
    #print(coeffs_test.shape)



    # TODO: Initialize scores matrix with proper size
    scores = np.zeros((coeffs_train.shape[0], coeffs_test.shape[0]))
    # TODO: Iterate over all images and calculate pairwise correlation
    for img_index, coeff_test in enumerate(coeffs_test):
        for train_img_index, coeff_train in enumerate(coeffs_train):
            scores[train_img_index][img_index] = np.arccos(np.dot(coeff_test,coeff_train)/(np.linalg.norm(coeff_test)*np.linalg.norm(coeff_train)))

    #print(scores)
    #print(scores)
    return scores, imgs_test, coeffs_test

#insertTrainImages("./data/train/")
#insertAllImages("./data/test/")


if __name__ == '__main__':

    print("All requested functions for the assignment have to be implemented in this file and uploaded to the "
          "server for the grading.\nTo test your implemented functions you can "
          "implement/run tests in the file tests.py (> python3 -v test.py [Tests.<test_function>]).")
