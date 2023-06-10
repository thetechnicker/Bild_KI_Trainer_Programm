from PyQt5 import QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileSystemModel

class ProjectDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the window title
        self.setWindowTitle('Open Project')

        # Create the project name label and line edit
        self.project_name_label = QtWidgets.QLabel('Project Name:')
        self.project_name_edit = QtWidgets.QLineEdit()

        # Create the project list label and tree view
        self.project_list_label = QtWidgets.QLabel('Existing Projects:')
        self.project_list_view = QtWidgets.QTreeView()
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        self.project_list_view.setModel(self.model)
        self.project_list_view.setRootIndex(self.model.index(QDir.currentPath()))

        # Create the buttons
        self.new_button = QtWidgets.QPushButton('New')
        self.open_button = QtWidgets.QPushButton('Open')
        self.cancel_button = QtWidgets.QPushButton('Cancel')

        # Create the button layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.cancel_button)

        # Create the main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.project_name_label)
        main_layout.addWidget(self.project_name_edit)
        main_layout.addWidget(self.project_list_label)
        main_layout.addWidget(self.project_list_view)
        main_layout.addLayout(button_layout)


if __name__ == '__main__':
    # Create the application
    app = QtWidgets.QApplication([])

    # Create and show the project dialog
    dialog = ProjectDialog()
    ret=dialog.exec_()
    print(ret)
    
    # Run the main loop
    app.exec_()