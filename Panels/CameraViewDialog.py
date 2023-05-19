import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QLineEdit, QPushButton

if not (__name__=="__main__") and True:
    from .WebcamWidget import WebcamWidget
else:
    from WebcamWidget import WebcamWidget

class CameraViewDialog(QDialog):
    def __init__(self, parent=None, GridHeight=None, GridWidth=None):
        super().__init__(parent)
        self.setMinimumSize(QtCore.QSize(1024, 480))
        self.resize(QtCore.QSize(1024, 480))
        self.setWindowTitle("PyQt Webcam Viewer")
        gridLayout = QGridLayout()

        self.cam=WebcamWidget()        

        # Add input fields for x and y coordinates of rectangle
        #self.xInput = QLineEdit(self)
        #self.yInput = QLineEdit(self)

        self.gxInput = QLineEdit(self)
        self.gyInput = QLineEdit(self)

        #self.xInput.setText("1")
        #self.yInput.setText("1")
        self.gxInput.setText("10")
        self.gyInput.setText("10")
        

        #self.xInput.setValidator(QtGui.QIntValidator())
        #self.xInput.textChanged.connect(self.updateGrid)

        #self.yInput.setValidator(QtGui.QIntValidator())
        #self.yInput.textChanged.connect(self.updateGrid)

        self.gxInput.setValidator(QtGui.QIntValidator())
        self.gxInput.textChanged.connect(self.updateGrid)

        self.gyInput.setValidator(QtGui.QIntValidator())
        self.gyInput.textChanged.connect(self.updateGrid)

        gridLayout.addWidget(QLabel("X:"), 0, 0)
        gridLayout.addWidget(self.xInput, 0, 1)
        gridLayout.addWidget(QLabel("Y:"), 1, 0)
        gridLayout.addWidget(self.yInput, 1, 1)
        
        gridLayout.addWidget(QLabel("GX:"), 0, 0)
        gridLayout.addWidget(self.gxInput, 0, 1)
        gridLayout.addWidget(QLabel("GY:"), 1, 0)
        gridLayout.addWidget(self.gyInput, 1, 1)

        # Add save and cancel buttons
        saveButton = QPushButton('Save', self)
        cancelButton = QPushButton('Cancel', self)
        gridLayout.addWidget(saveButton, 2, 0)
        gridLayout.addWidget(cancelButton, 2, 1)
        layout=QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.cam)
        layout.addLayout(gridLayout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        print(self.size())
    
    def updateGrid(self,text):
        try:
            x = None#int(self.xInput.text())
            y = None#int(self.yInput.text())
            gx = int(self.gxInput.text())
            gy = int(self.gyInput.text())
            self.cam.setGrid(x=x,y=y,horizontal_lines=gx,vertical_lines=gy)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = CameraViewDialog()
    dialog.show()
    sys.exit(app.exec_())