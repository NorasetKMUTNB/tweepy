########################################################################
## CONVERT .UI & .QRC
# pyrcc5 resources.qrc -o resource_rc.py
# pyuic5 -x ui_interface.ui -o tweety_interface.py 
# pyuic5 -x dialog_date.ui -o date_interface.py 
# pyuic5 -x popup_progress.ui -o popup_progress.py 
########################################################################

########################################################################
## IMPORTS
########################################################################
from contextlib import contextmanager
import os
import sys
import re

import shutil
import threading

import pandas as pd
from time import sleep

from dialog_gui import *
from TwitterManager import *

########################################################################
# IMPORT GUI FILE
from tweety_interface import *
from PyQt5.QtWidgets import QFileDialog, QListWidget, QTableWidgetItem, QApplication, QMainWindow, qApp, QListWidgetItem, QDialog, QMenu
from PyQt5.QtCore import Qt, QEvent, QDate
########################################################################

########################################################################
## MAIN WINDOW CLASS
########################################################################
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_App()
        self.ui.setupUi(self)
        self.list_keyword = []
        self.key = ''
        self.twm = twitter_manager()

        self.pbar = PopupProgress('')

        self.getListKeyword()
        self.date_now = QDate.currentDate()
        # print(QDate.fromString(self.date_now.toString(Qt.ISODate), Qt.ISODate))

        #######################################################################
        # ADD FUNCTION ELEMENT
        #######################################################################
        self.ui.date_label.setText("TODAY : "+ self.date_now.toString(Qt.ISODate) + ' UTC+00:00')
        self.ui.Search_LineEdit.returnPressed.connect(self.search)
        self.ui.SearchList.itemDoubleClicked.connect(self._handleDoubleClick)   # double-click
        self.ui.SearchList.installEventFilter(self) # right-click

        self.ui.seldate_btn.clicked.connect(self.selection_date)
        self.ui.base_date_comboBox.currentTextChanged.connect(self.date_changed)
        self.ui.reload_btn.clicked.connect(self.getListKeyword)
        #######################################################################
        # SHOW WINDOW
        #######################################################################
        self.show()
        #######################################################################

    ########################################################################
    ## FUNCTION
    ########################################################################
    def getListKeyword(self):
        """" Collect keywords have been searched """
        self.ui.SearchList.clear()
        folder = './/backup'
        self.list_keyword = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
        self.ui.SearchList.addItems(self.list_keyword)


    def loaddate(self, key):
        self.ui.base_date_comboBox.currentTextChanged.disconnect(self.date_changed)
        self.ui.Search_LineEdit.clear()
        self.ui.base_date_comboBox.clear()
        self.list_date = ['All']
        self.dict_date = {}
        self.key = key

        self.ui.Search_LineEdit.setText("{}".format(self.key))

        path = ".//backup//{}//file_date".format(self.key)
        for date in os.listdir(path):
            if date.endswith(".csv"):
                # Prints only text file present in My Folder
                date = date.replace('.csv', '')
                # print(x)
                self.list_date.append(date.split("_")[1])
                self.dict_date[date.split("_")[1]] = True

        self.ui.base_date_comboBox.addItems(self.list_date)
        self.ui.base_date_comboBox.currentTextChanged.connect(self.date_changed)


    def loaddata(self):
        """ This method will make all table """
        self.pbar.set_key_progress(self.key)
        self.pbar.show()

        self.workerCSV = WorkerCSV(self)
        self.workerCSV.start()
        self.workerCSV.finished.connect(self.finish_worker_csv)
        self.workerCSV.update_progress.connect(self.update_worker)


    def _handleDoubleClick(self, item): # double-click
        """ Selection item in Listwidget show dataframe 
        (i.e. it select keyword will show dataframe in table). 
        """
        self.key = item.text()
        self.loaddata()
        self.loaddate(self.key)


    # right-click item in listwidget
    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.ui.SearchList:
            menu = QMenu()

            upact = menu.addAction('Update')
            delact = menu.addAction('Delete')

            action = menu.exec_(event.globalPos())
            item = source.itemAt(event.pos())

            self.key = item.text()

            if action == upact:
                updia = UpdateDialog(self.key)   
                if updia.exec():
                    self.begin_date = updia.begin_date.toString(Qt.ISODate)
                    self.end_date = updia.end_date.toString(Qt.ISODate)

                    self.pbar = PopupProgress(self.key)
                    self.pbar.show()

                    self.workerTW = WorkerTweet(self)
                    self.workerTW.start()
                    self.workerTW.finished.connect(self.finish_worker_tweet)
                    self.workerTW.update_progress.connect(self.update_worker)

            elif action == delact:
                dlg = DialogDelete(self.key)
                if dlg.exec():
                    dir_path = './backup/{}'.format(self.key)
                    try:
                        shutil.rmtree(dir_path)
                        self.getListKeyword()

                    except OSError as e:
                        print("Error: %s : %s" % (dir_path, e.strerror))

            return True
        return super().eventFilter(source, event)


    def search(self):
        # getting text from the line edit
        self.key = self.ui.Search_LineEdit.text().lower()

        # check keyword is in listwidget
        if self.key in self.list_keyword: 
            self.loaddata()
            self.loaddate(self.key)
        else : 
            dlg = DialogNewKey(self.key)
            if dlg.exec():
                updia = UpdateDialog(self.key)
                if updia.exec():
                    self.twm.create_directory(self.key)

                    self.begin_date = updia.begin_date.toString(Qt.ISODate)
                    self.end_date = updia.end_date.toString(Qt.ISODate)

                    self.pbar.set_key_progress(self.key)
                    self.pbar.show()

                    self.workerTW = WorkerTweet(self)
                    self.workerTW.start()
                    self.workerTW.finished.connect(self.finish_worker_tweet)
                    self.workerTW.update_progress.connect(self.update_worker)


    def selection_date(self):
        self.key = self.ui.base_label.text().lower()
        datedia = DateDialog(self.key, self)
        datedia.show()


    def date_changed(self, value):
        self.pbar.set_key_progress(self.key)
        self.pbar.show()
        self.DateSelection = value

        self.workerCD = WorkerChangeDate(self)
        self.workerCD.start()
        self.workerCD.finished.connect(self.finish_worker_change_date)
        self.workerCD.update_progress.connect(self.update_worker)


    def finish_worker_tweet(self):
        self.workerTW.stop()
        self.pbar.close()
        self.getListKeyword()
        self.loaddata()

    def finish_worker_csv(self):
        self.workerCSV.stop()
        self.pbar.close()
        self.loaddate(self.key)

    def finish_worker_change_date(self):
        self.workerCD.stop()
        self.pbar.close()

    def update_worker(self, val):
        self.pbar.ui.progressBar.setValue(val)


    ########################################################################


########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END===>
########################################################################
    