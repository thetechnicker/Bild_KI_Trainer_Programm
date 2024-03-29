import json
import os
import sqlite3
from PyQt5 import QtWidgets, QtGui
import tensorflow as tf, keras
from tensorflow.keras.applications import VGG16, ResNet50, InceptionV3
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, Reshape, Input
from threading import Thread
import numpy as np
from PIL import Image


class NeuralNetEditor(QtWidgets.QWidget):
    def __init__(self, projectFolder=None, neuralnetFile=None):
        super().__init__()

        # Set the data
        self.data = {}

        # Create the UI elements
        self.pretrained_model_label = QtWidgets.QLabel('Pretrained model:')
        self.pretrained_model_combo = QtWidgets.QComboBox()
        self.pretrained_model_combo.addItems(['none', 'VGG16', 'ResNet50', 'InceptionV3'])
        self.layers_label = QtWidgets.QLabel('Layers:')
        self.layers_list = QtWidgets.QListWidget()
        self.add_layer_button = QtWidgets.QPushButton('Add layer')
        self.train_button = QtWidgets.QPushButton('Train')

        # Connect signals
        self.add_layer_button.clicked.connect(self.on_add_layer)
        self.train_button.clicked.connect(self.on_train_thread)

        # Lay out the UI elements
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.pretrained_model_label)
        layout.addWidget(self.pretrained_model_combo)
        layout.addWidget(self.layers_label)
        layout.addWidget(self.layers_list)
        layout.addWidget(self.add_layer_button)
        layout.addWidget(self.train_button)
        self.export_button = QtWidgets.QPushButton('Export')
        self.export_button.clicked.connect(self.on_export)
        layout.addWidget(self.export_button)


        #shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+S'), self)
        #shortcut.activated.connect(self.on_save)
        self.model=Sequential()
        self.neuralnetFile=neuralnetFile
        if neuralnetFile:
            self.load_settings(neuralnetFile)
        
        self.projectFolder=projectFolder
        self.LoadedModel=None
        self.pretrained_layers = {}

    def on_add_layer(self):
        # Add a new layer to the list
        layer_type, ok = QtWidgets.QInputDialog.getItem(self, 'Add layer', 'Layer type:', ['Dense', 'Dropout', 'Flatten', 'Conv2D', 'MaxPooling2D'])
        if ok:
          # Get the layer parameters
          if layer_type == 'Dense':
              units, ok = QtWidgets.QInputDialog.getInt(self, 'Add Dense layer', 'Units:')
              if ok:
                  self.layers_list.addItem(f'Dense({units})')
          elif layer_type == 'Dropout':
              rate, ok = QtWidgets.QInputDialog.getDouble(self, 'Add Dropout layer', 'Rate:')
              if ok:
                  self.layers_list.addItem(f'Dropout({rate})')
          elif layer_type == 'Conv2D':
              filters, ok = QtWidgets.QInputDialog.getInt(self, 'Add Conv2D layer', 'Filters:')
              if ok:
                  kernel_size, ok = QtWidgets.QInputDialog.getInt(self, 'Add Conv2D layer', 'Kernel size:')
                  if ok:
                      self.layers_list.addItem(f'Conv2D({filters}, {kernel_size})')
          elif layer_type == 'MaxPooling2D':
              pool_size, ok = QtWidgets.QInputDialog.getInt(self, 'Add MaxPooling2D layer', 'Pool size:')
              if ok:
                  self.layers_list.addItem(f'MaxPooling2D({pool_size})')
          else:
              self.layers_list.addItem(layer_type)

    def list_to_dict(self, lst):
        keys = ['id', 'label', 'file', 'gx', 'gy', 'x', 'y', 'class']
        return dict(zip(keys, lst))

    def on_export_thread(self):
      thread = Thread(target=self.on_export)
      thread.start()

    def on_train_thread(self):
      thread = Thread(target=self.on_train)
      thread.start()

    def on_train(self):
        tf.config.run_functions_eagerly(True)
        tf.data.experimental.enable_debug_mode()
        if self.model:
           self.model=Sequential()
        if not self.projectFolder:
          raise ValueError('projectFolder is not set')
        dbFile=self.projectFolder
        
        print(dbFile)
        connection = sqlite3.connect(dbFile)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM images')
        image_data = cursor.fetchall()
        # Query the database for the number of classes
        cursor.execute('SELECT COUNT(*) FROM classes')
        num_classes = cursor.fetchone()[0]
        # Query the database for the Yolo settings
        cursor.execute('SELECT label, value FROM Yolo')
        yolo_data = cursor.fetchall()
        print(yolo_data)
        
        yolo_settings = {row[0]: int(row[1]) for row in yolo_data}
        vgc = yolo_settings['VerticalGridCount']
        hgc = yolo_settings['HorizontalGridCount']
        output_size = 5 + num_classes
        # Create x and y datasets
        x = []
        y = []
        for img in image_data:
          image=self.list_to_dict(img)
          # Load image data into a numpy array
          l_image = Image.open(f"{image['file']}.jpg")
          # Convert the image to a NumPy array
          img_data = np.array(l_image)
          x.append(img_data)
          # Create yolo output for image
          gx, gy = image['gx'], image['gy']
          output = np.zeros((vgc, hgc, output_size))
          output[gy, gx, :5] = [image['x'], image['y'], image['gx'], image['gy'], 1]
          output[gy, gx, 5 + image['class']] = 1
          y.append(output)
        x = np.array(x)
        y = np.array(y)
        y_shape = y.shape[1:]
        output_size = np.prod(y_shape)
        print(x,y,sep="\n")

        # Get the selected pretrained model
        print(x.shape[1:])
        self.model.add(Input(shape=x.shape[1:]))
        pretrained_model_name = self.pretrained_model_combo.currentText()
        if pretrained_model_name == 'VGG16':
          base_model = VGG16(weights='imagenet', include_top=False, input_shape=x.shape[1:])
        elif pretrained_model_name == 'ResNet50':
          base_model = ResNet50(weights='imagenet', include_top=False, input_shape=x.shape[1:])
        elif pretrained_model_name == 'InceptionV3':
          base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=x.shape[1:])
        if not pretrained_model_name=='none':
          # Freeze the layers of the base model
          for layer in base_model.layers:
            layer.trainable = False
          # Create a new model by adding layers on top of the base model
          self.model.add(base_model)

        if self.LoadedModel:
          self.model.add(self.LoadedModel)
    
        # Add the new layers
        for i in range(self.layers_list.count()):
          layer_text = self.layers_list.item(i).text()
          if "(" in layer_text:
            layer_type, layer_params = layer_text.split('(', 1)
            layer_params = layer_params[:-1]
          else:
             layer_type=layer_text

          # Check if the layer is pretrained
          is_pretrained = False
          if layer_type in self.pretrained_layers:
            is_pretrained = True
            self.pretrained_layers[layer_type].pop(0)
            if not self.pretrained_layers[layer_type]:
              del self.pretrained_layers[layer_type]

          if not is_pretrained:
            if layer_type == 'Dense':
              units = int(layer_params)
              self.model.add(Dense(units, activation='relu'))
            elif layer_type == 'Dropout':
              rate = float(layer_params)
              self.model.add(Dropout(rate))
            elif layer_type == 'Flatten':
              self.model.add(Flatten())
            elif layer_type == 'Conv2D':
              filters, kernel_size = map(int, layer_params.split(','))
              self.model.add(Conv2D(filters, kernel_size, activation='relu'))
            elif layer_type == 'MaxPooling2D':
              pool_size = int(layer_params)
              self.model.add(MaxPooling2D(pool_size))

        self.model.add(Flatten())
        self.model.add(Dense(output_size, activation='softmax'))
        self.model.add(Reshape(y_shape))
        # Compile the model
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'], run_eagerly=True)
        self.model.summary()
        # Train the model
        self.model.fit(x, y, epochs=10)

    def on_save(self):
        if not self.neuralnetFile:
            raise ValueError('neuralnetFile is not set')
        self.save_settings(self.neuralnetFile)

    def save_settings(self, filename):
        # Create a dictionary with the settings
        settings = {
            'pretrained_model': self.pretrained_model_combo.currentText(),
            'layers': [self.layers_list.item(i).text() for i in range(self.layers_list.count())]
        }

        # Save the settings to a file
        with open(filename, 'w') as f:
            json.dump(settings, f)

    def load_settings(self, filename):
        # Load the settings from a file
        with open(filename, 'r') as f:
            settings = json.load(f)
        
        print(settings)
        if not settings=={}:
            # Set the pretrained model
            index = self.pretrained_model_combo.findText(settings['pretrained_model'])
            if index != -1:
                self.pretrained_model_combo.setCurrentIndex(index)

            # Set the layers
            self.layers_list.clear()
            for layer_text in settings['layers']:
                self.layers_list.addItem(layer_text)

    def on_export(self):
        folder=os.path.split(self.projectFolder)
        exportFolder=os.path.join(folder[0], "exports")
        filename=os.path.basename(self.neuralnetFile).replace(".json", "")
        #print(folder, exportFolder, filename, sep="\n")
        file=os.path.join(exportFolder, f"{filename}.h5")
        if self.model.optimizer is None:
          raise RuntimeError('Model has not been compiled')
        
        # Save the model to the file
        self.model.save(file)
        print(f"model saved, file path: {file}")

    def get_Model(self):
       if self.model.optimizer is None:
          raise RuntimeError('Model has not been compiled')
       return self.model
    
    def on_open(self):
        if not self.neuralnetFile:
            raise ValueError('neuralnetFile is not set')
        
        if self.neuralnetFile.endswith('.json'):
            # Load settings from a JSON file
            self.load_settings(self.neuralnetFile)
        else:
            # Load model from a TensorFlow file
            self.LoadedModel = load_model(self.neuralnetFile)
            self.update_layers_list()

    def update_layers_list(self):
        # Clear the layers list
        self.layers_list.clear()

        # Add the layers of the model to the list
        for layer in self.LoadedModel.layers:
            self.layers_list.addItem(f"{layer.__class__.__name__}")
            if hasattr(layer, 'is_pretrained') and layer.is_pretrained:
                layer_type = layer.__class__.__name__
                if layer_type not in self.pretrained_layers:
                    self.pretrained_layers[layer_type] = []
                self.pretrained_layers[layer_type].append(layer)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = NeuralNetEditor()
    window.show()
    app.exec_()
