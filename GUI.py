import sys
from PyQt6 import QtCore, uic, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTableView, QLineEdit, QComboBox

import DB_Mongo as db_manager
from datetime import datetime
import measurement.measures
import CustomWidgets

from AddTaskWidget import AddTask
from AddEntryWidget import AddEntry
from ManageEventClassWidget import ManageEventClasses
from NewEventInstanceWidget import NewEventInstance
from NewProjectClassWidget import NewProjectClass
from ManageEventClassWidget import ManageEventClasses

# TODO: Create BandedTableModel with support for headers that stretch multiple rows/columns
# Turns out this is pretty much impossible to do cleanly :(
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, headers, parent=None, orientation=Qt.Orientation.Horizontal):
        super(TableModel, self).__init__(parent)
        self.headers = headers
        self.orientation = orientation
        self.groupings = []
        self._data: list[dict] = []

    def get_cell(self, row, column):
        return self._data[row].get(column, False)

    def add_row(self, row: dict):
        self._data.append(row)

    def add_group(self, start, end, title):
        self.groupings.append((start, end, title))

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self.orientation == Qt.Orientation.Horizontal:
            return len(self._data)
        elif self.orientation == Qt.Orientation.Vertical:
            return len(self.headers)
        else:
            print(f"Unknown Orientation: {self.orientation}")

    def columnCount(self, parent=QtCore.QModelIndex()):
        if self.orientation == Qt.Orientation.Horizontal:
            return len(self.headers)
        elif self.orientation == Qt.Orientation.Vertical:
            return len(self._data)
        else:
            print(f"Unknown Orientation: {self.orientation}")

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if role == Qt.ItemDataRole.DisplayRole:
            if self.orientation == Qt.Orientation.Horizontal:
                return self._data[index.row()].get(self.headers[index.column()], QtCore.QVariant())
            elif self.orientation == Qt.Orientation.Vertical:
                return self._data[index.column()].get(self.headers[index.row()], QtCore.QVariant())
            else:
                print(f"Unknown Orientation: {self.orientation}")
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return QtCore.QVariant()
        if orientation != self.orientation:
            return f"Row {section}"
        # What's the header for the given section?
        return self.headers[section]


from dataclasses import dataclass


@dataclass
class EventProperty:
    measure: measurement.base.MeasureBase
    value: int
    default_unit: str
    name: str
    appropriate_units: list[str]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("mainwindow.ui", self)

        self.TabWidget.currentChanged.connect(self.tab_update)

        # Overview Tab
        self.NewTaskButton.clicked.connect(self.new_task)
        self.TaskList.currentItemChanged.connect(self.show_task_details)
        self.ManageEventClasses.clicked.connect(self.manage_event_classes)
        self.update_task_list()

        # Entries Tab
        self.NewEntryButton.clicked.connect(self.new_entry)

        self.update_entries_table()
        self.EntriesTable.clicked.connect(self.show_entry_details)

        self.UpdateEntryButton.clicked.connect(self.update_entry)

        # Enables UpdateEntryButton when the entry is modified
        def entry_modified():
            self.UpdateEntryButton.setEnabled(True)

        self.EntryTitle.editingFinished.connect(entry_modified)
        self.EntryContent.textChanged.connect(entry_modified)
        self.EntryDateTime.dateTimeChanged.connect(entry_modified)

        # Events Tab
        self.NewEventClass: QPushButton
        self.NewEventClass.clicked.connect(self.new_event_class)
        self.NewEventInstance.clicked.connect(self.new_event_instance)
        self.update_event_classes_tree()
        self.EventClassTree.itemClicked.connect(self.show_event_class_details)

        self.events_table_model = TableModel(["Date", "Type"])
        self.update_events_table()
        self.EventsTable.clicked.connect(self.show_event_details)

        self.event_details_table_model = TableModel(["Date", "Type", "Comment", "Properties"])
        self.EventDetailsTable.setModel(self.event_details_table_model)

        self.EditEventClass.clicked.connect(self.edit_event_class)

        # Projects Tab
        self.NewProjectClass.clicked.connect(self.new_project_class)

    def tab_update(self, new_tab_index):
        if new_tab_index == 1:
            self.new_entry()

    def new_project_class(self):
        new_project_class_window = NewProjectClass(self.update_project_classes_tree)
        new_project_class_window.show()

    def selected_event(self):
        print("finding selected event")
        selected_indexes = self.EventsTable.selectionModel().selectedRows()
        if not selected_indexes:
            return False
        selected_row = selected_indexes[0].row()
        date = self.events_table_model.get_cell(selected_row, "Date")
        type = self.events_table_model.get_cell(selected_row, "Type")
        query = {"Class": {"$eq": type},
                 "date_time": {"$gte": datetime.combine(date.toPyDate(), datetime.min.time()),
                                   "$lt": datetime.combine(date.addDays(1).toPyDate(), datetime.min.time())}}
        return db_manager.get_doc_from_where("Events", query)

    def manage_event_classes(self):
        manage_event_classes_window = ManageEventClasses(self.update_event_classes_tree)
        manage_event_classes_window.show()

    def show_event_details(self):
        if not (selected_event := self.selected_event()):
            return False
        print(f"{selected_event = }")
        self.event_details_table_model = TableModel(["Date", "Type", "Comment", "Properties"],
                                                    orientation=Qt.Orientation.Vertical)
        row = dict()
        row["Date"] = QtCore.QDateTime(selected_event["date_time"]).date()
        row["Type"] = selected_event["Class"]
        row["Comment"] = selected_event["Comment"]
        # Properties is a dictionary, so we want to represent that as a table in the table lol
        # event_properties_table_model = TableModel(list(selected_event["Properties"].keys()),
        #                                                 orientation=Qt.Orientation.Vertical)
        #
        # row["Properties"] = TableViewDelegate(QTableView())
        # row["Properties"].table_view.setModel(event_properties_table_model)
        # event_properties_table_model.add_row(selected_event["Properties"])

        # Might be easier to just show it as a string for now lmao
        row["Properties"] = "\n".join([f"{key} : {value}" for key, value in selected_event["Properties"].items()])
        self.event_details_table_model.add_row(row)
        print(f"{row = }")
        self.EventDetailsTable.setModel(self.event_details_table_model)

    def update_events_table(self):
        self.events_table_model = TableModel(["Date", "Type"])
        for doc in db_manager.get_docs_from("Events"):
            row = dict()
            row["Date"] = QtCore.QDateTime(doc["date_time"]).date()
            row["Type"] = doc["Class"]
            self.events_table_model.add_row(row)
        self.EventsTable.setModel(self.events_table_model)

    def new_event_instance(self):
        new_event_window = NewEventInstance(self.update_events_table)
        new_event_window.show()

    def update_event_classes_tree(self):
        self.EventClassTree.clear()
        event_classes = db_manager.get_docs_from("EventClasses")
        tree_item_dict = dict()
        for event_class in event_classes:
            if event_class["Parent"]:
                if not (parent := tree_item_dict.get(event_class["Parent"], False)):
                    event_classes.append(parent)
                    print("parent not processed adding to end of list")
                    continue
            else:
                parent = self.EventClassTree
            event_defaults = event_class["Defaults"]
            event_properties = event_class["Properties"]
            new_item = QtWidgets.QTreeWidgetItem(parent, [event_class["Name"], ",\n".join(
                [f"{key}: {value}" for key, value in event_properties.items()] +
                [f"{key}: ({value})" for key, value in event_defaults.items()])])
            tree_item_dict[event_class["Name"]] = new_item

    def show_event_class_details(self):
        properties_table_model = TableModel(["Property Name", "Data Type", "Default Value"])
        properties = dict()
        defaults = dict()
        selected_class = db_manager.get_doc_from_where("EventClasses",
                                                       {"Name": {"$eq": self.EventClassTree.currentItem().text(0)}})
        properties.update(selected_class["Properties"])
        defaults.update(selected_class["Defaults"])
        # Iterates through the parent classes adding the new parents properties to the start of the list
        while selected_class["Parent"]:
            selected_class = db_manager.get_doc_from_where("EventClasses",
                                                           {"Name": {"$eq": selected_class["Parent"]}})
            properties.update(selected_class["Properties"])
            defaults.update(selected_class["Defaults"])
        for key, value in reversed(properties.items()):
            row = dict()
            row["Property Name"] = key
            row["Data Type"] = value
            row["Default Value"] = defaults[key] if key in defaults else None
            properties_table_model.add_row(row)
        self.EventClassDetails.setModel(properties_table_model)
        self.EditEventClass.setEnabled(True)

    def edit_event_class(self):
        edit_event_class_window = ManageEventClasses(self.update_event_classes_tree,
                                                     self.EventClassTree.currentItem().text(0))
        edit_event_class_window.show()

    def new_event_class(self):
        new_event_class_window = ManageEventClasses(self.update_event_classes_tree)
        new_event_class_window.show()

    def selected_entry(self):
        selected_indexes = self.EntriesTable.selectionModel().selectedRows()
        if not selected_indexes:
            return False
        selected_row = selected_indexes[0].row()
        title = self.entries_table_model.get_cell(selected_row, "Title")
        date = self.entries_table_model.get_cell(selected_row, "Date")
        query = {"EntryTitle": {"$eq": title},
                 "EntryDateTime": {"$gte": datetime.combine(date.toPyDate(), datetime.min.time()),
                                   "$lt": datetime.combine(date.addDays(1).toPyDate(), datetime.min.time())}}
        return db_manager.get_doc_from_where("Entries", query)

    def update_entry(self):
        new_entry_doc = {"EntryDateTime": self.EntryDateTime.dateTime().toPyDateTime(),
                         "EntryTitle": self.EntryTitle.text(),
                         "EntryContents": self.EntryContent.toPlainText()}

        if not (selected_entry := self.selected_entry()):
            db_manager.add_doc("Entries", new_entry_doc)
        elif db_manager.update_doc_from("Entries", selected_entry,
                                        {"$set": new_entry_doc}).matched_count > 0:
            print(f"Entry Updated")
        self.update_entries_table()

        self.UpdateEntryButton.setEnabled(False)

    def new_entry(self):
        self.EntryTitle.setText("")
        self.EntryTitle.setFocus(Qt.FocusReason.OtherFocusReason)
        self.EntryContent.setText("")
        self.EntryDateTime.setDateTime(QtCore.QDateTime.currentDateTime())

        self.UpdateEntryButton.setText("Add Entry")
        self.UpdateEntryButton.setEnabled(False)

        self.update_entries_table()


    def show_entry_details(self):
        if not (selected_entry := self.selected_entry()):
            return False

        self.EntryTitle.setText(selected_entry["EntryTitle"])
        self.EntryContent.setText(selected_entry["EntryContents"])
        self.EntryDateTime.setDateTime(QtCore.QDateTime(selected_entry["EntryDateTime"]))
        self.UpdateEntryButton.setText("Update Entry")

        self.UpdateEntryButton.setEnabled(False)

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
