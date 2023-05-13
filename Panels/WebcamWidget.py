from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import sys

class CameraWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.camera = QCamera(QCameraInfo.defaultCamera())

        self.viewfinder = QCameraViewfinder()
        self.camera.setViewfinder(self.viewfinder)
        print(self.camera.focus().maximumDigitalZoom())
        self.zoom_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.zoom_slider.setRange(0, int(self.camera.focus().maximumDigitalZoom() * 100))
        self.zoom_slider.setValue(int(self.camera.focus().digitalZoom() * 100))
        self.zoom_slider.valueChanged.connect(self.update_zoom)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.viewfinder)
        layout.addWidget(self.zoom_slider)



        self.camera.start()

    def update_zoom(self, value):
        zoom_value = value / 100.0
        self.camera.focus().zoomTo(zoom_value, zoom_value)

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = CameraWidget()
    window.show()
    sys.exit(app.exec_())