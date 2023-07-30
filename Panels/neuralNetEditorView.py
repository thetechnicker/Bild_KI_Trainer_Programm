from PyQt5 import QtWidgets

if __name__=="__main__":
    from neuralNetEditor import NeuralNetEditor
else:
    from .neuralNetEditor import NeuralNetEditor

class NeuralNetTabView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Create the tab widget
        self.tab_widget = QtWidgets.QTabWidget()
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


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = NeuralNetTabView()
    window.show()
    app.exec_()
