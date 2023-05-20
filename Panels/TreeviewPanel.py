import os
import json
import sys
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
        return {
            'label': self.model().item(self.row(), 0).text(),
            'type': self.model().item(self.row(), 1).text()
        }

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
        if self.file_path and self.file_path.endswith('.json'):
            self.load_json(self.file_path)

    def on_double_click(self, index):
        item = self.model.itemFromIndex(index)
        if self.callback:
            self.callback(item)
    def set_callback(self, callback):
        self.callback=callback

    def remove_item(self):
        selected_indexes = self.tree_view.selectedIndexes()

        if selected_indexes:
            index = selected_indexes[0]
            item = self.model.itemFromIndex(index)
            if not item.is_non() and not item.is_folder():
                self.model.removeRow(index.row(), index.parent())

    def select_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if file_dialog.exec_():            
            self.model.clear()
            self.model.setColumnCount(2)
            self.model.setHeaderData(0, Qt.Horizontal, 'Name')
            self.model.setHeaderData(1, Qt.Horizontal, 'Type')
            self.tree_view.setModel(self.model)
            self.tree_view.hideColumn(1)
            self.file_path = file_dialog.selectedFiles()[0]
            self.load_json(self.file_path)

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

    def load_json(self, file_path):
        fail=False
        data=None
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                self.add_items(self.model.invisibleRootItem(), data)
            except:
                fail=True
                data={
                    "Classes": [
                    ],
                    "Neuronale Netze":[

                    ],
                    "Images": [

                    ]
                }
                self.add_items(self.model.invisibleRootItem(), data)
        if fail:
            with open(file_path, "w") as f:
                json.dump(data,f)

    def add_items(self, parent, data):
        #print(data)
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
                        d.append(item.child(i).text())
                structure["Neuronale Netze"]=d
            elif item.text()=="Images":
                d=[]
                if item.hasChildren():
                    for i in range(item.rowCount()):
                        item=item.child(i)
                        img_data={}
                        img_data["label"]=item.text()
                        if item.hasChildren():
                            for j in range(item.rowCount()):
                                print(item.child(j).text())
                                if item.child(j).text()=="File":
                                    img_data["File"]=item.child(j).child(0).text()
                                elif item.child(j).text()=="Yolo":
                                    
                                    Yolo_data={}
                                    item=item.child(j)
                                    if item.hasChildren():
                                        for k in range(item.rowCount()):
                                            Yolo_data[item.child(k).text()]=int(item.child(k).child(0).text())
                                    img_data["Yolo"]=Yolo_data
                                else:
                                    img_data["rest"]="Error"
                        d.append(img_data)
                        
                structure["Images"]=d
        return structure


    def saveJson(self):
        d=self.get_structure()
        #print(d)
        with open(self.file_path, "w") as f:
            json.dump(d,f)

    def add_item(self):
        dialog = AddDialog(self)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
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
                c_item = EditableStandardItem("c")

                file_item.appendRow([EditableStandardItem("0"),EditableStandardItem("val")])
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

                parent.appendRow([name_item,EditableStandardItem("img")])

            elif item_type == "Neural Net":
                parent_name = "Neuronale Netze"
                name = "cnn"
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
                    self.model.appendRow([name_item, type_item])
    
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    tree_view_panel = TreeviewPanel("C:/Users/lucas/Documents/Python/GUI/Bild_KI_Trainer_Programm/test.json")
    tree_view_panel.show()
    app.exec_()
    tree_view_panel.saveJson()