import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRect
"asdfih noiöansc vö msfnöoib önadf"
class TabEditor(QtWidgets.QLineEdit):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.parent = parent

        # Set the initial text and geometry of the editor
        self.setText(parent.tabText(index))
        self.setGeometry(self.getEditorRect())

        # Connect signals
        self.editingFinished.connect(self.finishEditing)

    def getEditorRect(self):
        # Get the rectangle of the tab at the given index
        rect = self.parent.tabBar().tabRect(self.index)
        # Map the rectangle to the coordinates of the tab widget
        rect.moveTopLeft(self.parent.tabBar().mapTo(self.parent, rect.topLeft()))
        return rect

    def finishEditing(self):
        # Set the new text of the tab and hide the editor
        self.parent.setTabText(self.index, self.text())
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # Discard changes and hide the editor
            self.hide()
        else:
            super().keyPressEvent(event)

        
class MyTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = None

    def mousePressEvent(self, event):
        #print(f"event: {event}")
        if event.button() == Qt.RightButton:
            #print("debug")
            index = self.tabBar().tabAt(event.pos())
            if index != -1:
                # Create and show the editor
                if self.editor is not None:
                    self.editor.deleteLater()
                self.editor = TabEditor(index, self)
                self.editor.show()
                self.editor.setFocus()
            elif self.editor:
                self.editor.hide()
        else:
            if self.editor:
                self.editor.hide()
                    
        super().mousePressEvent(event)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a tab widget
        tab_widget = MyTabWidget()
        self.setCentralWidget(tab_widget)

        # Add some tabs
        tab_widget.addTab(QtWidgets.QLabel('Tab 1 Content'), 'Tab 1')
        tab_widget.addTab(QtWidgets.QLabel('Tab 2 Content'), 'Tab 2')

if "main" in __name__:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
