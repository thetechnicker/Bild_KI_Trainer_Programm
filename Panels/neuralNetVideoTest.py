import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialog
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtCore import QThread
from PyQt5 import QtCore, QtGui
import tensorflow as tf
from tensorflow.keras.models import load_model

try:
    from overlay import Overlay
except:
    from .overlay import Overlay

try:
    from WebcamView_WB import WebcamWidget
except:
    from Panels.WebcamView_WB import WebcamWidget
    

class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.image = QtGui.QImage()
        self.predictions = None

    def setImage(self, image: np.ndarray):
        # Konvertiere das NumPy-Array in ein QImage
        h, w, c = image.shape
        if c == 3:
            qimage = QtGui.QImage(image.data, w, h, 3 * w, QtGui.QImage.Format_RGB888)
        elif c == 4:
            qimage = QtGui.QImage(image.data, w, h, 4 * w, QtGui.QImage.Format_RGBA8888)
        else:
            raise ValueError("Das Bild muss entweder 3 oder 4 Kanäle haben")
        self.image = qimage
        self.update()

    def setPredictions(self, predictions: np.ndarray):
        self.predictions = predictions
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # Calculate the scale factor to fit the image within the widget
        try:
            scale_factor = min(self.width() / self.image.width(), self.height() / self.image.height())
        except ZeroDivisionError:
            return
        # Scale the image
        scaled_image = scaled_image = self.image.scaled(int(self.image.width() * scale_factor), int(self.image.height() * scale_factor))
        # Calculate the position of the top-left corner of the image
        x =int( (self.width() - scaled_image.width()) / 2)
        y =int( (self.height() - scaled_image.height()) / 2)
        # Draw the scaled image
        painter.drawImage(QtCore.QPoint(x, y), scaled_image)
        # Draw the heatmap on top of the image
        if self.predictions is not None:
            heatmap = self.predictionsToHeatmap(self.predictions)
            painter.drawImage(QtCore.QRectF(x, y, scaled_image.width(), scaled_image.height()), heatmap)

    def predictionsToHeatmap(self, predictions: np.ndarray, threshold=0.01) -> QtGui.QImage:
        # Create a QImage to store the heatmap
        heatmap = QtGui.QImage(self.image.size(), QtGui.QImage.Format_ARGB32)
        heatmap.fill(QtCore.Qt.transparent)
        # Create a QPainter to draw on the heatmap
        painter = QtGui.QPainter(heatmap)
        # Get the dimensions of the grid
        gy, gx, _ = predictions.shape
        # Calculate the size of each grid cell
        cell_width = self.image.width() / gx
        cell_height = self.image.height() / gy
        # Iterate over the grid cells
        for i in range(gy):
            for j in range(gx):
                # Get the bounding box and objectness score for this cell
                x, y, w, h = predictions[i][j][:4]
                c = list(predictions[i][j][4:])
                #print(c)
                max_value = np.max(c)
                print(max_value)
                # Check if the objectness score is above the threshold
                if c[0] > threshold:
                    # Calculate the coordinates of the top-left corner of the bounding box
                    x1 = int((j + x - w / 2) * cell_width)
                    y1 = int((i + y - h / 2) * cell_height)
                    # Calculate the coordinates of the bottom-right corner of the bounding box
                    x2 = int((j + x + w / 2) * cell_width)
                    y2 = int((i + y + h / 2) * cell_height)
                    # Draw the bounding box on the heatmap
                    painter.setPen(QtGui.QPen(QtCore.Qt.red, 2))
                    painter.drawRect(x1, y1, x2 - x1, y2 - y1)
                    # Draw the objectness score on the heatmap
                    painter.setFont(QtGui.QFont("Arial", 14))
                    painter.drawText(x1, y1 - 10, f"{c}")
        return heatmap


class DisplayArrayThread(QThread):
    def __init__(self, webcamWidget, image_widget, model):
        super().__init__()
        self.webcamWidget = webcamWidget
        self.image_widget = image_widget
        self.stopped = False
        self.model=model
        self.input_slice = slice(None)

    def set_input_slice(self, x, y, w, h):
        self.input_slice = (slice(y, y + h), slice(x, x + w))

    def run(self):
        size=self.webcamWidget.getImageSize()
        print(size)
        while size is None and not self.stopped:
            size=self.webcamWidget.getImageSize()
            print(size)
        if self.stopped:
            return
        # Create a NumPy array of zeros
        array = np.zeros(size, dtype=np.uint8)
        
        # Set the array for the webcam widget
        self.webcamWidget.setArray(array)
        #cv2.imshow(array)
        
        # Continuously update the image in the image widget
        while not self.stopped:
            array_NoAlpha = array[..., :3]
            image=np.array(array_NoAlpha[..., ::-1])
            self.image_widget.setImage(image)
            if self.model:
                input_array = image[self.input_slice]
                batch_array = np.expand_dims(input_array, axis=0)
                with tf.device('/GPU:0'):
                    try:
                        predictions = self.model.predict(batch_array)
                    except Exception as e:
                        with open("log.dat", "w") as f:
                            print(e, file=f)
                            print(e)
                            continue
                print(predictions.shape)
                batch1 =np.array(predictions[0])
                print(batch1.shape)
                #with open("pred.dump", "w") as f:
                #    f.write(np.array2string(batch1))
                self.image_widget.setPredictions(np.array(predictions[0]))

            self.msleep(100)  # Update the image every 0.1 seconds

    def stop(self):
        self.stopped = True

class WebcamWindow(QDialog):
    def __init__(self, model:str=None, camera=QCameraInfo.defaultCamera()):
        super().__init__()
        self.model=None

        if model:
            self.model=load_model(model)
            self.model.summary()
            self.inputShape=np.array(self.model.input_shape)
            print(self.inputShape)
        else:
            self.inputShape=None
        self.webcamWidget = WebcamWidget(CameraInfo=camera)
        self.image_widget = ImageWidget(self)
        self.displayArrayThread=None
        self.initUI()

    def initUI(self):
        image_layout=QHBoxLayout()
        image_layout.addWidget(self.webcamWidget)
        image_layout.addWidget(self.image_widget)
        # Create layout
        layout = QVBoxLayout(self)
        layout.addLayout(image_layout)

        # Create input fields for overlay parameters
        overlayLayout = QHBoxLayout()
        self.xInput = QLineEdit()
        self.xInput.setText("0")
        self.yInput = QLineEdit()
        self.yInput.setText("0")
        self.widthInput = QLineEdit()
        self.heightInput = QLineEdit()
        if not self.inputShape is None:
            self.widthInput.setText(f"{self.inputShape[1]}")
            self.heightInput.setText(f"{self.inputShape[2]}")
        overlayLayout.addWidget(QLabel("x:"))
        overlayLayout.addWidget(self.xInput)
        overlayLayout.addWidget(QLabel("y:"))
        overlayLayout.addWidget(self.yInput)
        overlayLayout.addWidget(QLabel("width:"))
        overlayLayout.addWidget(self.widthInput)
        overlayLayout.addWidget(QLabel("height:"))
        overlayLayout.addWidget(self.heightInput)
        layout.addLayout(overlayLayout)

        # Create button to update overlay
        updateButton = QPushButton("Update Overlay")
        updateButton.clicked.connect(self.updateOverlay)
        layout.addWidget(updateButton)

        # Create button to show numpy array
        self.showArrayButton = QPushButton("Show Numpy Array")
        self.showArrayButton.clicked.connect(self.showNumpyArray)
        layout.addWidget(self.showArrayButton)
        
        # Create a cancel button
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)
        layout.addWidget(cancelButton)

    def updateOverlay(self):
        x = int(self.xInput.text())
        y = int(self.yInput.text())
        width = int(self.widthInput.text())
        height = int(self.heightInput.text())
        self.webcamWidget.setGrid(x=x, y=y, width=width, height=height)
        if self.displayArrayThread:
            self.displayArrayThread.set_input_slice(x, y, width, height)


    def showNumpyArray(self):
        if self.showArrayButton.text() == "Show Numpy Array":
            # Create a new thread to display the array
            self.displayArrayThread = DisplayArrayThread(self.webcamWidget, self.image_widget, self.model)
            self.displayArrayThread.start()
            # Change the button text to "Stop"
            self.showArrayButton.setText("Stop")
        else:
            # Stop the thread
            self.displayArrayThread.stop()
            self.displayArrayThread=None
            # Change the button text back to "Show Numpy Array"
            self.showArrayButton.setText("Show Numpy Array")

    def closeEvent(self, event):
        if self.displayArrayThread:
            self.displayArrayThread.stop()
        self.webcamWidget.stop()
        event.accept() 

if __name__ == '__main__':
    app = QApplication([])
    window = WebcamWindow()
    window.show()
    app.exec_()
