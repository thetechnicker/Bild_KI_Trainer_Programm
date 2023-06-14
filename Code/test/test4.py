import sys
from PyQt5 import QtWidgets
import platform

app = QtWidgets.QApplication([])
msg = QtWidgets.QMessageBox()

try:
    version = platform.python_version()
    msg.setWindowTitle('Success')
    msg.setText(f'Python is installed: {version}')
except Exception as e:
    msg.setWindowTitle('Error')
    msg.setText(f'Error: {str(e)}')
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()
    sys.exit()

msg.exec_()
del app