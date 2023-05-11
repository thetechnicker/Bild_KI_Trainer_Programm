import os
import json
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

class EditableStandardItem(QtGui.QStandardItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    # def setData(self, value, role=Qt.EditRole):
    #     super().setData(value, role)
    #     if role == Qt.EditRole:
    #         tree_view_panel = self.model().parent()
    #         tree_view_panel.update_data()

    def is_file(self):
        # Check if the second column contains the string 'file'
        if 'file' in self.model().item(self.row(), 1).text():
            return True
        return False

    def is_value(self):
        # Check if the second column contains the string 'value'
        if 'value' in self.model().item(self.row(), 1).text():
            return True
        return False

class EditDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Edit Item')

        # Create the label input
        self.label_input = QtWidgets.QLineEdit()

        # Create the type select
        self.type_select = QtWidgets.QComboBox()
        self.type_select.addItems(['file', 'folder'])

        # Create the OK and Cancel buttons
        self.ok_button = QtWidgets.QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)

        # Create the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Label:'))
        layout.addWidget(self.label_input)
        layout.addWidget(QtWidgets.QLabel('Type:'))
        layout.addWidget(self.type_select)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_data(self):
        return {
            'label': self.label_input.text(),
            'type': self.type_select.currentText()
        }

class TreeviewPanel(QtWidgets.QWidget):
    def __init__(self, file_path=None):
        super().__init__()

        self.file_path = file_path

        layout = QtWidgets.QVBoxLayout(self)

        #select_layout = QtWidgets.QHBoxLayout()
        #self.select_button = QtWidgets.QPushButton('Select JSON')
        #self.select_button.clicked.connect(self.select_file)
        #select_layout.addWidget(self.select_button)
        #layout.addLayout(select_layout)

        self.tree_view = QtWidgets.QTreeView()
        self.model = QtGui.QStandardItemModel(self)
        self.model.setColumnCount(2)  # Set the number of columns to 2
        self.model.setHeaderData(0, Qt.Horizontal, 'Name')  # Set the header for the first column
        self.model.setHeaderData(1, Qt.Horizontal, 'Type')  # Set the header for the first column
        self.tree_view.setModel(self.model)
        self.tree_view.hideColumn(1)
        layout.addWidget(self.tree_view)

        button_layout = QtWidgets.QHBoxLayout()
        add_button = QtWidgets.QPushButton('Add')
#        add_button.clicked.connect(self.add_item)
        button_layout.addWidget(add_button)

        remove_button = QtWidgets.QPushButton('Remove')
        remove_button.clicked.connect(self.remove_item)
        button_layout.addWidget(remove_button)
        layout.addLayout(button_layout)

        if self.file_path and self.file_path.endswith('.json'):
            self.load_json(self.file_path)
        #else: 
        #    self.select_file()
        self.tree_view.doubleClicked.connect(self.on_double_click)

    def setJson(self, file):
        self.load_json(file)


    def on_double_click(self, index):
        item = self.model.itemFromIndex(index)
        print(item)
        # Open the edit dialog here
        dialog = EditDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            


    def remove_item(self):
        selected_indexes = self.tree_view.selectedIndexes()

        if selected_indexes:
            # Get the first selected index
            index = selected_indexes[0]
            # Remove the corresponding item from the model
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
                    "classes": [
                    ],
                    "traindata": [

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


    def find_item(self, path_parts):
        parent_item = self.model.invisibleRootItem()
        for part in path_parts:
            for row in range(parent_item.rowCount()):
                item = parent_item.child(row)
                if item.text() == part:
                    parent_item = item
                    break
        return parent_item
    
    # def add_item(self):
    #     # Create a dialog with input fields for the name and type
    #     dialog = QtWidgets.QDialog()
    #     layout = QtWidgets.QVBoxLayout()
    #     name_label = QtWidgets.QLabel('Name:')
    #     name_edit = QtWidgets.QLineEdit()
    #     layout.addWidget(name_label)
    #     layout.addWidget(name_edit)
    #     type_label = QtWidgets.QLabel('Type:')
    #     type_combo = QtWidgets.QComboBox()
    #     type_combo.addItems(['file/value', 'folder/dict'])
    #     layout.addWidget(type_label)
    #     layout.addWidget(type_combo)
    #     button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
    #     layout.addWidget(button_box)
    #     dialog.setLayout(layout)

    #     # Connect the button box signals
    #     button_box.accepted.connect(dialog.accept)
    #     button_box.rejected.connect(dialog.reject)

    #     # Show the dialog and get the result
    #     result = dialog.exec_()
    #     if result == QtWidgets.QDialog.Accepted:
    #         name = name_edit.text()
    #         item_type = type_combo.currentText()
    #         selected_indexes = self.tree_view.selectedIndexes()
    #         if selected_indexes:
    #             parent_index = selected_indexes[0]
    #             parent_item = self.model.itemFromIndex(parent_index)
    #             # Check if parent item is not a file or value type
    #             if not (parent_item.is_file() or parent_item.is_value()):
            
    #                 # Create a new item with the specified name and type
    #                 new_item = EditableStandardItem(name)
    #                 new_item_type = QtGui.QStandardItem(item_type)
    #                 parent_item.appendRow([new_item, new_item_type])
    #                 if self.file_path and self.file_path.endswith('.json'):
    #                     data = json.loads(json.dumps(self.get_tree_structure()))
    #                     with open(self.file_path, 'w') as f:
    #                         json.dump(data, f, indent=4)
    #                 else:
    #                     os.mkdir(os.path.join(self.file_path, 'New Item'))
    #             else:
    #                 new_item = EditableStandardItem(name)
    #                 new_item_type = QtGui.QStandardItem(item_type)
    #                 self.model.appendRow([new_item, new_item_type])
    #         else:
    #             new_item = EditableStandardItem(name)
    #             new_item_type = QtGui.QStandardItem(item_type)
    #             self.model.appendRow([new_item, new_item_type])

    def get_tree_structure(root_item):
        def get_structure(item):
            if item.hasChildren():
                structure = []
                for row in range(item.rowCount()):
                    child_item = item.child(row)
                    value = get_structure(child_item)
                    structure.append(value)
                return {item.text(): structure}
            else:
                return item.text()
    
        tree_structure = {}
        for row in range(root_item.rowCount()):
            item = root_item.child(row)
            key = item.text()
            value = get_structure(item)[key]
            tree_structure[key] = value
    
        return tree_structure

    def saveJson(self):
        with open(self.select_file, "w") as f:
            json.dump(self.get_tree_structure(),f)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    tree_view_panel = TreeviewPanel("C:/Users/lucas/Documents/Python/GUI/Bild_KI_Trainer_Programm/test.json")
    tree_view_panel.show()
    app.exec_()