import os
from PyQt5 import QtWidgets, QtCore

class TabEditor(QtWidgets.QLineEdit):
    def __init__(self, index, parent=None, widget=None):
        super().__init__(parent)
        self.index = index
        self.parent = parent
        self.widget=widget


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
        project_folder=self.parent.parent.project_folder
        neuralnetFile=self.widget.neuralnetFile
        print(project_folder)
        print(neuralnetFile)
        for file in (project_folder, neuralnetFile):
            if not os.path.exists(file):
                raise FileNotFoundError(f"{file}: no such file or dictionary")
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            # Discard changes and hide the editor
            self.hide()
        else:
            super().keyPressEvent(event)

class MyTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent
        self.editor = None

    def setCallback(self, callback):
        self.callback=callback

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            index = self.tabBar().tabAt(event.pos())
            if index != -1:
                # Create and show the editor
                if self.editor is not None:
                    self.editor.deleteLater()
                widget=self.widget(index)
                self.editor = TabEditor(index, self,widget)
                self.editor.show()
                self.editor.setFocus()
            elif self.editor:
                self.editor.hide()
        else:
            if self.editor:
                self.editor.hide()
                    
        super().mousePressEvent(event)

if __name__=="__main__":
    from neuralNetEditor import NeuralNetEditor
else:
    from .neuralNetEditor import NeuralNetEditor

class NeuralNetTabView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Create the tab widget
        self.tab_widget = MyTabWidget(self)
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
        tab_name = f'Neural Net {self.tab_widget.count()+1}'
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

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = NeuralNetTabView()
    window.show()
    app.exec_()
