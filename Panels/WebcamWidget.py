import os
if os.name == 'nt':
    pass
else:
    os.environ['GST_PLUGIN_PATH']='/lib/x86_64-linux-gnu/gstreamer1.0'
    pass
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
import sys
try:
    from Panels.overlay import Overlay
except:
    from overlay import Overlay

if os.name == 'nt':
    bilder_pfad = os.path.join(os.environ['USERPROFILE'], 'Pictures')
else:
    bilder_pfad = os.path.join(os.environ['HOME'], 'Pictures')

try:
    default_cam=QCameraInfo.availableCameras()[-1]
except:
    default_cam=None

class WebcamWidget(QWidget):
    def __init__(self, CameraInfo=default_cam, imgPath=bilder_pfad):
        super().__init__()
        if not CameraInfo:
            raise ValueError("No Camera connected")
        self.path=imgPath
        #if not os.path.exists(os.path.split(self.path)[0]):
        #    os.mkdir(os.path.split(self.path)[0])
        self.offsetX=0
        self.offsetY=0
        self.camera = QCamera(CameraInfo)
        self.count=0
        self.viewfinder = QCameraViewfinder()
        size=self.viewfinder.size()
        self.width = size.width()-1
        self.height = size.height()-1

        self.overlay = Overlay(self.viewfinder)
        self.camera.setViewfinder(self.viewfinder)

        self.capture = QCameraImageCapture(self.camera)
        self.capture.setCaptureDestination(QCameraImageCapture.CaptureToFile)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.viewfinder)

        self.camera.start()

    def setGrid(self, x=None, y=None, width=None, height=None, horizontal_lines=None, vertical_lines=None):
        self.offsetX=x
        self.offsetY=y
        x_new, y_new, _, _ =self.getDimension()
        self.overlay.update_grid(x=x_new, y=y_new, width=width,height=height,horizontal_lines=horizontal_lines, vertical_lines=vertical_lines)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        x, y, w, h =self.getDimension() 
        #print(x,y, h, w, width, height, scale)
        self.overlay.update_grid(x=int(x),y=int(y),width=int(w),height=int(h))
        self.overlay.resize(self.viewfinder.size())
    
    def getDimension(self):
        size=self.viewfinder.size()
        FW=16
        FH=9
        width = size.width()
        height = size.height()
        width_scale = width / FW
        height_scale = height / FH
        scale = min(width_scale, height_scale)
        w=(FW*scale)#-self.offsetX
        h=(FH*scale)#-self.offsetY
        x = ((width - w) // 2) +self.offsetX
        y = ((height - h) // 2)+self.offsetY
        return (x, y, w, h)
    
    def capture_image(self, folder=None) -> str:
        """
            Captures an image and saves it to a file.

            :param folder: Optional; The folder in which to save the image. If not specified, the image will be saved in the default path.
            :type folder: str
            :return: The file path of the saved image.
            :rtype: str
        """
        if not folder:
            file=f"{self.path}{self.count}"
            self.capture.capture(file)
            self.count+=1
        else:
            file=f"{folder}/image{self.count}"
            self.capture.capture(file)
            self.count+=1
        #print("Lol")
        return file

    def stop(self):
        self.camera.stop()

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = WebcamWidget()
    window.show()
    sys.exit(app.exec_())