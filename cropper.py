#!/usr/bin/python
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
        self.initScale = .4
        self.imageScale = self.initScale
        self.ui.templateLabel.move(self.initPos, self.initPos)
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        if e.key() == QtCore.Qt.Key_Plus:
            self.zoomFrame(.005)
        if e.key() == QtCore.Qt.Key_Minus:
            self.zoomFrame(-.005)
        if e.key() == QtCore.Qt.Key_W:
            self.moveImage(0,3)
        if e.key() == QtCore.Qt.Key_S:
            self.moveImage(0,-3)
        if e.key() == QtCore.Qt.Key_A:
            self.moveImage(-3,0)
        if e.key() == QtCore.Qt.Key_D:
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
        finalScale = (self.imageScale / self.initScale)
        bounds_height = int(1080 / finalScale)
        bounds_width = int(1920 / finalScale)
        print bounds_width, bounds_height
        x = int(-self.imageXOffset/self.imageScale + (1920 - bounds_width) / 2)
        y = int(self.imageYOffset/self.imageScale + (1080 - bounds_height) / 2)
        print x, y
        if finalScale < 1:
            QtGui.QMessageBox.information(self, "Image Cropper","A crop scale of "+str(finalScale)+" is not a crop")
            return
        elif x + bounds_width > self.ui.imageLabel.pixmap().size().width() or \
            y + bounds_height > self.ui.imageLabel.pixmap().size().height() or \
            x < 0 or y < 0:
            QtGui.QMessageBox.information(self, "Image Cropper", "You are trying to crop outside of the video bounds.")
            return
        cropString = "crop={0}:{1}:{2}:{3}".format(bounds_width, bounds_height, x, y)
        command = ["avconv",
            '-i', self.openFile[0] +'/' + self.openFile[1],
            '-filter:v', cropString,
            '-an',
            '/home/peter/Desktop/cropped/' + self.openFile[1]
        ]
        print command
        sp.call(command)
        self.nextVideo()
    def nextVideo(self):
        if self.currentFileIndex < len(self.files):
            openFile = self.files[self.currentFileIndex]
            self.openFile = openFile
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
            QtGui.QMessageBox.information(self, "Image Loader",
                        "Cannot load frame from %s.", openFile)
            return
        self.ui.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.ui.templateLabel.setVisible(True)
        self.setScale(self.initScale)
        self.zoomFrame(0)
    def setScale(self, scaleFactor):
        self.templateScale = scaleFactor
        #self.imageScale = scaleFactor
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
