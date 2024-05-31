import sys
from PyQt6 import QtCore, uic, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTableView, QLineEdit, QComboBox
import DB_Mongo as db_manager
from datetime import datetime


DT_TO_WIDGET = {
            "datetime": QtWidgets.QDateTimeEdit,
            "int": QtWidgets.QSpinBox,
            "str": QtWidgets.QLineEdit,
            "float": QtWidgets.QDoubleSpinBox,
            "bool": QtWidgets.QCheckBox
        }
DT_WIDGET_TO_DATA = {
            "datetime": lambda x: x.dateTime().toPyDateTime(),
            "int": lambda x: x.value(),
            "float": lambda x: x.value(),
            "str": lambda x: x.text(),
            "bool": lambda x: x.isChecked()
        }


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, headers, parent=None, orientation=Qt.Orientation.Horizontal):
        super(TableModel, self).__init__(parent)
        self.headers = headers
        self.orientation = orientation
        self._data: list[dict] = []

    def get_cell(self, row, column):
        return self._data[row].get(column, False)

    def add_row(self, row: dict):
        self._data.append(row)

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
        if role != Qt.ItemDataRole.DisplayRole or orientation != self.orientation:
            return QtCore.QVariant()
        # What's the header for the given section?
        return self.headers[section]


class TableViewDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, table_view, parent=None):
        super().__init__(parent)
        self.table_view = table_view

    def createEditor(self, parent, option, index):
        table_widget = QtWidgets.QTableWidget(parent)
        table_widget.setRowCount(2)  # Example row count
        table_widget.setColumnCount(2)  # Example column count
        # Fill the inner table with some example data
        for row in range(2):
            for column in range(2):
                item = QtWidgets.QTableWidgetItem(f"{row},{column}")
                table_widget.setItem(row, column, item)
        return table_widget

    def setEditorData(self, editor, index):
        pass

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


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
            "isRecurringTask": self.ReccuringTask.isChecked()
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


class NewEventClass(QWidget):
    def __init__(self, update_event_class_list_method):
        super().__init__()
        self.ui = uic.loadUi("new_event_class.ui", self)
        # Widgets added by "new_event_class.ui"
        self.ClassProperties: QtWidgets.QTableView
        self.ConfirmAddEventClass: QPushButton
        self.ClearProperty: QPushButton
        self.ParentClass: QComboBox
        self.PropertyDataType: QtWidgets.QComboBox
        self.ClassName: QLineEdit
        self.PropertyName: QLineEdit
        self.AddProperty: QPushButton

        self.update_method = update_event_class_list_method
        self.new_properties = dict()
        self.new_property_defaults = dict()

        # initializing comboboxes
        self.PropertyDataType.addItems([data_type["Name"] for data_type in db_manager.get_docs_from("DataTypes")])
        self.update_parent_class_options()
        self.ParentClass.currentIndexChanged.connect(self.update_class_properties)

        # Adding custom properties
        self.AddProperty.clicked.connect(self.add_property)

        # Setting default property values
        self.PropertyDefaultWidget = None
        self.NewDefaultProperty.clicked.connect(self.add_property_default)

        def enable_add_property():
            if self.PropertyName.text() and self.PropertyDataType.currentText():
                self.AddProperty.setEnabled(True)
            else:
                self.AddProperty.setEnabled(False)

        self.PropertyName.textChanged.connect(enable_add_property)
        self.PropertyDataType.currentIndexChanged.connect(enable_add_property)

        # Don't let the user add a class without a name or parent
        def enable_add_class():
            if self.ClassName.text() and self.ParentClass.currentText():
                self.ConfirmAddEventClass.setEnabled(True)
            else:
                self.ConfirmAddEventClass.setEnabled(False)

        self.ClassName.textChanged.connect(enable_add_class)
        self.ParentClass.currentIndexChanged.connect(enable_add_class)
        self.ConfirmAddEventClass.clicked.connect(self.add_event_class)
        self.ClassProperties.clicked.connect(self.select_property_default)

    def update_parent_class_options(self):
        self.ParentClass.addItems(
            [event_class["Name"] for event_class in db_manager.get_docs_from("EventClasses")])

    def update_class_properties(self):
        properties_table_model = TableModel(["Property Name", "Value"])
        event_properties: dict = dict(self.new_properties)
        event_defaults: dict = dict(self.new_property_defaults)
        if parent_class_name := self.ParentClass.currentText():
            parent_class = db_manager.get_doc_from_where("EventClasses",
                                                         {"Name": {"$eq": parent_class_name}})
            event_properties.update(parent_class["Properties"])
            event_defaults.update(parent_class["Defaults"])
            # Iterates through the parent classes adding the new parents properties to the start of the list
            while parent_class["Parent"]:
                parent_class = db_manager.get_doc_from_where("EventClasses",
                                                             {"Name": {"$eq": parent_class["Parent"]}})
                event_properties.update(parent_class["Properties"])
                event_defaults.update(parent_class["Defaults"])

        for key, value in event_properties.items():
            row = dict()
            row["Property Name"] = key
            row["Value"] = f"{value}({event_defaults[key]})" if key in event_defaults else value
            properties_table_model.add_row(row)
        self.ClassProperties.setModel(properties_table_model)

    def selected_property(self):
        print("finding selected property")
        selected_indexes = self.ClassProperties.selectionModel().selectedRows()
        if not selected_indexes:
            return False
        selected_row = selected_indexes[0].row()
        property_name = self.ClassProperties.model().get_cell(selected_row, "Property Name")
        property_dt = self.ClassProperties.model().get_cell(selected_row, "Value").split("(")[0]
        print(f"{property_name = }, {property_dt = }")
        return {"Name": property_name,
                "DataType": property_dt}

    def select_property_default(self):
        if not (selected_property := self.selected_property()):
            return False
        if (layout := self.PropertyDefaultWidgetFrame.layout()) and (layout.count()):
            layout.takeAt(0).widget().deleteLater()
        self.PropertyDefaultWidget = DT_TO_WIDGET[selected_property["DataType"]]()
        self.DefaultPropertyLabel.setText(f"Default Value of: **{selected_property['Name']}**")
        self.PropertyDefaultWidgetFrame.layout().addWidget(DT_TO_WIDGET[selected_property["DataType"]]())

    def add_property_default(self):
        if not (selected_property := self.selected_property()):
            return False
        if (layout := self.PropertyDefaultWidgetFrame.layout()) and (layout.count()):
            widget = layout.itemAt(0).widget()
            new_property_default = {
                selected_property["Name"]: DT_WIDGET_TO_DATA[selected_property["DataType"]](widget)
            }
            self.new_property_defaults.update(new_property_default)
            self.update_class_properties()
            self.DefaultPropertyLabel.setText("Default Value of: ")
            widget.deleteLater()

    def add_property(self):
        new_property = {
            self.PropertyName.text(): self.PropertyDataType.currentText()
        }
        self.new_properties.update(new_property)
        self.PropertyName.clear()
        self.PropertyDataType.setCurrentIndex(-1)
        self.update_class_properties()

    def add_event_class(self):
        doc = {
            "Name": self.ClassName.text(),
            "Parent": self.ParentClass.currentText(),
            "Properties": self.new_properties,
            "Defaults": self.new_property_defaults
        }
        print(f"{doc = }")
        db_manager.add_doc("EventClasses", doc)
        self.update_method()
        self.close()


class NewEventInstance(QtWidgets.QDialog):
    def __init__(self, update_event_list_method):
        super().__init__()
        self.ui = uic.loadUi("add_event_instance.ui", self)

        # properties added by "new_event_instance.ui"
        self.EventDateTime: QtWidgets.QDateTimeEdit
        self.formLayout: QtWidgets.QFormLayout
        self.buttonBox: QtWidgets.QDialogButtonBox
        self.EventClass: QComboBox

        self.update_method = update_event_list_method

        self.EventClass.addItems([event_class["Name"] for event_class in db_manager.get_docs_from("EventClasses")])
        self.EventDateTime.setDateTime(QtCore.QDateTime.currentDateTime())

        self.EventClass.currentIndexChanged.connect(self.update_form)
        self.buttonBox.accepted.connect(self.add_event_instance)
        self.buttonBox.rejected.connect(self.close)

        self.form_widgets: dict = dict()
        self.dt_to_widget = {
            "datetime": QtWidgets.QDateTimeEdit,
            "int": QtWidgets.QSpinBox,
            "str": QtWidgets.QLineEdit,
            "float": QtWidgets.QDoubleSpinBox,
            "bool": QtWidgets.QCheckBox
        }
        self.dt_widget_to_data = {
            "datetime": lambda x: x.dateTime().toPyDateTime(),
            "int": lambda x: x.value(),
            "float": lambda x: x.value(),
            "str": lambda x: x.text(),
            "bool": lambda x: x.isChecked()
        }

    def update_form(self):
        print(f"{self.form_widgets = }")
        for widget in self.form_widgets.values():
            self.formLayout.removeRow(widget)
        event_class_name = self.EventClass.currentText()
        event_properties = db_manager.get_all_properties_of("EventClasses",
                                                            {"Name": {"$eq": event_class_name}})
        event_properties.pop("date_time")
        self.form_widgets = dict()
        for key, value in reversed(event_properties.items()):
            self.form_widgets[key] = self.dt_to_widget[value]()
            self.formLayout.addRow(key, self.form_widgets[key])

    def add_event_instance(self):
        event_properties = db_manager.get_all_properties_of("EventClasses",
                                                            {"Name": {"$eq": self.EventClass.currentText()}})
        event_properties.pop("date_time")
        doc = {
            "Class": self.EventClass.currentText(),
            "date_time": self.EventDateTime.dateTime().toPyDateTime(),
            "Comment": "blank for now",
            "Properties": {property: self.dt_widget_to_data[dt](self.form_widgets[property])
                           for property, dt in event_properties.items()}
        }
        print(f"{doc = }")
        db_manager.add_doc("Events", doc)
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

        self.update_entries_table()
        self.EntriesTable.clicked.connect(self.show_entry_details)

        self.UpdateEntryButton.clicked.connect(self.update_entry)

        # Enables UpdateEntryButton when the entry is modified
        self.EntryTitle.editingFinished.connect(self.entry_modified)
        self.EntryContent.textChanged.connect(self.entry_modified)
        self.EntryDateTime.dateTimeChanged.connect(self.entry_modified)

        # Events Tab
        self.NewEventClass: QPushButton
        self.NewEventClass.clicked.connect(self.new_event_class)
        self.NewEventInstance.clicked.connect(self.new_event_instance)
        self.update_event_classes_tree()
        self.EventClassTree.itemClicked.connect(self.show_event_class_details)

        self.events_table_model = TableModel(["Date", "Type"])
        self.update_events_table()
        self.EventsTable.clicked.connect(self.show_event_details)

        self.events_details_table_model = TableModel(["Date", "Type", "Comment", "Properties"])
        self.EventDetailsTable.setModel(self.events_details_table_model)

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

    def show_event_details(self):
        if not (selected_event := self.selected_event()):
            return False
        print(f"{selected_event = }")
        self.events_details_table_model = TableModel(["Date", "Type", "Comment", "Properties"],
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
        self.events_details_table_model.add_row(row)
        print(f"{row = }")
        self.EventDetailsTable.setModel(self.events_details_table_model)

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
            new_item = QtWidgets.QTreeWidgetItem(parent, [event_class["Name"], ",\n".join(
                [f"{key}: {value}" for key, value in event_class["Properties"].items()])])
            tree_item_dict[event_class["Name"]] = new_item

    def show_event_class_details(self):
        properties_table_model = TableModel(["Property Name", "Data Type"])
        properties = dict()
        selected_class = db_manager.get_doc_from_where("EventClasses",
                                                       {"Name": {"$eq": self.EventClassTree.currentItem().text(0)}})
        properties.update(selected_class["Properties"])
        # Iterates through the parent classes adding the new parents properties to the start of the list
        while selected_class["Parent"]:
            selected_class = db_manager.get_doc_from_where("EventClasses",
                                                           {"Name": {"$eq": selected_class["Parent"]}})
            properties.update(selected_class["Properties"])
        for key, value in reversed(properties.items()):
            row = dict()
            row["Property Name"] = key
            row["Data Type"] = value
            properties_table_model.add_row(row)
        self.EventClassDetails.setModel(properties_table_model)

    def new_event_class(self):
        new_event_class_window = NewEventClass(self.update_event_classes_tree)
        new_event_class_window.show()

    def entry_modified(self):
        self.UpdateEntryButton.setEnabled(True)

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
        if not (selected_entry := self.selected_entry()):
            return False
        # There is no property to check if datetime has been changed so will just always update lol
        # This works as a nice default tho :)
        update_operation = {"$set": {"EntryDateTime": self.EntryDateTime.dateTime().toPyDateTime()}}
        if self.EntryTitle.isModified():
            update_operation["$set"]["EntryTitle"] = self.EntryTitle.text()
        if self.EntryContent.document().isModified():
            update_operation["$set"]["EntryContents"] = self.EntryContent.toPlainText()

        if db_manager.update_doc_from("Entries", selected_entry, update_operation).matched_count > 0:
            print(f"Entry Updated")
            self.update_entries_table()

        self.UpdateEntryButton.setEnabled(False)

    def new_entry(self):
        add_entry_window = AddEntry(self.update_entries_table)
        add_entry_window.show()

    def show_entry_details(self):
        if not (selected_entry := self.selected_entry()):
            return False

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
