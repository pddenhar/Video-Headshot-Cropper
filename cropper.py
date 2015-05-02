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
        self.imageXOffset = 0
        self.imageYOffset = 0
        self.initPos = 50
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key_Plus:
            self.zoomFrame(.005)
        elif e.key() == QtCore.Qt.Key_Minus:
            self.zoomFrame(-.005)
        elif e.key() == QtCore.Qt.Key_W:
            self.moveImage(0,3)
        elif e.key() == QtCore.Qt.Key_S:
            self.moveImage(0,-3)
        elif e.key() == QtCore.Qt.Key_A:
            self.moveImage(-3,0)
        elif e.key() == QtCore.Qt.Key_D:
            self.moveImage(3,0)
    def openFolder(self):
        self.files = []
        self.currentFileIndex = 0
        fd = QFileDialog(self)
        plik = str(fd.getExistingDirectory())
        self.ui.fileList.clear()
        for root, dirs, files in os.walk(plik):
            files = [f for f in files if (not f[0] == '.') and f[-4:] == ".mp4"]
            dirs[:] = [d for d in dirs if (not d[0] == '.')]
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
        self.setScale(.4)
        self.positionStuff()
    def positionStuff(self):
        self.ui.templateLabel.move(self.initPos, self.initPos);
        self.ui.imageLabel.move(self.initPos, self.initPos);
    def setScale(self, scaleFactor):
        self.templateScale = scaleFactor
        self.imageScale = scaleFactor
        self.ui.imageLabel.adjustSize()
        self.ui.templateLabel.adjustSize()
        self.ui.imageLabel.resize(scaleFactor * self.ui.imageLabel.pixmap().size())
        self.ui.templateLabel.resize(scaleFactor * self.ui.templateLabel.pixmap().size())
    def zoomFrame(self, zoom):
        self.imageScale = self.imageScale + zoom
        scaleDiff = (self.imageScale - self.templateScale) / 2
        self.ui.imageLabel.move(self.initPos - scaleDiff*1920 + self.imageXOffset, 
            self.initPos - scaleDiff*1080 - self.imageYOffset);
        self.ui.imageLabel.resize(self.imageScale * self.ui.imageLabel.pixmap().size())
    def moveImage(self, x, y):
        self.imageXOffset += x
        self.imageYOffset += y
        self.zoomFrame(0)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = Cropper()
    myapp.show()
    sys.exit(app.exec_())
