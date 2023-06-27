import os
import sqlite3
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

class EditableStandardItem(QtGui.QStandardItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def is_folder(self):
        # Check if the second column contains the string 'folder'
        if 'folder' in self.model().item(self.row(), 1).text():
            return True
        return False

    def is_val(self):
        if 'val' in self.model().item(self.row(), 1).text():
            return True
        return False
    
    def is_non(self):
        # Check if the second column contains the string 'non'
        if 'non' in self.model().item(self.row(), 1).text():
            return True
        return False

    def is_cnn(self):
        # Check if the second column contains the string 'cnn'
        if 'cnn' in self.model().item(self.row(), 1).text():
            return True
        return False

    def is_class(self):
        # Check if the second column contains the string 'class'
        if 'class' in self.model().item(self.row(), 1).text():
            return True
        return False

    def is_img(self):
        # Check if the second column contains the string 'img'
        if 'img' in self.model().item(self.row(), 1).text():
            return True
        return False

    def get_data(self):
        return [
            self.model().item(self.row(), 0).text(),
            self.model().item(self.row(), 1).text()
        ]

class AddDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        type_label = QtWidgets.QLabel("Type:")
        layout.addWidget(type_label)
        self.type_select = QtWidgets.QComboBox()
        self.type_select.addItems(["Image", "Neural Net", "Class"])
        layout.addWidget(self.type_select)

        name_label = QtWidgets.QLabel("Name:")
        layout.addWidget(name_label)
        self.name_input = QtWidgets.QLineEdit()
        layout.addWidget(self.name_input)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        item_type = self.type_select.currentText()
        item_name = self.name_input.text()
        return (item_type, item_name)

    def setSelection(self, Type:str=None)->None:
        """Set the Type and hide the Combobox"""
        self.type_select.setCurrentText(Type)

class TreeviewPanel(QtWidgets.QWidget):
    def __init__(self, file_path=None):
        super().__init__()
        
        self.file_path = file_path

        layout = QtWidgets.QVBoxLayout(self)

        self.tree_view = QtWidgets.QTreeView()
        
        self.model = QtGui.QStandardItemModel(self)
        
        self.model.setColumnCount(2)
        
        self.model.setHeaderData(0, Qt.Horizontal,"Name")
        
        self.model.setHeaderData(1, Qt.Horizontal, "Type")
        
        self.tree_view.setModel(self.model)
        
        self.tree_view.hideColumn(1)
        
        layout.addWidget(self.tree_view)
        button_layout = QtWidgets.QHBoxLayout()
        
        add_button = QtWidgets.QPushButton('Add')
        
        add_button.clicked.connect(self.add_item)
        
        button_layout.addWidget(add_button)

        remove_button = QtWidgets.QPushButton('Remove')
        
        remove_button.clicked.connect(self.remove_item)
        
        button_layout.addWidget(remove_button)
        
        layout.addLayout(button_layout)
        self.callback=None
        self.tree_view.doubleClicked.connect(self.on_double_click)
        if self.file_path and self.file_path.endswith('.db'):
            self.load_db(self.file_path)

    def on_double_click(self, index):
        item = self.model.itemFromIndex(index)
        parent=item.parent()
        if self.callback:
            self.callback(item, parent)
            
    def set_callback(self, callback):
        self.callback=callback


    def setDB(self, file):
        self.file_path=file
        self.load_db(file)

    def remove_item(self):
        selected_indexes = self.tree_view.selectedIndexes()

        if selected_indexes:
            index = selected_indexes[0]
            item = self.model.itemFromIndex(index)
            if not item.is_non() and not item.is_folder():
                self.model.removeRow(index.row(), index.parent())

    def get_item_by_name(self, name=None):
        if name==None or name=="":
            return None
        def search_children(parent):
            for row in range(parent.rowCount()):
                child = parent.child(row)
                if child.text() == name:
                    return child
                result = search_children(child)
                if result:
                    return result
            return None

        root = self.model.invisibleRootItem()
        return search_children(root)


    def add_items(self, parent, data):
        print(data)
        for key, value in data.items():
            #print(f"{key}: {value}")
            if key=="Images":
                parent_name="Images"
                self.model.appendRow([EditableStandardItem(parent_name),EditableStandardItem("folder")])
                #print(value)
                for i in value:
                    #print(i)
                    parent = self.get_item_by_name("Images")
                    name_item = EditableStandardItem(i["label"])
                    file_item = EditableStandardItem("File")
                    name_item.appendRow([file_item,EditableStandardItem("non")])
                    if "Yolo" in i:
                        yolo_item = EditableStandardItem("Yolo")
                        gx_item = EditableStandardItem("gx")
                        gy_item = EditableStandardItem("gy")
                        x_item = EditableStandardItem("x")
                        y_item = EditableStandardItem("y")
                        c_item = EditableStandardItem("Class")
                        Yolo=i["Yolo"]

                        file_item.appendRow([EditableStandardItem(i["File"]),EditableStandardItem("val")])
                        gx_item.appendRow([EditableStandardItem(str(Yolo["gx"])),EditableStandardItem("val")])
                        gy_item.appendRow([EditableStandardItem(str(Yolo["gy"])),EditableStandardItem("val")])
                        x_item.appendRow([EditableStandardItem(str(Yolo["x"])),EditableStandardItem("val")])
                        y_item.appendRow([EditableStandardItem(str(Yolo["y"])),EditableStandardItem("val")])
                        c_item.appendRow([EditableStandardItem(str(Yolo["Class"])),EditableStandardItem("val")])

                        yolo_item.appendRow([gx_item,EditableStandardItem("non")])
                        yolo_item.appendRow([gy_item,EditableStandardItem("non")])
                        yolo_item.appendRow([x_item,EditableStandardItem("non")])
                        yolo_item.appendRow([y_item,EditableStandardItem("non")])
                        yolo_item.appendRow([c_item,EditableStandardItem("non")])
                        name_item.appendRow([yolo_item,EditableStandardItem("non")])

                    parent.appendRow([name_item,EditableStandardItem("img")])
            elif key == "Neuronale Netze":
                parent_name = "Neuronale Netze"
                self.model.appendRow([EditableStandardItem(parent_name),EditableStandardItem("folder")])
                name = "cnn"
                for i in value:
                    #print(i)

                    parent = self.get_item_by_name(parent_name)

                    name_item = EditableStandardItem(i)
                    type_item = EditableStandardItem(name)

                    if parent:
                        parent.appendRow([name_item, type_item])
                    else:
                        self.model.appendRow([name_item, type_item])
            elif key == "Classes":
                parent_name = "Classes"
                self.model.appendRow([EditableStandardItem(parent_name),EditableStandardItem("folder")])
                name = "class"
                for i in value:
                    #print(i)

                    parent = self.get_item_by_name(parent_name)
    
                    name_item = EditableStandardItem(i)
                    type_item = EditableStandardItem(name)
    
                    if parent:
                        parent.appendRow([name_item, type_item])
                    else:
                        self.model.appendRow([name_item, type_item])
            elif key=="Yolo":
                parent_name="Yolo"
                self.model.appendRow([EditableStandardItem(parent_name),EditableStandardItem("folder")])
                name = "Yolo"
                for v in value:
                    k=list(v.keys())[0]
                    i=v[k]
                    parent = self.get_item_by_name(parent_name)
                    parent.appendRow([EditableStandardItem(k),EditableStandardItem("folder")])
                    parent=self.get_item_by_name(k)
    
                    name_item = EditableStandardItem(i)
                    type_item = EditableStandardItem(name)
    
                    if parent:
                        parent.appendRow([name_item, type_item])
                    else:
                        self.model.appendRow([name_item, type_item])


    def find_item(self, path_parts):
        parent_item = self.model.invisibleRootItem()
        for part in path_parts:
            for row in range(parent_item.rowCount()):
                item = parent_item.child(row)
                if item.text() == part:
                    parent_item = item
                    break
        return parent_item
    
    def get_structure(self):
        root=self.model.invisibleRootItem()
        structure={}
        for i in range(root.rowCount()):
            item=root.child(i)
            if item.text()=="Classes":
                d=[]
                if item.hasChildren():
                    for j in range(item.rowCount()):
                        d.append(item.child(i).text())
                structure["Classes"]=d
            elif item.text()=="Neuronale Netze":
                d=[]
                if item.hasChildren():
                    for j in range(item.rowCount()):
                        t=item.child(j).text()
                        #print(t)
                        d.append(t)
                structure["Neuronale Netze"]=d
            elif item.text()=="Images":
                d=[]
                if item.hasChildren():
                    for j in range(item.rowCount()):
                        item=item.child(j)
                        img_data={}
                        img_data["label"]=item.text()
                        if item.hasChildren():
                            for k in range(item.rowCount()):
                                #print(item.child(k).text())
                                if item.child(k).text()=="File":
                                    img_data["File"]=item.child(k).child(0).text()
                                elif item.child(k).text()=="Yolo":
                                    
                                    Yolo_data={}
                                    item=item.child(k)
                                    if item.hasChildren():
                                        for l in range(item.rowCount()):
                                            try:
                                                p=item.child(l).text()
                                                t=item.child(l).child(0).text()
                                                try:
                                                    Yolo_data[p]=int(t)
                                                except:
                                                    Yolo_data[p]=t
                                            except:
                                                pass
                                    img_data["Yolo"]=Yolo_data
                                else:
                                    img_data["rest"]="Error"
                        d.append(img_data)
                        
                structure["Images"]=d
            elif item.text()=="Yolo":
                data={}
                if item.hasChildren():
                    for j in range(item.rowCount()):
                        s_item=item.child(j)
                        key=s_item.text()
                        if s_item.hasChildren():
                            value=s_item.child(0).text()
                            data[key]= value

                structure["Yolo"]=data

        return structure


    def add_item(self, Ditem_type=None, file=None):
        try:
            dialog=None
            if not Ditem_type:
                dialog = AddDialog(self)
                if file:
                    dialog.setSelection("Image")

            if dialog or Ditem_type:
                item_type=None
                item_name=None
                if Ditem_type:
                    item_type=Ditem_type
                    item_name=f"New {Ditem_type}"
                elif dialog.exec_() == QtWidgets.QDialog.Accepted:
                    item_type, item_name = dialog.get_data()

                name = ""
                parent_name=""
                if item_type == "Image":
                    parent = self.get_item_by_name("Images")
                    name_item = EditableStandardItem(item_name)
                    file_item = EditableStandardItem("File")
                    yolo_item = EditableStandardItem("Yolo")
                    gx_item = EditableStandardItem("gx")
                    gy_item = EditableStandardItem("gy")
                    x_item = EditableStandardItem("x")
                    y_item = EditableStandardItem("y")
                    c_item = EditableStandardItem("Class")
                    if file:
                         file_item.appendRow([EditableStandardItem(f"{file}"),EditableStandardItem("val")])
                    else:
                         file_item.appendRow([EditableStandardItem("unknown"),EditableStandardItem("val")])
                         
                    gx_item.appendRow([EditableStandardItem("0"),EditableStandardItem("val")])
                    gy_item.appendRow([EditableStandardItem("0"),EditableStandardItem("val")])
                    x_item.appendRow([EditableStandardItem("0"),EditableStandardItem("val")])
                    y_item.appendRow([EditableStandardItem("0"),EditableStandardItem("val")])
                    c_item.appendRow([EditableStandardItem("0"),EditableStandardItem("val")])

                    yolo_item.appendRow([gx_item,EditableStandardItem("non")])
                    yolo_item.appendRow([gy_item,EditableStandardItem("non")])
                    yolo_item.appendRow([x_item,EditableStandardItem("non")])
                    yolo_item.appendRow([y_item,EditableStandardItem("non")])
                    yolo_item.appendRow([c_item,EditableStandardItem("non")])

                    name_item.appendRow([file_item,EditableStandardItem("non")])
                    name_item.appendRow([yolo_item,EditableStandardItem("non")])
                    if parent:
                        parent.appendRow([name_item,EditableStandardItem("img")])
                    else:
                        raise Exception("No  project is opend")
                elif item_type == "Neural Net":
                    parent_name = "Neuronale Netze"
                    name = "cnn"
                    print(self.file_path)
                    head, _ = os.path.split(self.file_path)
                    main_path=os.path.join(head, "cnn" )
                    if not os.path.exists(main_path):
                        os.makedirs(main_path, exist_ok=True)
                    pathname=item_name.replace(" ", "_")
                    path=os.path.join(main_path,f"{pathname}.pynns")

                    print(path)
                    main_code=f"""#{pathname}.pynns"""

                    if not __name__ =="__main__":
                        with open(path, "w") as f:
                            f.write(main_code)

                elif item_type == "Class":
                    parent_name = "Classes"
                    name = "class"

                if not item_type=="Image":
                    parent = self.get_item_by_name(parent_name)

                    name_item = EditableStandardItem(item_name)
                    type_item = EditableStandardItem(name)

                    if parent:
                        parent.appendRow([name_item, type_item])
                    else:
                        raise Exception("No  project is opend")
        except Exception as e:
            print(f"error: {e}")


    def load_db(self, filename=None):
        if not filename:
            filename=self.file_path
        # Connect to the database
        conn = sqlite3.connect(filename)
        c = conn.cursor()
    
        # Create the tables if they don't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS neural_nets (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        c.execute('''
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
        c.execute('''
            CREATE TABLE IF NOT EXISTS Yolo (
                id INTEGER AUTO_INCREMENT NOT NULL,
                label TEXT,
                value ENUM,
                PRIMARY KEY (id)
            )
        ''')
        # Load data from the database
        data = {}
        data['Classes'] = [row[0] for row in c.execute('SELECT name FROM classes')]
        data['Neuronale Netze'] = [row[0] for row in c.execute('SELECT name FROM neural_nets')]
        data['Images'] = []
        for row in c.execute('SELECT label, file, gx, gy, x, y, class FROM images'):
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
            data['Images'].append(img_data)
    
        data["Yolo"]=[]
        for row in c.execute("SELECT label, value FROM Yolo"):
            Yolo={
                row[0]: row[1]
            }
            data["Yolo"].append(Yolo)
        # Close the database connection
        conn.close()
        print(data)
        # Add items to the tree view
        self.add_items(self.model.invisibleRootItem(), data)

    def saveDb(self, filename=None):
        if not filename:
            filename=self.file_path
        # Get the structure of the tree view
        d = self.get_structure()
        print(d)
        # Connect to the database
        conn = sqlite3.connect(filename)
        c = conn.cursor()

        # Clear the tables
        c.execute('DELETE FROM classes')
        c.execute('DELETE FROM neural_nets')
        c.execute('DELETE FROM images')
        c.execute('DELETE FROM Yolo')

        # Insert data into the tables
        try:
            for class_name in d['Classes']:
                c.execute('INSERT INTO classes (name) VALUES (?)', (class_name,))
        except Exception as e:
            print(f"error: e")
        try:
            for net_name in d['Neuronale Netze']:
                c.execute('INSERT INTO neural_nets (name) VALUES (?)', (net_name,))
        except Exception as e:
            print(f"error: e")
        try:
            for img_data in d['Images']:
                yolo_data = img_data['Yolo']
                values = (img_data['label'], img_data['File'], yolo_data['gx'], yolo_data['gy'], yolo_data['x'], yolo_data['y'], yolo_data['Class'])
                c.execute('INSERT INTO images (label, file, gx, gy, x, y, class) VALUES (?, ?, ?, ?, ?, ?, ?)', values)
        except Exception as e:
            print(f"error: e")
        try:
            for key, value in d["Yolo"].items():
                c.execute(f'INSERT INTO Yolo (label, value) VALUES ("{key}", "{value}")')
        except Exception as e:
            print(f"error: e")
        # Commit changes and close the database connection
        conn.commit()
        conn.close()

    def clear(self):
        root=self.model.invisibleRootItem()
        while root.hasChildren():
            for i in range(root.rowCount()):
                self.model.removeRow(i)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    tree_view_panel = TreeviewPanel("C:/Users/lucas/Documents/Python/GUI/Bild_KI_Trainer_Programm/test.db")
    tree_view_panel.show()
    app.exec_()
    tree_view_panel.saveDb()