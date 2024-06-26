from PyQt6 import uic

from PyQt6.QtWidgets import QWidget
import DB_Mongo as db_manager


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
