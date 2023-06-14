import json
from PyQt5 import QtWidgets

class settingDialog(QtWidgets.QDialog):
    def __init__(self, folder_name="", parent=None):
        super().__init__(parent)
        # Create the input field
        self.folder_input = QtWidgets.QLineEdit(folder_name)

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
        layout.addWidget(QtWidgets.QLabel('Project Directory:'))
        folder_layout = QtWidgets.QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(folder_button)
        layout.addLayout(folder_layout)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_inputs(self):
        return self.folder_input.text()

    def select_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_name:
            self.folder_input.setText(folder_name)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    
    with open("./settings.json") as f:
        data=json.load(f)
        folder_name=data["projectFolder"]

    dialog = settingDialog(folder_name)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        project_folder = dialog.get_inputs()
        print(f'Creating project in folder "{project_folder}"')