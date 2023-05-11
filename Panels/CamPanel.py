from PyQt5 import QtWidgets, QtGui

class CamPanel(QtWidgets.QWidget):
    def __init__(self, default_values=None):
        super().__init__()

        layout = QtWidgets.QVBoxLayout(self)

        labels = ['x1', 'y1', 'x2', 'y2', 'resize factor', 'Endsize']
        for i, text in enumerate(labels):
            sub_layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f'{text}:')
            sub_layout.addWidget(label)
            entry = QtWidgets.QLineEdit()
            entry.setValidator(QtGui.QIntValidator())
            if default_values:
                entry.setText(str(default_values[i]))
            sub_layout.addWidget(entry)
            layout.addLayout(sub_layout)

        button_layout = QtWidgets.QHBoxLayout()
        buttons = ['Start', 'Stop', 'Save']
        for text in buttons:
            button = QtWidgets.QPushButton(text)
            button_layout.addWidget(button)

        layout.addLayout(button_layout)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    CamPanel = CamPanel([0, 0, 640, 480, 1, 100])
    CamPanel.show()
    app.exec_()