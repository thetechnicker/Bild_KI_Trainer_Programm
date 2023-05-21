from PyQt5 import QtCore, QtWidgets, QtGui
import sys

class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

    def flush(self):
        # Empty implementation of the flush method
        pass
    
class PythonConsole(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PythonConsole, self).__init__(parent)

        # Set up the user interface
        self.output = QtWidgets.QPlainTextEdit()
        self.input = QtWidgets.QLineEdit()
        self.input.returnPressed.connect(self.handleInput)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.output)
        layout.addWidget(self.input)

        # Set up the output stream
        sys.stdout = Stream(newText=self.onUpdateText)

    def onUpdateText(self, text):
        cursor = self.output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def handleInput(self):
        data = self.input.text()
        if data == 'clear':
            self.output.clear()
            self.input.clear()
            return
        print(f'>>> {data}')
        try:
            result = eval(data)
            if result:
                print(result)
        except Exception as e:
            print(e)
        self.input.clear()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = PythonConsole()
    widget.show()
    sys.exit(app.exec_())