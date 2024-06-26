from PyQt6 import QtCore, uic, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTableView, QLineEdit, QComboBox
import DB_Mongo as db_manager


class NewProjectClass(QWidget):
    def __init__(self, update_project_class_list_method):
        super().__init__()
        self.ui = uic.loadUi("new_project_class.ui", self)
        self.update_method = update_project_class_list_method

        # Widgets added by "new_event_class.ui"
        self.ClassProperties: QtWidgets.QTableView
        self.ConfirmAddEventClass: QPushButton
        self.ClearProperty: QPushButton
        self.ParentClass: QComboBox
        self.PropertyDataType: QtWidgets.QComboBox
        self.ClassName: QLineEdit
        self.PropertyName: QLineEdit
        self.AddProperty: QPushButton

        self.TaskType.addItems([data_type["Name"] for data_type in db_manager.get_docs_from("DataTypes")])
        self.ProjectType.addItems(["Continuous", "Singular", "Recurring"])

        self.project_tasks: list[dict] = []

        self.update_project_tasks()

    def update_project_tasks(self):
        properties_table_model = TableModel(["Task", "Type", "Weighting"])
        for task in self.project_tasks:
            # for key, value in task.items():
            #     row = dict()
            #     row["Task"] = key
            #     row["Type"] = value["Type"]
            #     row["Weighting"] = value["Weighting"]
            #     properties_table_model.add_row(row)
            properties_table_model.add_row(task)
        self.TaskTable.setModel(properties_table_model)





