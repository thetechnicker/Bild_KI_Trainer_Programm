import math
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
import sys

class Overlay(QWidget):
    def __init__(self, parent=None, x=0, y=0, width=100, height=100, horizontal_lines=10, vertical_lines=10):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.horizontal_lines = horizontal_lines
        self.vertical_lines = vertical_lines#


    def update_grid(self, x=None, y=None, width=None, height=None, horizontal_lines=None, vertical_lines=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if horizontal_lines is not None:
            self.horizontal_lines = horizontal_lines
        if vertical_lines is not None:
            self.vertical_lines = vertical_lines
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(Qt.red)
        try:
            painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

            # Draw horizontal lines
            for i in range(1, self.horizontal_lines):
                y = self.y + i * (self.height / self.horizontal_lines)
                painter.drawLine(int(self.x), int(y), int(self.x + self.width), int(y))

            # Draw vertical lines
            for i in range(1, self.vertical_lines):
                x = self.x + i * (self.width / self.vertical_lines)
                painter.drawLine(int(x), int(self.y), int(x), int(self.y + self.height))
        except Exception as e:
            print(e)

class WebcamWidget(QWidget):
    def __init__(self, CameraInfo=QCameraInfo.defaultCamera(), imgPath="d:/Images/image"):
        super().__init__()
        self.path=imgPath
        self.offsetX=0
        self.offsetY=0
        self.camera = QCamera(CameraInfo)
        self.count=0
        self.viewfinder = QCameraViewfinder()
        size=self.viewfinder.size()
        self.width = size.width()-1
        self.height = size.height()-1

        self.overlay = Overlay(self.viewfinder)
        self.camera.setViewfinder(self.viewfinder)

        self.capture = QCameraImageCapture(self.camera)
        self.capture.setCaptureDestination(QCameraImageCapture.CaptureToFile)

        layout = QVBoxLayout(self)
        layout.addWidget(self.viewfinder)

        self.camera.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        x, y, w, h =self.getDimension() 
        #print(x,y, h, w, width, height, scale)
        self.overlay.update_grid(x=int(x),y=int(y),width=int(w),height=int(h))
        self.overlay.resize(self.viewfinder.size())

    def setGrid(self, x=None, y=None, width=None, height=None, horizontal_lines=None, vertical_lines=None):
        self.offsetX=x
        self.offsetY=y
        x_new, y_new, _, _ =self.getDimension()
        self.overlay.update_grid(x=x_new, y=y_new, width=width,height=height,horizontal_lines=horizontal_lines, vertical_lines=vertical_lines)
    
    def getDimension(self):
        size=self.viewfinder.size()
        FW=16
        FH=9
        width = size.width()
        height = size.height()
        width_scale = width / FW
        height_scale = height / FH
        scale = min(width_scale, height_scale)
        w=(FW*scale)#-self.offsetX
        h=(FH*scale)#-self.offsetY
        x = ((width - w) // 2) +self.offsetX
        y = ((height - h) // 2)+self.offsetY
        return (x, y, w, h)
    
    def capture_image(self, folder=None):
        if not folder:
            file=f"{self.path}{self.count}.png"
            self.capture.capture(file)
            self.count+=1
        else:
            file=f"{folder}/image{self.count}.png"
            self.capture.capture(file)
            self.count+=1
        print("Lol")
        return file

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = WebcamWidget()
    window.show()
    sys.exit(app.exec_())