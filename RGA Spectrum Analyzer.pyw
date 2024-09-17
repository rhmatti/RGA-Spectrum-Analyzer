#RGA Spectrum Analyzer
#Author: Richard Mattish
#Last Updated: 05/13/2024

#Function:  This program provides a graphical user interface for importing
#           and analyzing binary data files from the RGA to identify gases present in the
#           spectrum and determining total and partial pressure trends in the data


#Imports necessary packages
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
from tkinter import *
from scipy.signal import find_peaks
import os
import platform
import time
from tkinter import filedialog
from PIL import ImageTk, Image
import json
import struct
import webbrowser

#Defines location of the Desktop as well as font and text size for use in the software
desktop = os.path.expanduser("~\Desktop")
font1 = ('Helvetica', 16)
font2 = ('Helvetica', 14)
font3 = ('Helvetica', 18)
font4 = ('Helvetica', 12)
textSize = 20
colors = [[0.368417,0.506779,0.709798],[0.880722,0.611041,0.142051],[0.560181,0.691569,0.194885],\
          [0.922526,0.385626,0.209179],[0.528488,0.470624,0.701351],[0.772079,0.431554,0.102387],\
            [0.363898,0.618501,0.782349],[1,0.75,0],[0.647624,0.37816,0.614037]]

#Opens a url in a new tab in the default webbrowser
def callback(url):
    webbrowser.open_new_tab(url)

class RSA:
    def __init__(self):
        #Defines self.variables
        self.canvas = None
        self.fig = None
        self.ax = None
        self.line = None
        self.toolbar = None
        self.filename = None
        self.pressure_arr = None
        self.time_arr = None
        self.param_arr = None
        self.mass_arr = None
        self.scanCount = None
        self.minPressure = None
        self.graph = False
        self.graphType = 0
        self.error = None
        self.modes = []
        self.labels = []
        self.work_dir = None

        #Loads the variables V and minPressure from the variables file, and creates the file if none exists
        try:
            f = open('variables', 'r')
            variables = f.readlines()
            self.error = float(variables[0].split('=')[1])
            self.minPressure = float(variables[1].split('=')[1])
            self.work_dir = str(variables[2].split('=')[1])
        except:
            self.error = 0.2
            self.minPressure = 10**(-9)
            self.work_dir = desktop
            f = open("variables",'w')
            f.write('deltam='+str(self.error)+'\n'+'minPressure='+str(self.minPressure))
            f.write(f'work_dir={self.work_dir}')
            f.close()


    #Opens About Window with software information
    def About(self):
        name = "RGA Spectrum Analyzer"
        version = 'Version: 2.1.0'
        date = 'Date: 05/13/2024'
        support = 'Support: '
        url = 'https://github.com/rhmatti/RGA-Spectrum-Analyzer'
        copyrightMessage ='Copyright © 2024 Richard Mattish All Rights Reserved.'
        t = Toplevel(self.root)
        t.wm_title("About")
        t.geometry("400x300")
        t.resizable(False, False)
        t.configure(background='white')
        if platform.system() == 'Windows':
            t.iconbitmap("icons/RSA.ico")
        l1 = Label(t, text = name, bg='white', fg='blue', font=font2)
        l1.place(relx = 0.15, rely = 0.14, anchor = W)
        l2 = Label(t, text = version, bg='white', font=font4)
        l2.place(relx = 0.15, rely = 0.25, anchor = W)
        l3 = Label(t, text = date, bg='white', font=font4)
        l3.place(relx = 0.15, rely = 0.35, anchor = W)
        l4 = Label(t, text = support, bg = 'white', font=font4)
        l4.place(relx = 0.15, rely = 0.45, anchor = W)
        l5 = Label(t, text = 'https://github.com/rhmatti/\nRGA-Spectrum-Analyzer', bg = 'white', fg = 'blue', font=font4)
        l5.place(relx = 0.31, rely=0.48, anchor = W)
        l5.bind("<Button-1>", lambda e:
        callback(url))
        messageVar = Message(t, text = copyrightMessage, bg='white', font = font4, width = 600)
        messageVar.place(relx = 0.5, rely = 1, anchor = S)

    def Instructions(self):
        instructions = Toplevel(self.root)
        instructions.geometry('1280x720')
        instructions.wm_title("User Instructions")
        instructions.configure(bg='white')
        if platform.system() == 'Windows':
            instructions.iconbitmap("icons/RSA.ico")
        v = Scrollbar(instructions, orient = 'vertical')
        t = Text(instructions, font = font4, bg='white', width = 100, height = 100, wrap = NONE, yscrollcommand = v.set)
        t.insert(END, "*********************************************************************************************************************\n")
        t.insert(END, "Program: RGA Spectrum Analyzer\n")
        t.insert(END, "Author: Richard Mattish\n")
        t.insert(END, "Last Updated: 10/27/2021\n\n")
        t.insert(END, "Function:  This program provides a graphical user interface for quickly importing\n")
        t.insert(END, "\tRGA binary data files and identifying the presence/partial pressure of several of the most\n")
        t.insert(END, "\tcommon elements and gases.\n")
        t.insert(END, "*********************************************************************************************************************\n\n\n\n")
        t.insert(END, "User Instructions\n-------------------------\n")
        t.insert(END, "1. Open the file \"RGA Spectrum Analyzer.pyw\"\n\n")
        t.insert(END, "2. Select the \"Import\" option from the File menu (File>Import) or use the shortcut <Ctrl+I>\n\n")
        t.insert(END, "3. Using the navigation window, navigate to an output file generated from the SRS RGA software (ending in .ana) and import it\n\n")
        t.insert(END, "4. Automatic Analysis:\n")
        t.insert(END, "\ta) Select \"Auto-Anayze\" from the Analysis menu (Analysis>Auto-Analylze) or use the shortcut <Ctrl+R>\n")
        t.insert(END, "\tb) A separate window will open with the results of the analysis\n")
        t.insert(END, "\tc) The results will show the name of the gas, along with the partial pressure in Torr and % composition\n")
        t.insert(END, "\td) To save these results, click anywhere within the results window and use the <Ctrl+S> command\n")
        t.insert(END, "\te) The \"Auto-Anayze\" function searches for peak matches within a certain range of the expected mass (Δm)\n")
        t.insert(END, "\tand above a certain pressure threshold (P_min) which can be adjusted in the \"Settings\" (File>Settings)\n\n")
        t.insert(END, "5. Select a desired plot type from the \"Plot\" menu:\n")
        t.insert(END, "\ta) Single RGA Scan:\n")
        t.insert(END, "\t\t-Plots one RGA scan at a single instance in time from the binary data file\n")
        t.insert(END, "\t\t-Use the navigation controls to change which scan is plotted\n")
        t.insert(END, "\tb) All RGA Scans:\n")
        t.insert(END, "\t\t-Plots all of the RGA scans from the binary data file\n")
        t.insert(END, "\tc) Total Pressure Change:\n")
        t.insert(END, "\t\t-Plots the total pressure (sum of all partial pressures) as a function of time\n")
        t.insert(END, "\td) Partial Pressure Change:\n")
        t.insert(END, "\t\t-Plots the partial pressure of a specific gas that the user selects from the submenu\n")
        t.insert(END, "\t\t-The gases available for selection include: Methane, H2O, Ne, N2, NO, O2, Ar, and CO2\n\n")
        t.insert(END, "6. To save the graph on screen, use the save icon in the toolbar at the bottom of the screen,\n")
        t.insert(END, "\tselect \"Save\" from the drop-down File menu (File>Save), or use the shortcut <Ctrl+S>\n\n")


        t.pack(side=TOP, fill=X)
        v.config(command=t.yview)
    

    #Opens Settings Window, which allows the user to change the persistent self.variables V and R
    def Settings(self):
        t = Toplevel(self.root)
        t.geometry('400x300')
        t.wm_title("Settings")
        if platform.system() == 'Windows':
            t.iconbitmap("icons/settings.ico")
        L0 = Label(t, text = 'Settings', font = font3)
        L0.place(relx=0.5, rely=0.15, anchor = CENTER)
        L1 = Label(t, text = 'Δm:', font = font2)
        L1.place(relx=0.4, rely=0.3, anchor = E)
        E1 = Entry(t, font = font2, width = 10)
        E1.insert(0,str(self.error))
        E1.place(relx=0.4, rely=0.3, anchor = W)

        L2 = Label(t, text = 'P_min:', font = font2)
        L2.place(relx=0.4, rely=0.4, anchor = E)
        E2 = Entry(t, font = font2, width = 10)
        E2.insert(0,str(self.minPressure))
        E2.place(relx=0.4, rely=0.4, anchor = W)
        L3 = Label(t, text = 'Torr', font = font2)
        L3.place(relx=0.64, rely=0.4, anchor = W)
            
        b1 = Button(t, text = 'Update & Close', relief = 'raised', background='lightblue', activebackground='blue', font = font1, width = 15, height = 2,\
                    command = lambda: [self.updateSettings(float(E1.get()),float(E2.get())),t.destroy()])
        b1.place(relx=0.5, rely=0.6, anchor = CENTER)

        b2 = Button(t, text = 'Reset', relief = 'raised', background='pink', activebackground='red', font = font1, width = 10, height = 1, command = lambda: [self.updateSettings(0.2, 10**(-9)),t.destroy()])
        b2.place(relx=0.5, rely=0.9, anchor = CENTER)

    #Updates the persistent self.variables error and minPressure used for the Auto-Analyze option
    def updateSettings(self, E1, E2):
        self.error = E1
        self.minPressure = E2
        f = open("variables",'w')
        f.write(f'error={self.error}\nminPressure={self.minPressure}\nwork_dir={self.work_dir}')
        f.close()

        if self.graphType == 0:
            print('no graph needs changes')
        elif self.graphType == 1:
            self.totalPressureChange()
        elif self.graphType == 2:
            self.allPartialPressurePlot()
        elif self.graphType == 3:
            self.plotData(':')
        else:
            self.graphType = self.graphType.split(',')
            gas = self.graphType[0]
            mass = float(self.graphType[1])
            y_label = self.graphType[2]
            self.partialPressurePlot(gas, mass, y_label)
        
    
    #Used to import an RGA data file into the software
    def askopenfile(self):
        try:
            newfile = filedialog.askopenfilename(initialdir = self.work_dir,title = "Select file",filetypes = (("ANA files","*.ana*"),("ANA files","*.ana*")))
        except:
            newfile = filedialog.askopenfilename(initialdir = desktop,title = "Select file",filetypes = (("all files","*.*"),("all files","*.*")))

        if newfile == '':
            return
        self.filename = newfile
        folders = newfile.split('/')
        self.work_dir = ''
        for i in range(0,len(folders)-1):
            self.work_dir = f'{self.work_dir}{folders[i]}/'
        self.updateSettings(self.error, self.minPressure)
        self.getData()
        if self.graphType == 0:
            self.plotData(0)
        elif self.graphType == 1:
            self.totalPressureChange()
        elif self.graphType == 2:
            self.allPartialPressurePlot()
        elif self.graphType == 3:
            self.plotData(':')
        else:
            self.graphType = self.graphType.split(',')
            gas = self.graphType[0]
            mass = float(self.graphType[1])
            y_label = self.graphType[2]
            self.partialPressurePlot(gas, mass, y_label)

    #Lets user save a copy of the matplotlib graph displayed in the software
    def saveGraph(self):
        try:
            saveFile = str(filedialog.asksaveasfile(initialdir = self.work_dir,title = "Save file",filetypes = (("Portable Network Graphic","*.png"),("JPEG","*.jpeg")), defaultextension = (("Portable Network Graphic","*.png"),("JPEG","*.jpeg"))))
            print(saveFile)
            saveFile = saveFile.split("'")
            saveFile = saveFile[1]
            print(str(saveFile))
            plt.savefig(saveFile, bbox_inches='tight')
        except:
            pass

    #Opens a window with a periodic table for reference
    def PTable(self):
        ptable = Toplevel(self.root)
        ptable.geometry('1920x1080')
        ptable.configure(bg='white')
        if platform.system() == 'Windows':
            ptable.iconbitmap("icons/RSA.ico")
        ptable.wm_title('Periodic Table')
        load = Image.open('PeriodicTable.png')
        render = ImageTk.PhotoImage(load)
        img = Label(ptable, image=render)
        img.image = render
        img.pack(side="top",fill='both',expand=True)

    #Quits the program
    def quitProgram(self):
        print('quit')
        self.root.quit()
        self.root.destroy()

    def getData(self):
        with open(self.filename, mode='rb') as file:
            bin_data = file.read()
        #header_format = '52c'
        header_format = '15c15chhhh4c10c' #start, end, per amu, pps
        header_size = struct.calcsize(header_format)
        
        header = struct.unpack(header_format,bin_data[:header_size])
        
        start_amu = header[30]
        end_amu = header[31]
        ppamu = header[32] #points/amu
        pps = header[33] #points/scan
        
        self.param_arr = np.array((start_amu,end_amu,ppamu,pps))

        self.mass_arr = np.arange(self.param_arr[0], self.param_arr[1] + 1/self.param_arr[2], 1/self.param_arr[2])
        
        bin_data = bin_data[header_size:] #truncate header
        
        subheader_format = '50c'
        subheader_size = struct.calcsize(subheader_format)
        
        time_format = '25c'
        time_size = struct.calcsize(time_format)
        
        data_format = f'{pps}f'
        data_size = struct.calcsize(data_format)

        block_size = data_size + subheader_size
        blocks = len(bin_data)/block_size
        
        if not blocks.is_integer():
            print('Format Error')
            exit()
        else:
            blocks = int(blocks)

        self.pressure_arr = np.zeros((pps,blocks))
        self.time_arr = np.zeros(blocks)
        for i in range(blocks):
            t = struct.unpack(time_format, bin_data[:time_size])

            new_time = ''
            for character in t:
                new_time += character.decode('utf-8')
            str_time = time.strptime(new_time, '%b %d, %Y  %I:%M:%S %p')
            unix_time = time.mktime(str_time)
            
            self.time_arr[i] = unix_time
            bin_data = bin_data[subheader_size:] #truncate subheader
            
            data = struct.unpack(data_format,bin_data[:data_size])
            
            self.pressure_arr[:,i] = data
            bin_data = bin_data[data_size:] #truncate to next block

    #Creates a plot of the raw EBIT data for current vs. B-field
    def plotData(self, i):
        if i == ':':
            self.graphType = 3
        else:
            self.graphType = 0

        try:
            self.canvas.get_tk_widget().destroy()
        except:
            pass

        try:
            title = self.filename.split('/')
            # creating the Matplotlib figure
            plt.close('all')
            self.fig, self.ax = plt.subplots(figsize = (16,9))
            self.ax.tick_params(which='both', direction='in')
            plt.rcParams.update({'font.size': textSize})
            for label in (self.ax.get_xticklabels() + self.ax.get_yticklabels()):
                    label.set_fontsize(textSize)
            if i == ':':
                plt.plot(self.mass_arr, self.pressure_arr, linestyle = '-', linewidth = 2)
            else:
                plt.plot(self.mass_arr, self.pressure_arr[:,int(i)], linestyle = '-', linewidth = 2)
                self.scanCount = i
            plt.yscale('log')
            plt.xlim(0, self.param_arr[1] + 1/self.param_arr[2])
            plt.ylim(1e-10, 2*np.max(self.pressure_arr))
            plt.xlabel('Mass (amu)',fontsize=textSize)
            plt.ylabel('Pressure (Torr)',fontsize=textSize)
            plt.title(title[len(title)-1])

            # creating the Tkinter self.canvas
            # containing the Matplotlib figure
            self.canvas = FigureCanvasTkAgg(self.fig, master = self.root) 
            self.canvas.draw()
        
            
            if self.graph == True:
                self.toolbar.destroy()
                self.graph = False

            # creating the Matplotlib toolbar
            if self.graph == False:
                self.toolbar = NavigationToolbar2Tk(self.canvas, self.root, pack_toolbar=False)
                self.toolbar.update()
                self.toolbar.pack(side=BOTTOM, fill=X)
                self.graph = True
        
            # placing the self.canvas on the Tkinter window
            self.canvas.get_tk_widget().pack(side="top",fill='both',expand=True)

            # adding navigation controls to the Tkinter window to cycle through single scans
            if i != ':':
                navControls = Frame(self.root, width = 200, height = 75, background='white')
                navControls.place(relx=0.9, rely=0.05, anchor = CENTER)

                navTitle = Message(navControls, text = 'RGA Scan:', font = font4, width = 100)
                navTitle.config(bg='white', fg='black')
                navTitle.place(relx=0.5, rely = 0.15, anchor = CENTER)

                navCount = Message(navControls, text = '/' + str(len(self.pressure_arr[0,:])), font = font4, width = 700)
                navCount.config(bg='white', fg='black')
                navCount.place(relx = 0.5, rely = 0.5, anchor = W)

                scanNum = Entry(navControls, font = font4, width = 4)
                scanNum.insert(0,str(i+1))
                scanNum.bind('<Return>', lambda eff: self.plotData(int(scanNum.get())-1))
                scanNum.place(relx=0.5, rely=0.5, anchor = E)

                if i == 0:
                    firstButton = Button(navControls, text = '|ᐊ', background='lightgrey', relief='flat', font = font4)
                    firstButton.place(relw = 0.12, relh=0.3, relx=0.16, rely=0.5, anchor=E)

                    prevButton = Button(navControls, text = '≪', background='lightgrey', relief='flat', font = font4)
                    prevButton.place(relw = 0.12, relh = 0.3, relx=0.16, rely=0.5, anchor=W)
                else:
                    firstButton = Button(navControls, text = '|ᐊ', background='white', relief='flat', font = font4, command = lambda: self.plotData(0))
                    firstButton.place(relw = 0.12, relh=0.3, relx=0.16, rely=0.5, anchor=E)

                    prevButton = Button(navControls, text = '≪', background='white', relief='flat', font = font4, command = lambda: self.plotData(int(scanNum.get())-2))
                    prevButton.place(relw = 0.12, relh=0.3, relx=0.16, rely=0.5, anchor=W)

                if i == len(self.pressure_arr[0,:])-1:
                    nextButton = Button(navControls, text = '≫', background='lightgrey', relief='flat', font = font4)
                    nextButton.place(relw = 0.12, relh=0.3, relx=0.88, rely=0.5, anchor=E)

                    lastButton = Button(navControls, text = 'ᐅ|', background='lightgrey', relief='flat', font = font4)
                    lastButton.place(relw = 0.12, relh=0.3, relx=0.88, rely=0.5, anchor=W)
                else:
                    nextButton = Button(navControls, text = '≫', background='white', relief='flat', font = font4, command = lambda: self.plotData(int(scanNum.get())))
                    nextButton.place(relw = 0.12, relh=0.3, relx=0.88, rely=0.5, anchor=E)

                    lastButton = Button(navControls, text = 'ᐅ|', background='white', relief='flat', font = font4, command = lambda: self.plotData(len(self.pressure_arr[0,:])-1))
                    lastButton.place(relw = 0.12, relh=0.3, relx=0.88, rely=0.5, anchor=W)
        except NameError:
            helpMessage ='Please import a data file first.' 
            messageVar = Message(self.root, text = helpMessage, font = font2, width = 600) 
            messageVar.config(bg='lightgreen')
            messageVar.place(relx = 0, rely = 1, anchor = SW)


    #Creates a plot of total pressure vs. change in time
    def totalPressureChange(self):
        self.graphType = 1

        try:
            title = self.filename.split('/')
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            # creating the Matplotlib figure
            plt.close('all')
            self.fig, self.ax = plt.subplots(figsize = (16,9))
            self.ax.tick_params(which='both', direction='in')
            plt.rcParams.update({'font.size': textSize})
            for label in (self.ax.get_xticklabels() + self.ax.get_yticklabels()):
                label.set_fontsize(textSize)
            plt.plot((self.time_arr-self.time_arr[0])/60, np.sum(self.pressure_arr,axis=0), linestyle = '-', linewidth = 2)
            plt.xlim(0,np.max((self.time_arr-self.time_arr[0])/60))
            plt.yscale('log')
            plt.xlabel('Time (min)', fontsize=textSize)
            plt.ylabel('Pressure (Torr)',fontsize=textSize)
            plt.title(title[len(title)-1])

            # creating the Tkinter self.canvas containing the Matplotlib figure
            self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)
            self.canvas.draw()

            # creating the toolbar and placing it
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.root, pack_toolbar=False)
            self.toolbar.update()
            self.toolbar.pack(side=BOTTOM, fill=X)

            # placing the self.canvas on the Tkinter window
            self.canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
        
        except NameError:
            helpMessage ='Please import a data file first.' 
            messageVar = Message(self.root, text = helpMessage, font = font2, width = 600) 
            messageVar.config(bg='lightgreen')
            messageVar.place(relx = 0, rely = 1, anchor = SW)


    #Creates a plot of current vs. a given element's/gas's charge states for use in identifying if it is present in the ion beam
    def partialPressureChange(self, gas, mass, y_label):

        deltas = np.zeros(len(self.mass_arr))
        for i in range(0,len(self.mass_arr)):
            delta = abs(mass-self.mass_arr[i])
            deltas[i] = delta
        min_index = np.argmin(deltas)

        self.ax.plot((self.time_arr-self.time_arr[0])/60, self.pressure_arr[min_index,:], linestyle = '-', linewidth = 2, label = y_label)

    #Creates a plot of current vs. a given element's/gas's charge states for use in identifying if it is present in the ion beam
    def partialPressurePlot(self, gas, mass, y_label):
        self.graphType = gas + ',' + str(mass) + ',' + y_label

        deltas = np.zeros(len(self.mass_arr))
        for i in range(0,len(self.mass_arr)):
            delta = abs(mass-self.mass_arr[i])
            deltas[i] = delta
        min_index = np.argmin(deltas)
        print(min_index)
        print(self.pressure_arr[min_index])

        try:
            title = self.filename.split('/')
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            # creating the Matplotlib figure
            plt.close('all')
            self.fig, self.ax = plt.subplots(figsize = (16,9))
            self.ax.tick_params(which='both', direction='in')
            plt.rcParams.update({'font.size': textSize})
            for label in (self.ax.get_xticklabels() + self.ax.get_yticklabels()):
                label.set_fontsize(textSize)
            plt.plot((self.time_arr-self.time_arr[0])/60, self.pressure_arr[min_index,:], linestyle = '-', linewidth = 2)
            plt.xlim(0,np.max((self.time_arr-self.time_arr[0])/60))
            plt.yscale('log')
            plt.xlabel('Time (min)', fontsize=textSize)
            plt.ylabel(y_label + ' Pressure (Torr)',fontsize=textSize)
            plt.title(title[len(title)-1])

            # creating the Tkinter self.canvas containing the Matplotlib figure
            self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)
            self.canvas.draw()

            # creating the toolbar and placing it
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.root, pack_toolbar=False)
            self.toolbar.update()
            self.toolbar.pack(side=BOTTOM, fill=X)

            # placing the self.canvas on the Tkinter window
            self.canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
        
        except NameError:
            helpMessage ='Please import a data file first.' 
            messageVar = Message(self.root, text = helpMessage, font = font2, width = 600) 
            messageVar.config(bg='lightgreen')
            messageVar.place(relx = 0, rely = 1, anchor = SW)

    def allPartialPressurePlot(self):
        self.graphType = 2
        self.line = None

        try:
            title = self.filename.split('/')
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            # creating the Matplotlib figure
            plt.close('all')
            self.fig, self.ax = plt.subplots(figsize = (16,9))
            self.ax.tick_params(which='both', direction='in')
            plt.rcParams.update({'font.size': textSize})
            for label in (self.ax.get_xticklabels() + self.ax.get_yticklabels()):
                label.set_fontsize(textSize)

            #Graph partial pressure vs time of each gas
            self.partialPressureChange('H2O', 18, 'H$_2$O')
            self.partialPressureChange('Ne', 20, 'Ne')
            #partialPressureChange('Ne22', 22, 'Ne$^{22}$')
            #partialPressureChange('H', 1, 'H')
            self.partialPressureChange('H2', 2, 'H$_2$')
            self.partialPressureChange('N2', 28, 'N$_2$')
            self.partialPressureChange('O2', 32, 'O$_2$')
            self.partialPressureChange('CO2', 44, 'CO$_2$')
            self.partialPressureChange('Ar', 40, 'Ar')
            self.partialPressureChange('NO', 30, 'NO')

            self.ax.set_xlim(0,np.max((self.time_arr-self.time_arr[0])/60))
            plt.yscale('log')
            plt.xlabel('Time (min)', fontsize=textSize)
            plt.ylabel('Pressure (Torr)',fontsize=textSize)
            plt.legend()
            plt.title(title[len(title)-1])

            #Adds anotation to plot (used as interactive text box showing temperatures as location clicked)
            self.annot = self.ax.annotate('',xy=(0,0), fontsize=textSize-8, xytext=(20,20),textcoords='offset points',c='w',bbox=dict(boxstyle='round', fc='black'),arrowprops=dict(arrowstyle='->'))
            self.annot.set_visible(False)

            #Enalbes interactive left-click capability on plot
            self.fig.canvas.mpl_connect('button_press_event', self.onclick)
            

            # creating the Tkinter self.canvas containing the Matplotlib figure
            self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)
            self.canvas.draw()

            # creating the toolbar and placing it
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.root, pack_toolbar=False)
            self.toolbar.update()
            self.toolbar.pack(side=BOTTOM, fill=X)

            # placing the self.canvas on the Tkinter window
            self.canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
        
        except:
            helpMessage ='Please import a data file first.' 
            messageVar = Message(self.root, text = helpMessage, font = font2, width = 600) 
            messageVar.config(bg='lightgreen')
            messageVar.place(relx = 0, rely = 1, anchor = SW)

    #Enables left-click functionality on plot
    #Left-clicking on plot will display the temperature of both stages
    #as well as show a vertical line at the place clicked
    def onclick(self, event):
        global line

        x_click = event.xdata
        y_click = event.ydata
        button = str(event.button)
        print(button)

        #if button=='MouseButton.LEFT':
        if button=='1':
            lines = self.ax.lines
            labels = []
            pressures = []
            for line in lines:
                label = line.get_label()
                if '_child' not in label:
                    xdata = line.get_xdata()
                    ydata = line.get_ydata()
                    #Finds Pressure of each gas at that time
                    deltas = np.zeros(len(xdata))
                    for i in range(0,len(xdata)):
                        delta = abs(x_click-xdata[i])
                        deltas[i] = delta
                    index = np.argmin(deltas)
                    labels.append(label)
                    pressures.append(ydata[index])

        
        #Displays textbox and arrow showing partial pressures
        annot_text = ''
        for i in range(0,len(labels)):
            annot_text = f'{annot_text}\n{labels[i]} = {pressures[i]:.2e} Torr'
        self.annot.xy = (x_click,1.2*min(pressures))
        self.annot.set_text(annot_text)
        self.annot.get_bbox_patch().set_alpha(.7)
        self.annot.set_visible(True)

        #Places vertical line at x-coordinate
        if self.line is None:
            self.line = self.ax.axvline(x=x_click, color='black', ls='-', lw=1)
        else:
            self.line.set_xdata(x_click)
            
        self.fig.canvas.draw()


    #Analyzes spectrum and compares to all elements/molecules present in the json file
    def autoAnalyze(self):
        autoanalysis = Toplevel(self.root)
        autoanalysis.geometry('800x600')
        autoanalysis.wm_title("Results for Auto-Analysis")
        autoanalysis.configure(bg='white')
        if platform.system() == 'Windows':
            autoanalysis.iconbitmap("icons/RSA.ico")
        v = Scrollbar(autoanalysis, orient = 'vertical')
        t = Text(autoanalysis, font = font4, width = 100, height = 100, wrap = NONE, yscrollcommand = v.set)
        
        results = []
        with open('json_background.py') as f:
            J = json.load(f)
        for a in J['elements']:#finds element in json file and checks if the input is the same
            element=a['name']
            mass1=a['mass1']
            partialPressure = self.crossCheck(element, mass1, self.scanCount)
            if partialPressure != 0:
                results.append([element, partialPressure])
        for a in J['molecules']:#finds molecule in json file and checks if the input is the same
            molecule=a['name']
            mass1=a['mass1']
            partialPressure = self.crossCheck(molecule, mass1, self.scanCount)
            if partialPressure != 0:
                results.append([molecule, partialPressure])

        totalPressure = np.sum(self.pressure_arr[:,int(self.scanCount)],axis=0)
        print(str(totalPressure))
        t.insert(END, "Constituent Gases:\n-------------------------\n")
        for result in results:
            newLine = f'{result[0]}: \t{result[1]:.2e} Torr \t({result[1]/totalPressure*100:.2e}%)\n'
            t.insert(END, newLine)
                        
        t.pack(side=TOP, fill=X)
        v.config(command=t.yview)

        resultText = t.get("1.0","end-1c")
        autoanalysis.bind("<Control-s>", lambda eff: self.saveAutoAnalysisResults(resultText))

    #When called, this functions writes the results of the autoAnalyze function to a text file
    def saveAutoAnalysisResults(self, resultText):
        fileName = str(filedialog.asksaveasfile(initialdir = desktop,title = "Save",filetypes = (("Text Document","*.txt*"),("Text Document","*.txt*"))))
        fileName = fileName.split("'")
        fileName = fileName[1]
        outputFile = open(fileName + '.txt', "w")
        outputFile.write(resultText)
        outputFile.close()
        os.remove(fileName)

    #Checks to see if there are any peaks that match the given element/molecule's mass, and if so returns the partial pressure of that element/molecule
    def crossCheck(self, element, mass, i):
        self.mass_arr = np.arange(self.param_arr[0], self.param_arr[1] + 1/self.param_arr[2], 1/self.param_arr[2])

        peak_index, properties = find_peaks(self.pressure_arr[:,int(i)], height=self.minPressure)
        peak_mass = self.mass_arr[peak_index]
        peak_pressure = properties['peak_heights']
        peak_pressure2 = self.pressure_arr[peak_index,int(i)]

        
        
        for j in range(0, len(peak_mass)):
            if abs(peak_mass[j]-mass) < self.error:
                print(element + ': ' + str(mass))
                print(peak_mass[j])
                partialPressure = peak_pressure[j]
                print(partialPressure)
                return partialPressure
        
        return 0

    #This is the GUI for the software
    def makeGui(self, root=None):
        if root == None:
            self.root = Tk()
        else:
            self.root = root
            
        menu = Menu(self.root)
        self.root.config(menu=menu)

        self.root.title("RGA Spectrum Analyzer")
        self.root.geometry("1200x768")
        self.root.configure(bg='white')
        self.root.protocol("WM_DELETE_WINDOW", self.quitProgram)
        if platform.system() == 'Windows':
            self.root.iconbitmap("icons/RSA.ico")

        #Creates intro message
        introMessage ='Import a data file to begin'
        introMessageVar = Message(self.root, text = introMessage, font = font2, width = 600)
        introMessageVar.config(bg='white', fg='grey')
        introMessageVar.place(relx = 0.5, rely = 0.5, anchor = CENTER)
        introMessageVar.bind('<Button-1>', lambda  eff: self.askopenfile())

        #Creates File menu
        filemenu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Import", command=lambda: self.askopenfile(), accelerator="Ctrl+I")
        filemenu.add_command(label="Save", command=lambda: self.saveGraph(), accelerator="Ctrl+S")
        filemenu.add_command(label='Settings', command=lambda: self.Settings())
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=lambda: self.quitProgram())

        #Creates Plot menu
        plotmenu = Menu(menu, tearoff=0)
        ppmenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='Plot', menu=plotmenu)
        plotmenu.add_command(label='Single RGA Scan', command= lambda: self.plotData(0))
        plotmenu.add_command(label='All RGA Scans', command= lambda: self.plotData(':'))
        plotmenu.add_command(label='Total Pressure Change', command= lambda: self.totalPressureChange())
        plotmenu.add_cascade(label='Partial Pressure Change', menu=ppmenu)
        ppmenu.add_command(label='H2', command= lambda: self.partialPressurePlot('H2', 2, 'H$_2$'))
        ppmenu.add_command(label='Methane', command= lambda: self.partialPressurePlot('Methane', 16, 'Methane'))
        ppmenu.add_command(label='H2O', command= lambda: self.partialPressurePlot('H2O', 18, 'H$_2$O'))
        ppmenu.add_command(label='Ne', command= lambda: self.partialPressurePlot('Ne', 20, 'Ne'))
        ppmenu.add_command(label='N2', command= lambda: self.partialPressurePlot('N2', 28, 'N$_2$'))
        ppmenu.add_command(label='NO', command= lambda: self.partialPressurePlot('NO', 30, 'NO'))
        ppmenu.add_command(label='O2', command= lambda: self.partialPressurePlot('O2', 32, 'O$_2$'))
        ppmenu.add_command(label='Ar', command= lambda: self.partialPressurePlot('Ar', 40, 'Ar'))
        ppmenu.add_command(label='CO2', command= lambda: self.partialPressurePlot('CO2', 44, 'CO$_2$'))
        ppmenu.add_command(label='Show All', command= lambda: self.allPartialPressurePlot())


        #Creates Analysis menu
        analysismenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='Analysis', menu=analysismenu)
        analysismenu.add_command(label='Auto-Analyze', command= lambda: self.autoAnalyze(), accelerator="Ctrl+R")


        #Creates Help menu
        helpmenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='Help', menu=helpmenu)
        helpmenu.add_command(label='Instructions', command= lambda: self.Instructions())
        helpmenu.add_command(label='Periodic Table', command= lambda: self.PTable(), accelerator="Ctrl+P")
        helpmenu.add_command(label='About', command= lambda: self.About())

        #Binds keyboard shortcuts to functions
        self.root.bind_all("<Control-i>", lambda eff: self.askopenfile())
        self.root.bind("<Control-s>", lambda eff: self.saveGraph())
        self.root.bind_all("<Control-r>", lambda eff: self.autoAnalyze())
        self.root.bind_all("<Control-p>", lambda eff: self.PTable())


        self.root.mainloop()

if __name__ == "__main__":
    instance = RSA()
    instance.makeGui()

