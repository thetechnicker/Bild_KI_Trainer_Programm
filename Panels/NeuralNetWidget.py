import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit

class FileEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 500);
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabWidget = QTabWidget()
        layout.addWidget(self.tabWidget)

    def add_view(self, filename):
        textEdit = QTextEdit()
        with open(filename, 'r') as file:
            textEdit.setPlainText(file.read())
        self.tabWidget.addTab(textEdit, filename)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileEditor()
    window.add_view('./test.json')
    window.add_view('./test.json')
    window.add_view('./test.json')
    window.add_view('./test.json')
    window.add_view('./test.json')
    window.show()
    app.exec_()