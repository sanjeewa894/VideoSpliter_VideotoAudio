# This Python file uses the following encoding: utf-8
import sys
import os

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QProcess
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *


# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

class MainWindow(QMainWindow):

    videoDir = "";
    videofilePath = "";
    videofileName = "";
    timeFileName = "";

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.statusbar.showMessage('Ready');
        self.ui.timesFIle.released.connect(self.getTimesFile)
        self.ui.videoFIle.released.connect(self.getVideo)

        self.ui.splitVideo.released.connect(self.splitVideoToChunck)


    def getTimesFile(self):
        fname = QFileDialog.getOpenFileName(self, "Open file", ".","Text files (*.txt)")
        print(fname[0]);
        MainWindow.timeFileName = fname[0];
        self.ui.timeFileSelection.setText(fname[0]);

    def getVideo(self):
        fname = QFileDialog.getOpenFileName(self, "Open file", ".","Video files (*.mp4)")
        print(fname[0]);
        MainWindow.videofilePath = fname[0];
        self.ui.videoSelection.setText(fname[0]);
        dirList = fname[0].split("/");
        fileName = dirList[-1];
        fileName = fileName.removesuffix(".mp4");
        MainWindow.videofileName = fileName.replace(" ","");
        print(MainWindow.videofileName);
        dirList.remove(dirList[-1]);
        for t in dirList:
            MainWindow.videoDir+=t+"/";

        print(MainWindow.videoDir)

    def splitVideoToChunck(self):
        self.ui.plainTextEdit.clear();
        if not os.path.exists(MainWindow.timeFileName):
            self.ui.plainTextEdit.appendPlainText("Time file not found!");
            print("Time file not found!");
            return;

        if not os.path.exists(MainWindow.videofilePath):
            self.ui.plainTextEdit.appendPlainText("Video file not found!");
            print("Video file not found!");
            return;

        targetN = MainWindow.videoDir + MainWindow.videofileName;
        if not os.path.exists(targetN):
            os.makedirs(targetN)

        with open(MainWindow.timeFileName) as f:
            times = f.readlines()
        times = [x.strip() for x in times]

        self.ui.statusbar.showMessage('Progressing. Please wait...');
        progress = len(times);
        self.ui.progressBar.setValue(0);
        i=0;
        # loading video dsa gfg intro video
        clip = VideoFileClip(MainWindow.videofilePath);
        self.ui.plainTextEdit.appendPlainText("Opened: "+MainWindow.videofilePath);
        QApplication.processEvents();
        for time in times:
            starttime = (time.split("-")[0])
            endtime = (time.split("-")[1])

            self.ui.plainTextEdit.appendPlainText(time);

            # getting only first 5 seconds
            clip2 = clip.subclip(starttime, endtime)
            # looping video 3 times
            self.ui.plainTextEdit.appendPlainText("Write: "+targetN+"/"+MainWindow.videofileName+str(times.index(time)+1)+".mp4");
            clip2.write_videofile(targetN+"/"+MainWindow.videofileName+str(times.index(time)+1)+".mp4");
            i+=1;
            self.ui.progressBar.setValue((i*100/progress));
            QApplication.processEvents()

        self.ui.statusbar.showMessage('Ready');

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
