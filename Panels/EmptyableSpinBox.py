from PyQt5.QtWidgets import QApplication, QSpinBox, QVBoxLayout, QDialog

class EmptyableSpinBox(QSpinBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.setRange(0, 100)  # Set the range of the spin box
        self.clear()  # Clear the spin box

    def textFromValue(self, value):
        if value == 0:
            return ''  # Return an empty string when the value is 0
        else:
            return super().textFromValue(value)

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.spin_box1 = EmptyableSpinBox()
        self.spin_box2 = EmptyableSpinBox()
        layout.addWidget(self.spin_box1)
        layout.addWidget(self.spin_box2)
        self.setLayout(layout)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = InputDialog()
    dialog.show()
    sys.exit(app.exec_())
