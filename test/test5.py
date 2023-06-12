import sys
from PyQt5 import QtWidgets

#from Panels.cam_panel import cam_panel

import subprocess

app = QtWidgets.QApplication([])
msg = QtWidgets.QMessageBox()
try:
    msg.setWindowTitle('Succses')
    result = subprocess.run(['python', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    version = result.stdout.decode('utf-8').strip()
    if not version:
        version = result.stderr.decode('utf-8').strip()
    msg.setText(f'Python is installed: {version}')
except FileNotFoundError:
    msg.setWindowTitle('Error')
    #print('Python is not installed')
    msg.setText('Python is not installed')
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()
    sys.exit()

msg.exec_()
del app