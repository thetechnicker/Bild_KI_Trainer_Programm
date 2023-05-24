import os
import sys
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor, QIcon
from PyQt5.QtCore import QRegExp


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        keywordFormat1 = QTextCharFormat()
        keywordFormat1.setFontWeight(QFont.Bold)
        keywordFormat1.setForeground(QColor("blue"))

        keywordPatterns = ["\\bSequential\\b",
                           "\\bConv2D\\b",
                           "\\bMaxPooling2D\\b",
                           "\\bFlatten\\b",
                           "\\bDense\\b"]

        rules = [(QRegExp(pattern), keywordFormat1) for pattern in keywordPatterns]

        green_format = QTextCharFormat()
        green_format.setForeground(QColor("green"))

        function_pattern = QRegExp("\\b(def|class)\\s+(\\w+)\\s*\\(")
        rules.append((function_pattern, keywordFormat1))

        string_pattern = QRegExp('"(?:[^"\\\\]|\\\\.)*"')
        rules.append((string_pattern, green_format))

        self.highlightingRules = rules

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class FileEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 500);
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabWidget = QTabWidget()
        button = QtWidgets.QPushButton()
        button.clicked.connect(self.runCode)
        # Set the button icon to a green play image
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
        button.setIcon(icon)

        layout.addWidget(button)
        layout.setAlignment(button, QtCore.Qt.AlignRight)
        layout.addWidget(self.tabWidget)
        self.ScriptThread=None
    
    def runCode(self):
        index = self.tabWidget.currentIndex()
        tab_text = self.tabWidget.widget(index).toPlainText()
        if not self.ScriptThread:
            self.ScriptThread= threading.Thread(target=self.run_script,args=(tab_text,self.on_thread_finished))
            self.ScriptThread.setDaemon(True)
            self.ScriptThread.start()
        else:
            pass

    def run_script(self, text, calback):
        exec(text)
        calback()

    def on_thread_finished(self):
        self.ScriptThread = None


    def add_view(self, filename):
        textEdit = QTextEdit()
        font = QFont()
        font.setPointSize(9)
        textEdit.setFont(font)

        spaces_per_tab = 4

        # Calculate the width of a single space character in the current font
        font_metrics = textEdit.fontMetrics()
        space_width = font_metrics.horizontalAdvance(' ')

        # Set the tab stop distance to be equivalent to the desired number of spaces
        textEdit.setTabStopDistance(space_width * spaces_per_tab)

        highlighter = PythonHighlighter(textEdit.document())
        highlighter.setParent(textEdit)
        with open(filename, 'r') as file:
            textEdit.setPlainText(file.read())
        textEdit.textChanged.connect(lambda: self.update_highlighting(textEdit))
        self.tabWidget.addTab(textEdit, os.path.basename(filename))

    def save(self, path):
        for i in range(self.tabWidget.count()):
                tab_text = self.tabWidget.widget(i).toPlainText()
                tab_name = self.tabWidget.tabText(i)
                with open(os.path.join(path, tab_name), 'w') as file:
                    file.write(tab_text)

    def update_highlighting(self, textEdit):
            highlighter = textEdit.document().findChild(PythonHighlighter)
            if highlighter:
                highlighter.rehighlight()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileEditor()
    window.add_view('./cnn.py')
    window.show()
    app.exec_()