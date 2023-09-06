from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from Panels.overlay import Overlay


class ImageEditor(QtWidgets.QDialog):
    def __init__(self, image:str=None):
        super().__init__()
        self.setWindowTitle("My Dialog")

        # Create layout
        layout = QtWidgets.QHBoxLayout()

        # Add image view
        self.image_label = QtWidgets.QLabel()
        layout.addWidget(self.image_label)
        self.overlay = Overlay(self.image_label)

        # Add inputs
        input_layout = QtWidgets.QVBoxLayout()
        self.text_input = QtWidgets.QLineEdit()
        input_layout.addWidget(self.text_input)

        self.file_input = QtWidgets.QLineEdit()
        file_button = QtWidgets.QPushButton()
        file_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
        file_button.clicked.connect(self.select_file)
        file_layout = QtWidgets.QHBoxLayout()

        file_layout.addWidget(self.file_input)
        file_layout.addWidget(file_button)
        # Create OK and Cancel buttons
        self.ok_button = QtWidgets.QPushButton('OK')
        self.cancel_button = QtWidgets.QPushButton('Cancel')

        # Connect the buttons to their respective slots
        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button.clicked.connect(self.on_cancel)

        # Add the buttons to the layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)


        input_layout.addLayout(file_layout)
        input_layout.addLayout(button_layout)

        self.int_inputs = []
        for i in range(5):
            int_input = QtWidgets.QSpinBox()
            self.int_inputs.append(int_input)
            input_layout.addWidget(int_input)
        layout.addLayout(input_layout)

        # Set layout
        self.setLayout(layout)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_name:
            pixmap = QPixmap(file_name)
            self.image_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        x, y, w, h =self.getDimension() 
        #print(x,y, h, w, width, height, scale)
        self.overlay.update_grid(x=int(x),y=int(y),width=int(w),height=int(h))
        self.overlay.resize(self.image_label.size())
    
    def getDimension(self):
        size=self.image_label.size()
        FW=16
        FH=9
        width = size.width()
        height = size.height()
        width_scale = width / FW
        height_scale = height / FH
        scale = min(width_scale, height_scale)
        w=(FW*scale)#-self.offsetX
        h=(FH*scale)#-self.offsetY
        x = ((width - w) // 2) #+self.offsetX
        y = ((height - h) // 2)#+self.offsetY
        return (x, y, w, h)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dialog = ImageEditor()
    dialog.show()
    app.exec_()
