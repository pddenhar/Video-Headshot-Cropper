import sys, os
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from cropper_ui import Ui_MainWindow
import subprocess as sp
from PIL import Image

class Cropper(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.templateLabel.setVisible(False)
    def openFolder(self):
        self.files = []
        self.currentFileIndex = 0
        fd = QFileDialog(self)
        plik = str(fd.getExistingDirectory())
        self.ui.fileList.clear()
        for root, dirs, files in os.walk(plik):
            files = [f for f in files if (not f[0] == '.') and f[-4:] == ".mp4"]
            dirs[:] = [d for d in dirs if not d[0] == '.']
            short = root[len(plik):] + "/"
            self.ui.fileList.addItem(QListWidgetItem(short))
            for f in files:
                self.files += [(root, f)]
                self.ui.fileList.addItem(QListWidgetItem(f))
    def renderVideo(self):
        print "stinker"
    def nextVideo(self):
        if self.currentFileIndex < len(self.files):
            openFile = self.files[self.currentFileIndex]
            openFile = openFile[0] + "/" + openFile[1]
            self.currentFileIndex += 1
        command = [ "avconv",
            '-i', openFile,
            '-vcodec', 'png',
            '-ss', '1',
            '-vframes', '1',
            '-an',
            '-f', 'rawvideo',
            '-y',
            '/tmp/frame.png']
        sp.call(command)
        image = QImage("/tmp/frame.png")
        if image.isNull():
            QtGui.QMessageBox.information(self, "Image Viewer",
                        "Cannot load frame from %s.", openFile)
            return
        self.ui.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.ui.templateLabel.setVisible(True)
        self.scaleStuff(.4)
        self.positionStuff()
    def positionStuff(self):
        self.ui.templateLabel.move(100, 100);
        self.ui.imageLabel.move(100, 100);
    def scaleStuff(self, scaleFactor):
        self.ui.imageLabel.adjustSize()
        self.ui.templateLabel.adjustSize()
        self.ui.imageLabel.resize(scaleFactor * self.ui.imageLabel.pixmap().size())
        self.ui.templateLabel.resize(scaleFactor * self.ui.templateLabel.pixmap().size())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = Cropper()
    myapp.show()
    sys.exit(app.exec_())
