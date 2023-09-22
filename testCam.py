from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtCore import QTimer


class CameraTester(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.comboBox = QComboBox()
        self.layout.addWidget(self.comboBox)

        self.viewfinder = QCameraViewfinder()
        self.layout.addWidget(self.viewfinder)

        self.button = QPushButton("Test Camera")
        self.button.clicked.connect(self.test_camera)
        self.layout.addWidget(self.button)

        self.update_camera_list()

    def update_camera_list(self):
        cameras = QCameraInfo.availableCameras()
        for camera_info in cameras:
            self.comboBox.addItem(camera_info.description())

    def test_camera(self):
        index = self.comboBox.currentIndex()
        camera_info = QCameraInfo.availableCameras()[index]
        self.camera = QCamera(camera_info)

        try:
            self.camera.setViewfinder(self.viewfinder)
            self.camera.start()

            # Stop the camera after 5 seconds
            QTimer.singleShot(5000, self.camera.stop)
        except Exception as e:
            QMessageBox.critical(self, "Camera Error", str(e))

app = QApplication([])
window = CameraTester()
window.show()
app.exec_()
