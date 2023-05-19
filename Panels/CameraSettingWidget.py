from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QGridLayout
from PyQt5.QtMultimedia import QCameraInfo

import sys

if not (__name__=="__main__") :
    from .CameraViewDialog import CameraViewDialog
else:
    from CameraViewDialog import CameraViewDialog


class CameraWidget(QWidget):
    def __init__(self, *data, **data2):
        super().__init__()
        self.setMinimumSize(250, 500);
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        layout.setVerticalSpacing(20)
        layout.addWidget(QLabel('Kamera'), 0, 0)
        type_layout=QHBoxLayout()
        type_layout.addWidget(QLabel('type:'))
        self.type_box = QComboBox()
        self.type_box.addItems(['web', 'integratet'])
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

        layout.addWidget(self.container_widget, 2, 0)
        
        camera_list = []
        cameras = QCameraInfo.availableCameras()
        
        camera_list.append("Default")
        for i in range(len(cameras)):
            camera_list.append(str(i+1))
        
        self.CameraSelect = QComboBox()
        self.CameraSelect.addItems(camera_list)
        self.CameraLayout = QHBoxLayout()
        self.CameraLayout.addWidget(self.CameraSelect)
        
        self.Camera_container_widget = QWidget()
        self.Camera_container_widget.setLayout(self.CameraLayout)
        self.Camera_container_widget.hide()

        layout.addWidget(self.Camera_container_widget, 3, 0)


        button_layout = QHBoxLayout()
        self.open_button = QPushButton('open')
        self.open_button.clicked.connect(self.openCam)
        button_layout.addWidget(self.open_button)
        self.test_button = QPushButton('test cnn')
        button_layout.addWidget(self.test_button)

        layout.addLayout(button_layout, 5, 0)
        layout.setAlignment(button_layout, QtCore.Qt.AlignTop)
        layout.setRowStretch(4, 1)

        self.setLayout(layout)

    def openCam(self):
        dialog=CameraViewDialog(self)
        dialog.show()

    def chancheType(self, index):
        current_value = self.type_box.currentText()
        if current_value=="web":
            self.container_widget.show()
            self.Camera_container_widget.hide()
        else:
            self.container_widget.hide()
            self.Camera_container_widget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CameraWidget()
    ex.show()
    sys.exit(app.exec_())