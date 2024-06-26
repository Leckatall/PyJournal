from PyQt6 import QtCore, uic, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QTableView, QLineEdit, QComboBox
import DB_Mongo as db_manager

import MyDatatypes


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
        # self.EventDateTime.setDateTime(QtCore.QDateTime.currentDateTime())

        self.EventClass.currentIndexChanged.connect(self.update_form)
        self.buttonBox.accepted.connect(self.add_event_instance)
        self.buttonBox.rejected.connect(self.close)

        self.form_widgets: dict = dict()

    def update_form(self):
        print(f"{self.form_widgets = }")
        for widget in self.form_widgets.values():
            self.formLayout.removeRow(widget)
        event_class_name = self.EventClass.currentText()
        event_properties = db_manager.get_all_properties_of("EventClasses",
                                                            {"Name": {"$eq": event_class_name}})
        self.form_widgets = dict()
        for key, value in reversed(event_properties.items()):
            self.form_widgets[key] = MyDatatypes.DT_TO_WIDGET[value]()
            self.formLayout.addRow(key, self.form_widgets[key])

    def add_event_instance(self):
        event_properties = db_manager.get_all_properties_of("EventClasses",
                                                            {"Name": {"$eq": self.EventClass.currentText()}})
        doc = {
            "Class": self.EventClass.currentText(),
            "date_time": self.EventDateTime.dateTime().toPyDateTime(),
            "Comment": "blank for now",
            "Tags": ["TBD"],
            "Properties": {property: MyDatatypes.DT_WIDGET_TO_DATA[dt](self.form_widgets[property])
                           for property, dt in event_properties.items()}
        }
        print(f"{doc = }")
        db_manager.add_doc("Events", doc)
        self.update_method()
        self.close()

