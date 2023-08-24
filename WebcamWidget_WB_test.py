import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

from Panels.WebcamView_WB import WebcamWidget

class WebcamWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.webcamWidget = WebcamWidget()
        self.initUI()

    def initUI(self):
        # Create layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.webcamWidget)

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
        showArrayButton = QPushButton("Show Numpy Array")
        showArrayButton.clicked.connect(self.showNumpyArray)
        layout.addWidget(showArrayButton)

    def updateOverlay(self):
        x = int(self.xInput.text())
        y = int(self.yInput.text())
        width = int(self.widthInput.text())
        height = int(self.heightInput.text())
        self.webcamWidget.setGrid(x=x, y=y, width=width, height=height)

    def showNumpyArray(self):
        array = np.zeros((720,1280,3), dtype=np.uint8)
        self.webcamWidget.setArray(array)
        cv2.imshow("Numpy Array", array)

if __name__ == '__main__':
    app = QApplication([])
    window = WebcamWindow()
    window.show()
    app.exec_()
