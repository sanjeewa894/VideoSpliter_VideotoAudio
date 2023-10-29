# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QProgressDialog
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QThread, Qt, QEvent, QTimer, QObject, SIGNAL, Slot

from PySide6 import QtCore
from ProcessVedioOps import ProcessVedioOps, ProgressLogger
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

        self.ui.timesFIle.released.connect(self.getTimesFile)
        self.ui.videoFIle.released.connect(self.getVideo)
#        self.ui.splitVideo.released.connect(self.splitVideoToChunck)
        self.processThread = QThread()
        self.processor.moveToThread(self.processThread)
        self.ui.splitVideo.released.connect(self.processor.splitVideoToChunck)
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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
