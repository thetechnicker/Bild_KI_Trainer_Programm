import json
import os
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets, QtCore

#from Panels.cam_panel import cam_panel
from Panels.CameraSettingWidget import CameraWidget as CamPanel
from Panels.TreeviewPanel import TreeviewPanel
from Panels.NewProjectWindow import ProjectDialog
from Panels.settingDialog import settingDialog
from Panels.NeuralNetWidget import FileEditor as NeuralNetEditor




class MainWindow(QMainWindow):
    def __init__(self, projekt_folder, data):
        super().__init__()
        self.projekt_folder=projekt_folder
        self.cnn_folder=None
        self.setWindowTitle("AI Trainer")
        self.resize(800, 600)
        self.currentProjetk=None
        self.data=data

        # Create the menu bar
        menubar = self.menuBar()
        # Create the file menu and add actions
        file_menu = menubar.addMenu('File')

        new_action = QtWidgets.QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_projeck)

        open_action = QtWidgets.QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_projeck)

        save_action = QtWidgets.QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_projeck)

        settings = QtWidgets.QAction('Settings', self)
        settings.setShortcut('Ctrl+,')
        settings.triggered.connect(self.settings)

        close_action = QtWidgets.QAction('Close', self)
        close_action.setShortcut('Ctrl+Q')
        close_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(settings)
        file_menu.addSeparator()
        file_menu.addAction(close_action)

        # Create the options menu
        options_menu = menubar.addMenu('Options')

        # Create the window menu and add actions
        window_menu = menubar.addMenu('Window')
        trainingsdaten_action = QtWidgets.QAction('Trainingsdaten', self, checkable=True)
        window_menu.addAction(trainingsdaten_action)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QHBoxLayout(central_widget)
        self.treeview=TreeviewPanel()
        self.treeview.set_callback(self.Treeview_click_event)

        layout.addWidget(self.treeview)

        self.NeuralNetEditor=NeuralNetEditor()
        layout.addWidget(self.NeuralNetEditor)
    
        cam_panel = CamPanel([0, 0, 640, 480, 1, 100])
        layout.addWidget(cam_panel)
        layout.setAlignment(cam_panel, QtCore.Qt.AlignTop)
        self.openlast()
        

    def closeEvent(self,event):
        self.save_projeck()
        with open("./settings.json", "w") as f:
                json.dump(data,f)
        event.accept()

    
    def Treeview_click_event(self, item, parent):
        #print(item.text())
        if parent:
            #print(parent.text())
            if parent.text()=="Neuronale Netze":
                #print("test")
                path=os.path.join(self.cnn_folder,f"{item.text()}.py")
                self.NeuralNetEditor.add_view(path)

    def settings(self):
        dialog = settingDialog(self.projekt_folder, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            project_folder = dialog.get_inputs()
            self.projekt_folder=project_folder
            self.data["projectFolder"]=project_folder
            with open("./settings.json", "w") as f:
                json.dump(data,f)

    def new_projeck(self):
        dialog = ProjectDialog(self.projekt_folder, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            project_name, root_folder = dialog.get_inputs()
            ##print(f'Creating project "{project_name}" in folder "{project_folder}"')
            # Create the project folder
            project_folder = os.path.join(root_folder, project_name)
            self.data["lastProject"]=project_folder
            
            os.makedirs(project_folder, exist_ok=True)

            # Create the projectname.json file
            jsonfile=os.path.join(project_folder, f'{project_name}.json')
            open(jsonfile, 'w').close()

            # Create the traindata, cnn, and export folders
            traindata_folder = os.path.join(project_folder, 'traindata')
            os.makedirs(traindata_folder, exist_ok=True)
            self.cnn_folder = os.path.join(project_folder, 'cnn')
            os.makedirs(self.cnn_folder, exist_ok=True)
            export_folder = os.path.join(project_folder, 'export')
            os.makedirs(export_folder, exist_ok=True)
            self.treeview.setJson(jsonfile)

    def open_projeck(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Project',self.projekt_folder)
        self.data["lastProject"]=folder
        if folder:
            folder_name = os.path.basename(folder)
            file_name = f'{folder_name}.json'
            file_path = os.path.join(folder, file_name)
            if os.path.exists(file_path):
                self.treeview.setJson(file_path)
            
    def openlast(self):
        if "lastProject" in self.data:
            folder_name = os.path.basename(self.data["lastProject"])
            file_name = f'{folder_name}.json'
            file_path = os.path.join(self.data["lastProject"], file_name)
            self.cnn_folder=os.path.join(self.data["lastProject"],"cnn")
            if os.path.exists(file_path):
                self.treeview.setJson(file_path)

    def save_projeck(self):
        self.treeview.saveJson()
        self.NeuralNetEditor.save(self.cnn_folder)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("./settings.json") as f:
        data=json.load(f)
    if not "projectFolder" in data or not os.path.exists(data["projectFolder"]):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Folder')
        data["projectFolder"]=folder_name
        with open("./settings.json", "w") as f:
                json.dump(data,f)
    else:
        folder_name=data["projectFolder"]


    window = MainWindow(folder_name, data)
    window.show()
    app.exec_()

#FileEditor
