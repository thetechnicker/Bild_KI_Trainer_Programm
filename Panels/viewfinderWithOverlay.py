from PyQt5.QtMultimedia import QAbstractVideoSurface, QVideoFrame, QAbstractVideoBuffer
from PyQt5.QtGui import QImage, QPainter, QColor, QPen
from PyQt5.QtCore import QRect
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget

class CustomVideoSurface(QAbstractVideoSurface):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        if parent is not None:
            viewfinder_size = parent.size()
            viewfinder_width = viewfinder_size.width()
            viewfinder_height = viewfinder_size.height()
        else:
            viewfinder_width = 0
            viewfinder_height = 0
        self.x = 10
        self.y = 10
        self.width = viewfinder_width
        self.height = viewfinder_height
        self.horizontal_lines = 10
        self.vertical_lines = 10
        self.offsetX=0
        self.offsetY=0

    def update_grid(self, x=None, y=None, width=None, height=None, horizontal_lines=None, vertical_lines=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if horizontal_lines is not None:
            self.horizontal_lines = horizontal_lines
        if vertical_lines is not None:
            self.vertical_lines = vertical_lines

    def supportedPixelFormats(self, handleType):
        return [QVideoFrame.Format_RGB32,
                QVideoFrame.Format_ARGB32,
                QVideoFrame.Format_ARGB32_Premultiplied,
                QVideoFrame.Format_RGB565,
                QVideoFrame.Format_RGB555]

    def start(self, format):
        imageFormat = QVideoFrame.imageFormatFromPixelFormat(format.pixelFormat())
        size = format.frameSize()
        if imageFormat != QImage.Format_Invalid and not size.isEmpty():
            self.imageFormat = imageFormat
            super().start(format)
            return True
        else:
            return False

    def stop(self):
        super().stop()

    def present(self, frame):
        if frame.isValid():
            cloneFrame = QVideoFrame(frame)
            cloneFrame.map(QAbstractVideoBuffer.ReadOnly)
            image = QImage(cloneFrame.bits(), cloneFrame.width(), cloneFrame.height(), cloneFrame.bytesPerLine(), self.imageFormat)

            # Draw the grid on the image before displaying it
            img_withGrid=self.draw_grid(image, self.horizontal_lines, self.vertical_lines, self.x, self.y, self.width, self.height)
            
            # Pass the frame to the parent widget to draw it.
            if isinstance(self.parent, QWidget):
                self.parent.DrawFrame(img_withGrid)
            
            return True

    def draw_grid(self, img: QImage, gridCountX, gridCountY, offsetX=None, offsetY=None, offsetWidth=None, offsetHeight=None):
        # Create a copy of the image to draw on
        image = QImage(img)

        # Create a QPainter object
        painter = QPainter(image)

        # Set the pen color to green
        pen = QPen(QColor(0, 255, 0))
        painter.setPen(pen)

        # If no offsets are provided, use the whole image
        if offsetX is None:
            offsetX = 0
        if offsetY is None:
            offsetY = 0
        if offsetWidth is None:
            offsetWidth = image.width()
        if offsetHeight is None:
            offsetHeight = image.height()

        # Calculate the size of the cells based on the grid count and offsets
        cell_width = offsetWidth // gridCountX
        cell_height = offsetHeight // gridCountY

        # Draw the grid
        for i in range(gridCountX):
            for j in range(gridCountY):
                x = offsetX + i * cell_width
                y = offsetY + j * cell_height
                painter.drawRect(QRect(x, y, cell_width, cell_height))

        painter.end()
        
        return image



class CustomViewfinder(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.surface=CustomVideoSurface(self)
        self.frame=None
    
    def DrawFrame(self, frame:QImage):
        self.frame=frame
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.frame:
            painter.drawImage(0,0, self.frame)