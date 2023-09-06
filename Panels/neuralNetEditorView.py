import os
import sqlite3
from PyQt5 import QtWidgets, QtCore


class TabEditor(QtWidgets.QLineEdit):
    def __init__(self, index, parent=None, treeview=None, widget= None):
        super().__init__(parent)
        self.index = index
        self.parent = parent
        self.widget=widget
        self.treeview=treeview


        # Set the initial text and geometry of the editor
        self.oldText=parent.tabText(index)
        self.setText(self.oldText)
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
        text=self.text().replace(" ", "_")
        self.parent.setTabText(self.index, text)
        neuralnetFile=self.widget.neuralnetFile
        print(neuralnetFile)
        if not os.path.exists(neuralnetFile):
            raise FileNotFoundError(f"{neuralnetFile}: no such file or dictionary")
        fileName=list(os.path.split(neuralnetFile))
        fileName[-1]=f"{text}.json"
        newFile=os.path.join(fileName[0],fileName[1])
        print(fileName[0], fileName[1],neuralnetFile,newFile, sep="\n")
        os.rename(neuralnetFile,newFile)
        
        self.treeview.rename("neuralNet",self.oldText, text)
        self.hide()
        try:
            os.remove(neuralnetFile)
        finally:
            print("old file did had to been removed exta")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            # Discard changes and hide the editor
            self.hide()
        else:
            super().keyPressEvent(event)

class MyTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None, treeview=None):
        super().__init__(parent)
        self.parent=parent
        self.editor = None
        self.treeview=treeview
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)

    def setCallback(self, callback):
        self.callback=callback

    def closeTab(self, index):
        self.removeTab(index)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            index = self.tabBar().tabAt(event.pos())
            if index != -1:
                # Create and show the editor
                if self.editor is not None:
                    self.editor.deleteLater()
                widget=self.widget(index)
                self.editor = TabEditor(index, self,self.treeview, widget)
                self.editor.show()
                self.editor.setFocus()
            elif self.editor:
                self.editor.hide()
        elif event.button() == QtCore.Qt.MiddleButton:
            index = self.tabBar().tabAt(event.pos())
            if index != -1:
                self.closeTab(index)
                    
        super().mousePressEvent(event)


if __name__=="__main__":
    from neuralNetEditor import NeuralNetEditor
else:
    from .neuralNetEditor import NeuralNetEditor

class NeuralNetTabView(QtWidgets.QWidget):
    def __init__(self, treeview):
        super().__init__()

        # Create the tab widget
        self.tab_widget = MyTabWidget(self,treeview)
        self.project_folder = None

        # Lay out the UI elements
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tab_widget)

    def set_project_folder(self, project_folder):
        # Set the project folder for each tab
        self.project_folder = project_folder
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            editor.projectFolder = project_folder

    def add_tab(self, neuralnet_file=None):
        # Create a new neural net editor
        editor = NeuralNetEditor(projectFolder=self.project_folder, neuralnetFile=neuralnet_file)

        # Add the editor as a new tab
        tab_name = f'{os.path.basename(neuralnet_file)}'.replace(".json", "")
        self.tab_widget.addTab(editor, tab_name)

    def save_all(self):
        # Save the state of each tab
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            editor.on_save()

    def cnnImport(self, neuralnet):
        raise NotImplementedError()
    
    def cnnExport(self, neuralnet):
        raise NotImplementedError()

    def getCurrentNeuralnet(self):
        current_index = self.tab_widget.currentIndex()
        current_tab_name = self.tab_widget.tabText(current_index)
        return current_tab_name

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = NeuralNetTabView()
    window.show()
    app.exec_()
