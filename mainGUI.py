from config import Config
import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog
import numpy as np
import os
import json
import codecs
import unit.files as f
import unit.calculateTools as ct

import hashlib

############################################################
##                          GUI                           ##
############################################################

class GUI():
    def __init__(self, parameters):
        self.parameters = parameters
        self.isDemo = True
        self.carNumberSelected = 0
        self.initGUI()

    def initGUI(self):
        # main Frame
        self.controlPanel = tk.Tk()
        self.controlPanel.title('Labeling')

        # CV0 File Module
        cv_file = tk.Canvas(self.controlPanel)

        # F0-0 File
        frameOpenFile = tk.Frame(cv_file,relief=tk.RAISED)
        frameOpenFile.grid(row=0, column=0,sticky=tk.EW)
        tk.Label(frameOpenFile, text='ファイル', height=2, anchor=tk.SW).grid(row=0, columnspan=2, sticky=tk.W)
        # [button] Open file
        tk.Button(frameOpenFile, text='開く', command=self.BTN_openfile, width=10).grid(row=1, column=0,sticky=tk.EW)
        # [label] path
        self.filepath = tk.StringVar()
        self.filepath.set('左のボータンを押してファイル選択してください')
        self.label_filepath = tk.Label(frameOpenFile, textvariable=self.filepath, anchor='w', justify='left', wraplength=220, width=32)
        self.label_filepath.grid(row=1, column=1)

        # F1 Filename Listbox
        frameFilenameList = tk.Frame(cv_file,relief=tk.RAISED)
        frameFilenameList.grid(row=1, column=0,sticky=tk.EW)
        # Scrollbar
        slb_filenameList = tk.Scrollbar(frameFilenameList)
        slb_filenameList.pack(side=tk.RIGHT, fill=tk.Y)
        # [list] filenames
        self.filenameList = tk.Listbox(frameFilenameList, yscrollcommand=slb_filenameList.set, width=42, exportselection=False)
        self.filenameList.bind('<<ListboxSelect>>', self.filenameOnSelected)
        self.filenameList.pack()
        slb_filenameList.config(command=self.filenameList.yview)

        # CV1 File Module
        cv_labeling = tk.Canvas(self.controlPanel)
        tk.Label(cv_labeling, text='Cars & Areas', height=2, anchor=tk.SW).grid(row=0, columnspan=2, sticky=tk.W)
        # F2 carNumber Label and button
        frameCarNumber = tk.Frame(cv_labeling,relief=tk.RAISED)
        frameCarNumber.grid(row=1, column=0,sticky=tk.NW)
        tk.Label(frameCarNumber, text='Car NO.', height=2, anchor=tk.SW).grid(row=0, column=0, sticky=tk.W)
        tk.Button(frameCarNumber,text='+', width=4,command=self.BTN_carNumPlus).grid(row=0, column=1,sticky=tk.EW)
        tk.Button(frameCarNumber,text='-', width=4,command=self.BTN_carNumminus).grid(row=0, column=2,sticky=tk.EW)

        # F3 areaNumber Label and button
        frameAreaInfoLabel = tk.Frame(cv_labeling,relief=tk.RAISED)
        frameAreaInfoLabel.grid(row=1, column=1,sticky=tk.NW)
        tk.Label(frameAreaInfoLabel, text='Area Information', height=2, anchor=tk.SW).grid(row=0, column=0, sticky=tk.W)

        # F4 carNumber Listbox
        frameCarNumberList = tk.Frame(cv_labeling,relief=tk.RAISED)
        frameCarNumberList.grid(row=2, column=0,sticky=tk.EW)
        # Scrollbar
        slb_carNumList = tk.Scrollbar(frameCarNumberList)
        slb_carNumList.pack(side=tk.RIGHT, fill=tk.Y)
        # [list] carNumber
        self.carNumberList = tk.Listbox(frameCarNumberList, yscrollcommand=slb_carNumList.set, width=20, exportselection=False)
        self.carNumberList.bind('<<ListboxSelect>>', self.List_carNumberOnSelected)
        self.carNumberList.pack()
        slb_carNumList.config(command=self.carNumberList.yview)

        # F5 areaNumber Label and button
        frameAreaInfo = tk.Frame(cv_labeling,relief=tk.RAISED)
        frameAreaInfo.grid(row=2, column=1,sticky=tk.NW)
        # area Info Label
        tk.Label(frameAreaInfo, text='車両：', height=2, anchor=tk.SW).grid(row=0, column=0, sticky=tk.W)
        self.carNameStr = tk.StringVar()
        tk.Label(frameAreaInfo, textvariable=self.carNameStr, height=2, anchor=tk.SW).grid(row=0, column=1, sticky=tk.W)
        tk.Label(frameAreaInfo, text='面積：', height=2, anchor=tk.SW).grid(row=1, column=0, sticky=tk.W)
        self.areaStr = tk.StringVar()
        tk.Label(frameAreaInfo, textvariable=self.areaStr, height=2, anchor=tk.SW).grid(row=1, column=1, sticky=tk.W)

        # Canvas pack
        cv_file.pack()
        cv_labeling.pack()

        # init data
        self.initParameters()
        self.initPos()

        # Value update
        self.controlPanel.after(Config.GUI_REFRESH_RATE, self.mainUpdate)
        self.controlPanel.mainloop()

    def mainUpdate(self):
        self.getNewParameters()
        # update areaSize
        self.areaStr.set(str(self.areaSize))
        self.controlPanel.after(Config.GUI_REFRESH_RATE, self.mainUpdate)

    def setDisplayImage(self, newSelected=-1):
        if self.filenameList.curselection() != ():
            selected = newSelected if newSelected!=-1 else self.filenameList.curselection()[0]
            path = os.path.join(self.filepath.get(), self.filenames[selected])
            path = bytes(path, encoding='utf8')
            self.parameters['filePath'].value = path
            self.parameters['fileNum'].value = selected
            self.setNewPos()

    def setSelectedCar(self):
        if self.carNumberList.curselection() != ():
            selected = self.carNumberList.curselection()[0]
            self.carNameStr.set('Car No.%d'%selected)
            if self.isDemo:
                self.initAndSetNewPos()
            else:
                self.setNewPos()

    # find pos info in log
    def setNewPos(self):
        _fileNum = self.filenameList.curselection()[0]
        _carNum = self.carNumberList.curselection()[0]

        print(_fileNum)
        print(self.log.__contains__(_fileNum))

        # get pos from log
        if self.log.__contains__(_fileNum):
            # get car Number (keys) of Image
            NumOfKeys = len(self.log.keys())
            print(NumOfKeys)
            while NumOfKeys > self.carNumberList.size():
                self.BTN_carNumPlus() # add car Number
            if self.log[_fileNum].__contains__(_carNum):
                points = self.log[_fileNum][_carNum]
                # send to OpenCV
                pos = ct.list2str(points['pos'])
                self.parameters['pos'].value = bytes(pos, encoding='utf8')
                self.areaSize = float(points['areaSize'])
            else :
                self.initAndSetNewPos()
        else :
            self.initAndSetNewPos()

    def initAndSetNewPos(self):
        self.parameters['pos'].value = bytes('', encoding='utf8')

    def getNewParameters(self):
        _pos = str(self.parameters['pos'].value, encoding='utf-8')
        _pos = ct.str2list(_pos)

        if self.pos != _pos:
            self.areaSize = ct.getPolyArea(_pos)
            self.pos = _pos
            if not self.isDemo: self.updateLog()

    def checkLogfiles(self):
        # get filepath hashValue(MD5)
        path = self.filepath.get()
        self.pathMD5 = hashlib.md5(path.encode()).hexdigest()
        # find log file
        logFilePath = os.path.join(Config.LOG_FILE_PATH,'%s.json'%self.pathMD5)
        if os.path.exists(logFilePath):
            with open(logFilePath,'r') as load_f:
                load_dict = json.load(load_f)
                self.log = load_dict['files']
        # new object
        else:
            self.initLog()

    def initLog(self):
        self.log = {}
        self.log2file()

    def updateLog(self):
        _fileNum = self.filenameList.curselection()[0]
        _filename = self.filenames[_fileNum]
        _carNum = self.carNumberList.curselection()[0]
        _info = {
            'pos':      self.pos,
            'areaSize': self.areaSize,
        }

        if not self.log.__contains__(_fileNum):
            self.log[_fileNum] = {'filename': _filename}

        self.log[_fileNum][_carNum] = _info
        self.log2file()

    def log2file(self):
        _log = {
            'filepath':self.filepath.get(),
            'files':self.log,
        }
        dir = Config.LOG_FILE_PATH
        logFilePath = os.path.join(dir,'%s.json'%self.pathMD5)
        if not os.path.exists(dir):
            os.mkdir(dir)
        with open(logFilePath,"w") as logfile:
            json.dump(_log,logfile)

        print(_log)

    def log2cache(self):
        #要施工
        #添加写入cache文件的代码
        pass

    def initPos(self):
        if self.carNumberList.size() == 0:
            self.BTN_carNumPlus()

    def initParameters(self):
        self.pos = str(self.parameters['pos'].value, encoding='utf-8')
        self.areaSize = 0.0

    ############################################################
    ##                     Buttom command                     ##
    ############################################################
    
    # [button] Open file
    def BTN_openfile(self):
        filepath = filedialog.askdirectory()
        files = f.getFileName(filepath)
        if len(files) > 0:
            self.isDemo = False
            self.filenames = files
            self.filepath.set(str(filepath))
            self.label_filepath.configure(bg='#44DD44')
            self.filenameList.delete(0,tk.END)
            # insert filename into listbox
            for filename in files:
                self.filenameList.insert('end',filename)
            # select the first one
            self.filenameList.selection_clear(0,tk.END)
            self.filenameList.selection_set(0)
            # Load info from logfile
            self.checkLogfiles()
            self.setDisplayImage()
        else:
            self.filenameList.delete(0,tk.END)
            self.filepath.set('NO IMAGE FILE')
            self.label_filepath.configure(bg='#DD2222')
        

    # [list] select image File 
    def filenameOnSelected(self, event):
        self.setDisplayImage()

    # [button] add car number
    def BTN_carNumPlus(self):
        self.carNumberList.insert(tk.END,'Car No.%d'%self.carNumberList.size())
        self.carNumberList.selection_clear(0,tk.END)
        self.carNumberList.selection_set(tk.END)
        self.setSelectedCar()

    # [button] del car number
    def BTN_carNumminus(self):
        if self.carNumberList.size() > 0:
            selected = self.carNumberList.curselection()[0]
            self.carNumberList.delete(selected)
            if self.carNumberList.size() > 0:
                selectedNew = selected - 1 if selected - 1 >= 0 else 0
                self.carNumberList.selection_clear(0,tk.END)
                self.carNumberList.selection_set(selectedNew)
                self.setSelectedCar()
            else:
                self.BTN_carNumPlus()

    # [list] select Car Number
    def List_carNumberOnSelected(self, event):
        self.setSelectedCar()


if __name__ == '__main__':
    from multiprocessing import Process
    from multiprocessing.sharedctypes import Value, Array
    # 変数初期化
    parameters = {
        'filePath': Array('c', 200), # path
        'fileNum':  Value('i', -1), # path
        'pos':      Array('c', 200), # 点の座標
    }

    process_GUI = Process(target=GUI, args=(parameters,))
    process_GUI.start()
    process_GUI.join()
