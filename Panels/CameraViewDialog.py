import os

import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QLineEdit, QPushButton, QSpinBox
from PyQt5.QtMultimedia import QCamera, QCameraInfo


try:
    from .EmptyableSpinBox import EmptyableSpinBox
    from .WebcamView_WB import WebcamWidget as WebcamWidget
except:
    from EmptyableSpinBox import EmptyableSpinBox
    from WebcamView_WB import WebcamWidget as WebcamWidget

class CameraViewDialog(QDialog):
    def __init__(self, parent=None, GridHeight=None, GridWidth=None, folder=None, camera:QCameraInfo=None):
        
        super().__init__(parent)
        if folder:
            self.folder=folder
        self.setMinimumSize(QtCore.QSize(1024, 480))
        self.resize(QtCore.QSize(1024, 480))
        self.setWindowTitle("PyQt Webcam Viewer")
        gridLayout = QGridLayout()
        if(camera):
            self.cam=WebcamWidget(CameraInfo=camera)

        self.cam=WebcamWidget()
        # Add input fields for x and y coordinates of rectangle
        self.xInput = EmptyableSpinBox(self)
        self.yInput = EmptyableSpinBox(self)
        
        self.wInput = EmptyableSpinBox(self)
        self.hInput = EmptyableSpinBox(self)

        self.gxInput = EmptyableSpinBox(self)
        self.gyInput = EmptyableSpinBox(self)

        self.xInput.setValue(0)
        self.yInput.setValue(0)

        self.wInput.setValue(0)
        self.hInput.setValue(0)

        self.gxInput.setValue(0)
        self.gyInput.setValue(0)
        

        #self.xInput.setValidator(QtGui.QIntValidator())
        self.xInput.setFixedWidth(100)
        self.xInput.valueChanged.connect(self.updateGrid)

        #self.yInput.setValidator(QtGui.QIntValidator())
        self.yInput.setFixedWidth(100)
        self.yInput.textChanged.connect(self.updateGrid)
        
        #self.wInput.setValidator(QtGui.QIntValidator())
        self.wInput.setFixedWidth(100)
        self.wInput.textChanged.connect(self.updateGrid)
        if GridWidth:
            self.wInput.setReadOnly(True)

        #self.hInput.setValidator(QtGui.QIntValidator())
        self.hInput.setFixedWidth(100)
        self.hInput.textChanged.connect(self.updateGrid)
        if GridHeight:
            self.hInput.setReadOnly(True)

        #self.gxInput.setValidator(QtGui.QIntValidator())
        self.gxInput.setFixedWidth(100)
        self.gxInput.textChanged.connect(self.updateGrid)

        #self.gyInput.setValidator(QtGui.QIntValidator())
        self.gyInput.setFixedWidth(100)
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
        saveButton.setFixedWidth(100)
        saveButton.clicked.connect(self.saveIMG)

        cancelButton = QPushButton('Cancel', self)
        cancelButton.setFixedWidth(100)
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
        #print(self.size())

    def closeEvent(self, event):
        self.cam.stop()
        event.accept() 
    
    def updateGrid(self,text):
        try:
            x = int(self.xInput.text())
        except:
            x = None

        try:
            y = int(self.yInput.text())
        except:
            y = None

        try:
            w = int(self.wInput.text())
        except:
            w = None

        try:
            h = int(self.hInput.text())
        except:
            h = None

        try:
            gx = int(self.gxInput.text())
        except:
            gx = None

        try:
            gy = int(self.gyInput.text())
        except:
            gy = None
            
        self.cam.setGrid(x=x,y=y,width=w,height=h,horizontal_lines=gx,vertical_lines=gy)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = CameraViewDialog()
    dialog.show()
    sys.exit(app.exec_())