# @Author: Julius U. Heller <thekalk>
# @Date:   2021-06-03T22:21:03+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: BVGUI.py
# @Last modified by:   Julian Flieller
# @Last modified time: 2023-06-23
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
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..', 'src', 'DBM'))
import DatabaseManagement as DBM
from threading import Thread

#Face Detection
import platform
if platform.system() == 'Linux':
    from FaceDetectionClass import FaceDetection



class BVGUI (tk.Frame):
    """
    Benchmark Viewer Graphical User Interface
    BVGUI:
        Type Master class:
            - Managages displaying of Windows
            - Managages Data from foreign Dataset
            - Configures Main GUI Variables
            - Has control over tk.root
    """
    def __init__(self, master):

        # Init Master
        self.master = master

        self.master.withdraw()
        tk.Frame.__init__(self, self.master)

        self.updateFunctions = []
        self.DB = DBM.wire_DB()
        self.exitFlag = False

        # Set Window Dimensions
        self.windowDimension_x = 1500
        self.windowDimension_y = 600

        # Optimal Threshold Calculation
        self.threshold_calc = Threshold_Calc(data = None, labels = None)

        #Progress Window with progressbar
        self.pW = BVU.progresWindow(self.master,"BenchmarkViewer",self.windowDimension_x,self.windowDimension_y)
        self.pW.createProgressbar("guiInit")

        self.FaceDetection = None
        if platform.system() == 'Linux':
            self.FaceDetection = FaceDetection()
        #self.pW.dropDown(self.master,self)

        # Update progress window with custom text and progressbar position
        self.pW.update("guiInit","Initialising Benchmarks...",0)

        # Init Benchmark Class
        self.DbUsers = self.fetchDatabaseUsers()
        self.bR = benchRecog(root = self.master,master = self,pW = self.pW)
        self.update()
        self.pW.update("guiInit","Running Benchmarks...",0)

        self.pW.update("guiInit","Done...",85)

        # Initialize windows
        self.pW.createProgressbar("FrameInit")
        self.pW.update("FrameInit","Initialising True Positive Viewer...", 0)
        self.TPV = BVW.TPViewer(self, "visible")
        self.pW.update("FrameInit","Initialising True Negative Viewer...", 10)
        self.TNV = BVW.TNViewer(self, "hidden")
        self.pW.update("FrameInit","Initialising Mixed Viewer...", 20)
        self.MV = BVW.MixedViewer(self, "hidden")
        self.pW.update("FrameInit","Initialising User Viewer...", 30)
        self.UV = BVW.UserViewer(self, "visible", "UserViewer")
        self.pW.update("FrameInit","Initialising CV2 True Positive Viewer...", 40)
        self.CV2TP = BVW.CV2TPViewer(self, "hidden")
        self.pW.update("FrameInit","Initialising CV2 True Negative Viewer...", 50)
        self.CV2TN = BVW.CV2TNViewer(self, "hidden")
        self.pW.update("FrameInit","Initialising Face Recognition 2023 Viewer...", 60)
        self.FaceRecog2023 = BVW.FaceRecog2023Viewer(self, "hidden")
        self.pW.update("FrameInit","Initialising Face Recognition 2023 Positive Viewer...", 70)
        self.FaceRecog2023Positive = BVW.FaceRecog2023PositiveViewer(self, "hidden")
        self.pW.update("FrameInit","Initialising Face Recognition 2023 Negative Viewer...", 80)
        self.FaceRecog2023Negative = BVW.FaceRecog2023NegativeViewer(self, "hidden")
        ## add viewers that are available on all systems
        self.BVWindows = [
                self.TPV, self.TNV, self.MV, self.UV,
                self.CV2TP, self.CV2TN, self.FaceRecog2023, 
                self.FaceRecog2023Positive, self.FaceRecog2023Negative
             ]
        ## linux specific windows
        if platform.system() == 'Linux':
            self.OFTP = BVW.OFTPViewer(self,"hidden")
            self.pW.update("FrameInit","Initialising Openface True Positive Viewer...", 90)
            self.BVWindows.append(self.OFTP)

            self.OFTN = BVW.OFTNViewer(self,"hidden")
            self.pW.update("FrameInit","Initialising Openface True Negative Viewer...",100)
            self.BVWindows.append(self.OFTN)
        self.pW.finProgress("FrameInit")

        self.update()

        # Configure master variables
        self.configureMaster()

        self.pW.update("guiInit","Done...",100)
        self.pW.finProgress("guiInit")

        self.master.deiconify()

    def configureMaster(self):

        _bgcolor = '#FFFFFF'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'

        # Global Init of ttk.Styles
        self.style = ttk.Style()
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font=('Arial', 8))
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        self.titleFontStyle = ttk.Style()
        self.titleFontStyle.configure('.',background=_bgcolor)
        self.titleFontStyle.configure('.',foreground=_fgcolor)
        self.titleFontStyle.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])
        self.titleFontStyle.configure('title.TLabel', font=('Arial', 12))

        # Set geometry
        self.master.geometry("{}x{}+758+131".format(self.windowDimension_x,self.windowDimension_y))
        self.master.minsize(120, 1)
        self.master.maxsize(5764, 1041)
        self.master.resizable(1, 1)
        self.master.title("BenchmarkViewer")
        self.master.configure(background="#d9d9d9")

        # GUI Menubar
        self.menubar = tk.Menu(self.master,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        self.master.configure(menu = self.menubar)

        ## Initializing menubar of Wire benchmarks
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

        ## Creating and initializing menubar of Wire benchmarks
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

        # Creating and initializing menubar of openface benchmarks
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

        # Creating and initializing menubar of Face Recognition 2023 benchmark
        self.faceRecog2023Bar = tk.Menu(self.master,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        self.faceRecog2023Bar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="FaceRecog2023 Benchmark Viewer",
                command = lambda: self.switchWindow("FaceRecog2023"))
        self.faceRecog2023Bar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="FaceRecog2023 Positive Viewer",
                command = lambda: self.switchWindow("FaceRecog2023Positive"))
        self.faceRecog2023Bar.add_command(
                activebackground="#ececec",
                activeforeground="#000000",
                background="#d9d9d9",
                foreground="#000000",
                label="FaceRecog2023 Negative Viewer",
                command = lambda: self.switchWindow("FaceRecog2023Negative"))
        self.menubar.add_cascade(label="FaceRecog2023", menu=self.faceRecog2023Bar)

        # Creating and initializing menubar for CV2 benchmarks
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
        self.bR = benchRecog(
            root=self.master, 
            master=self, 
            userlimit=userlimit, 
            pW=self.pW
        )

    def update(self):
        """
        Update method Currently empty
        If foreign Classes need to be refreshed this is done here
        """
        for function in self.updateFunctions:
            function(self)

    def switchWindow(self,windowName):

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
        maxPicSize = 0
        maxShape = None
        pics = []
        pic_uuids = []
        user_uuids = []
        counter = 0
        for key, value in userDict.items():
            counter += 1
            u_pics , u_pic_uuids = self.DB.getTrainingPictures(user_uuid=key)
            pics += u_pics
            pic_uuids += u_pic_uuids
            for x in u_pics:
                user_uuids.append(key)

            self.pW.update("bbInit","Fetching Big Brother Users : {}".format(value),(counter / len(userDict)) * 100)
        for pic_index, pic in enumerate(pics):
            #flattened = pic.reshape(pic.shape[0] * pic.shape[1])
            if len(pic.shape) == 3 and pic.shape[2] == 3:
                pic = cv2.cvtColor(pic.astype("uint8"), cv2.COLOR_BGR2GRAY)
            flattened = pic.flatten()

            if flattened.shape[0] > maxPicSize:
                maxPicSize = flattened.shape[0]
                maxShape = pic.shape

        self.imShape = maxShape
        UserPicDf = pd.DataFrame(data = {'user_uuid' : user_uuids, 'pic_uuid' : pic_uuids, 'pic_data' : pics}).set_index('user_uuid')
        newUserDict = {}
        print(maxShape)
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
            #pics , pic_uuids = self.DB.getTrainingPictures(user_uuid=key)

            recogPictureNum = 0
            trainPictureNum = 0

            #t_user_uuids, new_pic_uuids, user_pics = UserPicDf[UserPicDf['user_uuid'] == user_uuid]
            user_pics = UserPicDf[UserPicDf.index == user_uuid]

            for index in range(len(user_pics)):
                # TODO: is 3 the number of images? Or what does this magic number
                # stand for?
                if index % 3 == 0:
                    recogPictureNum += 1
                else:
                    trainPictureNum +=  1

            testPicToTrainPicRatio = 0.2
            picNum = len(user_pics)
            #recogPictureNum = int(picNum * testPicToTrainPicRatio)
            #recogPictureNum = 1

            DBUser.imgShape = maxShape

            DBUser.recogPictures = np.zeros((recogPictureNum, maxPicSize))
            DBUser.trainPictures = np.zeros((trainPictureNum, maxPicSize))
            trainFillPointer = 0
            recogFillPointer = 0

            for index,picTuple in enumerate(user_pics.itertuples()):
                pic = getattr(picTuple,'pic_data')
                # Convert into grayscale to avoid size
                if len(pic.shape) == 3 and pic.shape[2] == 3:
                    pic = cv2.cvtColor(pic.astype("uint8"), cv2.COLOR_BGR2GRAY)

                if pic.shape[0] == 0 or pic.shape[1] == 0:
                    #create empty pic if its corrupted
                    pic = np.random.randint(255, size=(maxShape[0],maxShape[1],3),dtype=np.uint8)
                resizedPic = cv2.resize(pic.astype("uint8"), dsize=(maxShape[1],maxShape[0]), interpolation=cv2.INTER_CUBIC).flatten()

                if index % 3 == 0:
                    DBUser.recogPictures[recogFillPointer] = resizedPic
                    recogFillPointer += 1
                else:
                    DBUser.trainPictures[trainFillPointer] = resizedPic
                    trainFillPointer += 1
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

        #Crop the final user
        finalUserList = []
        for key, user in newUserDict.items():
            finalUser = userRecog(user.username)
            finalUser.recogPictures = user.recogPictures[:minRecog]
            finalUser.trainPictures = user.trainPictures[:minTrain]
            finalUser.imgShape = user.imgShape
            finalUserList.append(finalUser)

        return finalUserList

    def closeGraceful(self):
        """
        Controlled shutdown of GUI, Closes foreign classes, database connections etc.
        """
        self.master.destroy()
        self.exitFlag = True
        self.DB.close()

if __name__ == '__main__':
   root = tk.Tk()
   main_app =  BVGUI(root)

   while True:
       t.sleep(0.01)

       if not main_app.exitFlag:
           main_app.update()
           root.update()
       else:
           exit()
