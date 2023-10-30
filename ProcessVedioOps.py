# This Python file uses the following encoding: utf-8
import os
from PySide6 import QtCore
from PySide6.QtCore import  Signal, QObject
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor

from proglog import ProgressBarLogger
import moviepy.editor as mp
import glob


class ProgressLogger(QObject,ProgressBarLogger):
    progressValue = Signal(int)
    progressText = Signal(str)

    def callback(self, **changes):
        # Every time the logger message is updated, this function is called with
        # the `changes` dictionary of the form `parameter: new value`.
        for (parameter, value) in changes.items():
            print(str(value))
            self.progressText.emit(value)

    def bars_callback(self, bar, attr, value,old_value=None):
        # Every time the logger progress is updated, this function is called
        percentage = (value / self.bars[bar]['total']) * 100
        self.progressValue.emit(int(percentage))

class ProcessVedioOps(QtCore.QObject):
    clearTextArea = Signal()
    appendTextArea = Signal(str)
    mainProgress = Signal(int)
    statusbarMsg = Signal(str)
    buttonStatus = Signal(bool)

    def __init__(self, mainWindow, progressB, logger):
        super().__init__()
        self.therdQuit = False
        self.processRun = False
        self.mainWindow = mainWindow
        self.progressB = progressB
        self.myLogger = logger

    def updateTermination(self):
        self.therdQuit = True
        if(self.processRun==True):
            self.progressB.exec()

    def splitVideoToChunck(self):
        self.clearTextArea.emit()
        if not os.path.exists(self.mainWindow.timeFileName):
            self.appendTextArea.emit("Time file not found!");
            return;

        if not os.path.exists(self.mainWindow.videofilePath):
            self.appendTextArea.emit("Video file not found!");
            return;

        targetN = self.mainWindow.videoDir + self.mainWindow.videofileName;
        if not os.path.exists(targetN):
            os.makedirs(targetN)

        with open(self.mainWindow.timeFileName) as f:
            times = f.readlines()
        times = [x.strip() for x in times]

        self.statusbarMsg.emit('Progressing. Please wait...');
        progress = len(times);
        self.mainProgress.emit(0);
        i=0;
        # loading video dsa gfg intro video
        clip = mp.VideoFileClip(self.mainWindow.videofilePath);
        self.appendTextArea.emit(str("Opened: "+self.mainWindow.videofilePath));
        self.processRun = True
        self.buttonStatus.emit(False)
        QApplication.processEvents();
        for time1 in times:
            print("\nQUit ", self.therdQuit)
            if self.therdQuit== True:
                break;
            starttime = (time1.split("-")[0])
            endtime = (time1.split("-")[1])

            self.appendTextArea.emit(time1);

            # getting only first 5 seconds
            clip2 = clip.subclip(starttime, endtime)
            clip2.write_videofile(targetN+"/"+self.mainWindow.videofileName+str(times.index(time1)+1)+".mp4",logger=self.myLogger);
            i+=1;
            self.mainProgress.emit((i*100/progress));
            QApplication.processEvents()

        self.progressB.cancel()
        self.processRun = False
        self.therdQuit = False
        self.buttonStatus.emit(True)
        QApplication.restoreOverrideCursor()
        self.statusbarMsg.emit('Ready');

    def writeToMp3(self,pathtoRead,direct):
        self.statusbarMsg.emit('Progressing. Please wait...');
        fileList = glob.glob(pathtoRead+"/*.mp4")
        if not os.path.exists(direct):
            # Create a new directory because it does not exist
            os.makedirs(direct)

        self.processRun = True
        self.buttonStatus.emit(False)
        progress = len(fileList);
        i=0
        self.mainProgress.emit(0);
        for fileName in fileList:
            if self.therdQuit== True:
                break;
            # Insert Local Video File Path
            clip = mp.VideoFileClip(fileName)
            output =  ((fileName.split("/")[-1]).replace(" ","")).replace(".mp4",".mp3")
            print(fileName,output)
            # Insert Local Audio File Path
            clip.audio.write_audiofile(direct + "/" +output,logger=self.myLogger)
            i+=1;
            self.mainProgress.emit((i*100/progress));
            QApplication.processEvents()

        self.progressB.cancel()
        self.processRun = False
        self.therdQuit = False
        self.buttonStatus.emit(True)
        QApplication.restoreOverrideCursor()
        self.statusbarMsg.emit('Ready');
