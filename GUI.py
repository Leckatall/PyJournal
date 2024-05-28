import sys
from PyQt6 import QtCore, uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTableView, QLineEdit
import DB_Mongo as db_manager
from datetime import datetime


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, columns, parent=None):
        super(TableModel, self).__init__(parent)
        self.columns = columns
        self._data: list[dict] = []

    def get_cell(self, row, column):
        return self._data[row].get(column, False)

    def add_row(self, row: dict):
        self._data.append(row)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()].get(self.columns[index.column()], QtCore.QVariant())
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return QtCore.QVariant()
        # What's the header for the given column?
        return self.columns[section]


class AddTask(QWidget):
    def __init__(self, update_task_list_method):
        super().__init__()
        self.ui = uic.loadUi("add_task.ui", self)
        self.update_method = update_task_list_method

        self.ConfirmAddTask.clicked.connect(self.add_task)

    def add_task(self):
        doc = {
            "TaskTitle": self.TaskTitle.text(),
            "TaskDescription": self.TaskDescription.toPlainText(),
            "TaskDeadline": self.Deadline.dateTime().toString(),
            "isTaskProject": self.ProjectTask.isChecked(),
            "isReccuringTask": self.ReccuringTask.isChecked()
        }
        print(f"{doc = }")
        db_manager.add_doc("Tasks", doc)
        self.update_method()
        self.close()


class AddEntry(QWidget):
    def __init__(self, update_entry_list_method):
        super().__init__()
        self.ui = uic.loadUi("add_entry.ui", self)
        self.update_method = update_entry_list_method

        self.ConfirmAddEntry.clicked.connect(self.add_entry)

    def add_entry(self):
        doc = {
            "EntryTitle": self.EntryTitle.text(),
            "EntryContents": self.EntryContent.toPlainText(),
            "EntryDateTime": self.EntryDateTime.dateTime().toPyDateTime()
        }
        print(f"{doc = }")
        db_manager.add_doc("Entries", doc)
        self.update_method()
        self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("mainwindow.ui", self)

        # Overview Tab
        self.NewTaskButton.clicked.connect(self.new_task)
        self.TaskList.currentItemChanged.connect(self.show_task_details)
        self.update_task_list()

        # Entries Tab
        self.NewEntryButton.clicked.connect(self.new_entry)

        self.entries_table_model = TableModel(["Date", "Title"])
        self.update_entries_table()
        self.EntriesTable.setModel(self.entries_table_model)
        self.EntriesTable.clicked.connect(self.show_entry_details)

        self.UpdateEntryButton.clicked.connect(self.update_entry)

        # Enables UpdateEntryButton when the entry is modified
        self.EntryTitle.editingFinished.connect(self.entry_modified)
        self.EntryContent.textChanged.connect(self.entry_modified)
        self.EntryDateTime.dateTimeChanged.connect(self.entry_modified)

    def entry_modified(self):
        self.UpdateEntryButton.setEnabled(True)

    def selected_entry(self):
        selected_row = self.EntriesTable.selectionModel().selectedRows()[0].row()
        title = self.entries_table_model.get_cell(selected_row, "Title")
        date = self.entries_table_model.get_cell(selected_row, "Date")
        query = {"EntryTitle": {"$eq": title},
                 "EntryDateTime": {"$gte": datetime.combine(date.toPyDate(), datetime.min.time()),
                                   "$lt": datetime.combine(date.addDays(1).toPyDate(), datetime.min.time())}}
        return db_manager.get_doc_from_where("Entries", query)

    def update_entry(self):
        selected_entry = self.selected_entry()
        # There is no property to check if datetime has been changed so will just always update lol
        # This works as a nice default tho :)
        update_operation = {"$set": {"EntryDateTime": self.EntryDateTime.dateTime().toPyDateTime()}}
        if self.EntryTitle.modified:
            update_operation["$set"]["EntryTitle"] = self.EntryTitle.text
        if self.EntryContent.document.modified:
            update_operation["$set"]["EntryContent"] = self.EntryContents.plainText

        db_manager.update_doc_from("Entries", selected_entry, update_operation)

    def new_entry(self):
        add_entry_window = AddEntry(self.update_entries_table)
        add_entry_window.show()

    def show_entry_details(self):
        selected_entry = self.selected_entry()

        self.EntryTitle.setText(selected_entry["EntryTitle"])
        self.EntryContent.setText(selected_entry["EntryContents"])
        self.EntryDateTime.setDateTime(QtCore.QDateTime(selected_entry["EntryDateTime"]))

        self.UpdateEntryButton.setEnabled(False)

        self.EntryTitle.setReadOnly(False)
        self.EntryContent.setReadOnly(False)
        self.EntryDateTime.setReadOnly(False)

    def update_entries_table(self):
        self.entries_table_model = TableModel(["Date", "Title"])
        for doc in db_manager.get_docs_from("Entries"):
            row = dict()
            row["Date"] = QtCore.QDateTime(doc["EntryDateTime"]).date()
            row["Title"] = doc["EntryTitle"]
            self.entries_table_model.add_row(row)
        self.EntriesTable.setModel(self.entries_table_model)

    def new_task(self):
        add_task_window = AddTask(self.update_task_list)
        add_task_window.show()

    def show_task_details(self):
        query = {"TaskTitle": {"$eq": self.TaskList.currentItem().text()}}
        self.TaskDetails.setText(db_manager.get_doc_from_where("Tasks", query)["TaskDescription"])

    def update_task_list(self):
        self.TaskList.clear()
        for doc in db_manager.get_docs_from("Tasks"):
            self.TaskList.addItem(doc["TaskTitle"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

# app = QtWidgets.QApplication(sys.argv)
#
# window = MainWindow()
# window.show()
#
# app.exec()
