import json
import os
import sqlite3
from threading import Thread
from PyQt5 import QtWidgets, QtGui
import numpy as np
import torch
from torch import nn
from torchvision import models
from PIL import Image

class NeuralNetEditor(QtWidgets.QWidget):
    def __init__(self, projectFolder=None, neuralnetFile=None):
        super().__init__()
        self.model=None
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
        
        self.neuralnetFile=neuralnetFile
        if neuralnetFile:
            self.load_settings(neuralnetFile)
        
        self.projectFolder=projectFolder

    def on_add_layer(self):
      # Add a new layer to the list
      layer_type, ok = QtWidgets.QInputDialog.getItem(self, 'Add layer', 'Layer type:', 
      ['Linear', 'Dropout', 'Flatten', 'Conv2d', 'MaxPool2d'])
      if ok:
          # Get the layer parameters
          if layer_type == 'Linear':
              units, ok = QtWidgets.QInputDialog.getInt(self, 'Add Linear layer', 'Units:')
              if ok:
                  self.layers_list.addItem(f'Linear({units})')
          elif layer_type == 'Dropout':
              rate, ok = QtWidgets.QInputDialog.getDouble(self, 'Add Dropout layer', 'Rate:')
              if ok:
                  self.layers_list.addItem(f'Dropout({rate})')
          elif layer_type == 'Conv2d':
              filters, ok = QtWidgets.QInputDialog.getInt(self, 'Add Conv2d layer', 'Filters:')
              if ok:
                  kernel_size, ok = QtWidgets.QInputDialog.getInt(self, 'Add Conv2d layer', 'Kernel size:')
                  if ok:
                      self.layers_list.addItem(f'Conv2d({filters}, {kernel_size})')
          elif layer_type == 'MaxPool2d':
              pool_size, ok = QtWidgets.QInputDialog.getInt(self, 'Add MaxPool2d layer', 'Pool size:')
              if ok:
                  self.layers_list.addItem(f'MaxPool2d({pool_size})')
          else:
              self.layers_list.addItem(layer_type)

    def on_train(self):
        if not self.projectFolder:
            raise ValueError('projectFolder is not set')
        dbFile = self.projectFolder

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
            image = self.list_to_dict(img)
            print(image)
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
        
        x = torch.tensor(x).float()
        y = torch.tensor(y).float()
        print(list(x.size()))
        print(list(y.size()))
        
        self.pretrained_model_name=self.pretrained_model_combo.currentText()
        base_model=None
        # Get the selected pretrained model
        if self.pretrained_model_name == 'VGG16':
            base_model = models.vgg16(pretrained=True)
            base_model.classifier[6] = nn.Identity()
            
        elif self.pretrained_model_name == 'ResNet50':
            base_model = models.resnet50(pretrained=True)
            base_model.fc = nn.Identity()
            
        elif self.pretrained_model_name == 'InceptionV3':
            base_model = models.inception_v3(pretrained=True)
            base_model.fc = nn.Identity()

        # Freeze the layers of the base model
        if base_model:
          for param in base_model.parameters():
            param.requires_grad = False

        # Create a new model by adding layers on top of the base model
        if base_model is not None:
          modules = [base_model]
        else:
          modules = []
         # Add the new layers
        items = [self.layers_list.item(i).text() for i in range(self.layers_list.count())]
        print(items)

        input = torch.randn(1, 3, 720, 1280)

        # Initialize in_channels for Conv2d and Linear layers
        in_channels_conv = input.shape[1]
        in_channels_linear = None

        for layer_text in items:
            print(layer_text)
            if "(" in layer_text:
                layer_type, layer_params = layer_text.split('(', 1)
                layer_params = layer_params[:-1]
                print(layer_type, layer_params)
            else:
                layer_type=layer_text

            if layer_type == 'Linear':
                units = int(layer_params)
                modules.append(nn.Linear(in_features=in_channels_linear, out_features=units))
                modules.append(nn.ReLU())
                in_channels_linear = units

            elif layer_type == 'Dropout':
                rate = float(layer_params)
                modules.append(nn.Dropout(rate))

            elif layer_type == 'Flatten':
                modules.append(nn.Flatten())
                # Update in_channels for Linear layers after flattening
                in_channels_linear = input.numel()

            elif layer_type == 'Conv2d':
                filters, kernel_size = map(int, layer_params.split(','))
                modules.append(nn.Conv2d(in_channels=in_channels_conv, out_channels=filters, kernel_size=kernel_size))
                modules.append(nn.ReLU())
                # Update in_channels for next Conv2d layers
                in_channels_conv = filters

            elif layer_type == 'MaxPool2d':
                pool_size = int(layer_params)
                modules.append(nn.MaxPool2d(pool_size))

            # Pass the input through the current module
            for module in modules:
                input = module(input)

            # Print the output size
            print(input.size())

        if len(modules) == 0:
            raise ValueError("Model not defined")

        modules.append(nn.Flatten())
        modules.append(nn.Linear(output_size)
        modules.append(nn.Softmax(dim=-1))
        self.model=nn.Sequential(*modules)

        # Compile the model
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters())

        # Train the model
        for epoch in range(10):
          optimizer.zero_grad()
          outputs = self.model(x)
          loss = criterion(outputs, y)
          print(f'Epoch {epoch+1}, Loss: {loss.item()}')
          loss.backward()
          optimizer.step()


    def list_to_dict(self,img):
      return {'id':img[0], 'label':img[1],'file':img[2],'x':img[3],'y':img[4],'gx':img[5],'gy':img[6],'class':img[7]}

    def on_export_thread(self):
      thread = Thread(target=self.on_export)
      thread.start()

    def on_train_thread(self):
      thread = Thread(target=self.on_train)
      thread.start()

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
      file=os.path.join(exportFolder, f"{filename}.pt")
      
      # Save the model to the file
      torch.save(self.model.state_dict(), file)
      print(f"model saved, file path: {file}")

    def get_Model(self):
      return self.model

    def on_open(self):
      if not self.neuralnetFile:
          raise ValueError('neuralnetFile is not set')

      if self.neuralnetFile.endswith('.json'):
          # Load settings from a JSON file
          self.load_settings(self.neuralnetFile)
      else:
          # Load model from a PyTorch file
          self.model.load_state_dict(torch.load(self.neuralnetFile))
          self.update_layers_list()

    def update_layers_list(self):
      # Clear the layers list
      self.layers_list.clear()
      # Add the layers of the model to the list
      for layer in self.model.children():
          self.layers_list.addItem(f"{layer.__class__.__name__}")

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = NeuralNetEditor()
    window.show()
    app.exec_()
