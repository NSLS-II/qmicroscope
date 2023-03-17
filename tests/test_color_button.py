import pytest
from qtpy.QtGui import QColor, QMouseEvent
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import Qt
from microscope.widgets.color_button import ColorButton


@pytest.fixture
def button():
    app = QApplication([])
    button = ColorButton(color=QColor("blue"))
    yield button
    app.quit()


def test_default_color(button):
    assert button.color() == QColor("blue")


def test_setting_color(button):
    button.setColor(QColor("red"))
    assert button.color() == QColor("red")
    assert button.styleSheet() == "background-color: #ff0000"


def test_color_picker_dialog(button, mocker):
    mocker.patch("qtpy.QtWidgets.QColorDialog.getColor", return_value=QColor("green"))
    button.onColorPicker()
    assert button.color() == QColor("green")
    assert button.styleSheet() == "background-color: #008000"
