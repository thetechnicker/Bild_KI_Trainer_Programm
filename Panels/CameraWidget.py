from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
import sys

class CameraWidget(QWidget):
    def __init__(self, *data, **data2):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Kamera'))
        type_layout=QHBoxLayout()
        type_layout.addWidget(QLabel('type:'))
        self.type_box = QComboBox()
        self.type_box.addItems(['web', 'integratet'])
        
        type_layout.addWidget(self.type_box)

        layout.addLayout(type_layout)

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

        layout.addLayout(self.web_layout)

        layout.addWidget(QLabel('size:'))
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel('Height:'))
        self.x_size_line = QLineEdit()
        size_layout.addWidget(self.x_size_line)
        size_layout.addWidget(QLabel('Width:'))
        self.y_size_line = QLineEdit()
        size_layout.addWidget(self.y_size_line)
        layout.addLayout(size_layout)

        layout.addWidget(QLabel('used part:'))
        used_part_layout1 = QVBoxLayout()
        used_part_layout1.addWidget(QLabel('X:'))
        self.x_used_line = QLineEdit()
        used_part_layout1.addWidget(self.x_used_line)
        used_part_layout1.addWidget(QLabel('Y:'))
        self.y_used_line = QLineEdit()
        used_part_layout1.addWidget(self.y_used_line)
        
        used_part_layout2 = QVBoxLayout()
        used_part_layout2.addWidget(QLabel('Height:'))
        self.h_used_line = QLineEdit()
        used_part_layout2.addWidget(self.h_used_line)
        used_part_layout2.addWidget(QLabel('Width:'))
        self.w_used_line = QLineEdit()
        used_part_layout2.addWidget(self.w_used_line)

        used_part_layout=QHBoxLayout()
        used_part_layout.addLayout(used_part_layout1)
        used_part_layout.addLayout(used_part_layout2)
        layout.addLayout(used_part_layout)

        button_layout = QHBoxLayout()
        self.open_button = QPushButton('open')
        button_layout.addWidget(self.open_button)
        self.test_button = QPushButton('test cnn')
        button_layout.addWidget(self.test_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CameraWidget()
    ex.show()
    sys.exit(app.exec_())
