from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtGui import QPainter, QImage, QColor, QPen
from PyQt5.QtCore import Qt, QRect

class CustomViewfinder(QCameraViewfinder):
    def __init__(self, parent=None):
        super().__init__(parent)
        viewfinder_size = self.size()
        viewfinder_width = viewfinder_size.width()
        viewfinder_height = viewfinder_size.height()
        self.x = 10
        self.y = 10
        self.width = viewfinder_width
        self.height = viewfinder_height
        self.horizontal_lines = 10
        self.vertical_lines = 10
        self.offsetX=0
        self.offsetY=0
        self.setMinimumSize(400, 300)


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
        self.update()

    def paintEvent(self, event):
        # Call the parent paintEvent to ensure the viewfinder is drawn correctly
        super().paintEvent(event)

        # Create a QImage of the current frame
        image = QImage(self.size(), QImage.Format_ARGB32)

        # Create a QPainter to draw on the image
        painter = QPainter(image)

        # Set the pen color to black
        pen = QPen(QColor(0,0,0))
        painter.setPen(pen)

        # Draw the grid on the image
        image = self.draw_grid(image, self.horizontal_lines, self.vertical_lines, self.x, self.y, self.width, self.height)

        # Rescale the image (replace new_width and new_height with your desired dimensions)
        viewfinder_size = self.size()
        viewfinder_width = viewfinder_size.width()
        viewfinder_height = viewfinder_size.height()
        image = image.scaled(viewfinder_width, viewfinder_height, Qt.KeepAspectRatio)

        painter.drawImage(0, 0, image)
        painter.end()


    def draw_grid(self, image: QImage, gridCountX, gridCountY, offsetX=None, offsetY=None, offsetWidth=None, offsetHeight=None):
        # Create a copy of the image to draw on
        image = QImage(image)

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