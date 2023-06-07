import os
import sys
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor, QIcon
from PyQt5.QtCore import QRegExp
if __name__ == "__main__":
    from cnn import *
else:
    from .cnn import *

projectFolder=None

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
                           "\\bDense\\b",
                           "\\badd\\b",
                           "\\bpadding\\b",
                           "\\bactivation\\b",
                           "\\bpool_size\\b"]

        rules = [(QRegExp(pattern), keywordFormat1) for pattern in keywordPatterns]

        green_format = QTextCharFormat()
        green_format.setForeground(QColor("green"))

        function_pattern = QRegExp("\\b(def|class)\\s+(\\w+)\\s*\\(")
        rules.append((function_pattern, keywordFormat1))

        string_pattern = QRegExp('"(?:[^"\\\\]|\\\\.)*"')
        rules.append((string_pattern, green_format))

        string_pattern = QRegExp("'(?:[^'\\\\]|\\\\.)*'")
        rules.append((string_pattern, green_format))
        

        string_pattern = QRegExp('"""(?:[^"\\\\]|\\\\.)*"""')
        rules.append((string_pattern, green_format))

        string_pattern = QRegExp("'''(?:[^'\\\\]|\\\\.)''*'")
        rules.append((string_pattern, green_format))

        self.highlightingRules = rules
        self.green_format=green_format
        self.ismultiLine=False


    def highlightBlock(self, text):
        #print(f"test: {text}")
        if "'''" in text or '"""' in text:
            if not self.ismultiLine:
                self.ismultiLine=True
                self.setFormat(0, len(text), self.green_format)
            else:
                self.ismultiLine=False
                self.setFormat(0, len(text), self.green_format)
               
        elif self.ismultiLine:
            self.setFormat(0, len(text), self.green_format)

        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class MyTabWidget(QtWidgets.QTabWidget):
    def mousePressEvent(self, event):
        global projectFolder
        if event.button() == QtCore.Qt.RightButton:
            try:
                index = self.tabBar().tabAt(event.pos())
                print(f'Left-clicked on tab: {index}')
                projectName,_=os.path.split(projectFolder)
                oldName=self.tabText(index)
                name, ok = QtWidgets.QInputDialog.getText(self, "Name",'', text=oldName)
                if ok:
                    if not name==oldName:
                        self.setTabText(index, name)
                        if not ".pynns" in name:
                            name+=".pynns"
                        oldfile=os.path.join(projectName,"cnn",oldName)
                        file=os.path.join(projectName,"cnn",name)
                        print("",oldfile, file, sep="\t\n")
                        #os.rename(oldfile, file)
            except Exception as e:
                print(f"error: {e}")
                    
        super().mousePressEvent(event)

class FileEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 500);
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabWidget = MyTabWidget()
        button = QtWidgets.QPushButton()
        button.clicked.connect(self.runCode)
        # Set the button icon to a green play image
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
        button.setIcon(icon)

        layout.addWidget(button)
        layout.setAlignment(button, QtCore.Qt.AlignRight)
        layout.addWidget(self.tabWidget)
        self.ScriptThread=None

    def setProjectFolder(self, ProjectFolder):
        global projectFolder
        projectFolder=ProjectFolder

    def runCode(self):
        global projectFolder
        try:
            index = self.tabWidget.currentIndex()
            tab_text = self.tabWidget.widget(index).toPlainText()
            if projectFolder:
                projectName=os.path.basename(projectFolder)
                print(projectName)
                db=os.path.join(projectFolder,projectName,".db")
                print(db)
                #data=loadData(db)
            #else:
                data=None
            if not self.ScriptThread:
                self.ScriptThread= threading.Thread(target=self.run_script,args=(tab_text,self.on_thread_finished, data))
                self.ScriptThread.setDaemon(True)
                self.ScriptThread.start()
            else:
                pass
        except Exception as e:
            print(f"error: {e}")


    def run_script(self, text, calback, data):
        #createModel(text,data)
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
    window = FileEditor()
    window.add_view('./neuralNet.pynns')
    window.setProjectFolder("C:/Users/lucas/Documents/Python/GUI/Bild_KI_Trainer_Programm/test.db")
    window.show()
    app.exec_()