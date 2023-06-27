from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap

class MyDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(MyDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("My Dialog")

        # Create layout
        layout = QtWidgets.QHBoxLayout()

        # Add image view
        self.image_label = QtWidgets.QLabel()
        layout.addWidget(self.image_label)

        # Add inputs
        input_layout = QtWidgets.QVBoxLayout()
        self.text_input = QtWidgets.QLineEdit()
        input_layout.addWidget(self.text_input)
        self.file_input = QtWidgets.QPushButton("Select File")
        self.file_input.clicked.connect(self.select_file)
        input_layout.addWidget(self.file_input)
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

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dialog = MyDialog()
    dialog.show()
    app.exec_()
