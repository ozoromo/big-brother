# @Author: Julius U. Heller <thekalk>
# @Date:   2021-05-29T00:08:55+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: BV_Utils.py
# @Last modified by:   thekalk
# @Last modified time: 2021-06-09T14:58:08+02:00



import tkinter as tk
import tkinter.ttk as ttk
import time as t
import pandas as pd
py3 = True

#
# Util Classes to be imported
# Mostly Tkinter Subclasses
#

class BenchmarkTimer():

    def __init__ (self):

        self.bootUpTime = None

    def startTimer(self):

        startTime = t.time()

    def endTimer(self):

        endTime = t.time()

    def clear(self):

        self.__init__()

class UserTimer(BenchmarkTimer):

    #
    # Timer Class for easy benchmark Timing
    # USAGE:
    # This class is used to properly time a User Benchmark
    # 1. Init class
    # 2. call class.startTimer(user)
    # 3. Benchmark
    # 4. call class.endTimer(user)
    # 5. fetch times with class.getTimes()
    #

    def __init__ (self):

        BenchmarkTimer.__init__(self)

        self.userStartTimesRaw = []
        self.userEndTimesRaw = []
        self.userList = []
        #self.userTimeDf = None

    def startTimer(self,user):
        startTime = t.time()

        self.userList.append(user)
        self.userStartTimesRaw.append(startTime)


    def endTimer(self,user):
        # TODO: The user isn't used here! Could this lead to inconsistencies?
        endTime = t.time()
        self.userEndTimesRaw.append(endTime)

    def getTimes(self):
        # TODO: Find out error here! Because this condition is meet it would
        # mean that there are scenarios in which the timer are not stopped!
        while len(self.userEndTimesRaw) < len(self.userStartTimesRaw):
            self.endTimer(None)
            print("WARNING: End timer hasn't been stopped and had to be stopped manually")

        df = pd.DataFrame({'user':      self.userList,
                           'startTime': self.userStartTimesRaw, 
                           'endTime':   self.userEndTimesRaw})
        df['executeTime'] = df['endTime'] - df['startTime']
        return df


class progresWindow:
    #
    # This Class is a Window with possibly multiple progressbars
    #
    # USAGE:
    # 1. Initialize
    # 2. call class.createProgressbar("name of progressbar")
    #  -> you can create multiple progressbars by calling 2. again with different names
    # 3. update your progress with class.update("name of progressbar to be updated","Display Text",percentage of progress in int)
    # 4. remove the progressbar with class.finProgress("name of progressbar")
    #

    def __init__(self,master,name,windowDimension_x,windowDimension_y):

        self.master = master
        self.t0 = t.time()
        self.progresWindow = tk.Toplevel(self.master )
        self.progresWindow.title(name )
        self.windowDimension_x = windowDimension_x
        self.windowDimension_y = windowDimension_y
        self.windowPosx = int(self.master.winfo_x() + ((windowDimension_x / 2) - 250))
        self.windowPosy = int(self.master.winfo_y() + ((windowDimension_y / 2) - 37))

        self.name = name
        self.status = "init"
        self.progressbars =  {}

        self.dropFrame = tk.Frame(master=self.progresWindow,bg="#FFFFFF")
        self.progresWindow.geometry("500x75+{}+{}".format(self.windowPosx,self.windowPosy))

        self.master.update_idletasks()

    def createProgressbar(self,name):

        #
        # Creates new PB and adds it to class dict
        #
        # ARGUMENTS:
        # name = "name of progressbar to be created"
        #

        try:

            if self.progressbars[name]:
                print("Warning: Name already in class!")
                return

        except KeyError:
            pass

        if self.status == "hidden":
            #
            # The Class automatically hides itself if no progressbars are active
            # If the window is hidden it gets reinitialized
            #

            self.show()

        #Create widgets

        newPb = ttk.Progressbar(self.dropFrame, orient = tk.HORIZONTAL,length = 400, mode = 'determinate')
        newLabel = tk.Label(self.dropFrame,  text ="PLACEHOLDER",bg = '#FFFFFF')

        #Add to class dict

        self.progressbars[name] = [newPb,newLabel]

        #organize

        self.organize()

    def finProgress(self,name):

        #
        # Removes Progressbars
        # ARGUMENTS:
        #  name = "name of progressbar to be deleted"
        #

        try:
            self.progressbars[name]
        except KeyError:
            print(f"Warning : Name ({name}) not found!")
            return

        self.progressbars[name][0].destroy()
        self.progressbars[name][1].destroy()
        del self.progressbars[name]

        if len(self.progressbars) == 0:
            #
            # The Class automatically hides itself if no progressbars are active
            #
            self.hide()



    def dropDown(self):

        passedTime = time.time() - self.t0
        yFunc = passedTime * 0.1
        if yFunc < 0.3 and not self.status == "hidden":
            self.dropFrame.place(relx = 0.7,rely = yFunc - 0.3,relheight = 0.3,relwidth = 1)
            self.master.after(1000, self.dropDown)


    def organize(self):

        #
        # This Method organizes the Multiple progressbars
        # with proper Spacings and window Extension
        #

        count = len(self.progressbars)
        index = 0

        for progressName, pB in self.progressbars.items():
            #pB[1].grid(row=index, columnspan=50)
            #pB[0].grid(row=index + 1, columnspan=50)
            pB[1].place(x = 0,y = index * 35, width = 500,height = 25)
            pB[0].place(x = 0,y = (index + 1) * 35, width = 500,height = 25)
            index += 2

        self.progresWindow.geometry("500x{}+{}+{}".format(index * 35,self.windowPosx,self.windowPosy))
        self.dropFrame.place(relx = 0,rely = 0,relwidth = 1,relheight = 1)
        #self.dropFrame.grid(row = 0,column = 0)




    def update(self, name, displayText, percentage):

        try:
            self.progressbars[name]
        except KeyError:
            print(f"Warning : Name ({name}) not found!")
            return

        #print(self.progressbars[name][1])

        self.progressbars[name][1].config(text=displayText)

        self.progressbars[name][0]['value'] = percentage

        self.organize()

        self.master.update_idletasks()

    def hide(self):

        self.progresWindow.destroy()
        self.status = "hidden"

    def show(self):

        self.progresWindow = tk.Toplevel(self.master )
        self.progresWindow.title(self.name )
        self.progresWindow.geometry("500x75+{}+{}".format(self.windowPosx,self.windowPosy))

        self.dropFrame = tk.Frame(master=self.progresWindow,bg="#FFFFFF")

        self.master.update_idletasks()
        self.status = "visible"





    def destroy(self):
        self.progresWindow.destroy()





class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)

        #self.configure(yscrollcommand=_autoscroll(vsb),
        #    xscrollcommand=_autoscroll(hsb))
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass

        hsb.grid(column=0, row=1, sticky='ew')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Copy geometry methods of master  (taken from ScrolledText.py)
        if py3:
            methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
                  | tk.Place.__dict__.keys()
        else:
            methods = tk.Pack.__dict__.keys() + tk.Grid.__dict__.keys() \
                  + tk.Place.__dict__.keys()

        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)

def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
        container.bind('<Leave>', lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)
    return wrapped

class ScrolledListBox(AutoScroll, tk.Listbox):
    '''A standard Tkinter Listbox widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        tk.Listbox.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)
    def size_(self):
        sz = tk.Listbox.size(self)
        return sz

import platform
def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-MouseWheel>', lambda e: _on_shiftmouse(e, child))
    else:
        child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
        child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))

def _unbound_to_mousewheel(event, widget):
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        widget.unbind_all('<MouseWheel>')
        widget.unbind_all('<Shift-MouseWheel>')
    else:
        widget.unbind_all('<Button-4>')
        widget.unbind_all('<Button-5>')
        widget.unbind_all('<Shift-Button-4>')
        widget.unbind_all('<Shift-Button-5>')

def _on_mousewheel(event, widget):
    if platform.system() == 'Windows':
        widget.yview_scroll(-1*int(event.delta/120),'units')
    elif platform.system() == 'Darwin':
        widget.yview_scroll(-1*int(event.delta),'units')
    else:
        if event.num == 4:
            widget.yview_scroll(-1, 'units')
        elif event.num == 5:
            widget.yview_scroll(1, 'units')

def _on_shiftmouse(event, widget):
    if platform.system() == 'Windows':
        widget.xview_scroll(-1*int(event.delta/120), 'units')
    elif platform.system() == 'Darwin':
        widget.xview_scroll(-1*int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.xview_scroll(-1, 'units')
        elif event.num == 5:
            widget.xview_scroll(1, 'units')
