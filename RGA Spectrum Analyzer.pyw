#RGA Spectrum Analyzer
#Author: Richard Mattish
#Last Updated: 05/09/2024

#Function:  This program provides a graphical user interface for importing
#           and analyzing binary data files from the RGA to identify gases present in the
#           spectrum and determining total and partial pressure trends in the data


#Imports necessary packages
from logging import root
import matplotlib
from scipy.signal.waveforms import square
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import style
from matplotlib.figure import Figure
import numpy as np
from tkinter import *
from tkinter import ttk
from scipy.signal import find_peaks
from scipy.stats import mode
import sys
import os
import platform
import time
import datetime
from decimal import Decimal
from tkinter import filedialog
from PIL import ImageTk, Image
import json
import struct
import webbrowser


#Defines global variables
global canvas
global fig
global ax
global toolbar
global filename
global pressure_arr
global time_arr
global param_arr
global mass_arr
global scanCount
global minPressure
global graph
global graphType
global calibrate
global error

modes = []
graphType = 0
labels = []

colors = [[0.368417,0.506779,0.709798],[0.880722,0.611041,0.142051],[0.560181,0.691569,0.194885],\
          [0.922526,0.385626,0.209179],[0.528488,0.470624,0.701351],[0.772079,0.431554,0.102387],\
            [0.363898,0.618501,0.782349],[1,0.75,0],[0.647624,0.37816,0.614037]]


#Defines location of the Desktop as well as font and text size for use in the software
desktop = os.path.expanduser("~\Desktop")
font1 = ('Helvetica', 16)
font2 = ('Helvetica', 14)
font3 = ('Helvetica', 18)
font4 = ('Helvetica', 12)
textSize = 20
graph = False

#Variable used to store last-accessed folder for file imports
work_dir = None

#Loads the variables V and minPressure from the variables file, and creates the file if none exists
try:
    f = open('variables', 'r')
    variables = f.readlines()
    error = float(variables[0].split('=')[1])
    minPressure = float(variables[1].split('=')[1])
    work_dir = str(variables[2].split('=')[1])
except:
    error = 0.2
    minPressure = 10**(-9)
    work_dir = desktop
    f = open("variables",'w')
    f.write('deltam='+str(error)+'\n'+'minPressure='+str(minPressure))
    f.write(f'work_dir={work_dir}')
    f.close()

#Opens a url in a new tab in the default webbrowser
def callback(url):
    webbrowser.open_new_tab(url)


#Opens About Window with software information
def About():
    name = "RGA Spectrum Analyzer"
    version = 'Version: 1.0.0'
    date = 'Date: 05/09/2024'
    support = 'Support: '
    url = 'https://github.com/rhmatti/RGA-Spectrum-Analyzer'
    copyrightMessage ='Copyright © 2024 Richard Mattish All Rights Reserved.'
    t = Toplevel(root)
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

def Instructions():
    instructions = Toplevel(root)
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
    

#Opens Settings Window, which allows the user to change the persistent global variables V and R
def Settings():
    global error
    global minPressure
    t = Toplevel(root)
    t.geometry('400x300')
    t.wm_title("Settings")
    if platform.system() == 'Windows':
        t.iconbitmap("icons/settings.ico")
    L0 = Label(t, text = 'Settings', font = font3)
    L0.place(relx=0.5, rely=0.15, anchor = CENTER)
    L1 = Label(t, text = 'Δm:', font = font2)
    L1.place(relx=0.4, rely=0.3, anchor = E)
    E1 = Entry(t, font = font2, width = 10)
    E1.insert(0,str(error))
    E1.place(relx=0.4, rely=0.3, anchor = W)

    L2 = Label(t, text = 'P_min:', font = font2)
    L2.place(relx=0.4, rely=0.4, anchor = E)
    E2 = Entry(t, font = font2, width = 10)
    E2.insert(0,str(minPressure))
    E2.place(relx=0.4, rely=0.4, anchor = W)
    L3 = Label(t, text = 'Torr', font = font2)
    L3.place(relx=0.64, rely=0.4, anchor = W)
        
    b1 = Button(t, text = 'Update & Close', relief = 'raised', background='lightblue', activebackground='blue', font = font1, width = 15, height = 2,\
                command = lambda: [updateSettings(float(E1.get()),float(E2.get())),t.destroy()])
    b1.place(relx=0.5, rely=0.6, anchor = CENTER)

    b2 = Button(t, text = 'Reset', relief = 'raised', background='pink', activebackground='red', font = font1, width = 10, height = 1, command = lambda: [updateSettings(0.2, 10**(-9)),t.destroy()])
    b2.place(relx=0.5, rely=0.9, anchor = CENTER)

#Updates the persistent global variables error and minPressure used for the Auto-Analyze option
def updateSettings(E1, E2):
    global error
    global minPressure
    global graphType
    global calibrate
    global work_dir
    error = E1
    minPressure = E2
    f = open("variables",'w')
    f.write(f'error={error}\nminPressure={minPressure}\nwork_dir={work_dir}')
    f.close()

    if graphType == 0:
        print('no graph needs changes')
    elif graphType == 1:
        totalPressureChange()
    elif graphType == 2:
        allPartialPressurePlot()
    elif graphType == 3:
        plotData(':')
    else:
        graphType = graphType.split(',')
        gas = graphType[0]
        mass = float(graphType[1])
        y_label = graphType[2]
        partialPressurePlot(gas, mass, y_label)
        
    
#Used to import an RGA data file into the software
def askopenfile():
    global filename
    global scanNum
    global work_dir
    global error
    global minPressure
    global graphType
    try:
        newfile = filedialog.askopenfilename(initialdir = work_dir,title = "Select file",filetypes = (("ANA files","*.ana*"),("ANA files","*.ana*")))
    except:
        newfile = filedialog.askopenfilename(initialdir = desktop,title = "Select file",filetypes = (("all files","*.*"),("all files","*.*")))

    if newfile == '':
        return
    filename = newfile
    folders = newfile.split('/')
    work_dir = ''
    for i in range(0,len(folders)-1):
        work_dir = f'{work_dir}{folders[i]}/'
    updateSettings(error, minPressure)
    getData()
    if graphType == 0:
        plotData(0)
    elif graphType == 1:
        totalPressureChange()
    elif graphType == 2:
        allPartialPressurePlot()
    elif graphType == 3:
        plotData(':')
    else:
        graphType = graphType.split(',')
        gas = graphType[0]
        mass = float(graphType[1])
        y_label = graphType[2]
        partialPressurePlot(gas, mass, y_label)

#Lets user save a copy of the matplotlib graph displayed in the software
def saveGraph():
    try:
        saveFile = str(filedialog.asksaveasfile(initialdir = work_dir,title = "Save file",filetypes = (("Portable Network Graphic","*.png"),("JPEG","*.jpeg")), defaultextension = (("Portable Network Graphic","*.png"),("JPEG","*.jpeg"))))
        print(saveFile)
        saveFile = saveFile.split("'")
        saveFile = saveFile[1]
        print(str(saveFile))
        plt.savefig(saveFile, bbox_inches='tight')
    except:
        pass

#Opens a window with a periodic table for reference
def PTable():
    ptable = Toplevel(root)
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

def quitProgram():
    print('quit')
    root.quit()
    root.destroy()

def getData():
    global filename
    global pressure_arr
    global time_arr
    global param_arr
    global mass_arr

    with open(filename, mode='rb') as file:
        bin_data = file.read()
    #header_format = '52c'
    header_format = '15c15chhhh4c10c' #start, end, per amu, pps
    header_size = struct.calcsize(header_format)
    
    header = struct.unpack(header_format,bin_data[:header_size])
    
    start_amu = header[30]
    end_amu = header[31]
    ppamu = header[32] #points/amu
    pps = header[33] #points/scan
    
    param_arr = np.array((start_amu,end_amu,ppamu,pps))

    mass_arr = np.arange(param_arr[0], param_arr[1] + 1/param_arr[2], 1/param_arr[2])
    
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

    pressure_arr = np.zeros((pps,blocks))
    time_arr = np.zeros(blocks)
    for i in range(blocks):
        t = struct.unpack(time_format, bin_data[:time_size])

        new_time = ''
        for character in t:
            new_time += character.decode('utf-8')
        str_time = time.strptime(new_time, '%b %d, %Y  %I:%M:%S %p')
        unix_time = time.mktime(str_time)
        
        time_arr[i] = unix_time
        bin_data = bin_data[subheader_size:] #truncate subheader
        
        data = struct.unpack(data_format,bin_data[:data_size])
        
        pressure_arr[:,i] = data
        bin_data = bin_data[data_size:] #truncate to next block

#Creates a plot of the raw EBIT data for current vs. B-field
def plotData(i):
    global pressure_arr
    global time_arr
    global mass_arr
    global param_arr
    global canvas
    global toolbar
    global plt
    global graph
    global filename
    global scanCount
    global graphType

    if i == ':':
        graphType = 3
    else:
        graphType = 0

    try:
        canvas.get_tk_widget().destroy()
    except:
        pass

    try:
        title = filename.split('/')
        # creating the Matplotlib figure
        plt.close('all')
        fig, ax = plt.subplots(figsize = (16,9))
        ax.tick_params(which='both', direction='in')
        plt.rcParams.update({'font.size': textSize})
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
                label.set_fontsize(textSize)
        if i == ':':
            plt.plot(mass_arr, pressure_arr, linestyle = '-', linewidth = 2)
        else:
            plt.plot(mass_arr, pressure_arr[:,int(i)], linestyle = '-', linewidth = 2)
            scanCount = i
        plt.yscale('log')
        plt.xlim(0, param_arr[1] + 1/param_arr[2])
        plt.ylim(1e-10, 2*np.max(pressure_arr))
        plt.xlabel('Mass (amu)',fontsize=textSize)
        plt.ylabel('Pressure (Torr)',fontsize=textSize)
        plt.title(title[len(title)-1])

        # creating the Tkinter canvas
        # containing the Matplotlib figure
        canvas = FigureCanvasTkAgg(fig, master = root)  
        canvas.draw()
    
        
        if graph == True:
            toolbar.destroy()
            graph = False

        # creating the Matplotlib toolbar
        if graph == False:
            toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(side=BOTTOM, fill=X)
            graph = True
    
        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().pack(side="top",fill='both',expand=True)

        # adding navigation controls to the Tkinter window to cycle through single scans
        if i != ':':
            navControls = Frame(root, width = 200, height = 75, background='white')
            navControls.place(relx=0.9, rely=0.05, anchor = CENTER)

            navTitle = Message(navControls, text = 'RGA Scan:', font = font4, width = 100)
            navTitle.config(bg='white', fg='black')
            navTitle.place(relx=0.5, rely = 0.15, anchor = CENTER)

            navCount = Message(navControls, text = '/' + str(len(pressure_arr[0,:])), font = font4, width = 700)
            navCount.config(bg='white', fg='black')
            navCount.place(relx = 0.5, rely = 0.5, anchor = W)

            scanNum = Entry(navControls, font = font4, width = 4)
            scanNum.insert(0,str(i+1))
            scanNum.bind('<Return>', lambda eff: plotData(int(scanNum.get())-1))
            scanNum.place(relx=0.5, rely=0.5, anchor = E)

            if i == 0:
                firstButton = Button(navControls, text = '|ᐊ', background='lightgrey', relief='flat', font = font4)
                firstButton.place(relw = 0.12, relh=0.3, relx=0.16, rely=0.5, anchor=E)

                prevButton = Button(navControls, text = '≪', background='lightgrey', relief='flat', font = font4)
                prevButton.place(relw = 0.12, relh = 0.3, relx=0.16, rely=0.5, anchor=W)
            else:
                firstButton = Button(navControls, text = '|ᐊ', background='white', relief='flat', font = font4, command = lambda: plotData(0))
                firstButton.place(relw = 0.12, relh=0.3, relx=0.16, rely=0.5, anchor=E)

                prevButton = Button(navControls, text = '≪', background='white', relief='flat', font = font4, command = lambda: plotData(int(scanNum.get())-2))
                prevButton.place(relw = 0.12, relh=0.3, relx=0.16, rely=0.5, anchor=W)

            if i == len(pressure_arr[0,:])-1:
                nextButton = Button(navControls, text = '≫', background='lightgrey', relief='flat', font = font4)
                nextButton.place(relw = 0.12, relh=0.3, relx=0.88, rely=0.5, anchor=E)

                lastButton = Button(navControls, text = 'ᐅ|', background='lightgrey', relief='flat', font = font4)
                lastButton.place(relw = 0.12, relh=0.3, relx=0.88, rely=0.5, anchor=W)
            else:
                nextButton = Button(navControls, text = '≫', background='white', relief='flat', font = font4, command = lambda: plotData(int(scanNum.get())))
                nextButton.place(relw = 0.12, relh=0.3, relx=0.88, rely=0.5, anchor=E)

                lastButton = Button(navControls, text = 'ᐅ|', background='white', relief='flat', font = font4, command = lambda: plotData(len(pressure_arr[0,:])-1))
                lastButton.place(relw = 0.12, relh=0.3, relx=0.88, rely=0.5, anchor=W)
    except NameError:
        helpMessage ='Please import a data file first.' 
        messageVar = Message(root, text = helpMessage, font = font2, width = 600) 
        messageVar.config(bg='lightgreen')
        messageVar.place(relx = 0, rely = 1, anchor = SW)


#Creates a plot of total pressure vs. change in time
def totalPressureChange():
    global pressure_arr
    global time_arr

    global canvas
    global toolbar
    global filename
    global graphType

    graphType = 1


    try:
       title = filename.split('/')
       canvas.get_tk_widget().destroy()
       toolbar.destroy()
       # creating the Matplotlib figure
       plt.close('all')
       fig, ax = plt.subplots(figsize = (16,9))
       ax.tick_params(which='both', direction='in')
       plt.rcParams.update({'font.size': textSize})
       for label in (ax.get_xticklabels() + ax.get_yticklabels()):
           label.set_fontsize(textSize)
       plt.plot((time_arr-time_arr[0])/60, np.sum(pressure_arr,axis=0), linestyle = '-', linewidth = 2)
       plt.xlim(0,np.max((time_arr-time_arr[0])/60))
       plt.yscale('log')
       plt.xlabel('Time (min)', fontsize=textSize)
       plt.ylabel('Pressure (Torr)',fontsize=textSize)
       plt.title(title[len(title)-1])

       # creating the Tkinter canvas containing the Matplotlib figure
       canvas = FigureCanvasTkAgg(fig, master = root)
       canvas.draw()

       # creating the toolbar and placing it
       toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
       toolbar.update()
       toolbar.pack(side=BOTTOM, fill=X)

       # placing the canvas on the Tkinter window
       canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
       
    except NameError:
        helpMessage ='Please import a data file first.' 
        messageVar = Message(root, text = helpMessage, font = font2, width = 600) 
        messageVar.config(bg='lightgreen')
        messageVar.place(relx = 0, rely = 1, anchor = SW)


#Creates a plot of current vs. a given element's/gas's charge states for use in identifying if it is present in the ion beam
def partialPressureChange(gas, mass, y_label):
    global pressure_arr
    global mass_arr
    global ax

    deltas = np.zeros(len(mass_arr))
    for i in range(0,len(mass_arr)):
        delta = abs(mass-mass_arr[i])
        deltas[i] = delta
    min_index = np.argmin(deltas)

    ax.plot((time_arr-time_arr[0])/60, pressure_arr[min_index,:], linestyle = '-', linewidth = 2, label = y_label)

#Creates a plot of current vs. a given element's/gas's charge states for use in identifying if it is present in the ion beam
def partialPressurePlot(gas, mass, y_label):
    global canvas
    global fig
    global ax
    global toolbar
    global filename
    global graphType
    global pressure_arr
    global mass_arr

    graphType = gas + ',' + str(mass) + ',' + y_label

    deltas = np.zeros(len(mass_arr))
    for i in range(0,len(mass_arr)):
        delta = abs(mass-mass_arr[i])
        deltas[i] = delta
    min_index = np.argmin(deltas)
    print(min_index)
    print(pressure_arr[min_index])

    #plt.plot(np.arange(param_arr[0], param_arr[1] + 1/param_arr[2], 1/param_arr[2]), pressure_arr[:,int(i)], linestyle = '-', linewidth = 2)

    try:
       title = filename.split('/')
       canvas.get_tk_widget().destroy()
       toolbar.destroy()
       # creating the Matplotlib figure
       plt.close('all')
       fig, ax = plt.subplots(figsize = (16,9))
       ax.tick_params(which='both', direction='in')
       plt.rcParams.update({'font.size': textSize})
       for label in (ax.get_xticklabels() + ax.get_yticklabels()):
           label.set_fontsize(textSize)
       plt.plot((time_arr-time_arr[0])/60, pressure_arr[min_index,:], linestyle = '-', linewidth = 2)
       plt.xlim(0,np.max((time_arr-time_arr[0])/60))
       plt.yscale('log')
       plt.xlabel('Time (min)', fontsize=textSize)
       plt.ylabel(y_label + ' Pressure (Torr)',fontsize=textSize)
       plt.title(title[len(title)-1])

       # creating the Tkinter canvas containing the Matplotlib figure
       canvas = FigureCanvasTkAgg(fig, master = root)
       canvas.draw()

       # creating the toolbar and placing it
       toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
       toolbar.update()
       toolbar.pack(side=BOTTOM, fill=X)

       # placing the canvas on the Tkinter window
       canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
       
    except NameError:
        helpMessage ='Please import a data file first.' 
        messageVar = Message(root, text = helpMessage, font = font2, width = 600) 
        messageVar.config(bg='lightgreen')
        messageVar.place(relx = 0, rely = 1, anchor = SW)

def allPartialPressurePlot():
    global canvas
    global fig
    global ax
    global toolbar
    global filename
    global graphType
    global pressure_arr
    global mass_arr

    graphType = 2

    try:
        title = filename.split('/')
        canvas.get_tk_widget().destroy()
        toolbar.destroy()
        # creating the Matplotlib figure
        plt.close('all')
        fig, ax = plt.subplots(figsize = (16,9))
        ax.tick_params(which='both', direction='in')
        plt.rcParams.update({'font.size': textSize})
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontsize(textSize)

        #Graph partial pressure vs time of each gas
        partialPressureChange('H2O', 18, 'H$_2$O')
        partialPressureChange('Ne', 20, 'Ne')
        #partialPressureChange('Ne22', 22, 'Ne$^{22}$')
        #partialPressureChange('H', 1, 'H')
        partialPressureChange('H2', 2, 'H$_2$')
        partialPressureChange('N2', 28, 'N$_2$')
        partialPressureChange('O2', 32, 'O$_2$')
        partialPressureChange('CO2', 44, 'CO$_2$')
        partialPressureChange('Ar', 40, 'Ar')
        partialPressureChange('NO', 30, 'NO')

        ax.set_xlim(0,np.max((time_arr-time_arr[0])/60))
        plt.yscale('log')
        plt.xlabel('Time (min)', fontsize=textSize)
        plt.ylabel('Pressure (Torr)',fontsize=textSize)
        plt.legend()
        plt.title(title[len(title)-1])
        

        # creating the Tkinter canvas containing the Matplotlib figure
        canvas = FigureCanvasTkAgg(fig, master = root)
        canvas.draw()

        # creating the toolbar and placing it
        toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=BOTTOM, fill=X)

        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
    
    except:
        helpMessage ='Please import a data file first.' 
        messageVar = Message(root, text = helpMessage, font = font2, width = 600) 
        messageVar.config(bg='lightgreen')
        messageVar.place(relx = 0, rely = 1, anchor = SW)


#Analyzes spectrum and compares to all elements/molecules present in the json file
def autoAnalyze():
    global scanCount
    autoanalysis = Toplevel(root)
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
        partialPressure = crossCheck(element, mass1, scanCount)
        if partialPressure != 0:
            results.append([element, partialPressure])
    for a in J['molecules']:#finds molecule in json file and checks if the input is the same
        molecule=a['name']
        mass1=a['mass1']
        partialPressure = crossCheck(molecule, mass1, scanCount)
        if partialPressure != 0:
            results.append([molecule, partialPressure])

    totalPressure = np.sum(pressure_arr[:,int(scanCount)],axis=0)
    print(str(totalPressure))
    t.insert(END, "Constituent Gases:\n-------------------------\n")
    for result in results:
        newLine = f'{result[0]}: \t{result[1]:.2e} Torr \t({result[1]/totalPressure*100:.2e}%)\n'
        t.insert(END, newLine)
                    
    t.pack(side=TOP, fill=X)
    v.config(command=t.yview)

    resultText = t.get("1.0","end-1c")
    autoanalysis.bind("<Control-s>", lambda eff: saveAutoAnalysisResults(resultText))

#When called, this functions writes the results of the autoAnalyze function to a text file
def saveAutoAnalysisResults(resultText):
    fileName = str(filedialog.asksaveasfile(initialdir = desktop,title = "Save",filetypes = (("Text Document","*.txt*"),("Text Document","*.txt*"))))
    fileName = fileName.split("'")
    fileName = fileName[1]
    outputFile = open(fileName + '.txt', "w")
    outputFile.write(resultText)
    outputFile.close()
    os.remove(fileName)

#Checks to see if there are any peaks that match the given element/molecule's mass, and if so returns the partial pressure of that element/molecule
def crossCheck(element, mass, i):
    global pressure_arr
    global param_arr
    global minPressure
    global error

    mass_arr = np.arange(param_arr[0], param_arr[1] + 1/param_arr[2], 1/param_arr[2])

    peak_index, properties = find_peaks(pressure_arr[:,int(i)], height=minPressure)
    peak_mass = mass_arr[peak_index]
    peak_pressure = properties['peak_heights']
    peak_pressure2 = pressure_arr[peak_index,int(i)]

    
    
    for j in range(0, len(peak_mass)):
        if abs(peak_mass[j]-mass) < error:
            print(element + ': ' + str(mass))
            print(peak_mass[j])
            partialPressure = peak_pressure[j]
            print(partialPressure)
            return partialPressure
    
    return 0





#This is the GUI for the software
root = Tk()
menu = Menu(root)
root.config(menu=menu)

root.title("RGA Spectrum Analyzer")
root.geometry("1200x768")
root.configure(bg='white')
root.protocol("WM_DELETE_WINDOW", quitProgram)
if platform.system() == 'Windows':
    root.iconbitmap("icons/RSA.ico")

#Creates intro message
introMessage ='Import a data file to begin'
introMessageVar = Message(root, text = introMessage, font = font2, width = 600)
introMessageVar.config(bg='white', fg='grey')
introMessageVar.place(relx = 0.5, rely = 0.5, anchor = CENTER)
introMessageVar.bind('<Button-1>', lambda  eff: askopenfile())

#Creates File menu
filemenu = Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Import", command=lambda: askopenfile(), accelerator="Ctrl+I")
filemenu.add_command(label="Save", command=lambda: saveGraph(), accelerator="Ctrl+S")
filemenu.add_command(label='Settings', command=lambda: Settings())
filemenu.add_separator()
filemenu.add_command(label='Exit', command=lambda: quitProgram())

#Creates Plot menu
plotmenu = Menu(menu, tearoff=0)
ppmenu = Menu(menu, tearoff=0)
menu.add_cascade(label='Plot', menu=plotmenu)
plotmenu.add_command(label='Single RGA Scan', command= lambda: plotData(0))
plotmenu.add_command(label='All RGA Scans', command= lambda: plotData(':'))
plotmenu.add_command(label='Total Pressure Change', command= lambda: totalPressureChange())
plotmenu.add_cascade(label='Partial Pressure Change', menu=ppmenu)
ppmenu.add_command(label='Methane', command= lambda: partialPressurePlot('Methane', 16, 'Methane'))
ppmenu.add_command(label='H2O', command= lambda: partialPressurePlot('H2O', 18, 'H$_2$O'))
ppmenu.add_command(label='Ne', command= lambda: partialPressurePlot('Ne', 20, 'Ne'))
ppmenu.add_command(label='N2', command= lambda: partialPressurePlot('N2', 28, 'N$_2$'))
ppmenu.add_command(label='NO', command= lambda: partialPressurePlot('NO', 30, 'NO'))
ppmenu.add_command(label='O2', command= lambda: partialPressurePlot('O2', 32, 'O$_2$'))
ppmenu.add_command(label='Ar', command= lambda: partialPressurePlot('Ar', 40, 'Ar'))
ppmenu.add_command(label='CO2', command= lambda: partialPressurePlot('CO2', 44, 'CO$_2$'))
ppmenu.add_command(label='Show All', command= lambda: allPartialPressurePlot())


#Creates Analysis menu
analysismenu = Menu(menu, tearoff=0)
menu.add_cascade(label='Analysis', menu=analysismenu)
analysismenu.add_command(label='Auto-Analyze', command= lambda: autoAnalyze(), accelerator="Ctrl+R")


#Creates Help menu
helpmenu = Menu(menu, tearoff=0)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='Instructions', command= lambda: Instructions())
helpmenu.add_command(label='Periodic Table', command= lambda: PTable(), accelerator="Ctrl+P")
helpmenu.add_command(label='About', command= lambda: About())

#Binds keyboard shortcuts to functions
root.bind_all("<Control-i>", lambda eff: askopenfile())
root.bind("<Control-s>", lambda eff: saveGraph())
root.bind_all("<Control-r>", lambda eff: autoAnalyze())
root.bind_all("<Control-p>", lambda eff: PTable())


root.mainloop()

