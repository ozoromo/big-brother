# @Author: Julius U. Heller <thekalk>
# @Date:   2021-05-26T01:00:49+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: benchmark.py
# @Last modified by:   thekalk
# @Last modified time: 2021-06-09T14:53:39+02:00



#System Libraries
import sys
import os

#Facerecog Libraries
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','WiReTest'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','DBM'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','FaceRecognition'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','FaceRecognition', 'haar_and_lbph'))
import main
import uuid
import cv2
import face_rec_main
from cv2RecogClass import cv2Recog
from Threshold_Calc import Threshold_Calc

# Dataset Library
from sklearn.datasets import fetch_lfw_people
from sklearn.model_selection import train_test_split

#Plotting Libraries
import matplotlib.pyplot as plt
from matplotlib import gridspec
import pylab

#Datastructures
import pandas as pd
import numpy as np
import random

#Gui Libraries
import tkinter as tk
import tkinter.ttk as ttk
import BV_Utils as BVU
import BV_Windows as BVW

#Time Management
import time as t

class userRecog():
    #
    # User Object
    # Used in Benchmarks to organize Image Ownership
    #

    def __init__(self,username):
        self.username = username
        self.recogPictures = []
        self.trainPictures = []
        self.recogScores = None
        self.imgShape = None


class benchRecog():
    #
    # Main Benchmark Class for WiRe Facerecognition
    #

    def __init__(self,**kwargs):

        # Since Benchmarks can take long the
        # Master Class can define a Progresswindow so the GUI doesnt freeze
        # and can update
        
        # tkinter elements
        self.master = None
        self.root = None
        self.pW = None          # progress window

        self.userLimit = 5
        self.trainPictureAmount = 20
        self.recogPictureAmount = 10

        # initialize timers for respective tests
        self.TPUserTimer = BVU.UserTimer()
        self.TNUserTimer = BVU.UserTimer()
        self.CV2TPUserTimer = BVU.UserTimer()
        self.CV2TNUserTimer = BVU.UserTimer()
        self.OFTPUserTimer = BVU.UserTimer()
        self.OFTNUserTimer = BVU.UserTimer()
        self.MixedUserTimer = BVU.UserTimer()

        self.exitFlag = False
        self.cv2Inst = cv2Recog()

        # Fetch optional Arguments
        for key, value  in kwargs.items():
            if key == 'root':
                self.root = value
            if key == 'master':
                self.master = value
            if key == 'userlimit':
                self.userLimit = value
            if key == 'pW':
                self.pW = value
                self.pW.createProgressbar("benchProg")

        # Optimal Threshold Calculation
        self.threshold_calc = self.master.threshold_calc

        # update progress window
        if self.pW:
            self.pW.update("benchProg","Fetching Dataset...",0)

        #Fetch the Learning set from sklearn
        lfw_people = fetch_lfw_people(
                min_faces_per_person=self.recogPictureAmount+self.trainPictureAmount, 
                resize=1
            )

        # update progress window
        if self.pW:
            self.pW.update("benchProg","Resizing Images...",30)

        #Fetch Names and Images
        imgs = lfw_people.images
        targets = lfw_people.target
        target_names = lfw_people.target_names

        if target_names.size < self.userLimit:
            if tk.messagebox.askyesno("Benchmark","Only : {} users available, continue with {}?".format(target_names.size,target_names.size)):
                self.userLimit = target_names.size
            else:
                self.exitFlag = True
                return

        resizedImgs = []
        self.image_shape = imgs[0].shape

        # Resize images
        # Since WiRe Algo needs all images to be the same height and width
        for img in imgs:
            resizedImgs.append(img.reshape((self.image_shape[1] * self.image_shape[0])))

        # update progress window
        if self.pW:
            self.pW.update("benchProg","Building Image Data...",35)

        self.df = pd.DataFrame(data = {
            'target' : targets,
            'name' : list(map(lambda x: target_names[x],targets)), 
            'img' : resizedImgs
        })
        self.df = self.df.set_index('target').sort_index()

        self.FaceDetection = self.master.FaceDetection

        # Init Users: Assignes Images to their right owner, assignes Username and necessary Variables
        self.users = []
        self.dbUsers = self.master.DbUsers
        userCount = self.userLimit
        userFin = 0

        # TODO: Since I switched to Dataframes this could be done better
        self.recogPictureCount = 0
        self.trainPictureCount = 0

        # Initializing users for benchmark tests: Inserting train and recognition images
        for index in range(self.userLimit):
            # update progress window
            if self.pW:
                self.pW.update("benchProg","Initialize Users...",35 + (userFin/userCount)*65)

            data = self.df.loc[index]
            username = list(data['name'])[0]
            user_ = userRecog(username)

            dataRecog = np.asarray(data['img'].iloc[:self.recogPictureAmount])
            dataTrain = np.asarray(data['img'].iloc[self.recogPictureAmount:self.trainPictureAmount+self.recogPictureAmount])
            self.recogPictureCount += len(dataRecog)
            self.trainPictureCount += len(dataTrain)

            user_.recogPictures = np.zeros((dataRecog.shape[0], dataRecog[0].shape[0]))
            user_.trainPictures = np.zeros((dataTrain.shape[0], dataTrain[0].shape[0]))
            for index, img in enumerate(dataRecog):
                user_.recogPictures[index] += img
            for index, img in enumerate(dataTrain):
                user_.trainPictures[index] += img

            self.users.append(user_)
            userFin += 1

        # update progress window
        if self.pW:
            self.pW.finProgress("benchProg")

        self.users = self.master.DbUsers
        self.dbUsers = self.master.DbUsers

        self.image_shape = self.master.imShape

    def modified_project_faces(self, pcs: np.ndarray, images: np.ndarray, mean_data: np.ndarray) -> np.ndarray:
        """
        Modified Method from WiRe Algo: Project given image set into basis.

        Arguments:
        pcs: matrix containing principal components / eigenfunctions as rows
        images: original input images from which pcs were created
        mean_data: mean data that was subtracted before computation of SVD/PCA

        Return:
        coefficients: basis function coefficients for input images, each row contains coefficients of one image
        """

        # initialize coefficients array with proper size
        coefficients = np.zeros((len(images), pcs.shape[0]))

        # Doesnt need to be executed, done in Benchmark Init
        #images = setup_data_matrix(images)

        # Iterate over images and project each normalized image into principal component basis
        for img_index, img in enumerate(images):
            images[img_index] = images[img_index] - mean_data

        for img_index, img in enumerate(images):
            for row_index, row in enumerate(pcs):
                coefficients[img_index][row_index] = np.dot(row,img)

        return coefficients

    def modified_identify_faces(self,coeffs_train: np.ndarray, pcs: np.ndarray, mean_data: np.ndarray, imgs_test) -> (
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
        # TODO: Properly comment this method
        """
        # Doesnt need to be executed, done in Benchmark Init
        # TODO: load test data set
        # TODO: project test data set into eigenbasis
        #coeffs_test = np.zeros(coeffs_train.shape)
        #coeffs_test = np.zeros((len(imgs_test),))
        #coeffs_test = project_faces(pcs, imgs_test, mean_data)
        """
        d_matrix = imgs_test
        test_pcs, test_sval, test_mean = main.calculate_pca(d_matrix)
        coeffs_test = self.modified_project_faces(pcs, imgs_test, mean_data)

        # The score is the (angular) distance between the images
        scores = np.zeros((coeffs_train.shape[0], coeffs_test.shape[0]))
        # Iterate over all images and calculate pairwise correlation
        for img_index, coeff_test in enumerate(coeffs_test):
            for train_img_index, coeff_train in enumerate(coeffs_train):
                # TODO: Perhapss explain this calculation better in the future
                # TODO: A runtime warning occurs here. Try to figure out what causes it!
                scores[train_img_index][img_index] = np.arccos(np.dot(coeff_test, coeff_train)/(np.linalg.norm(coeff_test)*np.linalg.norm(coeff_train)))

        return scores, imgs_test, coeffs_test

    def wireAlgo(self, imgs_test, imgs_train):
        # TODO: Properly comment this section
        pcs, sv, mean_data  = main.calculate_pca(imgs_train) 
        cutoff_threshold = 0.8
        k = main.accumulated_energy(sv, cutoff_threshold)
        pcs = pcs[0:k,:]
        coeffs_train = self.modified_project_faces(pcs, imgs_train, mean_data)
        scores, imgs_test, coeffs_test = self.modified_identify_faces(
                coeffs_train, pcs, mean_data,imgs_test
            )
        return scores

    def run_true_negatives(self):
        if self.pW:
            self.pW.createProgressbar("TNProg")

        userCount = len(self.users)
        userFin = 0

        testImageIndices = []
        recogImageIndices = []
        recogImageScores = []
        usernames = []
        recogUsernames = []

        self.TNUserTimer.clear()

        for user_index, user_ in enumerate(self.users):
            # TODO: The start of this enumeration is very similar across all benchmark methods
            # it might be good to clean this up
            if self.pW:
                self.pW.update(
                    "TNProg","[TN] Benchmarking User: {}/{}...".format(user_.username,self.userLimit), 
                    userFin/userCount * 100
                )

            if self.root:
                self.root.update()

            if len(user_.trainPictures) == 0:
                continue

            self.TNUserTimer.startTimer(user_)

            # Get index of user that is different from current one
            rand = random.randint(0, userCount - 1)
            while rand == user_index:
                rand = random.randint(0, userCount - 1)

            # Images are flattened
            imgs_train = self.users[rand].trainPictures
            imgs_test = user_.recogPictures

            # Running WiRe Algo on user
            try:
               scores = self.wireAlgo(imgs_test ,imgs_train)
            except ValueError as e:
                print("WARNING: wireAlgo terminated with an error:")
                print(e)
                return

            # Prepare Score Dataframe
            user_.recogScores = None
            for testImageIndex in range(scores.shape[1]):
                recognisedImageIndex = np.argmin(scores[:, testImageIndex])
                recognisedImageScore = np.min(scores[:, testImageIndex])
                testImageIndices.append(testImageIndex)
                recogImageIndices.append(recognisedImageIndex)
                recogImageScores.append(recognisedImageScore)
                usernames.append(user_.username)
                recogUsernames.append(self.users[rand].username)

            userFin += 1
            self.TNUserTimer.endTimer(user_)

        if self.pW:
            self.pW.finProgress("TNProg")

        recogScores = pd.DataFrame(
            data = {
                'testImageIndex':    testImageIndices,
                'username':          usernames,
                'recogImageIndex':   recogImageIndices,
                'recogUsername':     recogUsernames,
                'recogScore' :       recogImageScores
            }
        ).set_index('recogImageIndex').sort_values(by='testImageIndex')

        return recogScores

    def run_mixed_positives(self, numSelfImages, numDecoyUsers, numDecoyUserImages):
        """
        Benchmark method for mixed benchmark
        Compares user images with image mixture of different users and a pic from the query user
        """

        if self.pW:
            self.pW.createProgressbar("MProg")

        userCount = len(self.users)
        userFin = 0

        testImageIndices = []
        recogImageIndices = []
        recogImageScores = []
        usernames = []
        recogUsernames = []

        user_ = self.users[0]

        if numSelfImages > len(user_.trainPictures) or numDecoyUserImages > len(user_.trainPictures) or numDecoyUsers > len(self.users):
            tk.messagebox.showinfo("Benchmark","Adjusting Parameters:\nNum. Of Query Images: {} -> {}\nNum. Of Other Users: {} -> {}\nNum. Pic. Of Other Users: {} -> {}\n".format(
            numSelfImages,np.min((numSelfImages,len(user_.trainPictures))),numDecoyUsers,np.min((numDecoyUsers,len(self.users))),
            numDecoyUserImages,np.min((numDecoyUserImages,len(user_.trainPictures)))))


        self.MixedUserTimer.clear()

        for user_ in self.users:

            if self.pW:
                self.pW.update(
                    "MProg","[MP] Benchmarking User: {}/{}...".format(user_.username,self.userLimit),
                    userFin/userCount * 100
                )

            if self.root:
                self.root.update()

            if len(user_.trainPictures) == 0:
                continue

            self.MixedUserTimer.startTimer(user_)

            #Fetch User pictures
            #imgs_train = user_.trainPictures # Images are flattened
            imgs_test = user_.recogPictures
            #Make Sure Parameter isnt higher than actual length of list
            numSelfImages = np.min((numSelfImages,len(user_.trainPictures)))
            numDecoyUserImages = np.min((numDecoyUserImages,len(user_.trainPictures)))

            # numDecoyUsers must not be higher than len(self.users)
            # select the minimum

            decoyRange = np.min((numDecoyUsers,len(self.users)))

            # + 1 for user_

            imgs_train = np.zeros((numDecoyUserImages * (decoyRange) + numSelfImages,user_.trainPictures.shape[1]))

            decoyUsers = []


            for decoyUserIndex in range(decoyRange):
                #Get user
                decoyUser = self.users[decoyUserIndex]

                decoyUsers.append(decoyUser)
                #Select Images per decoy User

                decoyImages = decoyUser.trainPictures[:numDecoyUserImages]
                #Concatenate lists

                #print(decoyUserIndex * numDecoyUserImages,":",(decoyUserIndex * numDecoyUserImages) + numDecoyUserImages)
                imgs_train[decoyUserIndex * numDecoyUserImages:(decoyUserIndex * numDecoyUserImages) + numDecoyUserImages] += decoyImages
                #Usernames must be mapped exactly like images_train for identification


            selfImages = user_.trainPictures[:numSelfImages]

            imgs_train[(decoyRange) * numDecoyUserImages:] += selfImages

            decoyUsers.append(user_)

            try:
                scores = self.wireAlgo(imgs_test ,imgs_train)
            except ValueError as e:
                print("WARNING: wireAlgo terminated with an error:")
                print(e)
                return

            # Prepare Score Dataframe
            user_.recogScores = None
            for testImageIndex in range(scores.shape[1]):
                recognisedImageIndex = np.argmin(scores[:, testImageIndex])
                recognisedImageScore = np.min(scores[:, testImageIndex])

                #Correctly map imgs_train to Index
                testImageIndices.append(testImageIndex)
                recogImageIndices.append(recognisedImageIndex // numDecoyUserImages)
                recogImageScores.append(recognisedImageScore)

                usernames.append(user_.username)
                #print("recogIndex : {} numDecoys : {}".format(recognisedImageIndex,numDecoyUserImages))
                #print(recognisedImageIndex // numDecoyUserImages)
                recogUsernames.append(decoyUsers[recognisedImageIndex // numDecoyUserImages].username)

            userFin += 1
            self.MixedUserTimer.endTimer(user_)

        if self.pW:
            self.pW.finProgress("MProg")

        recogScores = pd.DataFrame(
            data = {
                'testImageIndex':  testImageIndices,
                'username':        recogUsernames, 
                'recogImageIndex': recogImageIndices, 
                'recogUsername':   usernames,
                'recogScore':      recogImageScores
            }
        ).set_index('recogImageIndex').sort_values(by='testImageIndex')
        return recogScores

    def run_true_positives(self):
        """
        Benchmark method for ture positive classes
        Compares user images with images of that exact user
        creating a True Positive case
        """

        if self.pW:
            self.pW.createProgressbar("TPProg")

        userCount = len(self.users)
        userFin = 0

        testImageIndices = []
        recogImageIndices = []
        recogImageScores = []
        usernames = []

        self.TPUserTimer.clear()

        for user_ in self.users:
            if self.pW:
                self.pW.update(
                    "TPProg","[TP] Benchmarking User: {}/{}...".format(user_.username,self.userLimit),
                    userFin/userCount * 100
                )

            if self.root:
                self.root.update()

            if len(user_.trainPictures) == 0:
                continue

            self.TPUserTimer.startTimer(user_)

            # Fetch User pictures
            imgs_train = user_.trainPictures # Images are flattened
            imgs_test = user_.recogPictures

            try:
                scores = self.wireAlgo(imgs_test ,imgs_train)
            except ValueError:
                return

            # Prepare Score Dataframe
            user_.recogScores = None
            for testImageIndex in range(scores.shape[1]):
                recognisedImageIndex = np.argmin(scores[:, testImageIndex])
                recognisedImageScore = np.min(scores[:, testImageIndex])
                testImageIndices.append(testImageIndex)
                recogImageIndices.append(recognisedImageIndex)
                recogImageScores.append(recognisedImageScore)
                usernames.append(user_.username)

            userFin += 1
            self.TPUserTimer.endTimer(user_)

        if self.pW:
            self.pW.finProgress("TPProg")

        recogScores = pd.DataFrame(
            data = {
                'testImageIndex':  testImageIndices,
                'username':        usernames, 
                'recogImageIndex': recogImageIndices,
                'recogUsername':   usernames,
                'recogScore':      recogImageScores
            }).set_index('recogImageIndex').sort_values(by='testImageIndex')

        return recogScores



    def plot_user(self,fig,user_,scores):
        """
        Plots Score Dataframe needs to be called from a GraphViewer Class in BV_Windows
        """

        slotIndex = 1

        for scoreIndex, scoreTuple in enumerate(scores.itertuples()):
            if slotIndex > 10:
                return
            query_image = user_.recogPictures[int(scoreTuple[1])]

            fig.add_subplot(5, 2 , slotIndex)
            #plt.imshow(query_image.reshape(self.image_shape[0],self.image_shape[1]), cmap="Greys_r")
            plt.imshow(query_image.reshape(user_.imgShape).astype("uint8"))
            #axs[scoreIndex][0].imshow(query_image.reshape(self.image_shape[0],self.image_shape[1]), cmap="Greys_r")
            plt.xlabel('Query image : {}'.format(scoreTuple[2]),rotation=0)

            recogUser = self.findUsername(scoreTuple[3])

            fig.add_subplot(5, 2, slotIndex + 1)
            #axs[scoreIndex][1].imshow(user_.trainPictures[int(scoreTuple[1])].reshape(self.image_shape[0],self.image_shape[1]), cmap="Greys_r")
            #plt.imshow(recogUser.trainPictures[int(scoreTuple[1])].reshape(self.image_shape[0],self.image_shape[1]), cmap="Greys_r")
            plt.imshow(recogUser.trainPictures[int(scoreTuple[1])].reshape(user_.imgShape).astype("uint8"))
            plt.xlabel('Identified: {} with Score: {}'.format(scoreTuple[3],round(scoreTuple[4],4)),rotation=0)

            slotIndex += 2

    def findUsername(self,username):
        # TODO: This looks very inefficient
        for user in self.users:
            if user.username == username:
                return user

    def openface_algo(self, train_imgs , test_imgs, crop_and_align = True):
        self.FaceDetection.init()

        scores = np.zeros((len(train_imgs), len(test_imgs)))
        for train_index, train_img in enumerate(train_imgs):

            train_img = train_img.reshape((self.image_shape[0],self.image_shape[1]))
            train_img = cv2.normalize(src=train_img, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            if crop_and_align == True:
                #get face position and align face
                train_box = (0,0,train_img.shape[1], train_img.shape[0]) #(left,top,right,bottom)
                #FaceDetection.get_boxes(train_img)
                train_alignedFace = self.FaceDetection.aligner(train_box, train_img)
            else:
                train_alignedFace = train_img

            for test_index, test_img in enumerate(test_imgs):
                test_img = test_img.reshape((self.image_shape[0],self.image_shape[1]))
                test_img = cv2.normalize(src=test_img, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                if crop_and_align == True:
                    #prepare test picture
                    #test_box = FaceDetection.get_boxes(test_img)
                    test_box = (0,0,test_img.shape[1], test_img.shape[0])
                    test_alignedFace = self.FaceDetection.aligner(test_box, test_img)
                else:
                    test_alignedFace = test_img

                scores[train_index, test_index] = self.FaceDetection.get_dist_from_images(train_alignedFace, test_alignedFace)

        return scores

    def openface_run_true_positives(self):
        """
        Benchmark method for ture positive classes
        Compares user images with images of that exact user
        creating a True Positive case
        """

        if self.pW:
            self.pW.createProgressbar("Openface_TPProg")

        userCount = len(self.users)
        userFin = 0

        testImageIndices = []
        recogImageIndices = []
        recogImageScores = []
        usernames = []

        self.OFTPUserTimer.clear()
        #random.shuffle(self.users)

        for user_ in self.users:
            if self.pW:
                self.pW.update(
                    "Openface_TPProg","[TP] Benchmarking User: {}/{}...".format(user_.username,self.userLimit),
                    userFin/userCount * 100
                )

            if self.root:
                self.root.update()

            if len(user_.trainPictures) == 0:
                continue

            self.OFTPUserTimer.startTimer(user_)

            #Fetch User pictures
            imgs_train = user_.trainPictures # Images are flattened
            imgs_test = user_.recogPictures

            # Running Openface Algo on user
            scores = self.openface_algo(imgs_train, imgs_test, crop_and_align=True)

            # Prepare Score Dataframe
            user_.recogScores = None

            for testImageIndex in range(scores.shape[1]):
                recognisedImageIndex = np.argmin(scores[:, testImageIndex])
                recognisedImageScore = np.min(scores[:, testImageIndex])
                testImageIndices.append(testImageIndex)
                recogImageIndices.append(recognisedImageIndex)
                recogImageScores.append(recognisedImageScore)
                usernames.append(user_.username)

            #recogScores.append(pd.DataFrame(data = {'testImageIndex' : testImageIndices,'recogImageIndex' : recogImageIndices,'recogScore' : recogImageScores}).set_index('recogImageIndex').sort_values(by='testImageIndex'))

            userFin += 1
            self.OFTPUserTimer.endTimer(user_)

        if self.pW:
            self.pW.finProgress("Openface_TPProg")

        recogScores = pd.DataFrame(
            data = {
                'testImageIndex':  testImageIndices,
                'username':        usernames, 
                'recogImageIndex': recogImageIndices,
                'recogUsername':   usernames,
                'recogScore':      recogImageScores
            }).set_index('recogImageIndex').sort_values(by='testImageIndex')

        return recogScores

    def opencv_haar_lbph_algo(self, imgs_test_raw,imgs_train_raw):
        # pre-process pictures to be in the right format
        imgs_train = []
        for train_img in imgs_train_raw:
            train_img_resized = train_img.reshape((self.image_shape[0],self.image_shape[1])) #back into original shape
            train_img_norm = cv2.normalize(src=train_img_resized, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U) #normalize, so that its an int array between 0 and 255
            imgs_train.append(train_img_norm)


        imgs_test = []
        for test_img in imgs_test_raw:
            test_img_resized = test_img.reshape((self.image_shape[0],self.image_shape[1])) #back into original shape
            test_img_norm = cv2.normalize(src=test_img_resized, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U) #normalize, so that its an int array between 0 and 255
            imgs_test.append(test_img_norm)

        # use temporary integer ID to train a completely new model and check if it recognized the same person in authorisation login picture
        temp_ID = 22
        face_rec_main.train_add_faces(temp_ID, imgs_train, new_model=True, save_model=False, crop_to_face=False)

        # Authorize: check if the training pitures are the same person as the given login picture
        _, dists = face_rec_main.authorize_faces(temp_ID, imgs_test, crop_to_face=False)

        return dists

    def opencv_single_dist_algo(self, imgs_test_raw,imgs_train_raw):
        #pre-process pictures to be in the right format
        imgs_train = []
        for train_img_processing in imgs_train_raw:
            #train_img_resized = train_img_processing.reshape((self.image_shape[0],self.image_shape[1])) #back into original shape
            train_img_resized = train_img_processing.reshape((self.image_shape)).astype("uint8") #back into original shape
            train_img_norm = cv2.normalize(src=train_img_resized, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U) #normalize, so that its an int array between 0 and 255
            imgs_train.append(train_img_norm)


        imgs_test = []
        for test_img_processing in imgs_test_raw:
            #test_img_resized = test_img_processing.reshape((self.image_shape[0],self.image_shape[1])) #back into original shape
            test_img_resized = test_img_processing.reshape((self.image_shape)).astype("uint8") #back into original shape
            test_img_norm = cv2.normalize(src=test_img_resized, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U) #normalize, so that its an int array between 0 and 255
            imgs_test.append(test_img_norm)

        # 2d array of results: each row is one train picture, each column is one test picture
        res = np.zeros((len(imgs_train), len(imgs_test)))
        for train_ind, train_img in enumerate(imgs_train):
            for test_ind, test_img in enumerate(imgs_test):
                res[train_ind, test_ind] = self.cv2Inst.dist_between_two_pics(train_img, test_img)

        return res

    def opencv_run_true_positives(self):
        """
        Benchmark method for true positive classes of the opencv haar+lbph models
        Compares user images with images of that exact user
        creating a True Positive case
        """

        if self.pW:
            self.pW.createProgressbar("OpenCVTPProg")

        userCount = len(self.users)
        userFin = 0

        testImageIndices = []
        recogImageIndices = []
        recogImageScores = []
        usernames = []

        self.CV2TPUserTimer.clear()

        for user_ in self.users:
            if self.pW:
                self.pW.update(
                    "OpenCVTPProg","[CV2TP] Benchmarking User: {}/{}...".format(user_.username,self.userLimit),
                    userFin/userCount * 100
                )

            if self.root:
                self.root.update()

            if len(user_.trainPictures) == 0:
                continue

            self.CV2TPUserTimer.startTimer(user_)

            #Fetch User pictures
            imgs_train = user_.trainPictures # Images are flattened
            imgs_test = user_.recogPictures

            # Running opencv haar and lpph Algo on user
            scores = self.opencv_single_dist_algo(imgs_test, imgs_train)

            # Prepare Score Dataframe
            user_.recogScores = None
            for testImageIndex in range(scores.shape[1]):
                recognisedImageIndex = np.argmin(scores[:, testImageIndex])
                recognisedImageScore = np.min(scores[:, testImageIndex])
                testImageIndices.append(testImageIndex)
                recogImageIndices.append(recognisedImageIndex)
                recogImageScores.append(recognisedImageScore)
                usernames.append(user_.username)

            # TODO: Find out what it does
            # Data to calculate optimal Threshold
            # we're in true positive case so all labels are True
            labels = np.full(shape=(len(imgs_train),len(imgs_test)), 
                             fill_value=True, 
                             dtype=bool)
            self.threshold_calc.add_data_and_labels(scores, labels)

            userFin += 1
            self.CV2TPUserTimer.endTimer(user_)

        if self.pW:
            self.pW.finProgress("OpenCVTPProg")

        recogScores = pd.DataFrame(
            data = {
                'testImageIndex': testImageIndices,
                'username' : usernames, 
                'recogImageIndex' : recogImageIndices,
                'recogUsername' : usernames,
                'recogScore' : recogImageScores
            }).set_index('recogImageIndex').sort_values(by='testImageIndex')

        return recogScores

    def opencv_run_true_negatives(self):
        if self.pW:
            self.pW.createProgressbar("CV2TNProg")

        userCount = len(self.users)
        userFin = 0

        testImageIndices = []
        recogImageIndices = []
        recogImageScores = []
        usernames = []
        recogUsernames = []

        self.CV2TNUserTimer.clear()

        for user_index,user_ in enumerate(self.users):
            if self.pW:
                self.pW.update(
                    "CV2TNProg","[CV2TN] Benchmarking User: {}/{}...".format(user_.username,self.userLimit),
                    userFin/userCount * 100
                )

            if self.root:
                self.root.update()

            if len(user_.trainPictures) == 0:
                print("WARNING: Training pictures empty!")
                continue

            self.CV2TNUserTimer.startTimer(user_)

            #Fetch User pictures
            rand = random.randint(0,userCount - 1)
            while rand == user_index:
                rand = random.randint(0,userCount - 1)

            imgs_train = self.users[rand].trainPictures # Images are flattened
            imgs_test = user_.recogPictures

            scores = self.opencv_single_dist_algo(imgs_test, imgs_train)

            # Prepare Score Dataframe
            user_.recogScores = None
            for testImageIndex in range(scores.shape[1]):
                recognisedImageIndex = np.argmin(scores[:, testImageIndex])
                recognisedImageScore = np.min(scores[:, testImageIndex])
                testImageIndices.append(testImageIndex)
                recogImageIndices.append(recognisedImageIndex)
                recogImageScores.append(recognisedImageScore)
                usernames.append(user_.username)
                recogUsernames.append(self.users[rand].username)

            userFin += 1
            self.CV2TNUserTimer.endTimer(user_)

            # Data to calculate optimal Threshold
            # We're in true positive case so all labels are True
            labels = np.full(shape=(len(imgs_train), len(imgs_test)), 
                             fill_value=False, 
                             dtype=bool)
            self.threshold_calc.add_data_and_labels(scores, labels)

        if self.pW:
            self.pW.finProgress("CV2TNProg")

        recogScores = pd.DataFrame(
            data = {
                'testImageIndex':  testImageIndices,
                'username':        usernames, 
                'recogImageIndex': recogImageIndices,
                'recogUsername' :  recogUsernames,
                'recogScore' :     recogImageScores
            }).set_index('recogImageIndex').sort_values(by='testImageIndex')

        # Calculate optimal threshold (for this data)
        f_score_level = 0.25  # recall is x times as important as precision
        self.threshold_calc.set_thres_range(min_threshold = 160, max_threshold = 185, step_num = 300)  #choose more accurately with smaller range and/or more steps
        self.threshold_calc.calc_and_print_results(f_score_level)

        return recogScores
