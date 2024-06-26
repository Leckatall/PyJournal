
from PyQt6 import QtCore, uic, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTableView, QLineEdit, QComboBox
import DB_Mongo as db_manager
import MyDatatypes


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


class ManageEventClasses(QWidget):
    def __init__(self, update_event_class_list_method):
        super().__init__()
        self.ui = uic.loadUi("manage_event_class.ui", self)
        # Widgets added by "new_event_class.ui"
        self.ClassProperties: QtWidgets.QTableView
        self.ConfirmAddEventClass: QPushButton
        self.ClearProperty: QPushButton
        self.ParentClass: QComboBox
        self.PropertyDataType: QtWidgets.QComboBox
        self.ClassName: QLineEdit
        self.PropertyName: QLineEdit
        self.AddProperty: QPushButton

        self.update_event_classes_tree()
        self.EventClassesTree.clicked.connect(self.update_class_properties)
        self.EditParentClassButton.clicked.connect(self.edit_event_class)

        self.UpdateEventClassButton.clicked.connect(self.update_event_class)

        # Enables UpdateEntryButton when the entry is modified
        def entry_modified():
            self.UpdateEventClassButton.setEnabled(True)
        #TODO:
        # self.EntryTitle.editingFinished.connect(entry_modified)
        # self.EntryContent.textChanged.connect(entry_modified)
        # self.EntryDateTime.dateTimeChanged.connect(entry_modified)

        self.update_method = update_event_class_list_method
        # self.starting_event_class_name = ""
        # self.original_doc = db_manager.get_doc_from_where("EventClasses",
        #                                                         {"Name": {"$eq": event_class_name}})
        self.new_properties = dict()
        self.new_defaults = dict()
        # self.ParentClass.addItems([event_class["Name"] for event_class in db_manager.get_docs_from("EventClasses")])
        #
        # if event_class_name:
        #     # Editing a Class not creating a new one
        #     self.ClassName.setText(event_class_name)
        #     self.ParentClass.setCurrentIndex(self.ParentClass.findText(self.original_doc["Parent"],
        #                                                                Qt.MatchFlag.MatchFixedString))
        #     self.new_properties = self.original_doc["Properties"]
        #     self.new_defaults = self.original_doc["Defaults"]
        #     self.update_class_properties()
        #     self.ConfirmAddEventClass.setText(f"Update {event_class_name}")

        self.editing_event_class = ""

        # initializing comboboxes
        self.PropertyDatatype.addItems([data_type["Name"] for data_type in db_manager.get_docs_from("DataTypes")])

        # Adding custom properties
        self.AddPropertyButton.clicked.connect(self.add_property)

        def enable_add_property():
            if self.PropertyName.text() and self.PropertyDatatype.currentText():
                self.AddPropertyButton.setEnabled(True)
            else:
                self.AddPropertyButton.setEnabled(False)

        self.PropertyName.textChanged.connect(enable_add_property)
        self.PropertyDatatype.currentIndexChanged.connect(enable_add_property)

        # Don't let the user add a class without a name or parent
        def enable_add_class():
            if self.ClassName.text() and self.EventClassesTree.currentItem():
                self.UpdateEventClassButton.setEnabled(True)
            else:
                self.UpdateEventClassButton.setEnabled(False)

        self.ClassName.textChanged.connect(enable_add_class)
        # self.ParentClass.currentIndexChanged.connect(enable_add_class)
        self.UpdateEventClassButton.clicked.connect(self.add_event_class)

    def update_class_properties(self):
        self.ShowParentLabel.setText(f"Inherits: {self.EventClassesTree.currentItem().text(0)}")
        properties_table_model = TableModel(["Property Name", "Data Type", "Default"])
        inherited_properties: dict = dict()
        inherited_defaults: dict = dict()
        if parent_class_name := self.EventClassesTree.currentItem().text(0):
            parent_class = db_manager.get_doc_from_where("EventClasses",
                                                         {"Name": {"$eq": parent_class_name}})
            inherited_properties.update(parent_class["Properties"])
            inherited_defaults.update(parent_class["Defaults"])
            # Iterates through the parent classes adding the new parents properties to the start of the list
            while parent_class["Parent"]:
                parent_class = db_manager.get_doc_from_where("EventClasses",
                                                             {"Name": {"$eq": parent_class["Parent"]}})
                inherited_properties.update(parent_class["Properties"])
                inherited_defaults.update(parent_class["Defaults"])

        for key, value in inherited_properties.items():
            row = dict()
            row["Property Name"] = key
            row["Data Type"] = value
            # row["Default"] = self.new_defaults[key] if key in self.new_defaults else inherited_defaults.get(key, "")
            # print(f"{self.new_defaults.get(key, "") = }")
            properties_table_model.add_row(row)

        # Update Table of new properties
        for key, value in self.new_properties.items():
            row = dict()
            row["Data Type"] = value
            # row["Default"] = self.new_defaults.get(key, "")
            # print(f"{self.new_defaults.get(key, "") = }")

            properties_table_model.add_row(row)

        properties_table_model.groupings = [(0, len(inherited_properties), "Inherited"),
                                            (len(inherited_properties), properties_table_model.rowCount(), "New")]
        self.ClassProperties.setModel(properties_table_model)

        # Vertical header separating inherited and non-inherited properties
        # header = CustomWidgets.BandedHeaderView(Qt.Orientation.Vertical)
        # self.ClassProperties.setVerticalHeader(header)
        # header.add_band(0, 2, "Inherited Properties")
        # header.add_band(3, 4, "New Properties")

    def update_event_classes_tree(self):
        self.EventClassesTree.clear()
        event_classes = db_manager.get_docs_from("EventClasses")
        tree_item_dict = dict()
        for event_class in event_classes:
            if event_class["Parent"]:
                if not (parent := tree_item_dict.get(event_class["Parent"], False)):
                    event_classes.append(parent)
                    print("parent not processed adding to end of list")
                    continue
            else:
                parent = self.EventClassesTree
            event_defaults = event_class["Defaults"]
            event_properties = event_class["Properties"]
            new_item = QtWidgets.QTreeWidgetItem(parent, [event_class["Name"], ",\n".join(
                [f"{key}: {value}" for key, value in event_properties.items()] +
                [f"{key}: ({value})" for key, value in event_defaults.items()])])
            tree_item_dict[event_class["Name"]] = new_item

    def edit_event_class(self):
        event_class_name = self.EventClassesTree.currentItem().text(0)
        self.editing_event_class = event_class_name
        self.original_doc = db_manager.get_doc_from_where(
            "EventClasses",
            {"Name": {"$eq": event_class_name}})

        self.ClassName.setText(event_class_name)
        self.EventClassesTree.setCurrentItem(self.EventClassesTree.currentItem().parent())

        self.new_properties = self.original_doc["Properties"]
        self.new_defaults = self.original_doc["Defaults"]
        self.update_class_properties()

        self.UpdateEventClassButton.setText(f"Update {event_class_name}")

    def update_new_property_units(self):
        ...

    def selected_event_class(self):
        ...

    def update_event_class(self):
        event_class_doc = {"Name": self.ClassName.text(),
                           "ParentClass": self.ParentClass.currentText(),
                           "EntryContents": self.EntryContent.toPlainText()}

        if not self.EventClassesTree.currentItem():
            db_manager.add_doc("Entries", event_class_doc)
        elif db_manager.update_doc_from("Entries", self.EventClassesTree.currentItem().text(0),
                                        {"$set": event_class_doc}).matched_count > 0:
            print("Event Class Updated")
        else:
            print("Failed to update Event Class")

    def selected_property(self):
        print("finding selected property")
        selected_indexes = self.ClassProperties.selectionModel().selectedRows()
        if not selected_indexes:
            return False
        selected_row = selected_indexes[0].row()
        property_name = self.ClassProperties.model().get_cell(selected_row, "Property Name")
        property_dt = self.ClassProperties.model().get_cell(selected_row, "Data Type")
        property_default = self.ClassProperties.model().get_cell(selected_row, "Default")
        print(f"{property_name = }, {property_dt = }, {property_default = }")
        return {"Name": property_name,
                "DataType": property_dt,
                "Default": property_default}

    def add_property_default(self):
        if not (selected_property := self.selected_property()):
            return False
        if (layout := self.PropertyDefaultWidgetFrame.layout()) and (layout.count()):
            widget = layout.itemAt(0).widget()
            new_property_default = {
                selected_property["Name"]: MyDatatypes.DT_WIDGET_TO_DATA[selected_property["DataType"]](widget)
            }
            self.new_defaults.update(new_property_default)
            self.update_class_properties()
            self.DefaultPropertyLabel.setText("Default Value of: ")
            widget.deleteLater()

    def add_property(self):
        new_property = {
            self.PropertyName.text(): self.PropertyDatatype.currentText()
        }
        self.new_properties.update(new_property)
        self.PropertyName.clear()
        self.PropertyDatatype.setCurrentIndex(-1)
        self.update_class_properties()

    def add_event_class(self):
        doc = {
            "Name": self.ClassName.text(),
            "Parent": self.ParentClass.currentText(),
            "Properties": self.new_properties,
            "Defaults": self.new_defaults
        }
        print(f"{doc = }")
        if self.event_class_name:
            db_manager.update_doc_from("EventClasses", self.original_doc, {"$set": doc})
        else:
            db_manager.add_doc("EventClasses", doc)
        self.update_method()
        self.close()