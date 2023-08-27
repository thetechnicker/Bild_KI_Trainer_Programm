import math
import os
import cv2
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QAbstractVideoBuffer, QCameraImageCapture, QImageEncoderSettings, QAbstractVideoSurface, QVideoFrame, QVideoSurfaceFormat
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
import sys
import qimage2ndarray


class Overlay(QWidget):
    def __init__(self, parent=None, x=0, y=0, width=100, height=100, horizontal_lines=10, vertical_lines=10):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.horizontal_lines = horizontal_lines
        self.vertical_lines = vertical_lines

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

class VideoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.image = QtGui.QImage()

    def setImage(self, image):
        self.image = image
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if not self.image.isNull():
            # Berechne das Seitenverhältnis des Bildes
            imageAspectRatio = self.image.width() / self.image.height()
            # Berechne das Seitenverhältnis des Widgets
            widgetAspectRatio = self.width() / self.height()
            # Skaliere das Bild entsprechend dem kleineren Seitenverhältnis
            if imageAspectRatio > widgetAspectRatio:
                scaledImage = self.image.scaledToWidth(self.width())
            else:
                scaledImage = self.image.scaledToHeight(self.height())
            # Zentriere das Bild im Widget
            x = (self.width() - scaledImage.width()) / 2
            y = (self.height() - scaledImage.height()) / 2
            painter.drawImage(QtCore.QPoint(int(x), int(y)), scaledImage)


class VideoBufferSurface(QAbstractVideoSurface):
    def __init__(self, widget=None):
        super().__init__(widget)
        self.widget = widget
        self.imageFormat = QtGui.QImage.Format_Invalid
        self.array = None

    def supportedPixelFormats(self, handleType):
        return [QVideoFrame.Format_RGB32,
                QVideoFrame.Format_ARGB32,
                QVideoFrame.Format_ARGB32_Premultiplied,
                QVideoFrame.Format_RGB565,
                QVideoFrame.Format_RGB555]

    def isFormatSupported(self, format):
        imageFormat = QVideoFrame.imageFormatFromPixelFormat(format.pixelFormat())
        size = format.frameSize()
        return imageFormat != QtGui.QImage.Format_Invalid and not size.isEmpty() and format.handleType() == QAbstractVideoBuffer.NoHandle

    def start(self, format):
        imageFormat = QVideoFrame.imageFormatFromPixelFormat(format.pixelFormat())
        size = format.frameSize()
        if imageFormat != QtGui.QImage.Format_Invalid and not size.isEmpty():
            self.imageFormat = imageFormat
            super().start(format)
            return True
        else:
            return False

    def stop(self):
        super().stop()
    

    def present(self, frame):
        if frame.isValid():
            cloneFrame = QVideoFrame(frame)
            cloneFrame.map(QAbstractVideoBuffer.ReadOnly)
            image = QtGui.QImage(cloneFrame.bits(), cloneFrame.width(), cloneFrame.height(), cloneFrame.bytesPerLine(), self.imageFormat)
            transform = QtGui.QTransform().rotate(180)
            image = image.transformed(transform)
            #image_array = qimage2ndarray.rgb_view(image)

            width = image.width()
            height = image.height()
            ptr = image.bits()
            ptr.setsize(height * width * 4)
            image_array = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
            #print(image_array)
            #image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            #cv2.imshow("Image", image_array)

            if self.widget:
                self.widget.setImage(image)

            if self.array is not None:
                self.array[:,:] = np.array(image_array)

            cloneFrame.unmap()
            return True
        return False
        #result = super().present(frame)
        #return result


    def setArray(self, array):
        self.array = array


class WebcamWidget(QWidget):
    def __init__(self, CameraInfo=QCameraInfo.defaultCamera(), imgPath="d:/Images/image"):
        super().__init__()
        self.resize(400, 300)
        self.path = imgPath
        self.count = 0
        self.camera = QCamera(CameraInfo)
        self.viewfinder = VideoWidget()
        self.overlay = Overlay(self.viewfinder)
        self.surface = VideoBufferSurface(self.viewfinder)
        #-----------------------------------------
        self.camera.setViewfinder(self.surface)
        #-----------------------------------------
        self.capture = QCameraImageCapture(self.camera)
        self.capture.setCaptureDestination(QCameraImageCapture.CaptureToFile)
        layout = QVBoxLayout(self)
        #self.viewfinder.show()
        layout.addWidget(self.viewfinder)
        self.camera.start()


    def setGrid(self, x=None, y=None, width=None, height=None, horizontal_lines=None, vertical_lines=None):
        x_new, y_new, _, _ = self.getDimension()
        self.overlay.update_grid(x=x_new, y=y_new, width=width, height=height,
                                 horizontal_lines=horizontal_lines, vertical_lines=vertical_lines)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        x, y, w, h = self.getDimension()
        self.overlay.update_grid(x=int(x), y=int(y), width=int(w), height=int(h))
        self.overlay.resize(self.viewfinder.size())

    def getDimension(self):
        size = self.viewfinder.size()
        FW = 16
        FH = 9
        width = size.width()
        height = size.height()
        width_scale = width / FW
        height_scale = height / FH
        scale = min(width_scale, height_scale)
        w = (FW * scale)
        h = (FH * scale)
        x = (width - w) // 2
        y = (height - h) // 2
        return x, y, w, h

    def capture_image(self, folder=None) -> str:
        if not folder:
            file = f"{self.path}{self.count}"
            self.capture.capture(file)
            return file
        else:
            file = f"{folder}/image{self.count}"
            self.capture.capture(file)
            return file

    def stop(self):
        self.camera.stop()

    def setArray(self, array):
        self.surface.setArray(array)
    

if __name__ == '__main__':
    app = QApplication([])
    window = WebcamWidget()
    window.show()
    app.exec_()
