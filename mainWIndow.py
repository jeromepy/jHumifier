from tkinter import *
import tkinter.ttk
import math
from queue import Queue


class mainWindow(object):

    def __init__(self):

        self.taskQueue = Queue()


        self.initWindow()

    def initWindow(self):
        '''
            Initiate tkinter window
        '''
        self.colorTheme = {"Fg": "#e0e0e0", "BgOne": "#DADADA", "BgTwo": "#0B2B53"}

        # setup main Window and page
        self.tk = Tk()
        self.footer = Frame(self.tk, borderwidth=10)
        self.mainFrame = Frame(self.tk, borderwidth=10)
        self.mainFrame.pack(fill=BOTH, expand=True)
        self.footer.pack(fill=BOTH)  # expand=True,

        # general settings
        screenwidth = str(math.floor(self.tk.winfo_screenwidth() * 0.8))
        screenheight = str(self.tk.winfo_screenheight())
        self.tk.geometry(screenwidth + "x" + screenheight)
        self.tk.title("jHumidity Client")
        self.tk.option_add("*Font", ("gothic", 12))
        self.tk.option_add("*Background", self.colorTheme["BgTwo"])
        self.tk.option_add("*Foreground", self.colorTheme["Fg"])
        self.tk.option_add("*Button*Background", self.colorTheme["BgTwo"])
        self.tk.option_add("*Label*Background", self.colorTheme["BgTwo"])
        self.tk.option_add("*Scrollbar*Background", self.colorTheme["BgOne"])
        self.tk.option_add("*Listbox*Background", self.colorTheme["BgOne"])
        self.tk.option_add("*Listbox*Foreground", self.colorTheme["Fg"])
        self.tk.option_add("*Entry*Background", self.colorTheme["BgOne"])
        self.tk.option_add("*Entry*Foreground", self.colorTheme["Fg"])
        self.tk.option_add("*tkinter.ttk.Combobox*Foreground", self.colorTheme["Fg"])
        self.tk.option_add("*tkinter.ttk.Combobox*Background", self.colorTheme["BgOne"])
        self.tk.option_add("*tearOff", FALSE)
        self.mainFrame.configure(bg=self.colorTheme["BgTwo"])
        self.footer.configure(bg=self.colorTheme["BgTwo"])

        '''
        Top frame (topFrame) - State information
        '''

        self.topFrame = Frame(self.mainFrame, borderwidth=5)

        self.label1 = Label(self.topFrame, text="Current weather state")
        self.label2 = Label(self.topFrame, text="Date:", anchor=W)
        self.label3 = Label(self.topFrame, text="Temperature", anchor=W)
        self.label4 = Label(self.topFrame, text="Relative Humidity", anchor=W)
        self.label5 = Label(self.topFrame, text="Pressure", anchor=W)
        self.label6 = Label(self.topFrame, text="Status Messages:")

        self.dataDate = Label(self.topFrame, text="-", anchor=W)
        self.tempData = Label(self.topFrame, text="-", anchor=W)
        self.humData = Label(self.topFrame, text="-", anchor=W)
        self.pressData = Label(self.topFrame, text="-", anchor=W)

        self.statusFrame = Frame(self.topFrame, bd=5)
        self.m_statusMessages = Listbox(self.statusFrame)
        self.m_statusMessages.pack(side="left", fill=BOTH, expand=True)
        self.m_scrollB = Scrollbar(self.statusFrame, orient="vertical")
        self.m_scrollB.pack(side="right", fill=Y)
        self.m_statusMessages.config(yscrollcommand=self.m_scrollB.set)
        self.m_scrollB.config(command=self.m_statusMessages.yview)

        self.label1.grid(row=0, column=0, columnspan=2, sticky=W+E)
        self.label2.grid(row=1, column=0, sticky=W+E)
        self.dataDate.grid(row=1, column=1, sticky=W+E)
        self.label3.grid(row=2, column=0, sticky=W+E)
        self.tempData.grid(row=2, column=1, sticky=W+E)
        self.label4.grid(row=3, column=0, sticky=W+E)
        self.humData.grid(row=3, column=1, sticky=W+E)
        self.label5.grid(row=4, column=0, sticky=W+E)
        self.pressData.grid(row=4, column=1, sticky=W+E)

        Grid.columnconfigure(self.topFrame, 2, weight=1)  # to make the last column expand to resize
        self.statusFrame.grid(row=0, column=2, columnspan=2, rowspan=5, sticky=W+E)

        '''
        Lower frame (lowFrame) - Controller
        
        '''

        self.lowFrame = Frame(self.mainFrame, borderwidth=5)

        self.label7 = Label(self.lowFrame, text="Current state of Humifier")
        self.label8 = Label(self.lowFrame, text="Desired Humidity [%]:")
        self.label9 = Label(self.lowFrame, text="Max. runtime: [h]")
        self.label10 = Label(self.lowFrame, text="Min. stop time [h]:")
        self.label11 = Label(self.lowFrame, text="Manual start:")

        self.humConButton = Button(self.lowFrame, text="Idle", bg="red",
                                   fg="black", command=self.changeHumiState)
        self.desHumEntry = Entry(self.lowFrame, justify=RIGHT)
        self.maxRunTime = Entry(self.lowFrame, justify=RIGHT)
        self.minStopTime = Entry(self.lowFrame, justify=RIGHT)
        self.manHumStart = Button(self.lowFrame, text="Man Start", command=self.doManualStart)

        self.label7.grid(row=0, column=0, sticky=W+E)
        self.humConButton.grid(row=0, column=1, sticky=W+E)
        self.label8.grid(row=1, column=0, sticky=W+E)
        self.desHumEntry.grid(row=1, column=1, sticky=W+E)
        self.label9.grid(row=2, column=0, sticky=W+E)
        self.maxRunTime.grid(row=2, column=1, sticky=W+E)
        self.label10.grid(row=3, column=0, sticky=W+E)
        self.minStopTime.grid(row=3, column=1, sticky=W+E)
        self.label11.grid(row=4, column=0, sticky=W+E)
        self.manHumStart.grid(row=4, column=1, sticky=W+E)


        '''
        Footer layout (footer)
        '''
        # fill footer frame
        self.m_statusBar = Label(self.footer, text="Sleeping...", anchor=W, relief=SUNKEN)
        self.m_statusBar.pack(fill=X)

        self.m_mConButton = Button(self.footer, text="Wait for wake up", bg="orange",
                                   fg="black", command=self.changeHumiState)
        self.m_mConButton.pack(side="left", anchor=W)

        '''
        Global Layout
        '''

        self.topFrame.pack(fill=BOTH, expand=True)
        self.lowFrame.pack(fill=BOTH)
        # start GUI
        self.tk.protocol("WM_DELETE_WINDOW", self.onClose)
        # & start Queue check
        self.tk.after(100, self.processQueue)

        # start mainloop of GUI
        self.tk.mainloop()

    def changeHumiState(self):
        pass

    def doManualStart(self):
        pass

    def processQueue(self):

        pass

    def onClose(self):

        self.tk.quit()