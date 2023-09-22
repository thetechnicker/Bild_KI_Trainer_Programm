import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QLineEdit, QPushButton
from PyQt5.QtMultimedia import QCamera, QCameraInfo

try:
    from .WebcamWidget import WebcamWidget
except:
    from WebcamWidget import WebcamWidget

class CameraViewDialog(QDialog):
    def __init__(self, parent=None, GridHeight=None, GridWidth=None, folder=None, camera:QCameraInfo=None):
        super().__init__(parent)
        if folder:
            self.folder=folder
        self.setMinimumSize(QtCore.QSize(1024, 480))
        self.resize(QtCore.QSize(1024, 480))
        self.setWindowTitle("PyQt Webcam Viewer")
        gridLayout = QGridLayout()

        self.cam=WebcamWidget(CameraInfo=camera)

        # Add input fields for x and y coordinates of rectangle
        self.xInput = QLineEdit(self)
        self.yInput = QLineEdit(self)
        
        self.wInput = QLineEdit(self)
        self.hInput = QLineEdit(self)

        self.gxInput = QLineEdit(self)
        self.gyInput = QLineEdit(self)

        self.xInput.setText("0")
        self.yInput.setText("0")

        self.wInput.setText("")
        self.hInput.setText("")

        self.gxInput.setText("10")
        self.gyInput.setText("10")
        

        self.xInput.setValidator(QtGui.QIntValidator())
        self.xInput.textChanged.connect(self.updateGrid)

        self.yInput.setValidator(QtGui.QIntValidator())
        self.yInput.textChanged.connect(self.updateGrid)
        
        self.wInput.setValidator(QtGui.QIntValidator())
        self.wInput.textChanged.connect(self.updateGrid)
        if GridWidth:
            self.wInput.setReadOnly(True)

        self.hInput.setValidator(QtGui.QIntValidator())
        self.hInput.textChanged.connect(self.updateGrid)
        if GridHeight:
            self.hInput.setReadOnly(True)

        self.gxInput.setValidator(QtGui.QIntValidator())
        self.gxInput.textChanged.connect(self.updateGrid)

        self.gyInput.setValidator(QtGui.QIntValidator())
        self.gyInput.textChanged.connect(self.updateGrid)

        gridLayout.addWidget(QLabel("X:"), 0, 0)
        gridLayout.addWidget(self.xInput, 0, 1)
        gridLayout.addWidget(QLabel("Y:"), 1, 0)
        gridLayout.addWidget(self.yInput, 1, 1)
        
        gridLayout.addWidget(QLabel("Width:"), 2, 0)
        gridLayout.addWidget(self.wInput, 2, 1)
        gridLayout.addWidget(QLabel("Height:"), 3, 0)
        gridLayout.addWidget(self.hInput, 3, 1)
        
        gridLayout.addWidget(QLabel("Horizontal Splitcount:"), 4, 0)
        gridLayout.addWidget(self.gxInput, 4, 1)
        gridLayout.addWidget(QLabel("Vertikal Splitcount:"), 5, 0)
        gridLayout.addWidget(self.gyInput, 5, 1)


        saveButton = QPushButton('Save', self)
        saveButton.clicked.connect(self.saveIMG)

        cancelButton = QPushButton('Cancel', self)
        cancelButton.clicked.connect(self.close)

        gridLayout.addWidget(saveButton, 6, 0)
        gridLayout.addWidget(cancelButton, 6, 1)
        layout=QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.cam)
        layout.addLayout(gridLayout)
        self.saveCallback=None

    def setSaveCallback(self, callback):
        self.saveCallback=callback

    def saveIMG(self):
        try:
            file=self.cam.capture_image(self.folder)
            self.saveCallback(file=file)
        except:
            raise FileNotFoundError(f"No such file or directory: {self.folder}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        print(self.size())

    def closeEvent(self, event):
        self.cam.stop()
        event.accept() 
    
    def updateGrid(self,text):
        try:
            w = int(self.wInput.text())
            h = int(self.hInput.text())
        except:
            w = None
            h = None
        try:
            x = int(self.xInput.text())
            y = int(self.yInput.text())
            gx = int(self.gxInput.text())
            gy = int(self.gyInput.text())
            self.cam.setGrid(x=x,y=y,width=w,height=h,horizontal_lines=gx,vertical_lines=gy)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = CameraViewDialog()
    dialog.show()
    sys.exit(app.exec_())