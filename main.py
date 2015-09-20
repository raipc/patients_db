#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from PyQt4 import QtGui, QtSql, QtCore

from view import Ui_MainWindow
from config import debug as config
from query_helpers import generate_query, get_document_types_query


class View(QtGui.QMainWindow):
    def __init__(self):
        super(View, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        validator = QtGui.QIntValidator(0, 150)
        self.ui.age_from.setValidator(validator)
        self.ui.age_to.setValidator(validator)

        self.db = None
        self.model = None
        self.open_database()

        doc_query = QtSql.QSqlQuery()
        doc_query.exec_(get_document_types_query())
        self.document_type = {}
        while doc_query.next():
            qs = unicode(doc_query.value(0).toString())
            self.document_type[qs] = doc_query.value(1).toString()
            self.ui.document_type.addItem(qs)
        self.ui.document_type.setCurrentIndex(-1)

        self.ui.age_from.textChanged.connect(lambda: update_date_to(
            self))
        self.ui.age_to.textChanged.connect(lambda: update_date_from(
          self))

        self.connect(self.ui.query_button, QtCore.SIGNAL("clicked()"),
                     self.query_on_button_click)
        self._filter_from = DateFromFilter()
        self._filter_to = DateToFilter()
        self.ui.birth_date_from.installEventFilter(self._filter_from)
        self.ui.birth_date_to.installEventFilter(self._filter_to)

    def _get_fields_values(self):
        return (
            self.ui.last_name.text(),
            self.ui.first_name.text(),
            self.ui.patr_name.text(),
            self._get_document_type(self.ui.document_type),
            self._prepare_serial(self.ui.document_serial.text()),
            self.ui.document_number.text(),
            self.ui.sex.currentText(),
            self._get_date(self.ui.birth_date_from),
            self._get_date(self.ui.birth_date_to),
            self.ui.age_from.text(),
            self.ui.age_to.text(),
            self.ui.snils_number.text()
        )

    def _get_date(self, form_object):
        if isinstance(form_object, QtGui.QDateEdit):
            return form_object.date().toString('yyyy-MM-dd')
        try:
            return form_object.text()
        except:
            return ""

    def _get_document_type(self, form_object):
        if isinstance(form_object, QtGui.QComboBox):
            try:
                return self.document_type[unicode(form_object.currentText())]
            except:
                return ""
        try:
            return form_object.text()
        except:
            return ""

    def _prepare_serial(self, serial):
        without_spaces = unicode(serial).replace(" ", "")
        if len(without_spaces) < 2:
            return without_spaces
        return without_spaces[:2] + " " + without_spaces[2:]

    @QtCore.pyqtSlot()
    def query_on_button_click(self):
        query = generate_query(*list(unicode(value)
                               for value in self._get_fields_values()))
        self.model.setQuery(query)
        self.ui.response_table.resizeColumnsToContents()
        # with open('queries.log', "a") as logfile:
        #   logfile.write(str(QtCore.QDate.currentDate().toString)+"\n")
        #   logfile.write(query+"\n")

    def create_db_connection(self):
        db = QtSql.QSqlDatabase.addDatabase(config.DATABASE_DRIVER)
        db.setDatabaseName(config.DATABASE_NAME)
        db.setHostName(config.DATABASE_HOST)
        db.setPort(config.DATABASE_PORT)
        db.setUserName(config.DATABASE_USER)
        db.setPassword(config.DATABASE_PASSWORD)
        if not db.open():
            sys.stderr.write(
                "Error connecting to database %s. Program is terminated\n" %
                config.DATABASE_NAME)
            sys.exit(1)
        return db

    def open_database(self):
        if self.db:
            self.close_database()
        self.db = self.create_db_connection()
        self.model = QtSql.QSqlQueryModel()
        self.ui.response_table.setModel(self.model)

    def close_database(self):
        self.ui.response_table.setModel(None)
        del self.model
        self.db.close()
        del self.db
        QtSql.QSqlDatabase.removeDatabase(config.DATABASE_NAME)

    def closeEvent(self, event):
        self.close_database()


def update_age_to(self):
    now = QtCore.QDate.currentDate()
    date = self.ui.birth_date_from.date()
    years_to = str(int(date.daysTo(now) / 365.25))
    target = self.ui.age_to
    if target.text() != "":
        target.setText(years_to)


def update_age_from(self):
    now = QtCore.QDate.currentDate()
    date = self.ui.birth_date_to.date().addYears(-1).addDays(1)
    years_to = str(int(date.daysTo(now) / 365.25))
    target = self.ui.age_from
    if target.text() != "":
        target.setText(years_to)


def update_date_from(self):
    age = self.ui.age_to
    now = QtCore.QDate.currentDate()
    years_to = int(self.ui.birth_date_from.date().daysTo(now) / 365.25)
    if years_to - int(age.text()) != 0:
        self.ui.birth_date_from.setDate(
            now.addYears(-int(age.text()) - 1).addDays(1))


def update_date_to(self):
    age = self.ui.age_from
    now = QtCore.QDate.currentDate()
    years_to = int(self.ui.birth_date_from.date().daysTo(now) / 365.25)
    if years_to - int(age.text()) != 0:
        self.ui.birth_date_to.setDate(now.addYears(-int(age.text())))


def make_calendar(element, parent, qdate):
    height = element.height()
    element.deleteLater()
    element = QtGui.QDateEdit()
    element.setDate(qdate)
    element.setFixedHeight(height)
    element.setFixedWidth(100)
    element.setFrame(False)
    element.setCalendarPopup(True)
    element.setDisplayFormat("dd.MM.yyyy")
    parent.addWidget(element)
    return element


class DateFromFilter(QtCore.QObject):
    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and (
                isinstance(widget, QtGui.QLineEdit)):
            widget.removeEventFilter(self)
            date = QtCore.QDate(1900, 1, 1)
            if window.ui.age_to.text():
                date = QtCore.QDate().currentDate().addYears(
                    -int(window.ui.age_to.text()))
            window.ui.birth_date_from = make_calendar(
                widget,
                window.ui.birth_date_from_layout,
                date
            )
            window.ui.birth_date_from.dateChanged.connect(
                lambda: update_age_to(window))
        return False


class DateToFilter(QtCore.QObject):
    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and (
                isinstance(widget, QtGui.QLineEdit)):
            date = QtCore.QDate().currentDate()
            if window.ui.age_from.text():
                date = date.addYears(
                    -int(window.ui.age_from.text()))
            widget.removeEventFilter(self)
            window.ui.birth_date_to = make_calendar(
                widget,
                window.ui.birth_date_to_layout,
                date
            )
            window.ui.birth_date_to.dateChanged.connect(
                lambda: update_age_from(window))
        return False


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = View()
    window.show()
    sys.exit(app.exec_())
