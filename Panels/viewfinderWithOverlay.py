from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import Qt

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
        self.setMinimumSize(200, 200)

    def update_grid(self, x=None, y=None, width=None, height=None, horizontal_lines=None, vertical_lines=None, offsetX=None, offsetY=None):
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
        if offsetX is not None:
            self.offsetX = offsetX
            self.width=self.width-self.offsetX
        if offsetY is not None:
            self.offsetY = offsetY
            self.height=self.height-self.offsetY
        self.update()

    def paintEvent(self, event):
        # Call the parent paintEvent to ensure the viewfinder is drawn correctly
        super().paintEvent(event)

        # Create a QImage of the current frame
        image = QImage(self.size(), QImage.Format_ARGB32)
        
        # Create a QPainter to draw on the image
        painter = QPainter(image)
        
        painter.setPen(Qt.red)
        
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        # Draw horizontal lines
        for i in range(1, self.horizontal_lines):
            y = self.y + i * (self.height / self.horizontal_lines)
            painter.drawLine(int(self.x), int(y), int(self.x + self.width), int(y))

        # Draw vertical lines
        for i in range(1, self.vertical_lines):
            x = self.x + i * (self.width / self.vertical_lines)
            painter.drawLine(int(x), int(self.y), int(x), int(self.y + self.height))
        
        painter.end()  # End drawing

        # Rescale the image (replace new_width and new_height with your desired dimensions)
        viewfinder_size = self.size()
        viewfinder_width = viewfinder_size.width()
        viewfinder_height = viewfinder_size.height()
        image = image.scaled(viewfinder_width, viewfinder_height, Qt.KeepAspectRatio)

        # Draw the rescaled image onto the viewfinder
        painter.begin(self)
        painter.drawImage(0, 0, image)
        painter.end()
