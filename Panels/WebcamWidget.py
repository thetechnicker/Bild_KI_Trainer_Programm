import cv2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel

def draw_grid(img, x, y, w, h, gitter_xcount, gitter_ycount):
    # Draw the rectangle
    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), 1)

    # Draw the grid lines
    x_step = w // gitter_xcount
    y_step = h // gitter_ycount
    for i in range(1, gitter_xcount):
        cv2.line(img, (x + i * x_step, y), (x + i * x_step, y + h), (255, 255, 255), 1)
    for i in range(1, gitter_ycount):
        cv2.line(img, (x, y + i * y_step), (x + w, y + i * y_step), (255, 255, 255), 1)

class Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QImage)

    def __init__(self, grid_x, grid_y, grid_w, grid_h, grid_xcount, grid_ycount):
        QtCore.QThread.__init__(self)
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.grid_xcount = grid_xcount
        self.grid_ycount = grid_ycount

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                # Draw the grid on the webcam image
                draw_grid(frame,
                          self.grid_x,
                          self.grid_y,
                          self.grid_w,
                          self.grid_h,
                          self.grid_xcount,
                          self.grid_ycount)

                # Make everything outside the grid slightly gray
                frame[:self.grid_y,:,:] = frame[:self.grid_y,:,:] * 0.9
                frame[self.grid_y+self.grid_h:,:,:] = frame[self.grid_y+self.grid_h:,:,:] * 0.9
                frame[:,:self.grid_x,:] = frame[:,:self.grid_x,:] * 0.9
                frame[:,self.grid_x+self.grid_w:,:] = frame[:,self.grid_x+self.grid_w:,:] * 0.9

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h,w,ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data,w,h,
                                           bytesPerLine,QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640,
                                             480,
                                             QtCore.Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

class LiveImageViewer(QWidget):
    def __init__(self,
                 grid_x=0,
                 grid_y=0,
                 grid_w=100,
                 grid_h=100,
                 grid_xcount=5,
                 grid_ycount=5):
        QWidget.__init__(self)
        self.label = QLabel(self)
        th = Thread(grid_x,
                    grid_y,
                    grid_w,
                    grid_h,
                    grid_xcount,
                    grid_ycount)
        th.changePixmap.connect(self.setImage)
        th.start()

    @QtCore.pyqtSlot(QImage)
    def setImage(self,image):
        self.label.setPixmap(QPixmap.fromImage(image))


if __name__=="__main__":
    app = QtWidgets.QApplication([])
    dialog = LiveImageViewer()
    dialog.show()
    app.exec_()
    