import os
    
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore  import QTimer
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QGridLayout
from PyQt5.QtMultimedia import QCameraInfo

import sys
try:
    from .neuralNetVideoTest import WebcamWindow
except:
    from neuralNetVideoTest import WebcamWindow

try:
    from .CameraViewDialog import CameraViewDialog
except:
    from CameraViewDialog import CameraViewDialog


class CameraWidget(QWidget):
    def __init__(self, parent=None, **data2):
        super().__init__()
        #print(data)
        #print(data2)
        self.folder=None
        if "folder" in data2:
            self.folder=data2["folder"]

        self.parent=parent

        self.setMinimumSize(250, 500);
        self.initUI()


    def SetFolder(self, folder):
        self.folder=folder

    def initUI(self):
        layout = QGridLayout()
        layout.setVerticalSpacing(20)
        layout.addWidget(QLabel('Kamera'), 0, 0)
        type_layout=QHBoxLayout()
        type_layout.addWidget(QLabel('type:'))
        self.type_box = QComboBox()
        self.type_box.addItems(['integratet'])#todo , 'web'])
        self.type_box.currentIndexChanged.connect(self.chancheType)
        
        type_layout.addWidget(self.type_box)

        layout.addLayout(type_layout, 1, 0)
        layout.setAlignment(type_layout, QtCore.Qt.AlignTop)
        self.web_layout = QVBoxLayout()
        address_layout = QHBoxLayout()
        address_layout.addWidget(QLabel('address:'))
        self.address_line = QLineEdit()
        address_layout.addWidget(self.address_line)
        self.web_layout.addLayout(address_layout)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel('port:'))
        self.port_line = QLineEdit()
        port_layout.addWidget(self.port_line)
        self.web_layout.addLayout(port_layout)

        connection_type_layout = QHBoxLayout()
        connection_type_layout.addWidget(QLabel('connection type:'))
        self.connection_type_box = QComboBox()
        self.connection_type_box.addItems(['ssh', 'http/https'])
        connection_type_layout.addWidget(self.connection_type_box)
        self.web_layout.addLayout(connection_type_layout)

        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel('username:'))
        self.username_line = QLineEdit()
        username_layout.addWidget(self.username_line)
        self.web_layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel('password:'))
        self.password_line = QLineEdit()
        self.password_line.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_line)
        self.web_layout.addLayout(password_layout)

        self.container_widget = QWidget()
        self.container_widget.setLayout(self.web_layout)
        self.container_widget.hide()

        layout.addWidget(self.container_widget, 2, 0)
        
        self.camera_list = {}
        cameras = QCameraInfo.availableCameras()
        
        for i in cameras:
            self.camera_list[f"{i.description()}"] = i
        #print(self.camera_list)
        
        self.CameraSelect = QComboBox()
        self.CameraSelect.addItems(list(self.camera_list.keys()))
        self.CameraLayout = QHBoxLayout()
        self.CameraLayout.addWidget(self.CameraSelect)
        
        self.Camera_container_widget = QWidget()
        self.Camera_container_widget.setLayout(self.CameraLayout)

        layout.addWidget(self.Camera_container_widget, 3, 0)


        button_layout = QHBoxLayout()
        self.open_button = QPushButton('open')
        self.open_button.clicked.connect(self.openCam)
        button_layout.addWidget(self.open_button)
        self.test_button = QPushButton('test cnn')
        button_layout.addWidget(self.test_button)
        self.test_button.clicked.connect(self.testNeuralNet)

        layout.addLayout(button_layout, 5, 0)
        layout.setAlignment(button_layout, QtCore.Qt.AlignTop)
        layout.setRowStretch(4, 1)

        self.setLayout(layout)
        self.Callback=None

        self.timer = QTimer()
        self.timer.timeout.connect(self.listupdater)
        self.timer.start(1000)  # Aktualisiert die Liste jede Sekunde

    def setCallback(self, Callback):
        self.Callback=Callback

    def openCam(self):
        cam=self.camera_list[self.CameraSelect.currentText()]
        dialog=CameraViewDialog(parent=self, folder=self.folder,camera=cam)
        dialog.setSaveCallback(self.Callback)
        dialog.show()

    def chancheType(self, index):
        current_value = self.type_box.currentText()
        if current_value=="web":
            self.container_widget.show()
            self.Camera_container_widget.hide()
        else:
            self.container_widget.hide()
            self.Camera_container_widget.show()

    # def testNeuralNet(self):
    #     var=self.parent.NeuralNetEditor.getCurrentNeuralnet()
    #     folder=self.parent.export_folder
    #     file=os.path.join(folder,f"{var}.h5")
    #     print(file)


    def testNeuralNet(self):
        try:
            var=self.parent.NeuralNetEditor.getCurrentNeuralnet()
            folder=self.parent.export_folder
            self.file=os.path.join(folder,f"{var}.h5")
            print(self.file)
        except:
            self.file=None
        # Add the WebcamWindow to the layout
        webcamWindow = WebcamWindow(model=self.file, camera=self.camera_list[self.CameraSelect.currentText()])
        try:
            webcamWindow.exec_()
        except:
            print("error")

    def listupdater(self):
        new_list={}
        cameras = QCameraInfo.availableCameras()
        
        
        for i in cameras:
            new_list[f"{i.description()}"] = i
        
        if not list(new_list.keys()) == list(self.camera_list.keys()):
            self.camera_list=dict(new_list)
            self.CameraSelect.clear()  # Alle vorhandenen Elemente entfernen
            self.CameraSelect.addItems(list(self.camera_list.keys()))  # Neue Elemente hinzufügen
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CameraWidget()
    ex.show()
    sys.exit(app.exec_())