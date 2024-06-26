
from PyQt6 import QtCore, uic, QtWidgets
from PyQt6.QtWidgets import QWidget
import DB_Mongo as db_manager


class AddEntry(QWidget):
    def __init__(self, update_entry_list_method):
        super().__init__()
        self.ui = uic.loadUi("add_entry.ui", self)
        self.update_method = update_entry_list_method

        self.EntryDateTime.setDateTime(QtCore.QDateTime.currentDateTime())
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
