import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QLineEdit, QPushButton

class ExampleDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.setMinimumSize(QtCore.QSize(640, 480))
        self.setWindowTitle("PyQt Webcam Viewer")

        gridLayout = QGridLayout(self)

        # Add webcam view
        # TODO: Add code to display webcam view

        # Add rectangle with grid lines
        # TODO: Add code to display rectangle with grid lines

        # Add input fields for x and y coordinates of rectangle
        self.xInput = QLineEdit(self)
        self.yInput = QLineEdit(self)
        gridLayout.addWidget(QLabel("X:"), 0, 0)
        gridLayout.addWidget(self.xInput, 0, 1)
        gridLayout.addWidget(QLabel("Y:"), 1, 0)
        gridLayout.addWidget(self.yInput, 1, 1)

        # Add save and cancel buttons
        saveButton = QPushButton('Save', self)
        cancelButton = QPushButton('Cancel', self)
        gridLayout.addWidget(saveButton, 2, 0)
        gridLayout.addWidget(cancelButton, 2, 1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = ExampleDialog()
    dialog.show()
    sys.exit(app.exec_())