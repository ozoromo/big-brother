# @Author: Julius U. Heller <thekalk>
# @Date:   2021-06-03T22:21:03+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: BVGUI.py
# @Last modified by:   thekalk
# @Last modified time: 2021-06-09T14:55:51+02:00



from benchmark import benchRecog
from benchmark import userRecog
import cv2

#Plotting Libraries
import matplotlib.pyplot as plt
from matplotlib import gridspec
import pylab

#Datastructures
import pandas as pd
import numpy as np
import random
from Threshold_Calc import Threshold_Calc
import pickle

#Gui Libraries
import tkinter as tk
import tkinter.ttk as ttk
import BV_Windows as BVW
import BV_Utils as BVU

#Time Management
import time as t

#Database
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','DBM'))
import DatabaseManagement as DBM
from threading import Thread

#Face Detection
import platform
if platform.system() == 'Linux':
    from FaceDetectionClass import FaceDetection


#
# GUI Class System
# Naming Convention:
# BVGUI = Benchmark Viewer Graphical User Interface


class BVGUI (tk.Frame):
    """
    Benchmark Viewer
    BVGUI:
        Type Master class:
            Managages displaying of Windows
            Managages Data from foreign Dataset
            Configures Main GUI Variables
            Has control over tk.root
    """
    def __init__(self, master):

        #Init Master
        self.master = master

        self.master.withdraw()
        tk.Frame.__init__(self, self.master)

        #Init global Variables
        #Set Window Dimensions

        self.windowDimension_x = 1500
        self.windowDimension_y = 600

        self.updateFunctions = []

        self.DB = DBM.wire_DB("h2938366.stratoserver.net")

        self.exitFlag = False

        # Optimal Threshold Calculation
        self.threshold_calc = Threshold_Calc(data = None, labels = None)

        #Progress Window with progressbar
        self.pW = BVU.progresWindow(self.master,"BenchmarkViewer",self.windowDimension_x,self.windowDimension_y)
        self.pW.createProgressbar("guiInit")

        self.FaceDetection = None
        if platform.system() == 'Linux':

            self.FaceDetection = FaceDetection()
        #self.pW.dropDown(self.master,self)

        #Update progress window with custom text and progressbar position

        self.pW.update("guiInit","Initialising Benchmarks...",0)

        #Init Benchmark Class
        self.DbUsers = self.fetchDatabaseUsers()
        self.bR = benchRecog(root = self.master,master = self,pW = self.pW)
        self.update()
        self.pW.update("guiInit","Running Benchmarks...",0)

        self.pW.update("guiInit","Done...",85)

        self.pW.update("guiInit","Initialising GUI...",60)

        """
        self.pW.createProgressbar("FrameInit")

        #Initialize Windows



        self.pW.update("FrameInit","Initialising True Positive Viewer...",0)
        self.TPV = BVW.TPViewer(self,"visible")
        self.pW.update("FrameInit","Initialising True Positive Viewer...",25)
        self.pW.update("FrameInit","Initialising True Negative Viewer...",25)
        self.TNV = BVW.TNViewer(self,"hidden")
        self.pW.update("FrameInit","Initialising True Negative Viewer...",50)
        self.pW.update("FrameInit","Initialising Mixed Viewer...",50)
        self.MV = BVW.MixedViewer(self,"hidden")
        self.pW.update("FrameInit","Initialising Mixed Viewer...",75)
        self.pW.finProgress("FrameInit")
        """



        self.UV = BVW.UserViewer(self,"visible","UserViewer")

        #self.BVWindows = [self.TPV,self.TNV,self.MV,self.UV]
        self.BVWindows = [self.UV]

        if platform.system() == 'Linux':

            self.OFTP = BVW.OFTPViewer(self,"hidden")
            self.pW.update("FrameInit","Initialising Openface True Positive Viewer...",100)
            self.pW.finProgress("FrameInit")
            self.BVWindows.append(self.OFTP)

            self.OFTN = BVW.OFTNViewer(self,"hidden")
            self.pW.update("FrameInit","Initialising Openface True Negative Viewer...",100)
            self.pW.finProgress("FrameInit")
            self.BVWindows.append(self.OFTN)

        self.pW.update("FrameInit","Initialising CV2",75)
        self.CV2TP = BVW.CV2TPViewer(self,"hidden")
        self.pW.update("FrameInit","Initialising CV2 True Positive Viewer...",75)
        self.pW.finProgress("FrameInit")
        self.BVWindows.append(self.CV2TP)

        self.CV2TN = BVW.CV2TNViewer(self,"hidden")
        self.pW.update("FrameInit","Initialising CV2 True Negative Viewer...",100)
        self.pW.finProgress("FrameInit")
        self.BVWindows.append(self.CV2TN)


        self.update()

        #,self.OFTN,self.OFTP]

        #Configure Master Variables
        self.configureMaster()

        self.pW.update("guiInit","Done...",100)

        #Hide Progress Window
        self.pW.finProgress("guiInit")

        self.master.deiconify()



    def configureMaster (self):

        _bgcolor = '#FFFFFF'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'

        #
        # Global Init of ttk.Styles
        #

        self.style = ttk.Style()
        #if sys.platform == "win32":
            #self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font=('Arial', 8))
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        self.titleFontStyle = ttk.Style()
        #if sys.platform == "win32":
            #self.style.theme_use('winnative')
        self.titleFontStyle.configure('.',background=_bgcolor)
        self.titleFontStyle.configure('.',foreground=_fgcolor)
        self.titleFontStyle.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])
        self.titleFontStyle.configure('title.TLabel', font=('Arial', 12))

        #Set geometry
        self.master.geometry("{}x{}+758+131".format(self.windowDimension_x,self.windowDimension_y))
        self.master.minsize(120, 1)
        self.master.maxsize(5764, 1041)
        self.master.resizable(1, 1)
        self.master.title("BenchmarkViewer")
        self.master.configure(background="#d9d9d9")

        #
        # GUI Menubar
        #

        self.menubar = tk.Menu(self.master,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        self.master.configure(menu = self.menubar)

        self.wireBar = tk.Menu(self.master,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)


        self.wireBar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="True Positive Viewer",
                command= lambda: self.switchWindow("TPViewer"))

        self.wireBar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="True Negative Viewer",
                command = lambda: self.switchWindow("TNViewer"))

        self.wireBar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="Mixed Viewer",
                command = lambda: self.switchWindow("MixedViewer"))

        self.menubar.add_cascade(label="Wire Benchmarks", menu=self.wireBar)

        self.OFBar = tk.Menu(self.master,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)

        self.OFBar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="True Positive Viewer",
                command= lambda: self.switchWindow("OFTPViewer"))

        self.OFBar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="True Negative Viewer",
                command = lambda: self.switchWindow("OFTNViewer"))

        self.menubar.add_cascade(label="OpenFace Benchmarks", menu=self.OFBar)

        self.cv2Bar = tk.Menu(self.master,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)

        self.cv2Bar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="True Positive Viewer",
                command= lambda: self.switchWindow("CV2TPViewer"))

        self.cv2Bar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="True Negative Viewer",
                command = lambda: self.switchWindow("CV2TNViewer"))

        self.menubar.add_cascade(label="CV2 Benchmarks", menu=self.cv2Bar)
        self.menubar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="User Viewer",
                command = lambda: self.switchWindow("UserViewer"))




        self.master.protocol("WM_DELETE_WINDOW", self.closeGraceful)

    def updateBenchmark(self,**kwargs):

        userlimit = 5

        for key, value in kwargs.items():
            if key == 'userlimit':
                userlimit = value

        self.bR = benchRecog(root = self.master,master = self,userlimit=userlimit,pW = self.pW)


    def update(self):
        """

        Update method Currently empty
        If foreign Classes need to be refreshed this is done here

        """

        for function in self.updateFunctions:
            #print("executing : {}".format(function))
            function(self)

    def switchWindow(self,windowName):

        #
        # Switch Windows
        #

        if windowName == "OFTNViewer" or windowName == "OFTPViewer":

            tk.messagebox.showerror("Error","Openface Algorithms are only available on Linux/Mac OS")

            return

        for window in self.BVWindows:
            if window.name == windowName:
                window.show()
            else:
                window.hide()

    def fetchDatabaseUsers(self):
        self.pW.createProgressbar("bbInit")
        self.pW.update("bbInit","Fetching Big Brother Users...",0)

        userDict = self.DB.getUsers(limit = 10)
        userList = []
        counter = 0
        #return
        maxPicSize = 0
        maxShape = None
        pics = []
        pic_uuids = []
        user_uuids = []
        counter = 0
        for key, value in userDict.items():
            counter += 1
            u_pics , u_pic_uuids = self.DB.getTrainingPictures("WHERE user_uuid = '{}'".format(key))
            pics += u_pics
            pic_uuids += u_pic_uuids
            for x in u_pics:
                user_uuids.append(key)

            self.pW.update("bbInit","Fetching Big Brother Users : {}".format(value),(counter / len(userDict)) * 100)
        print(len(user_uuids),len(pic_uuids),len(pics))
        for pic_index, pic in enumerate(pics):

            #flattened = pic.reshape(pic.shape[0] * pic.shape[1])
            flattened = pic.flatten()

            if flattened.shape[0] > maxPicSize:
                maxPicSize = flattened.shape[0]
                maxShape = pic.shape

        self.imShape = maxShape
        UserPicDf = pd.DataFrame(data = {'user_uuid' : user_uuids, 'pic_uuid' : pic_uuids, 'pic_data' : pics}).set_index('user_uuid')
        newUserDict = {}

        for user_uuid in user_uuids:
            counter += 1
            username = userDict[user_uuid]

            try:
                newUserDict[user_uuid]
            except KeyError:
                newUserDict[user_uuid] = userRecog(username)

            self.pW.update("bbInit","Processing Big Brother Users : {}".format(username),(counter / len(userDict)) * 100)

            DBUser = newUserDict[user_uuid]
            DBUser.imgShape = maxShape

            #imgs_test.append(cv2.cvtColor(cv2.resize(img, dsize=(98,116), interpolation=cv2.INTER_CUBIC),cv2.COLOR_BGR2GRAY))
            #pics , pic_uuids = self.DB.getTrainingPictures("WHERE user_uuid = '{}'".format(key))

            recogPictureNum = 0
            trainPictureNum = 0

            #t_user_uuids, new_pic_uuids, user_pics = UserPicDf[UserPicDf['user_uuid'] == user_uuid]
            user_pics = UserPicDf[UserPicDf.index == user_uuid]
            #print(user_pics)

            for index in range(len(user_pics)):
                if index % 3 == 0:
                    recogPictureNum += 1
                else:
                    trainPictureNum +=  1

            #print("RecogNum: ",recogPictureNum)
            #print("TrainNum: ",trainPictureNum)

            testPicToTrainPicRatio = 0.2
            picNum = len(user_pics)
            #recogPictureNum = int(picNum * testPicToTrainPicRatio)
            #recogPictureNum = 1

            DBUser.imgShape = maxShape

            DBUser.recogPictures = np.zeros((recogPictureNum,maxPicSize))
            #newDatabaseUser.trainPictures = np.zeros((picNum - recogPictureNum,maxPicSize))
            DBUser.trainPictures = np.zeros((trainPictureNum,maxPicSize))

            for index,picTuple in enumerate(user_pics.itertuples()):
                #print(picTuple)

                #resizedPic = cv2.resize(pic, dsize=maxShape[:2], interpolation=cv2.INTER_CUBIC).reshape(maxShape[0] * maxShape[1] * 3)

                pic = getattr(picTuple,'pic_data')
                if pic.shape[0] == 0 or pic.shape[1] == 0:
                    #create empty pic if its corrupted
                    pic = np.random.randint(255, size=(maxShape[0],maxShape[1],3),dtype=np.uint8)
                #print(pic.shape)
                resizedPic = cv2.resize(pic.astype("uint8"), dsize=(maxShape[1],maxShape[0]), interpolation=cv2.INTER_CUBIC).flatten()

                #if index < recogPictureNum:
                if index % 3 == 0:

                    DBUser.recogPictures[index // 3] = resizedPic

                else:

                    DBUser.trainPictures[index // 3] = resizedPic


                    #newDatabaseUser.trainPictures[index - recogPictureNum] = resizedPic

            #userList.append(DBUser)

        self.pW.finProgress("bbInit")

        #Get Minimum number of recog and train pictures

        minRecog = np.Inf
        minTrain = np.Inf
        minUserRecog = None
        minUserTrain = None
        for key, user in newUserDict.items():
            if len(user.recogPictures) < minRecog:
                minRecog = len(user.recogPictures)
                minUserRecog = user
            if len(user.trainPictures) < minTrain:
                minTrain = len(user.trainPictures)
                minUserTrain = user
        #print("minUserRecog: ",minUserRecog.username)
        #print("minUserTrain: ",minUserTrain.username)
        #print("minRecog: ",minRecog)
        #print("minRecog: ",minTrain)

        #Crop the final user
        finalUserList = []
        for key, user in newUserDict.items():
            print(key)
            finalUser = userRecog(user.username)
            finalUser.recogPictures = user.recogPictures[:minRecog]
            finalUser.trainPictures = user.trainPictures[:minTrain]
            finalUser.imgShape = user.imgShape
            #print("user : {}\nLen recog: {}\n len train: {}".format(user.username,len(finalUser.recogPictures),len(finalUser.trainPictures)))
            finalUserList.append(finalUser)

        return finalUserList


    def closeGraceful(self):

        #
        # Controlled shutdown of GUI
        # Closes foreign classes
        # database connections etc.
        #

        self.master.destroy()
        self.exitFlag = True
        self.DB.close()

if __name__ == '__main__':
#
# Driver Code
#
   root = tk.Tk()
   main_app =  BVGUI(root)

   while True:
       t.sleep(0.01)

       if not main_app.exitFlag:
           main_app.update()
           root.update()

       else:
           exit()
