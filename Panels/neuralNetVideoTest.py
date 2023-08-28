import threading
import time
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QThread

if __name__=="__main__":
    from WebcamView_WB import WebcamWidget
else:
    from Panels.WebcamView_WB import WebcamWidget
    
class ImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QtGui.QImage()

    def setImage(self, image: np.ndarray):
        # Konvertiere das NumPy-Array in ein QImage
        h, w, c = image.shape
        if c == 3:
            qimage = QtGui.QImage(image.data, w, h, 3 * w, QtGui.QImage.Format_RGB888)
        elif c == 4:
            qimage = QtGui.QImage(image.data, w, h, 4 * w, QtGui.QImage.Format_RGBA8888)
        else:
            raise ValueError("Das Bild muss entweder 3 oder 4 Kanäle haben")
        self.image = qimage
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(QtCore.QPoint(0, 0), self.image)


class DisplayArrayThread(QThread):
    def __init__(self, webcamWidget, image_widget):
        super().__init__()
        self.webcamWidget = webcamWidget
        self.image_widget = image_widget
        self.stopped = False

    def run(self):
        # Create a NumPy array of zeros
        array = np.zeros((720, 1280, 4), dtype=np.uint8)
        
        # Set the array for the webcam widget
        self.webcamWidget.setArray(array)
        
        # Continuously update the image in the image widget
        while not self.stopped:
            self.image_widget.setImage(array)
            self.msleep(100)  # Update the image every 0.1 seconds

    def stop(self):
        self.stopped = True

class WebcamWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.webcamWidget = WebcamWidget()
        self.image_widget = ImageWidget(self)
        self.initUI()

    def initUI(self):
        image_layout=QHBoxLayout()
        image_layout.addWidget(self.webcamWidget)
        image_layout.addWidget(self.image_widget)
        # Create layout
        layout = QVBoxLayout(self)
        layout.addLayout(image_layout)

        # Create input fields for overlay parameters
        overlayLayout = QHBoxLayout()
        self.xInput = QLineEdit()
        self.yInput = QLineEdit()
        self.widthInput = QLineEdit()
        self.heightInput = QLineEdit()
        overlayLayout.addWidget(QLabel("x:"))
        overlayLayout.addWidget(self.xInput)
        overlayLayout.addWidget(QLabel("y:"))
        overlayLayout.addWidget(self.yInput)
        overlayLayout.addWidget(QLabel("width:"))
        overlayLayout.addWidget(self.widthInput)
        overlayLayout.addWidget(QLabel("height:"))
        overlayLayout.addWidget(self.heightInput)
        layout.addLayout(overlayLayout)

        # Create button to update overlay
        updateButton = QPushButton("Update Overlay")
        updateButton.clicked.connect(self.updateOverlay)
        layout.addWidget(updateButton)

        # Create button to show numpy array
        self.showArrayButton = QPushButton("Show Numpy Array")
        self.showArrayButton.clicked.connect(self.showNumpyArray)
        layout.addWidget(self.showArrayButton)

    def updateOverlay(self):
        x = int(self.xInput.text())
        y = int(self.yInput.text())
        width = int(self.widthInput.text())
        height = int(self.heightInput.text())
        self.webcamWidget.setGrid(x=x, y=y, width=width, height=height)

    def showNumpyArray(self):
        if self.showArrayButton.text() == "Show Numpy Array":
            # Create a new thread to display the array
            self.displayArrayThread = DisplayArrayThread(self.webcamWidget, self.image_widget)
            self.displayArrayThread.start()
            # Change the button text to "Stop"
            self.showArrayButton.setText("Stop")
        else:
            # Stop the thread
            self.displayArrayThread.stop()
            # Change the button text back to "Show Numpy Array"
            self.showArrayButton.setText("Show Numpy Array")


            

if __name__ == '__main__':
    app = QApplication([])
    window = WebcamWindow()
    window.show()
    app.exec_()
