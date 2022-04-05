########################################################################
## CONVERT .UI & .QRC
# pyrcc5 resources.qrc -o resource_rc.py
# pyuic5 -x ui_interface.ui -o tweety_interface.py 
# pyuic5 -x dialog_newkey.ui -o new_key_interface.py 
########################################################################

########################################################################
## IMPORTS
########################################################################
from contextlib import contextmanager
import os
import sys
import re

import pandas as pd
from dialog_gui import *
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

        self.getListKeyword()

        self.date_now = QDate.currentDate()
        # print(QDate.fromString(self.date_now.toString(Qt.ISODate), Qt.ISODate))

        #######################################################################
        # ADD FUNCTION ELEMENT
        #######################################################################
        self.ui.Search_LineEdit.returnPressed.connect(self.search)
        self.ui.date_label.setText("TODAY : "+ self.date_now.toString(Qt.ISODate) + ' UTC')
        self.ui.SearchList.installEventFilter(self)
        self.ui.SearchList.itemDoubleClicked.connect(self._handleDoubleClick)
        self.ui.base_date_combobox.currentTextChanged.connect(self.date_changed)
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
        """" Collect keywords have been searched 
        """
        self.ui.SearchList.clear()
        folder = './/backup'
        self.list_keyword = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
        self.ui.SearchList.addItems(self.list_keyword)
        

    def loaddata(self, key):
        """ This method will make all table """
        # base_table
        self.ui.base_label.setText("{}".format(key))
        self.df_base = pd.read_csv('.//backup//{}//{}.csv'.format(key, key))

        len_row_base = len(self.df_base.index)
        len_col_base = len(self.df_base.columns)

        self.ui.base_table.setColumnCount(len_col_base)
        self.ui.base_table.setRowCount(len_row_base)
        self.ui.base_table.setHorizontalHeaderLabels(self.df_base.columns)

        for i in range(len_row_base):
            for j in range(len_col_base):
                self.ui.base_table.setItem(i ,j, QTableWidgetItem(str(self.df_base.iat[i, j])))

        self.ui.base_table.resizeColumnsToContents()
        self.ui.status_base_label.setText("{} Tweets".format(len_row_base))

        # word_table
        self.ui.word_label.setText("{}".format(key))
        self.df_word = pd.read_csv('.//backup//{}//{}_count_word.csv'.format(key, key))

        len_row_word = len(self.df_word.index)
        len_col_word = len(self.df_word.columns)

        self.ui.word_table.setColumnCount(len_col_word)
        self.ui.word_table.setRowCount(len_row_word)
        self.ui.word_table.setHorizontalHeaderLabels(self.df_word.columns)

        for i in range(len_row_word):
            for j in range(len_col_word):
                self.ui.word_table.setItem(i ,j, QTableWidgetItem(str(self.df_word.iat[i, j])))

        self.ui.word_table.resizeColumnsToContents()
        self.ui.status_word_label.setText("{} Words".format(len_row_word))
        
        # hashtag_table
        self.ui.hashtag_label.setText("{}".format(key))
        self.df_hashtag = pd.read_csv('.//backup//{}//{}_count_hashtag.csv'.format(key, key))

        len_row_hashtag = len(self.df_hashtag.index)
        len_col_hashtag = len(self.df_hashtag.columns)

        self.ui.hashtag_table.setColumnCount(len_col_hashtag)
        self.ui.hashtag_table.setRowCount(len_row_hashtag)
        self.ui.hashtag_table.setHorizontalHeaderLabels(self.df_hashtag.columns)

        for i in range(len_row_hashtag):
            for j in range(len_col_hashtag):
                self.ui.hashtag_table.setItem(i ,j, QTableWidgetItem(str(self.df_hashtag.iat[i, j])))

        self.ui.hashtag_table.resizeColumnsToContents()
        self.ui.status_hashtag_label.setText("{} Hashtags".format(len_row_hashtag))
        

    def _handleDoubleClick(self, item):
        """ Selection item in Listwidget show dataframe 
        (i.e. it select keyword will show dataframe in table).
        """

        self.ui.Search_LineEdit.clear()
        self.ui.base_date_combobox.clear()
        list_date = ['All']
        self.key = item.text()
        # item.setSelected(False)
        self.ui.Search_LineEdit.setText("{}".format(self.key))
        self.loaddata(self.key)

        path = ".//backup//{}//file_date".format(self.key)
        for date in os.listdir(path):
            if date.endswith(".csv"):
                # Prints only text file present in My Folder
                date = date.replace('.csv', '')
                # print(x)
                list_date.append(date.split("_")[1])

        self.ui.base_date_combobox.addItems(list_date)

    # right-cilck item in listwidget
    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.ui.SearchList:
            menu = QMenu()

            upact = menu.addAction('Update')
            delact = menu.addAction('Delete')

            action = menu.exec_(event.globalPos())
            item = source.itemAt(event.pos())

            if action == upact:
                print("update ", item.text())
                updia = UpdateDialog(item.text())   
                if updia.exec():
                    print("Success!")
                    begin_date = updia.begin_date.toString(Qt.ISODate)
                    end_date = updia.end_date.toString(Qt.ISODate)
                    twm.serach_tweet(item.text(), end_date, begin_date)

                    self.getListKeyword()
                else:
                    print("Cancel!")

            elif action == delact:
                print("delete ", item.text())
                dlg = DialogDelete(item.text())
                if dlg.exec():
                    print("Success!")
                else:
                    print("Cancel!")

            return True
        return super().eventFilter(source, event)


    def search(self):
        # getting text from the line edit
        self.key = self.ui.Search_LineEdit.text().lower()
        # print(self.key)

        # check keyword in listwidget
        if self.key in self.list_keyword: 
            # print(self.key)
            self.loaddata(self.key)
        else : 
            # print("% s it's new word" %self.key)
            dlg = DialogNewKey(self.key)
            if dlg.exec():
                print("Success!")
                updia = UpdateDialog(self.key)
                if updia.exec():
                    twm.create_directory(self.key)
                    begin_date = updia.begin_date.toString(Qt.ISODate)
                    end_date = updia.end_date.toString(Qt.ISODate)
                    twm.serach_tweet(self.key, end_date, begin_date)

                    self.getListKeyword()
                else:
                    pass
            else:
                print("Cancel!")


    def date_changed(self, value):
        self.key = self.ui.Search_LineEdit.text().lower()

        if value == 'All':
            key = self.ui.base_label.text()
            self.df_base = pd.read_csv('.//backup//{}//{}.csv'.format(key, key))

            len_row_base = len(self.df_base.index)
            len_col_base = len(self.df_base.columns)

            self.ui.base_table.setColumnCount(len_col_base)
            self.ui.base_table.setRowCount(len_row_base)
            self.ui.base_table.setHorizontalHeaderLabels(self.df_base.columns)

            for i in range(len_row_base):
                for j in range(len_col_base):
                    self.ui.base_table.setItem(i ,j, QTableWidgetItem(str(self.df_base.iat[i, j])))

            self.ui.base_table.resizeColumnsToContents()
            self.ui.status_base_label.setText("{} Tweets".format(len_row_base))

        elif value != '':
            key = self.ui.base_label.text()
            self.df_base = pd.read_csv('.//backup//{}//file_date//{}_{}_twitterCrawler.csv'.format(key, key, value))

            len_row_base = len(self.df_base.index)
            len_col_base = len(self.df_base.columns)

            self.ui.base_table.setColumnCount(len_col_base)
            self.ui.base_table.setRowCount(len_row_base)
            self.ui.base_table.setHorizontalHeaderLabels(self.df_base.columns)

            for i in range(len_row_base):
                for j in range(len_col_base):
                    self.ui.base_table.setItem(i ,j, QTableWidgetItem(str(self.df_base.iat[i, j])))

            self.ui.base_table.resizeColumnsToContents()
            self.ui.status_base_label.setText("{} Tweets".format(len_row_base))

        
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
