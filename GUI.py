import sys
from PyQt5.QtCore import QSize, Qt
from PyQt6 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyJournal")

        self.text_display1 = QtWidgets.QTextEdit()
        self.text_display2 = QtWidgets.QTextEdit()

        self.manage_tasks_button = QtWidgets.QPushButton("Manage Tasks")
        self.manage_tasks_button.clicked.connect(self.manage_tasks)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.text_display1)
        layout.addWidget(self.text_display2)
        layout.addWidget(self.manage_tasks_button)

        self.setLayout(layout)
        self.setGeometry(100, 100, 400, 300)


    def manage_tasks(self):
        print("manage tasks")


app = QtWidgets.QApplication(sys.argv)


window = MainWindow()
window.show()

app.exec()






