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

        if self.file_path and self.file_path.endswith('.json'):
            self.load_json(self.file_path)

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

    def add_items(self, parent_item, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if not key=="label":
                    name_item = EditableStandardItem(key)
                    type_item = EditableStandardItem('folder')
                    parent_item.appendRow([name_item, type_item])
                    self.add_items(name_item, value)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                label=""
                if isinstance(value, dict):
                    if value["label"]:
                        label= value["label"]
                    else:
                        label=str(index + 1)
                name_item = EditableStandardItem(label)
                type_item = EditableStandardItem('folder')
                parent_item.appendRow([name_item, type_item])
                self.add_items(name_item, value)
        else:
            name_item = EditableStandardItem(str(data))
            type_item = EditableStandardItem('file')
            parent_item.appendRow([name_item, type_item])

    def add_items2(self, parent, data):
        try:
            for key, value in data.items():
                if key=="Images":
                    self.model.appendRow([parent_name,EditableStandardItem("folder")])
                    pass
                elif key == "Neural Net":
                    parent_name = "Neuronale Netze"
                    self.model.appendRow([parent_name,EditableStandardItem("folder")])
                    name = "cnn"
                    for i in value:
                        
                        parent = self.get_item_by_name(parent_name)

                        name_item = EditableStandardItem(i)
                        type_item = EditableStandardItem(name)

                        if parent:
                            parent.appendRow([name_item, type_item])
                        else:
                            self.model.appendRow([name_item, type_item])
                elif key == "Class":
                    parent_name = "Classes"
                    self.model.appendRow([parent_name,EditableStandardItem("folder")])
                    name = "class"
                    for i in value:
                        parent = self.get_item_by_name(parent_name)
        
                        name_item = EditableStandardItem(i)
                        type_item = EditableStandardItem(name)
        
                        if parent:
                            parent.appendRow([name_item, type_item])
                        else:
                            self.model.appendRow([name_item, type_item])
        except:
            print("error")
            sys.exit()
                   
        # parent = self.get_item_by_name("Images")
        # name_item = EditableStandardItem(item_name or "test")
        # file_item = EditableStandardItem("File")
        # yolo_item = EditableStandardItem("Yolo")
        # gx_item = EditableStandardItem("gx")
        # gy_item = EditableStandardItem("gy")
        # x_item = EditableStandardItem("x")
        # y_item = EditableStandardItem("y")
        # c_item = EditableStandardItem("c")

        # file_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
        # value=EditableStandardItem()
        # gx_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
        # value=EditableStandardItem()
        # gy_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
        # value=EditableStandardItem()
        # x_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
        # value=EditableStandardItem()
        # y_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
        # value=EditableStandardItem()
        # c_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])

        # yolo_item.appendRow([gx_item,EditableStandardItem("non")])
        # yolo_item.appendRow([gy_item,EditableStandardItem("non")])
        # yolo_item.appendRow([x_item,EditableStandardItem("non")])
        # yolo_item.appendRow([y_item,EditableStandardItem("non")])
        # yolo_item.appendRow([c_item,EditableStandardItem("non")])

        # name_item.appendRow([file_item,EditableStandardItem("non")])
        # name_item.appendRow([yolo_item,EditableStandardItem("non")])

        # parent.appendRow([name_item,EditableStandardItem("img")])

    def find_item(self, path_parts):
        parent_item = self.model.invisibleRootItem()
        for part in path_parts:
            for row in range(parent_item.rowCount()):
                item = parent_item.child(row)
                if item.text() == part:
                    parent_item = item
                    break
        return parent_item

    def tree_to_dict(self,tree: QtWidgets.QTreeView) -> dict:
        model = tree.model()
        root = model.invisibleRootItem()
        result = {}

        def process_node(node):
            if node.hasChildren():
                children = [node.child(i) for i in range(node.rowCount())]
                if all(not child.hasChildren() for child in children):
                    return [child.text() for child in children]
                else:
                    return {child.text(): process_node(child) for child in children}
            else:
                return node.text()

        for i in range(root.rowCount()):
            item = root.child(i)
            result[item.text()] = process_node(item)

        return result
    
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
                structure["Images"]=d
        return structure


    def saveJson(self):
        d=self.get_structure()
        print(d)
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

                file_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
                value=EditableStandardItem()
                gx_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
                value=EditableStandardItem()
                gy_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
                value=EditableStandardItem()
                x_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
                value=EditableStandardItem()
                y_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])
                value=EditableStandardItem()
                c_item.appendRow([EditableStandardItem(),EditableStandardItem("val")])

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