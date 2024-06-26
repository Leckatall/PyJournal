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


class GroupedTableModel(QtCore.QAbstractTableModel):
    def __init__(self, headers, groups, parent=None, orientation=Qt.Orientation.Horizontal):
        super(GroupedTableModel, self).__init__(parent)
        self.headers = headers
        self.groups = groups
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
        if role != Qt.ItemDataRole.DisplayRole:
            return QtCore.QVariant()
        if orientation != self.orientation:
            return self.groups[section]
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
# GPT attempt 3


class CustomTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, headers, parent=None):
        super().__init__(parent)
        self._data = data
        self._headers = headers

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data[0])

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
            if orientation == Qt.Orientation.Vertical:
                return f"Row {section}"
        return QtCore.QVariant()


class BandedHeaderView(QtWidgets.QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.bands = []
        self.resizeSection()


    def add_band(self, start, end, title):
        self.bands.append((start, end, title))

    def paintSection(self, painter, rect, logicalIndex):
        for start, end, title in self.model().groupings:
            if start <= logicalIndex <= end:
                if logicalIndex == start:
                    painter.save()
                    option = QStyleOptionHeader()
                    self.initStyleOption(option)
                    if self.orientation() == Qt.Orientation.Horizontal:
                        option.rect = QRect(rect.left(), rect.top(), rect.width() * (end - start + 1), rect.height())
                    else:
                        option.rect = QRect(rect.left(), rect.top(), rect.width(), rect.height() * (end - start + 1))
                    option.text = title
                    self.style().drawControl(self.style().ControlElement.CE_Header, option, painter)
                    painter.restore()
                return
        super().paintSection(painter, rect, logicalIndex)

        def sectionSizeFromContents(self, logicalIndex):
            size = super().sectionSizeFromContents(logicalIndex)
            for start, end, _ in self.bands:
                if start <= logicalIndex <= end:
                    if self.orientation() == Qt.Orientation.Horizontal:
                        size.setWidth(size.width() * (end - start + 1))
                    else:
                        size.setHeight(size.height() * (end - start + 1))
            return size

import sys
from PyQt6.QtWidgets import QApplication, QTableWidget, QHeaderView, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QModelIndex, QEvent, QVariant


class MyHeaderModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(MyHeaderModel, self).__init__(parent)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        return QVariant()

    def index(self, row, column, parent=QModelIndex()):
        return QModelIndex()

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return 0


class MyHeader(QHeaderView):
    def __init__(self, header, parent=None):
        super(MyHeader, self).__init__(Qt.Orientation.Horizontal, header)
        self.mainHeader = header
        self.setModel(MyHeaderModel(self))
        # This example uses hardcoded groups, you can extend
        # this yourself to save the groups
        # Group 1 is 0-2 and Group 2 is 3-4
        self.resizeSection(0, self.getSectionSizes(0, 2))
        self.resizeSection(1, self.getSectionSizes(3, 4))
        self.sectionResized.connect(self.updateSizes)
        self.mainHeader.parentWidget().horizontalScrollBar().valueChanged.connect(self.updateOffset)
        self.setGeometry(0, 0, header.width(), header.height())
        self.updateOffset()
        self.mainHeader.installEventFilter(self)

    def updateSizes(self):
        self.setOffset(self.mainHeader.offset())
        self.mainHeader.resizeSection(2, self.mainHeader.sectionSize(2) + (self.sectionSize(0) - self.getSectionSizes(0, 2)))
        self.mainHeader.resizeSection(4, self.mainHeader.sectionSize(4) + (self.sectionSize(1) - self.getSectionSizes(3, 4)))

    def updateOffset(self):
        self.setOffset(self.mainHeader.offset())

    def eventFilter(self, obj, event):
        if obj == self.mainHeader:
            if event.type() == QEvent.Type.Resize:
                self.setOffset(self.mainHeader.offset())
                self.setGeometry(0, 0, self.mainHeader.width(), self.mainHeader.height())
            return False
        return QHeaderView.eventFilter(self, obj, event)

    def getSectionSizes(self, first, second):
        size = 0
        for a in range(first, second + 1):
            size += self.mainHeader.sectionSize(a)
        return size


def make_banded_table_view(table_view):
    # Set custom horizontal header view
    horizontal_header = BandedHeaderView(Qt.Orientation.Horizontal)
    table_view.setHorizontalHeader(horizontal_header)

    # Add horizontal banded headers
    horizontal_header.add_band(0, 2, "Band 1")
    horizontal_header.add_band(3, 4, "Band 2")

    # # Set custom vertical header view
    # vertical_header = BandedHeaderView(Qt.Orientation.Vertical)
    # table_view.setVerticalHeader(vertical_header)
    #
    # # Add vertical banded headers
    # vertical_header.add_band(0, 2, "V-Band 1")
    # vertical_header.add_band(2, 2, "V-Band 2")
    # vertical_header.add_band(4, 1, "V-Band 3")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nested QTableView Example")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QtWidgets.QVBoxLayout(central_widget)
        self.table_view = QTableView(central_widget)


        # Sample data
        data = [
            [1, 2, 3, 4, 5],
            [11, 12, 13, 14, 15]
        ]

        headers = ["Col 0", "Col 1", "Col 2", "Col 3", "Col 4"]
        model = CustomTableModel(data, headers)
        self.table_view.setModel(model)
        self.table_view.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                      QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        header = MyHeader(self.table_view.horizontalHeader())
        # self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        # self.table_view.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        # self.child_table = QTableView()
        # data = [
        #     ["a", "b"],
        #     ["c", "d"]
        # ]
        # child_headers = ["Col A", "Col B"]
        # child_model = CustomTableModel(data, child_headers)
        # self.child_table.setModel(child_model)
        # self.child_table.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
        #                               QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        # self.child_table.setSpan(0,0, 2, 1)
        # self.table_view.setIndexWidget(model.index(0, 0), self.child_table)
        #
        # self.table_view.resizeRowsToContents()
        # self.table_view.resizeColumnsToContents()

        # Add the table view to the layout
        self.layout.addWidget(self.table_view)

        # horizontal_header = BandedHeaderView(Qt.Orientation.Vertical)
        # self.table_view.setVerticalHeader(horizontal_header)
        #
        # # Add horizontal banded headers
        # horizontal_header.add_band(0, 2, "Group 1")
        # horizontal_header.add_band(3, 4, "Group 2")

        # Button to apply banded header
        self.button = QPushButton("Apply Banded Header")
        self.button.clicked.connect(self.apply_banded_header)
        self.layout.addWidget(self.button)

    def apply_banded_header(self):
        make_banded_table_view(self.table_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())









