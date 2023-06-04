import json
import os
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets, QtCore
import sqlite3

#from Panels.cam_panel import cam_panel
from Panels.CameraSettingWidget import CameraWidget as CamPanel
from Panels.TreeviewPanel import TreeviewPanel
from Panels.NewProjectWindow import ProjectDialog
from Panels.settingDialog import settingDialog
from Panels.NeuralNetWidget import FileEditor as NeuralNetEditor
from Panels.consolenWidget import PythonConsole

import subprocess

try:
    result = subprocess.run(['python', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    version = result.stdout.decode('utf-8').strip()
    if not version:
        version = result.stderr.decode('utf-8').strip()
    #print(f'Python is installed: {version}')
except FileNotFoundError:
    #print('Python is not installed')
    app = QtWidgets.QApplication([])

    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle('Error')
    msg.setText('Python is not installed')
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()
    sys.exit()


class MainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("AI Trainer")
        self.resize(800, 600)
        self.data=data
        self.cnn_folder    =None
        self.img_folder    =None
        self.export_folder =None
        self.currentProject=None

        self.DatabaseFile=None

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

        main_layout = QtWidgets.QVBoxLayout(central_widget)
        layout = QtWidgets.QHBoxLayout()
        self.treeview = TreeviewPanel()
        self.treeview.set_callback(self.Treeview_click_event)

        self.NeuralNetEditor = NeuralNetEditor()

        cam_panel = CamPanel([0, 0, 640, 480, 1, 100])
        layout.setAlignment(cam_panel, QtCore.Qt.AlignTop)

        # Create a horizontal splitter and add the treeview and NeuralNetEditor
        h_splitter = QtWidgets.QSplitter()
        h_splitter.addWidget(self.treeview)
        h_splitter.addWidget(self.NeuralNetEditor)
        h_splitter.addWidget(cam_panel)

        # Create a vertical splitter and add the horizontal splitter and cam_panel
        v_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        v_splitter.addWidget(h_splitter)
        v_splitter.addWidget(PythonConsole())

        main_layout.addWidget(v_splitter)
        #self.openlast()

    def closeEvent(self,event):
        #self.save_projeck()
        with open("./settings.json", "w") as f:
                json.dump(data,f)
        event.accept()


    def Treeview_click_event(self, item, parent):
        print(item.text())
        if parent:
            print(parent.text())
            if parent.text()=="Neuronale Netze":
                print("test")
                path=os.path.join(self.cnn_folder,f"{item.text()}.py")
                self.NeuralNetEditor.add_view(path)

    def settings(self):
        dialog = settingDialog(data["projectFolder"], self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            project_folder = dialog.get_inputs()
            data["projectFolder"]=project_folder
            self.data["projectFolder"]=project_folder
            with open("./settings.json", "w") as f:
                json.dump(data,f)

    def new_projeck(self):
        dialog = ProjectDialog(data["projectFolder"], self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            project_name, root_folder = dialog.get_inputs()
            ##print(f'Creating project "{project_name}" in folder "{project_folder}"')
            # Create the project folder
            project_folder = os.path.join(root_folder, project_name)
            self.data["lastProject"]=project_folder
            #if True:
            try:
                os.makedirs(project_folder, exist_ok=True)

                # Create the projectname.json file
                self.DatabaseFile=os.path.join(project_folder, f'{project_name}.db')
                connection=sqlite3.connect(self.DatabaseFile)
                DataBase=connection.cursor()
                DataBase.execute('''
                    CREATE TABLE IF NOT EXISTS classes (
                        id INTEGER PRIMARY KEY,
                        name TEXT
                    )
                ''')
                DataBase.execute('''
                    CREATE TABLE IF NOT EXISTS neural_nets (
                        id INTEGER PRIMARY KEY,
                        name TEXT
                    )
                ''')
                DataBase.execute('''
                    CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY,
                        label TEXT,
                        file TEXT,
                        gx INTEGER,
                        gy INTEGER,
                        x INTEGER,
                        y INTEGER,
                        class INTEGER
                    )
                ''')

                DataBase.execute('''
                    CREATE TABLE IF NOT EXISTS Yolo (
                        id INTEGER AUTO_INCREMENT,
                        label TEXT,
                        value ,
                        PRIMARY KEY (id)
                    )
                ''')
                for k, i in {"VerticalGridCount":13, "HorizontalGridCount":13}.items():
                    DataBase.execute(
                        f"""
                        INSERT INTO Yolo (label, value) VALUES ('{k}', '{i}')
                        """
                    )

                connection.commit()

                data_db = {}
                data_db['Classes'] = [row[0] for row in connection.execute('SELECT name FROM classes')]
                data_db['Neuronale Netze'] = [row[0] for row in connection.execute('SELECT name FROM neural_nets')]
                data_db['Images'] = []
                for row in connection.execute('SELECT label, file, gx, gy, x, y, class FROM images'):
                    img_data = {
                        'label': row[0],
                        'File': row[1],
                        'Yolo': {
                            'gx': row[2],
                            'gy': row[3],
                            'x': row[4],
                            'y': row[5],
                            'Class': row[6]
                        }
                    }
                    data_db['Images'].append(img_data)

                data_db["Yolo"]=[]
                for row in connection.execute("SELECT label, value FROM Yolo"):
                    Yolo={
                        row[0]: row[1]
                    }
                    data_db["Yolo"].append(Yolo)
                print(data_db)
                connection.close()
            except Exception as e:
                print(f"Error: {e}")
            else:
                self.cnn_folder     = os.path.join(project_folder, "cnn")
                self.img_folder     = os.path.join(project_folder, "img")
                self.export_folder  = os.path.join(project_folder, "exports")
                self.currentProject = project_folder
                os.mkdir(self.cnn_folder)
                os.mkdir(self.img_folder)
                os.mkdir(self.export_folder)
                self.treeview.setDB(self.DatabaseFile)
                self.setWindowTitle(f"AI Trainer\t\t{self.currentProject}")

    def open_projeck(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Project',data["projectFolder"])
        self.data["lastProject"]=folder
        if folder:
            folder_name = os.path.basename(folder)
            file_name = f'{folder_name}.db'
            self.DatabaseFile = os.path.join(folder, file_name)
            if os.path.exists(self.DatabaseFile):
                try:                
                    connection=sqlite3.connect(self.DatabaseFile)
                    connection.close()
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    self.cnn_folder     = os.path.join(folder, "cnn")
                    self.img_folder     = os.path.join(folder, "img")
                    self.export_folder  = os.path.join(folder, "exports")
                    self.currentProject = folder
                    self.treeview.setDB(self.DatabaseFile)
                    self.setWindowTitle(f"AI Trainer\t\t{self.currentProject}")
            else:
                print("Projectfolder has no database")
        else:
            print("error")

    def openlast(self):
        if "lastProject" in self.data:
            folder_name = os.path.basename(self.data["lastProject"])
            file_name = f'{folder_name}.db'
            file_path = os.path.join(self.data["lastProject"], file_name)
            folder_name = os.path.basename(file_path)
            file_name = f'{folder_name}.db'
            self.DatabaseFile = os.path.join(folder_name, file_name)
            if os.path.exists(self.DatabaseFile):
                try:                
                    connection=sqlite3.connect(self.DatabaseFile)
                    connection.close()
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    self.cnn_folder     = os.path.join(folder_name, "cnn")
                    self.img_folder     = os.path.join(folder_name, "img")
                    self.export_folder  = os.path.join(folder_name, "exports")
                    self.currentProject = folder_name
                    self.treeview.setDB(self.DatabaseFile)
                    self.setWindowTitle(f"AI Trainer\t\t{self.currentProject}")
            else:
                print("Projectfolder has no database")



    def save_projeck(self):
        try:
            self.treeview.saveDb()
            #self.NeuralNetEditor.save(self.cnn_folder)
        except Exception as e:
            print(f"error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("./settings.json") as f:
        data=json.load(f)
    if not "projectFolder" in data or not os.path.exists(data["projectFolder"]):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Folder')
        data["projectFolder"]=folder_name
        with open("./settings.json", "w") as f:
                json.dump(data,f)

    window = MainWindow(data)
    window.show()
    app.exec_()
