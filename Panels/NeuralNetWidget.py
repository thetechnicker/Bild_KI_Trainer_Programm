import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PyQt5.QtCore import QRegExp

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        keywordFormat1 = QTextCharFormat()
        keywordFormat1.setFontWeight(QFont.Bold)
        keywordFormat1.setForeground(QColor("blue"))

        keywordPatterns = ["\\band\\b",
                           "\\bas\\b",
                           "\\bassert\\b",
                           "\\bbreak\\b",
                           "\\bclass\\b",
                           "\\bcontinue\\b",
                           "\\bdef\\b",
                           "\\bdel\\b",
                           "\\belif\\b",
                           "\\belse\\b",
                           "\\bexcept\\b",
                           "\\bFalse\\b",
                           "\\bfinally\\b",
                           "\\bfor\\b",
                           "\\bfrom\\b",
                           "\\bglobal\\b",
                           "\\bif\\b",
                           "\\bin\\b",
                           "\\bis\\b",
                           "\\bimport\\b",
                           "\\bin\\b",
                           "\\bis\\b",
                           "\\blambda\\b",
                           "\\bNone\\b",
                           "\\bnonlocal\\b",
                           "\\bnot\\b",
                           "\\bor\\b",
                           "\\bpass\\b",
                           "\\braise\\b",
                           "\\breturn\\b",
                           "\\bTrue\\b",
                           "\\btry\\b",
                           "\\bwhile\\b",
                           "\\bwith\\b",
                           "\\byield\\b"]

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
        layout.addWidget(self.tabWidget)

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