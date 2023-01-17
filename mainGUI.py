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
import time

import hashlib

############################################################
##                          GUI                           ##
############################################################

class GUI():
    def __init__(self, parameters):
        self.parameters = parameters
        self.objNumberSelected = 0
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
        tk.Label(cv_labeling, text='Objects & Areas', height=2, anchor=tk.SW).grid(row=0, columnspan=2, sticky=tk.W)
        # F2 objNumber Label and button
        frameObjNumber = tk.Frame(cv_labeling,relief=tk.RAISED)
        frameObjNumber.grid(row=1, column=0,sticky=tk.NW)
        tk.Label(frameObjNumber, text='Object Number', height=2, anchor=tk.SW).grid(row=0, column=0, sticky=tk.W)
        # tk.Button(frameObjNumber,text='+', width=4,command=self.BTN_objNumPlus).grid(row=0, column=1,sticky=tk.EW)
        # tk.Button(frameObjNumber,text='-', width=4,command=self.BTN_objNumminus).grid(row=0, column=2,sticky=tk.EW)

        # F3 areaNumber Label and button
        frameAreaInfoLabel = tk.Frame(cv_labeling,relief=tk.RAISED)
        frameAreaInfoLabel.grid(row=1, column=1,sticky=tk.NW)
        tk.Label(frameAreaInfoLabel, text='Area Information', height=2, anchor=tk.SW).grid(row=0, column=0, sticky=tk.W)

        # F4 objNumber Listbox
        frameObjNumberList = tk.Frame(cv_labeling,relief=tk.RAISED)
        frameObjNumberList.grid(row=2, column=0,sticky=tk.EW)
        # Scrollbar
        slb_objNumList = tk.Scrollbar(frameObjNumberList)
        slb_objNumList.pack(side=tk.RIGHT, fill=tk.Y)
        # [list] objNumber
        self.objNumberList = tk.Listbox(frameObjNumberList, yscrollcommand=slb_objNumList.set, width=20, exportselection=False)
        self.objNumberList.bind('<<ListboxSelect>>', self.List_objNumberOnSelected)
        self.objNumberList.pack()
        slb_objNumList.config(command=self.objNumberList.yview)

        # F5 areaNumber Label and button
        frameAreaInfo = tk.Frame(cv_labeling,relief=tk.RAISED)
        frameAreaInfo.grid(row=2, column=1,sticky=tk.NW)
        # area Info Label
        tk.Label(frameAreaInfo, text='Object：', height=2, anchor=tk.SW).grid(row=0, column=0, sticky=tk.W)
        self.objNameStr = tk.StringVar()
        tk.Label(frameAreaInfo, textvariable=self.objNameStr, height=2, anchor=tk.SW).grid(row=0, column=1, sticky=tk.W)
        tk.Label(frameAreaInfo, text='面積：', height=2, anchor=tk.SW).grid(row=1, column=0, sticky=tk.W)
        self.areaStr = tk.StringVar()
        tk.Label(frameAreaInfo, textvariable=self.areaStr, height=2, anchor=tk.SW).grid(row=1, column=1, sticky=tk.W)

        # CV2 output Module
        cv_save = tk.Canvas(self.controlPanel)
        tk.Label(cv_save, text='Save', height=2, anchor=tk.SW).grid(row=0, columnspan=2, sticky=tk.W)
        # F6 Save
        frameSave = tk.Frame(cv_save,relief=tk.RAISED)
        frameSave.grid(row=1, column=0,sticky=tk.NW)
        tk.Button(frameSave,text='Save CSV', width=8,command=self.save2csv).grid(row=0, column=0,sticky=tk.NW)

        # Canvas pack
        cv_file.pack(anchor=tk.SW)
        cv_labeling.pack(anchor=tk.SW)
        cv_save.pack(anchor=tk.SW)

        # init data
        self.initParameters()

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

    def setSelectedObj(self):
        if self.objNumberList.curselection() != ():
            selected = self.objNumberList.curselection()[0]
            self.objNameStr.set('No.%d'%selected)
            self.setNewPos()

    # find pos info in log
    def setNewPos(self):
        if not len(self.filenameList.curselection()) > 0:
            return None
        # if not len(self.objNumberList.curselection()) > 0:
        #     self.BTN_objNumPlus()
        _fileNum = self.filenameList.curselection()[0]
        _objNum = self.objNumberList.curselection()[0]
        # get pos from log
        if self.log.__contains__(str(_fileNum)):
            # # get obj Number (keys) of Image
            # NumOfKeys = len(self.log[str(_fileNum)].keys())
            # while NumOfKeys > self.objNumberList.size():
            #     self.BTN_objNumPlus() # add obj Number
            if self.log[str(_fileNum)].__contains__(str(_objNum)):
                points = self.log[str(_fileNum)][str(_objNum)]
                # send to OpenCV
                pos = ct.list2str(points['pos'])
                self.parameters['pos'].value = bytes(pos, encoding='utf8')
                self.areaSize = float(points['areaSize'])
                print(self.areaSize, pos)
            else:
                self.parameters['pos'].value = bytes('', encoding='utf8')
                self.areaSize = float(0.0)
        else:
            self.parameters['pos'].value = bytes('', encoding='utf8')
            self.areaSize = float(0.0)

    def getNewParameters(self):
        if not len(self.filenameList.curselection()) > 0:
            return None
        # if not len(self.objNumberList.curselection()) > 0:
        #     self.BTN_objNumPlus()
        _pos = str(self.parameters['pos'].value, encoding='utf-8')
        _pos = ct.str2list(_pos)

        if self.pos != _pos:
            print(1)
            print(_pos)
            print(ct.getPolyArea(_pos))
            self.areaSize = ct.getPolyArea(_pos)
            self.pos = _pos
            self.updateLog()

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
        _objNum = self.objNumberList.curselection()[0]
        _info = {
            'pos':      self.pos,
            'areaSize': self.areaSize,
        }

        if not self.log.__contains__(str(_fileNum)):
            self.log[str(_fileNum)] = {'filename': _filename}

        self.log[str(_fileNum)][str(_objNum)] = _info
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

    def log2cache(self):
        #要施工
        #添加写入cache文件的代码
        pass

    # save to csv file
    def save2csv(self):
        ImageFilePath = self.filepath.get()
        logFilePath = os.path.join('output_%d.csv'%int(time.time()))
        totalObjs = self.objNumberList.size()
        totalFiles = self.filenameList.size()
        totalPixel = Config.DISPLAY_HEIGHT * Config.DISPLAY_WIDTH

        if totalFiles <= 0: return False

        # write header
        header = 'filepath,filename,fileNumber,totalSize'
        for objNum in range(totalObjs):
            header = header + ',OBJ.%d Size,OBJ.%d Per.'%(objNum, objNum)
        header = header +'\n'

        datas = []
        # write data
        for fileNum in range(totalFiles):
            filename = self.filenames[fileNum]
            _data = '%s,%s,%d,%d'%(ImageFilePath,filename,fileNum,totalPixel)
            if self.log.__contains__(str(fileNum)):
                for objNum in range(totalObjs):
                    if self.log[str(fileNum)].__contains__(str(objNum)):
                        areaSize = self.log[str(fileNum)][str(objNum)]['areaSize']
                        _data = _data + ',%d,%f'%(int(areaSize), float(areaSize/totalPixel))
                    else:
                        # fileNum havent this objNum
                        _data = _data + ',0,0'
            else:
                # fileNum havent any obj
                _data = _data + ',0,0'*totalObjs

            datas.append(_data+'\n')

        with open(logFilePath,"w") as logfile:
            logfile.writelines(header)
            logfile.writelines(datas)

    def initParameters(self):
        self.pos = str(self.parameters['pos'].value, encoding='utf-8')
        self.areaSize = 0.0

        for n in range(10):
            self.objNumberList.insert(tk.END,'No.%d'%n)
        self.objNumberList.selection_clear(0,tk.END)
        self.objNumberList.selection_set(0)

    ############################################################
    ##                     Buttom command                     ##
    ############################################################
    
    # [button] Open file
    def BTN_openfile(self):
        filepath = filedialog.askdirectory()
        files = f.getFileName(filepath)
        if len(files) > 0:
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

    # # [button] add obj number
    # def BTN_objNumPlus(self):
    #     self.objNumberList.insert(tk.END,'Obj No.%d'%self.objNumberList.size())
    #     self.objNumberList.selection_clear(0,tk.END)
    #     self.objNumberList.selection_set(tk.END)
    #     self.setSelectedObj()

    # # [button] del obj number
    # def BTN_objNumminus(self):
    #     if self.objNumberList.size() > 0:
    #         selected = self.objNumberList.curselection()[0]
    #         self.objNumberList.delete(selected)
    #         if self.objNumberList.size() > 0:
    #             selectedNew = selected - 1 if selected - 1 >= 0 else 0
    #             self.objNumberList.selection_clear(0,tk.END)
    #             self.objNumberList.selection_set(selectedNew)
    #             self.setSelectedObj()
    #         else:
    #             self.BTN_objNumPlus()

    # [list] select Obj Number
    def List_objNumberOnSelected(self, event):
        self.setSelectedObj()


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
