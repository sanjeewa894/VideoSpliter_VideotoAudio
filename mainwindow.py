# This Python file uses the following encoding: utf-8
import sys, glob

from PySide6.QtWidgets import QApplication, QMainWindow, QProgressDialog
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QThread, Qt, QEvent, QTimer, Slot, Signal

from ProcessVedioOps import ProcessVedioOps, ProgressLogger
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow


class MainWindow(QMainWindow):
    runVideoAudioConvert = Signal(str,str)
    videoDir = "";
    videofilePath = "";
    videofileName = "";
    timeFileName = "";

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)        
        self.progressB = QProgressDialog("Wrapping Up. Please Wait....", None, 0, 0,None)
        self.progressB.setWindowTitle("Aborting Process")
        self.progressB.setWindowModality(Qt.WindowModal)
        self.ui.statusbar.showMessage('Ready');
        self.progressB.findChild(QTimer).stop()
        self.progressB.setHidden(1)
        self.myLogger = ProgressLogger()
        self.myLogger.progressValue.connect(self.showImediateProgress)
        self.myLogger.progressText.connect(self.addTexted)
        self.processor = ProcessVedioOps(MainWindow,self.progressB,self.myLogger)
        self.processor.clearTextArea.connect(self.clearTexted)
        self.processor.appendTextArea.connect(self.addTexted)
        self.processor.mainProgress.connect(self.ui.progressBar.setValue)
        self.processor.statusbarMsg.connect(self.ui.statusbar.showMessage)
        self.processor.buttonStatus.connect(self.enableButtons)
        self.ui.splitVideo.released.connect(self.processor.splitVideoToChunck)
        self.ui.abortProcess.released.connect(self.stopProcess)
        self.ui.videoAudio.released.connect(self.getPathForAudioConvert)
        self.runVideoAudioConvert.connect(self.processor.writeToMp3)
        self.ui.timesFIle.released.connect(self.getTimesFile)
        self.ui.videoFIle.released.connect(self.getVideo)

        self.processThread = QThread()
        self.processor.moveToThread(self.processThread)
        self.processThread.finished.connect(self.processThread.quit)
        self.processThread.finished.connect(self.processor.deleteLater)
        self.processThread.finished.connect(self.processThread.deleteLater)
        self.processThread.start()

    def clearTexted(self):
        self.ui.plainTextEdit.clear()

    @Slot(str)
    def addTexted(self, text):
        self.ui.plainTextEdit.appendPlainText(text)

    @Slot(int)
    def showImediateProgress(self, value):
        self.ui.progressBar_2.setValue(value)

    def closeEvent(self, event):
        print("\nQuit True\n",event)
        #show popup
        if event.type() == QEvent.Close:
            print("\nExt Program\n")
            self.processor.updateTermination()
            self.processThread.quit()
            self.processThread.wait()
            print("\nExt Program\n")
            self.progressB.close()
            event.accept()

    def stopProcess(self):
        print("\nExt Program\n")
        self.processor.updateTermination()


    def enableButtons(self,enabled):
        self.ui.timesFIle.setEnabled(enabled)
        self.ui.videoFIle.setEnabled(enabled)
        self.ui.splitVideo.setEnabled(enabled)
        self.ui.videoAudio.setEnabled(enabled)
        self.ui.abortProcess.setEnabled(not enabled)


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

    def getPathForAudioConvert(self):
        #writeToMp3
#        pathtoRead,direct
        pathtoRead = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        direct = QFileDialog.getExistingDirectory(self, "Select Destination Root Directory")
        direct+="/"+pathtoRead.split("/")[-1] + "_Mp3"
        #check directory contains videos
        fileList = glob.glob(pathtoRead+"/*.mp4")
        if len(fileList)>0:
            self.runVideoAudioConvert.emit(pathtoRead,direct)
        else:
            self.addTexted("Not Found any Video Files !")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
