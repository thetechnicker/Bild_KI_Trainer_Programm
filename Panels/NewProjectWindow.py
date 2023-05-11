from PyQt5 import QtWidgets

class ProjectDialog(QtWidgets.QDialog):
    def __init__(self, initial_folder='', parent=None):
        super().__init__(parent)

        # Create the input fields
        self.name_input = QtWidgets.QLineEdit()
        self.folder_input = QtWidgets.QLineEdit(initial_folder)

        # Create the folder button
        folder_button = QtWidgets.QPushButton()
        folder_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
        folder_button.clicked.connect(self.select_folder)

        # Create the buttons
        ok_button = QtWidgets.QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)

        # Create the layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('Project Name:'))
        layout.addWidget(self.name_input)
        layout.addWidget(QtWidgets.QLabel('Project Folder:'))
        folder_layout = QtWidgets.QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(folder_button)
        layout.addLayout(folder_layout)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_inputs(self):
        return self.name_input.text(), self.folder_input.text()

    def select_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_name:
            self.folder_input.setText(folder_name)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    initial_folder = '/path/to/initial/folder'
    dialog = ProjectDialog(initial_folder)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        project_name, project_folder = dialog.get_inputs()
        print(f'Creating project "{project_name}" in folder "{project_folder}"')