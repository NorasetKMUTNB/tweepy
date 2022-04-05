import sys

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QDateTimeEdit, QApplication
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPalette, QTextCharFormat

from TwitterManager import *
twm = TwitterManger()

from new_key_interface import *
from datetime import datetime, timedelta


class DialogNewKey(QDialog):
    def __init__(self, key, parent=None):
        super().__init__(parent)
        self.key = key

        self.setWindowTitle("NEW KEY")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("% s is a new keyword, Do you want to search?"%self.key)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class DialogDelete(QDialog):
    def __init__(self, key, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Delete?")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Do you sure to detele {}?".format(key))
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class UpdateDialog(QDialog):
    def __init__(self, key, parent=None):
        super().__init__(parent)
        self.key = key
        self.ui = Ui_until_date_window()
        self.ui.setupUi(self)
        self.begin_date = None
        self.end_date = None

        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(self.palette().brush(QPalette.Highlight))
        self.highlight_format.setForeground(self.palette().color(QPalette.HighlightedText))

        # date now
        self.date_now = QDate.currentDate()

        date_now_str = self.date_now.toString(Qt.ISODate)
        date_now_obj = datetime.strptime(date_now_str, '%Y-%m-%d')

        self.ui.date_label.setText("TODAY : "+ date_now_str + " UTC")
        self.ui.keyword_label.setText(self.key)

        until_date_str = (date_now_obj - timedelta(days=7)).date().isoformat()
        until_date_obj = QDate.fromString(until_date_str, Qt.ISODate)
        print(until_date_obj)

        self.ui.aday_calendarWidget.setDateRange(until_date_obj, self.date_now);

        self.ui.aday_calendarWidget.clicked.connect(self.date_is_clicked)
        # print(super().dateTextFormat())

    def format_range(self, format):
        if self.begin_date and self.end_date:
            d0 = min(self.begin_date, self.end_date)
            d1 = max(self.begin_date, self.end_date)
            while d0 <= d1:
                self.ui.aday_calendarWidget.setDateTextFormat(d0, format)
                d0 = d0.addDays(1)

    def date_is_clicked(self, date):
        # reset highlighting of previously selected date range
        self.format_range(QTextCharFormat())
        if QApplication.instance().keyboardModifiers() & Qt.ShiftModifier and self.begin_date:
            self.end_date = date
            # set highilighting of currently selected date range
            self.format_range(self.highlight_format)
        else:
            self.begin_date = date
            self.end_date = date

        # print(self.begin_date.toString(Qt.ISODate), self.end_date.toString(Qt.ISODate))

        self.show()




