from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtMultimedia import QCamera, QCameraInfo
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
        painter.drawRect(self.x, self.y, self.width, self.height)

        # Draw horizontal lines
        for i in range(1, self.horizontal_lines):
            y = self.y + i * (self.height / self.horizontal_lines)
            painter.drawLine(int(self.x), int(y), int(self.x + self.width), int(y))

        # Draw vertical lines
        for i in range(1, self.vertical_lines):
            x = self.x + i * (self.width / self.vertical_lines)
            painter.drawLine(int(x), int(self.y), int(x), int(self.y + self.height))

class CameraWidget(QWidget):
    def __init__(self, CameraInfo=QCameraInfo.defaultCamera()):
        super().__init__()

        self.camera = QCamera(CameraInfo)
        viewfinder_settings = self.camera.viewfinderSettings()
        resolution = viewfinder_settings.resolution()
        self.width = resolution.width()
        self.height = resolution.height()

        self.viewfinder = QCameraViewfinder()
        self.overlay = Overlay(self.viewfinder)
        self.camera.setViewfinder(self.viewfinder)

        layout = QVBoxLayout(self)
        layout.addWidget(self.viewfinder)

        self.camera.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.resize(self.viewfinder.size())

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = CameraWidget()
    window.show()
    sys.exit(app.exec_())