# importing the required libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
 
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
         
         # string value
        title = "Crawler"
 
        # set the title
        self.setWindowTitle(title)
 
        # setting  the geometry of window
        self.resize(349, 108)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.key_label = QtWidgets.QLabel(self)
        self.key_label.setStyleSheet("font: 11pt \"Helvetica\";")
        self.key_label.setObjectName("key_label")
        self.gridLayout.addWidget(self.key_label, 0, 0, 1, 1)
        self.progress_label = QtWidgets.QLabel(self)
        self.progress_label.setObjectName("progress_label")
        self.gridLayout.addWidget(self.progress_label, 0, 1, 1, 1, QtCore.Qt.AlignRight)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 2)

        # set key_label
        self.show()
 
# create pyqt5 app
App = QApplication(sys.argv)
 
# create the instance of our Window
window = Window()
 
# start the app
sys.exit(App.exec())