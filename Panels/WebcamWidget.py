from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
import sys

class CameraWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.camera = QCamera(QCameraInfo.defaultCamera())

        self.viewfinder = QCameraViewfinder()
        self.camera.setViewfinder(self.viewfinder)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.viewfinder)

        

        self.camera.start()

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = CameraWidget()
    window.show()
    sys.exit(app.exec_())