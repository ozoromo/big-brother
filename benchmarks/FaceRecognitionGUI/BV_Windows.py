# @Author: Julius U. Heller <thekalk>
# @Date:   2021-05-29T00:06:34+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: BV_Windows.py
# @Last modified by:   thekalk
# @Last modified time: 2021-06-09T14:55:53+02:00

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

#Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
import matplotlib.dates as mdates
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
import time
from enum import Enum

import BV_Utils as BVU

class BenchmarkType(Enum):
    TP = 0
    TN = 1
    OFTN = 2
    OFTP = 3
    CV2TN = 4
    CV2TP = 5
    Mixed = 6
    FaceRecog2023 = 7
    FaceRecog2023Positive = 8
    FaceRecog2023Negative = 9


class BVWindow:
    def __init__(self,GUI,windowStatus,name):
        self.parent = GUI
        self.windowStatus = windowStatus
        self.DynSIPLabels = []
        self.DynTimeLabels = []
        self.DynMetaDataLabels = []
        self.name = name

        self.masterFrame = tk.Frame(GUI.master)
        self.masterFrame.configure(relief='groove')
        self.masterFrame.configure(borderwidth="0")
        self.masterFrame.configure(relief="groove")
        self.masterFrame.configure(background="#FFFFFF")

        #self.masterFrame = self.Frame1

    def show(self):
        self.masterFrame.place(relx=0.0, rely=0.0, relheight=1.058, relwidth=1.008)
        self.windowStatus = "visible"

    def hide(self):
        self.masterFrame.place_forget()
        self.windowStatus = "hidden"

    def buildSIPDynamicLabels(self, master, amount):
        labels = []
        portLen = amount
        spacing = (1 - 1/portLen)/portLen
        y = 0
        for column in range(amount):
            label = ttk.Label(master,text="PLACEHOLDER")
            #label.config(bg="#FFFFFF")
            label.config(anchor=tk.W)
            label.place(relx=0, rely=y, relheight=spacing, relwidth=1)
            labels.append(label)
            y += spacing
        return labels

    # TODO: Refactor this method. It isn't designed well.
    def updateBenchmark(self, benchmarkType: BenchmarkType):
        # TODO: self.getUserLimitEntry() is not defined in this class, but
        # rather in the class that inherits this class. This compiles, but
        # it seems to me that this code isn't clean! This needs to get resolved
        # changed! This is also the case for a lot of the methods that get
        # called in updateBenchmark()!
        userlimit = self.getUserLimitEntry()
        userTimes = None

        if userlimit == 0:
            return

        self.parent.updateBenchmark(userlimit = userlimit)

        if self.parent.bR.exitFlag:
            return

        if benchmarkType == BenchmarkType.TP:
            self.scores = self.parent.bR.run_true_positives()
            userTimes = self.parent.bR.TPUserTimer.getTimes()
        elif benchmarkType == BenchmarkType.TN:
            self.scores = self.parent.bR.run_true_negatives()
            userTimes = self.parent.bR.TNUserTimer.getTimes()
        elif benchmarkType == BenchmarkType.OFTN:
            pass
            # TODO: openface_run_true_negatives_doesn't exist somehow
            #self.scores = self.parent.bR.openface_run_true_positives()
            #userTimes = self.parent.bR.OFTNUserTimer.getTimes()
        elif benchmarkType == BenchmarkType.OFTP:
            self.scores = self.parent.bR.openface_run_true_positives()
            userTimes = self.parent.bR.OFTPUserTimer.getTimes()
        elif benchmarkType == BenchmarkType.CV2TN:
            self.scores = self.parent.bR.opencv_run_true_negatives()
            userTimes = self.parent.bR.CV2TNUserTimer.getTimes()
        elif benchmarkType == BenchmarkType.CV2TP:
            self.scores = self.parent.bR.opencv_run_true_positives()
            userTimes = self.parent.bR.CV2TPUserTimer.getTimes()
        elif benchmarkType == BenchmarkType.Mixed:
            numSelfIm = 5
            numDecoy = 5
            numDecoyIm = 10
            try:
                numSelfIm = int(self.numSelfImagesEntry.get())
                numDecoy = int(self.numDecoyUsersEntry.get())
                numDecoyIm = int(self.numDecoyUserImages.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid Input only numbers allowed")
                return
            self.scores = self.parent.bR.run_mixed_positives(numSelfIm ,numDecoy,numDecoyIm)
            userTimes = self.parent.bR.MixedUserTimer.getTimes()
        elif benchmarkType == BenchmarkType.FaceRecog2023:
            self.scores = self.parent.bR.face_recog_2023_run_benchmark()
            userTimes = self.parent.bR.FaceRecog2023UserTimer.getTimes()
        elif benchmarkType == BenchmarkType.FaceRecog2023Positive:
            self.scores = self.parent.bR.face_recog_2023_run_positive()
            userTimes = self.parent.bR.FaceRecog2023PositiveUserTimer.getTimes()
        elif benchmarkType == BenchmarkType.FaceRecog2023Negative:
            self.scores = self.parent.bR.face_recog_2023_run_negative()
            userTimes = self.parent.bR.FaceRecog2023NegativeUserTimer.getTimes()

        self.updateListbox()

        # Config Time Labels
        self.DynTimeLabels[0].config(text="Benchmark Time: {}s".format(round(userTimes['executeTime'].sum(), 2)))
        self.DynTimeLabels[1].config(text="Avg. User Time: {}s".format(round(userTimes['executeTime'].mean(), 2)))
        maxUserTime = userTimes[['user','executeTime']].iloc[userTimes['executeTime'].idxmax()]
        self.DynTimeLabels[2].config(text="Max User Time: {} {}s".format(maxUserTime[0].username,round(maxUserTime[1], 2)))
        minUserTime = userTimes[['user','executeTime']].iloc[userTimes['executeTime'].idxmin()]
        self.DynTimeLabels[3].config(text="Min User Time: {} {}s".format(minUserTime[0].username,round(minUserTime[1], 2)))
        self.DynTimeLabels[4].config(text="Min/Max Variance: {}s".format(round(maxUserTime[1] - minUserTime[1], 2)))

        # Config Benchmark Meta Data Labels
        self.DynMetaDataLabels_1[0].config(text="Benchmark Meta Data", style='title.TLabel')
        self.DynMetaDataLabels_1[1].config(text="Loaded Training Pictures: {}".format(self.parent.bR.trainPictureCount))
        self.DynMetaDataLabels_1[2].config(text="Loaded Input Pictures: {}".format(self.parent.bR.recogPictureCount))
        self.DynMetaDataLabels_1[3].config(text="Overall Score Mean: {}".format(round(self.scores['recogScore'].mean(), 2)))

        self.DynMetaDataLabels_2[0].config(text="", style = 'title.TLabel')
        self.DynMetaDataLabels_2[1].config(text="F score Level: {}".format(self.parent.threshold_calc.f_Score_Level))
        self.DynMetaDataLabels_2[2].config(text="F Score: {}".format(self.parent.threshold_calc.f_Score))
        self.DynMetaDataLabels_2[3].config(text="Threshold: {}".format(self.parent.threshold_calc.thresh))


class UserViewer(BVWindow):

    def __init__(self,GUI,windowStatus,name):
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        _lightgray = "#FAFAFA"

        self.ttkstyle = ttk.Style()
        self.ttkstyle.configure(
                'TScale',
                background=_lightgray,
                foreground='white',
                font=('Helvetica', 18, 'bold')
            )

        self.ttkstyle.configure('TCheckbutton',
        background=_lightgray,)

        self.selectedIndex = None

        BVWindow.__init__(self,GUI,windowStatus,name)

        self.RightLBFrame = tk.Frame(self.masterFrame)
        self.RightLBFrame.place(relx=0.0, rely=0.0, relheight=0.95, relwidth=0.3)
        self.RightLBFrame.configure(relief='groove')
        self.RightLBFrame.configure(borderwidth="0")
        self.RightLBFrame.configure(relief="groove")
        self.RightLBFrame.configure(background = _lightgray)

        self.titleLabel = ttk.Label(self.RightLBFrame,text = "Big Brother User Viewer")
        self.titleLabel.place(relx=0.0, rely=0.0, relheight=0.05, relwidth=1)
        self.titleLabel.config(text = "Big Brother User Viewer" ,style = 'title.TLabel')

        self.UserFrame = tk.Frame(self.masterFrame)
        self.UserFrame.place(relx=0.3, rely=0.0, relheight=0.95, relwidth=0.7)
        self.UserFrame.configure(relief='groove')
        self.UserFrame.configure(borderwidth="0")
        self.UserFrame.configure(relief="groove")
        self.UserFrame.configure(background = _lightgray)

        self.UFSubFrame1 = tk.Frame(self.UserFrame)
        self.UFSubFrame1.place(relx=0.0, rely=0.0, relheight=0.95, relwidth=0.5)
        self.UFSubFrame1.configure(relief='groove')
        self.UFSubFrame1.configure(borderwidth="0")
        self.UFSubFrame1.configure(relief="groove")
        self.UFSubFrame1.configure(background = _lightgray)

        self.UFSubFrame2 = tk.Frame(self.UserFrame)
        self.UFSubFrame2.place(relx=0.5, rely=0.0, relheight=0.95, relwidth=0.5)
        self.UFSubFrame2.configure(relief='groove')
        self.UFSubFrame2.configure(borderwidth="0")
        self.UFSubFrame2.configure(relief="groove")
        self.UFSubFrame2.configure(background = _lightgray)

        self.UserLB = BVU.ScrolledListBox(self.RightLBFrame)
        self.UserLB.place(relx=0.0, rely=0.05, relheight=0.5, relwidth=0.75)
        self.UserLB.configure(background="white")
        self.UserLB.configure(disabledforeground="#a3a3a3")
        self.UserLB.configure(font="TkFixedFont")
        self.UserLB.configure(foreground="black")
        self.UserLB.configure(highlightbackground="#d9d9d9")
        self.UserLB.configure(highlightcolor="#d9d9d9")
        self.UserLB.configure(selectbackground="#c4c4c4")
        self.UserLB.configure(selectforeground="black")

        self.UserLB.bind('<<ListboxSelect>>', lambda e: self.switchUser() )

        self.prevTestButton = ttk.Button(self.UFSubFrame1,text = "Prev. Test Picture", command=lambda : self.switchPic("test","prev"))
        self.prevTestButton.place(relx=0.25, rely=0.5,relheight = 0.06, relwidth = 0.20)

        self.nextTestButton = ttk.Button(self.UFSubFrame1,text = "Next Test Picture", command=lambda : self.switchPic("test","next"))
        self.nextTestButton.place(relx=0.50, rely=0.5,relheight = 0.06, relwidth = 0.20)

        self.prevTrainButton = ttk.Button(self.UFSubFrame2,text = "Prev. Train Picture", command=lambda : self.switchPic("train","prev"))
        self.prevTrainButton.place(relx=0.25, rely=0.5,relheight = 0.06, relwidth = 0.20)

        self.nextTrainButton = ttk.Button(self.UFSubFrame2,text = "Next Train Picture", command=lambda : self.switchPic("train","next"))
        self.nextTrainButton.place(relx=0.50, rely=0.5,relheight = 0.06, relwidth = 0.20)


        self.recogFig = plt.figure(self.name + "_recogPicFig",figsize=(1, 1))
        self.recogFig.set_size_inches(25, 25)

        plt.subplots_adjust(left= 0.1 , bottom=0.15  , right=0.9, top= 0.99 , wspace=0.3, hspace=0.7)

        self.recogPicCanvas = FigureCanvasTkAgg(self.recogFig, master=self.UFSubFrame1)  # A tk.DrawingArea.
        self.recogPicCanvas.draw()
        self.recogPicCanvas.get_tk_widget().place(relx = 0,rely = 0,relwidth = 1, relheight = 0.5)

        toolbar = NavigationToolbar2Tk(self.recogPicCanvas, self.UFSubFrame1)
        toolbar.place(relx = 0.0,rely= 0.93)
        toolbar.config(background=_lightgray)
        toolbar._message_label.config(background=_lightgray)

        self.trainPicFig = plt.figure(self.name + "_trainPicFig",figsize=(1, 1))

        plt.subplots_adjust(left= 0.1 , bottom=0.15  , right=0.9, top= 0.99 , wspace=0.3, hspace=0.7)

        self.trainPicCanvas  = FigureCanvasTkAgg(self.trainPicFig, master=self.UFSubFrame2)  # A tk.DrawingArea.
        self.trainPicCanvas .draw()
        #self.plotCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.trainPicCanvas .get_tk_widget().place(relx = 0,rely = 0,relwidth = 1, relheight = 0.5)

        toolbar = NavigationToolbar2Tk(self.trainPicCanvas, self.UFSubFrame2)
        toolbar.place(relx = 0.0,rely= 0.93)
        toolbar.config(background=_lightgray)
        toolbar._message_label.config(background=_lightgray)

        self.currentUser = None

        self.updateListbox()

        self.currentRecogPicIndex = 0
        self.currentTrainPicIndex = 0

    def switchUser(self):
        self.currentRecogPicIndex = 0
        self.currentTrainPicIndex = 0
        self.updateUserView()

    def switchPic(self,pictype,switchtype):
        if not self.currentUser:
            return

        if switchtype == "next":
            if pictype == "train":
                if self.currentTrainPicIndex + 1 < len(self.currentUser.trainPictures):
                    self.currentTrainPicIndex += 1
                    self.updateUserView()
            elif pictype == "test":
                if self.currentRecogPicIndex + 1 < len(self.currentUser.recogPictures):
                    self.currentRecogPicIndex += 1
                    self.updateUserView()
        elif switchtype == "prev":
            if pictype == "train":
                if self.currentTrainPicIndex - 1 >= 0:
                    self.currentTrainPicIndex -= 1
                    self.updateUserView()
            elif pictype == "test":
                if self.currentRecogPicIndex - 1 >= 0:
                    self.currentRecogPicIndex -= 1
                    self.updateUserView()

    def updateUserView(self):
        if self.UserLB.curselection() == ():
            return

        cursel = self.UserLB.curselection()[0]

        benchmarkRecog = self.parent.bR
        user = benchmarkRecog.dbUsers[cursel]

        self.currentUser = user

        self.trainPicFig.clf()
        self.recogFig.clf()

        plt.figure(self.name + "_recogPicFig")

        pic = user.recogPictures[self.currentRecogPicIndex]

        #reshapedPic = pic.reshape((user.imgShape[1],user.imgShape[0],3))
        #print(user.imgShape)
        reshapedPic = pic.reshape(user.imgShape)

        plt.imshow(reshapedPic.astype('uint8'))

        plt.figure(self.name + "_trainPicFig")

        pic = user.trainPictures[self.currentTrainPicIndex]

        #reshapedPic = pic.reshape((user.imgShape[1],user.imgShape[0],3))
        reshapedPic = pic.reshape(user.imgShape)

        plt.imshow(reshapedPic.astype('uint8'))

        self.trainPicCanvas.draw()
        self.recogPicCanvas.draw()

        return

    def updateListbox(self):
        if self.UserLB.size()[0] > 0:
            lastSel = self.UserLB.curselection()

        self.UserLB.delete(0,tk.END)

        for user in self.parent.bR.dbUsers:
            self.UserLB.insert(tk.END, "Username: {}".format(user.username))

        self.UserLB.selection_set(0)

        if len(lastSel) > 0:
            self.UserLB.selection_set(lastSel)


class GraphViewer(BVWindow):
    """
    Subclass of BVWindow
    """

    def __init__(self,GUI,windowStatus,name):
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        _lightgray = "#FAFAFA"

        self.ttkstyle = ttk.Style()
        self.ttkstyle.configure('TScale',
        background=_lightgray,
        foreground='white',
        font=('Helvetica', 18, 'bold'))

        self.ttkstyle.configure('TCheckbutton',
        background=_lightgray,)

        self.selectedIndex = None

        BVWindow.__init__(self,GUI,windowStatus,name)

        self.Frame2 = tk.Frame(self.masterFrame)
        self.Frame2.place(relx=0.150, rely=0.0, relheight=0.95, relwidth=0.5)
        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="0")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(background="#FFFFFF")
        self.Frame2.configure(cursor="sb_h_double_arrow")

        self.Frame3 = tk.Frame(self.masterFrame)
        self.Frame3.place(relx=0.0, rely=0.3, relheight=0.7, relwidth=0.15)
        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="0")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(background = _lightgray)

        self.plotFrame = tk.Frame(self.masterFrame)
        self.plotFrame.place(relx=0.5, rely=0.0, relheight=0.95, relwidth=0.5)
        self.plotFrame.configure(relief='groove')
        self.plotFrame.configure(borderwidth="0")
        self.plotFrame.configure(relief="groove")
        self.plotFrame.configure(background="#FFFFFF")
        self.plotFrame.configure(cursor="sb_h_double_arrow")

        self.titleLabel = ttk.Label(self.masterFrame,text = "PLACEHOLDER")
        self.titleLabel.place(relx=0.0, rely=0.0, relheight=0.05, relwidth=0.15)

        self.Scrolledlistbox1 = BVU.ScrolledListBox(self.masterFrame)
        self.Scrolledlistbox1.place(relx=0.0, rely=0.05, relheight=0.3, relwidth=0.15)
        self.Scrolledlistbox1.configure(background="white")
        self.Scrolledlistbox1.configure(disabledforeground="#a3a3a3")
        self.Scrolledlistbox1.configure(font="TkFixedFont")
        self.Scrolledlistbox1.configure(foreground="black")
        self.Scrolledlistbox1.configure(highlightbackground="#d9d9d9")
        self.Scrolledlistbox1.configure(highlightcolor="#d9d9d9")
        self.Scrolledlistbox1.configure(selectbackground="#c4c4c4")
        self.Scrolledlistbox1.configure(selectforeground="black")

        self.Scrolledlistbox1.bind('<<ListboxSelect>>', lambda e: self.updatePlot(e.widget) )

        self.userLimitLabel = ttk.Label(self.Frame3,text = "Enter User Limit:")
        self.userLimitLabel.place(relx=0.0, rely=0.1,relheight = 0.05, relwidth = 0.5)

        self.runTestOnParameterButton = ttk.Button(self.Frame3,text = "Run with Userlimit")
        self.runTestOnParameterButton.place(relx=0.35, rely=0.15,relheight = 0.06, relwidth = 0.6)

        self.userLimitEntry = ttk.Entry(self.Frame3)
        self.userLimitEntry.place(relx=0.0, rely=0.15,relheight = 0.05,relwidth = 0.3)
        self.userLimitEntry.insert(tk.END,"5")

        self.Scrolledlistbox1.bind('<<ListboxSelect>>', lambda e: self.updatePlot(e.widget) )

        self.timeFrame = tk.Frame(master=self.Frame3,background=_lightgray)
        #self.timeFrame.place(relx=0.0, rely=0.5,relheight = 0.5)
        self.timeFrame.place(relx=0.0, rely=0.6, relheight=0.4, relwidth=1)
        self.DynTimeLabels = self.buildSIPDynamicLabels(self.timeFrame,5)

        for label in self.DynTimeLabels:
            label.config(background = _lightgray)

        self.updateListbox()

        benchmarkRecog = self.parent.bR
        user = benchmarkRecog.users[0] # Users have to have same parameters

        #
        # Face Plot on the left side of the gui
        #

        self.fig = plt.figure(self.name + "_fig",figsize=(10, 10))
        self.fig.set_size_inches(25, 25)

        plt.subplots_adjust(left= 0.03 , bottom=0.164  , right=0.6, top= 0.99 , wspace=0.3, hspace=0.7)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.Frame2)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(self.canvas, self.Frame2)
        toolbar.place(relx = 0.0,rely= 0.93)
        toolbar.config(background='white')
        toolbar._message_label.config(background='white')

        self.plotFig = plt.figure(self.name + "_plotFig",figsize=(10, 10))

        plt.subplots_adjust(left= 0.13 , bottom=0.11  , right=0.95, top= 0.99 , wspace=0.07, hspace=0.7)

        self.plotCanvas = FigureCanvasTkAgg(self.plotFig, master=self.plotFrame)  # A tk.DrawingArea.
        self.plotCanvas.draw()
        #self.plotCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.plotCanvas.get_tk_widget().place(relx = 0,rely = 0.4,relwidth = 1, relheight = 0.45)

        toolbar = NavigationToolbar2Tk(self.plotCanvas, self.plotFrame)
        toolbar.place(relx = 0.0,rely= 0.93)
        toolbar.config(background='white')
        toolbar._message_label.config(background='white')


        self.metaDataFrame = tk.Frame(self.plotFrame,background="#FFFFFF")
        self.metaDataFrame.place(relx=0.0, rely=0.0, relheight=0.4, relwidth=1)

        self.metaDataFrame_1 = tk.Frame(self.metaDataFrame ,background="#FFFFFF")
        self.metaDataFrame_1.place(relx=0.0, rely=0.0, relheight=1, relwidth=0.5)

        self.metaDataFrame_2 = tk.Frame(self.metaDataFrame ,background="#FFFFFF")
        self.metaDataFrame_2.place(relx=0.5, rely=0.0, relheight=1, relwidth=0.5)

        self.DynMetaDataLabels_1 = self.buildSIPDynamicLabels(self.metaDataFrame_1,4)
        self.DynMetaDataLabels_2 = self.buildSIPDynamicLabels(self.metaDataFrame_2,4)

    def updateListbox(self):
        if self.Scrolledlistbox1.size()[0] > 0:
            lastSel = self.Scrolledlistbox1.curselection()

        self.Scrolledlistbox1.delete(0,tk.END)

        for user in self.parent.bR.users:
            self.Scrolledlistbox1.insert(tk.END, "Username: {}".format(user.username))

        self.Scrolledlistbox1.selection_set(0)

        if len(lastSel) > 0:
            self.Scrolledlistbox1.selection_set(lastSel)


    def updatePlot(self,widget):

        if widget.curselection() == ():
            return

        cursel = widget.curselection()[0]

        benchmarkRecog = self.parent.bR
        user = benchmarkRecog.users[cursel]

        self.fig.clf()
        self.plotFig.clf()

        plt.figure(self.name + "_fig")

        benchmarkRecog.plot_user(self.fig,user,self.scores[self.scores['username'] == user.username])

        #print(self.scores[self.scores['username'] == user.username])
        #print(self.fig.fignum)

        plt.figure(self.name + "_plotFig")

        plt.grid(True)

        #print(self.scores[self.scores['username'] == user.username])

        x = self.scores['testImageIndex'][self.scores['username'] == user.username]
        y = self.scores['recogScore'][self.scores['username'] == user.username]

        plt.plot(x,y,marker='o')

        #Plot Mean
        mean = y.mean()
        plt.plot([x.iloc[0],x.iloc[-1:]],[mean,mean])
        plt.text(x.iloc[0],mean, "Mean : {}".format(round(mean,4)), fontsize=10)

        #Plot Max
        max = y.max()
        plt.plot([x.iloc[0],x.iloc[-1:]],[max,max])
        plt.text(x.iloc[0],max, "Max : {}".format(round(max,4)), fontsize=10)

        #Plot Min
        min = y.min()
        plt.plot([x.iloc[0],x.iloc[-1:]],[min,min])
        plt.text(x.iloc[0],min, "Min : {}".format(round(min,4)), fontsize=10)

        plt.xlabel(self.plotPrettyLabel)
        plt.ylabel("Scores (Lower is Better)")


        self.canvas.draw()
        self.plotCanvas.draw()

    def getUserLimitEntry(self):
        userLimit = 0
        try:
            userLimit = int(self.userLimitEntry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid Input only numbers allowed")
            pass
        return userLimit


class TPViewer(GraphViewer):
    def __init__(self, GUI, windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self,GUI,windowStatus,"TPViewer")

        self.benchmarkType = BenchmarkType.TP

        # Configuring GUI elements
        self.titleLabel.config(text = "True Positive Viewer" ,style = 'title.TLabel')
        self.plotPrettyLabel = "True Positive Pictures"
        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))

        self.updateBenchmark(self.benchmarkType)

        if self.windowStatus == "visible":
            self.show()


class TNViewer(GraphViewer):
    def __init__(self,GUI,windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self,GUI,windowStatus,"TNViewer")

        self.benchmarkType = BenchmarkType.TN

        # Configuring GUI elements
        self.titleLabel.config(text = "True Negative Viewer",style = 'title.TLabel')
        self.plotPrettyLabel = "True Negative Pictures"
        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))

        self.updateBenchmark(self.benchmarkType)

        if self.windowStatus == "visible":
            self.show()


class OFTNViewer(GraphViewer):
    def __init__(self,GUI,windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self,GUI,windowStatus,"OFTNViewer")

        self.benchmarkType = BenchmarkType.OFTN

        # Configuring GUI elements
        self.titleLabel.config(text = "Openface True Negative Viewer",style = 'title.TLabel')
        self.plotPrettyLabel = "Openface True Negative Pictures"
        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))

        self.updateBenchmark(self.benchmarkType)

        if self.windowStatus == "visible":
            self.show()

class OFTPViewer(GraphViewer):
    def __init__(self,GUI,windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self,GUI,windowStatus,"OFTPViewer")

        self.benchmarkType = BenchmarkType.OFTP

        # Configuring GUI elements
        self.titleLabel.config(text = "Openface True Positive Viewer" ,style = 'title.TLabel')
        self.plotPrettyLabel = "Openface True Positive Pictures"
        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))

        self.updateBenchmark(self.benchmarkType)

        if self.windowStatus == "visible":
            self.show()

class CV2TNViewer(GraphViewer):
    def __init__(self,GUI,windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self,GUI,windowStatus,"CV2TNViewer")

        self.benchmarkType = BenchmarkType.CV2TN

        # Configuring GUI elements
        self.titleLabel.config(text = "CV2 True Negative Viewer",style = 'title.TLabel')
        self.plotPrettyLabel = "CV2 True Negative Pictures"
        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))

        self.updateBenchmark(self.benchmarkType)

        if self.windowStatus == "visible":
            self.show()


class CV2TPViewer(GraphViewer):
    def __init__(self,GUI,windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self,GUI,windowStatus,"CV2TPViewer")

        self.benchmarkType = BenchmarkType.CV2TP

        # Configuring GUI elements
        self.titleLabel.config(text = "CV2 True Positive Viewer" ,style = 'title.TLabel')
        self.plotPrettyLabel = "CV2 True Positive Pictures"
        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))

        self.updateBenchmark(self.benchmarkType)

        if self.windowStatus == "visible":
            self.show()


class MixedViewer(GraphViewer):
    def __init__(self,GUI,windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self,GUI,windowStatus,"MixedViewer")

        self.benchmarkType = BenchmarkType.Mixed

        # Configuring GUI elements
        self.runTestOnParameterButton.configure(text = "Run with Parameters")
        self.runTestOnParameterButton.place(relx=0.0, rely=0.55,relheight = 0.05,relwidth = 0.9)

        self.numSelfImagesLabel = ttk.Label(self.Frame3,text = "Num. of Query Images in Train Images:")
        self.numSelfImagesLabel.place(relx=0.0, rely=0.20,relheight = 0.05, relwidth = 1)

        self.numSelfImagesEntry = ttk.Entry(self.Frame3)
        self.numSelfImagesEntry.place(relx=0.0, rely=0.25,relheight = 0.05,relwidth = 0.3)
        self.numSelfImagesEntry.insert(tk.END,"5")

        self.numDecoyUsersLabel = ttk.Label(self.Frame3,text = "Num. of Other Users in Train Images")
        self.numDecoyUsersLabel.place(relx=0.0, rely=0.30,relheight = 0.05, relwidth = 1)

        self.numDecoyUsersEntry = ttk.Entry(self.Frame3)
        self.numDecoyUsersEntry.place(relx=0.0, rely=0.35,relheight = 0.05,relwidth = 0.3)
        self.numDecoyUsersEntry.insert(tk.END,"5")

        self.numDecoyUsersLabel = ttk.Label(self.Frame3,text = "Num. Pic. from other Users in Train Images")
        self.numDecoyUsersLabel.place(relx=0.0, rely=0.40,relheight = 0.05, relwidth = 1)

        self.numDecoyUserImages = ttk.Entry(self.Frame3)
        self.numDecoyUserImages.place(relx=0.0, rely=0.45,relheight = 0.05,relwidth = 0.3)
        self.numDecoyUserImages.insert(tk.END,"10")

        self.titleLabel.config(text = "Mixed Viewer",style = 'title.TLabel')

        self.plotPrettyLabel = "Mixed Pictures"

        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))


        self.updateBenchmark(self.benchmarkType)

        if (self.windowStatus == "visible"):
            self.show()


class FaceRecog2023Viewer(GraphViewer):
    def __init__(self,GUI,windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self, GUI, windowStatus,"FaceRecog2023")

        self.benchmarkType = BenchmarkType.FaceRecog2023

        # Configuring GUI elements
        self.titleLabel.config(text = "FaceRecog2023" ,style = 'title.TLabel')
        self.plotPrettyLabel = "Face Recognition 2023"
        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))

        self.updateBenchmark(self.benchmarkType)

        if (self.windowStatus == "visible"):
            self.show()


class FaceRecog2023PositiveViewer(GraphViewer):
    def __init__(self,GUI,windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self, GUI, windowStatus,"FaceRecog2023Positive")

        self.benchmarkType = BenchmarkType.FaceRecog2023Positive

        # Configuring GUI elements
        self.titleLabel.config(text = "FaceRecog2023Positive" ,style = 'title.TLabel')
        self.plotPrettyLabel = "Face Recognition 2023 Positive"
        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))

        self.updateBenchmark(self.benchmarkType)

        if (self.windowStatus == "visible"):
            self.show()


class FaceRecog2023NegativeViewer(GraphViewer):
    def __init__(self,GUI,windowStatus):

        # Starting GraphViewer Superclass
        GraphViewer.__init__(self, GUI, windowStatus,"FaceRecog2023Negative")

        self.benchmarkType = BenchmarkType.FaceRecog2023Negative

        # Configuring GUI elements
        self.titleLabel.config(text = "FaceRecog2023Negative" ,style = 'title.TLabel')
        self.plotPrettyLabel = "Face Recognition 2023 Negative"
        self.runTestOnParameterButton.config(command = lambda: self.updateBenchmark(self.benchmarkType))

        self.updateBenchmark(self.benchmarkType)

        if (self.windowStatus == "visible"):
            self.show()

if __name__ == '__main__':
    from BVGUI import BVGUI
    import time
    root = tk.Tk()
    main_app =  BVGUI(root)

    while True:
        time.sleep(0.1)
        if not main_app.exitFlag:
            root.update()
        else:
            exit()
