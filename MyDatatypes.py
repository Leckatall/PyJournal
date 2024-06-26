from abc import ABC

from PyQt6 import QtWidgets

DT_TO_WIDGET = {
    "any": "any",
    "datetime": QtWidgets.QDateTimeEdit,
    "int": QtWidgets.QSpinBox,
    "str": QtWidgets.QLineEdit,
    "float": QtWidgets.QDoubleSpinBox,
    "bool": QtWidgets.QCheckBox,
    "list": "find widget",
    "event": "another Event?!",
    "Mass": "",
    "Volume": "",
    "Area": "",
    "Distance": "",
    "Time": "",
    "Temperature": ""
}

DT_WIDGET_TO_DATA = {
    "datetime": lambda x: x.dateTime().toPyDateTime(),
    "int": lambda x: x.value(),
    "float": lambda x: x.value(),
    "str": lambda x: x.text(),
    "bool": lambda x: x.isChecked()
}

DT_WIDGET_SET_DATA = {
    "datetime": lambda widget, value: widget.setDateTime(value),
    "int": lambda widget, value: widget.setValue(value),
    "float": lambda widget, value: widget.setValue(value),
    "str": lambda widget, value: widget.setText(value),
    "bool": lambda widget, value: widget.setChecked(value)
}

DTT = {
    "$": "Const Value",
    "^": "Inherit from container",
    "+": "Compound data type"
}


class DataWidget(ABC):
    def widget(self):
        ...

    def set_value(self):
        ...


def string_to_DataWidget(datatype) -> DataWidget:
    match datatype:
        case "int":
            ...
        case "str":
            ...


