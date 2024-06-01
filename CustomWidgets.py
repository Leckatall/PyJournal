import sys
from PyQt6 import QtCore, uic, QtWidgets
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTableView, QLineEdit, QComboBox, \
    QStyleOptionHeader


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
        table_widget.setFixedSize(QtCore.QSize(200, 100))
        # Fill the inner table with some example data
        for row in range(2):
            for column in range(2):
                item = QtWidgets.QTableWidgetItem(f"{row},{column}")
                table_widget.setItem(row, column, item)
        table_widget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        return table_widget

    def setEditorData(self, editor, index):
        ...

    def setModelData(self, editor, model, index):
        # value = editor.currentText()
        # model.setData(index, value, Qt.ItemDataRole.EditRole)
        ...

    def paint(self, painter, option, index):
        if index.isValid():
            editor = self.createEditor(option.widget, option, index)
            editor.setGeometry(option.rect)
            editor.render(painter, option.rect.topLeft(), flags=QtWidgets.QWidget.RenderFlag.DrawChildren)
        else:
            super().paint(painter, option, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


# GPT EXAMPLE
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget, QStyledItemDelegate, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize
from PyQt6.QtGui import QStandardItemModel, QStandardItem

# class OuterTableModel(QtCore.QAbstractTableModel):
#     def __init__(self, data):
#         super().__init__()
#         self._data = data
#
#     def rowCount(self, parent=None):
#         return len(self._data)
#
#     def columnCount(self, parent=None):
#         return len(self._data[0])
#
#     def data(self, index, role=Qt.ItemDataRole.DisplayRole):
#         if role == Qt.ItemDataRole.DisplayRole:
#             return self._data[index.row()][index.column()]
#         return None
#
#     def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
#         if role == Qt.ItemDataRole.EditRole:
#             self._data[index.row()][index.column()] = value
#             self.dataChanged.emit(index, index, [role])
#             return True
#         return False
#
#     def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
#         if role == Qt.ItemDataRole.DisplayRole:
#             if orientation == Qt.Orientation.Horizontal:
#                 return f"Column {section + 1}"
#             elif orientation == Qt.Orientation.Vertical:
#                 return f"Row {section + 1}"
#         return None
#
#
# class InnerTableDelegate(QStyledItemDelegate):
#
#     def eventFilter(self, source, event):
#         if event.type() == QtCore.QEvent.Type.MouseButtonPress:
#             # Handle mouse press events
#             print(f"{source = }\n {event.type() = }")
#         elif event.type() == QtCore.QEvent.Type.MouseMove:
#             # Handle mouse move events
#             pass
#         # Pass the event to the base class for default processing
#         return False
#
#     def editorEvent(self, event, model, option, index):
#         if event.type() == QtCore.QEvent.Type.MouseButtonPress:
#             # Change the checkbox-state
#             self.setModelData(None, model, index)
#             return True
#
#         return False
#
#     def setEditorData(self, editor, index):
#         # Populate the inner table based on the outer model's data
#         outer_data = index.model().data(index, Qt.ItemDataRole.DisplayRole)
#         for row in range(editor.rowCount()):
#             for column in range(editor.columnCount()):
#                 item = QTableWidgetItem(f"{outer_data} ({row},{column})")
#                 editor.setItem(row, column, item)
#
#     def setModelData(self, editor, model, index):
#         # Collect data from the inner table to update the outer model
#         # inner_data = []
#         # for row in range(editor.rowCount()):
#         #     for column in range(editor.columnCount()):
#         #         item = editor.item(row, column)
#         #         if item:
#         #             inner_data.append(item.text())
#         # model.setData(index, ', '.join(inner_data), Qt.ItemDataRole.EditRole)
#         ...
#
#     def updateEditorGeometry(self, editor, option, index):
#         editor.setGeometry(option.rect)
#
#     def paint(self, painter, option, index):
#         inner_table = QTableWidget(option.widget)
#         inner_table.viewport().installEventFilter(self)  # Install event filter
#         inner_table.setRowCount(2)  # Example row count
#         inner_table.setColumnCount(2)  # Example column count
#         inner_table.setFixedSize(QSize(option.rect.width(), option.rect.height()))  # Adjust size as needed
#         inner_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
#         # inner_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable editing
#
#         self.setEditorData(inner_table, index)
#         inner_table.setGeometry(option.rect)
#         # Calculate the correct position for the inner table within the cell
#         painter.save()
#         painter.translate(option.rect.topLeft())
#         inner_table.render(painter, flags=QtWidgets.QWidget.RenderFlag.DrawChildren)
#         painter.restore()
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         # self.ui = uic.loadUi("test_window.ui", self)
#         #
#         # table_data = [{"Title": "blah", "Rating":  2},
#         #               {"Title": "bleh", "Rating":  10}]
#         # table_model = TableModel(["Title", "Rating"])
#         # [table_model.add_row(row) for row in table_data]
#         # table = QTableView()
#         # table.setModel(table_model)
#         # table.setItemDelegate(TableViewDelegate(""))
#         # self.setCentralWidget(table)
#
#         self.setWindowTitle("Embed QTableView in QTableView Example")
#         self.setGeometry(100, 100, 800, 600)
#
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#
#         layout = QVBoxLayout(central_widget)
#
#         # Sample data for the outer table
#         data = [
#             ["Inner Table 1", "Inner Table 2"],
#             ["Inner Table 3", "Inner Table 4"]
#         ]
#
#         # Create the outer table model
#         model = OuterTableModel(data)
#
#         # Create the outer table view and set the model
#         table_view = QTableView()
#         table_view.setModel(model)
#
#         # Set the custom delegate to the outer table view
#         delegate = InnerTableDelegate(table_view)
#         table_view.setItemDelegate(delegate)
#
#         # Set fixed row and column sizes to fit inner tables correctly
#         table_view.verticalHeader().setDefaultSectionSize(120)  # Adjust row height as needed
#         table_view.horizontalHeader().setDefaultSectionSize(240)  # Adjust column width as needed
#
#         layout.addWidget(table_view)
#

# GPT attempt 2


# class InnerTableModel(QStandardItemModel):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setHorizontalHeaderLabels(['Column 1', 'Column 2'])
#         self.appendRow([QStandardItem('Data 1'), QStandardItem('Data 2')])
#
#
# class OuterTableModel(QStandardItemModel):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setHorizontalHeaderLabels(['Outer Column'])
#         # Add some dummy data to the outer model
#         for _ in range(5):
#             item = QStandardItem('Outer Data')
#             self.appendRow(item)
#
#
# class InnerTableDelegate(QStyledItemDelegate):
#     def paint(self, painter, option, index):
#         inner_table = QTableView(option.widget)
#         inner_model = InnerTableModel()
#         inner_table.setModel(inner_model)
#         inner_table.setGeometry(option.rect)
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Nested QTableView Example")
#         self.setGeometry(100, 100, 800, 600)
#
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         layout = QVBoxLayout(central_widget)
#
#         # Outer table
#         outer_model = OuterTableModel()
#         outer_table = QTableView()
#         outer_table.setModel(outer_model)
#         # outer_table.setItemDelegate(InnerTableDelegate())
#         outer_table.setItemDelegateForColumn(0, InnerTableDelegate())
#         layout.addWidget(outer_table)

# GPT attempt 3


class BandedHeaderView(QtWidgets.QHeaderView):
    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.bands = []

    def add_band(self, start, length, title):
        self.bands.append((start, length, title))

    def paintSection(self, painter, rect, logicalIndex):
        for start, length, title in self.bands:
            if start <= logicalIndex < start + length:
                if logicalIndex == start:
                    painter.save()
                    option = QStyleOptionHeader()
                    self.initStyleOption(option)
                    option.rect = QRect(rect.left(), rect.top(), rect.width() * length, rect.height())
                    option.text = title
                    self.style().drawControl(self.style().ControlElement.CE_Header, option, painter)
                    painter.restore()
                return
        super().paintSection(painter, rect, logicalIndex)


class BandedTableWidget(QTableWidget):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.banded_header_view = BandedHeaderView()
        self.setHorizontalHeader(self.banded_header_view)

        # Add banded headers
        self.banded_header_view.add_band(0, 2, "Band 1")
        self.banded_header_view.add_band(2, 2, "Band 2")
        self.banded_header_view.add_band(4, 1, "Band 3")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nested QTableView Example")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        table = BandedTableWidget(5, 5)

        # Fill the table with some data for demonstration
        for row in range(5):
            for col in range(5):
                table.setItem(row, col, QTableWidgetItem(f"Row {row}, Col {col}"))

        layout.addWidget(table)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())









